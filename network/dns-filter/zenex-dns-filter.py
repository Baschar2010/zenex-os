#!/usr/bin/env python3
"""Small local DNS policy proxy for ZENEX (stdlib only).

Listens on loopback UDP/TCP port 5353, blocks configured names, forwards other
queries to the configured upstream DoT resolver, and fails closed. This module
does not decrypt HTTPS or classify unknown domains.
"""
from __future__ import annotations

import argparse
import ipaddress
import socket
import ssl
import struct
import threading
import time
from pathlib import Path


def load_domains(path: Path) -> set[str]:
    domains = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip().rstrip(".").lower()
        if not line:
            continue
        if len(line) > 253 or any(not label or len(label) > 63 for label in line.split(".")):
            raise ValueError(f"invalid domain in policy: {line!r}")
        domains.add(line)
    return domains


def parse_question(packet: bytes) -> tuple[str, int, int]:
    if len(packet) < 17:
        raise ValueError("short DNS packet")
    flags, qdcount = struct.unpack("!HH", packet[2:6])
    if flags & 0x8000 or flags & 0x7800 or qdcount != 1:
        raise ValueError("only one-question standard DNS queries are supported")
    pos, labels = 12, []
    while True:
        if pos >= len(packet):
            raise ValueError("truncated DNS question")
        size = packet[pos]
        pos += 1
        if size == 0:
            break
        if size & 0xC0 or pos + size > len(packet):
            raise ValueError("compressed or truncated question name")
        labels.append(packet[pos:pos + size].decode("ascii").lower())
        pos += size
    if pos + 4 > len(packet):
        raise ValueError("truncated DNS question type")
    qtype, qclass = struct.unpack("!HH", packet[pos:pos + 4])
    return ".".join(labels), qtype, pos + 4


def refused(packet: bytes, qend: int) -> bytes:
    # Preserve transaction ID and question; QR=1, RA=1, RCODE=REFUSED.
    flags = struct.unpack("!H", packet[2:4])[0]
    response_flags = 0x8000 | (flags & 0x0100) | 0x0080 | 0x0005
    header = packet[:2] + struct.pack("!HHHHH", response_flags, 1, 0, 0, 0)
    return header + packet[12:qend]


def blocked(name: str, deny: set[str]) -> bool:
    return any(name == item or name.endswith("." + item) for item in deny)


class Resolver:
    def __init__(self, upstream_host: str, upstream_ip: str, port: int, deny: set[str], timeout: float):
        self.upstream_host, self.upstream_ip, self.port, self.timeout = upstream_host, upstream_ip, port, timeout
        self.family = socket.AF_INET6 if ":" in upstream_ip else socket.AF_INET
        self.blocklist_path = None
        self.deny = deny
        self.policy_lock = threading.Lock()
        self.ctx = ssl.create_default_context()

    def resolve(self, query: bytes) -> bytes:
        name, _, qend = parse_question(query)
        with self.policy_lock:
            deny = self.deny
        if blocked(name, deny):
            return refused(query, qend)
        # RFC 7858 DNS-over-TLS framing. Certificate and hostname verification
        # are performed by the default SSL context.
        # Connect to a configured literal bootstrap address to avoid a DNS
        # recursion loop, while validating TLS against the resolver hostname.
        with socket.socket(self.family, socket.SOCK_STREAM) as raw:
            raw.settimeout(self.timeout)
            raw.connect((self.upstream_ip, self.port))
            with self.ctx.wrap_socket(raw, server_hostname=self.upstream_host) as tls:
                tls.settimeout(self.timeout)
                tls.sendall(struct.pack("!H", len(query)) + query)
                size = struct.unpack("!H", recv_exact(tls, 2))[0]
                if size < 12 or size > 65535:
                    raise OSError("invalid DoT response size")
                return recv_exact(tls, size)


def recv_exact(sock: socket.socket, count: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < count:
        part = sock.recv(count - len(chunks))
        if not part:
            raise OSError("upstream closed connection")
        chunks.extend(part)
    return bytes(chunks)


def serve_one(sock: socket.socket, resolver: Resolver, data: bytes, peer, tcp: bool):
    try:
        reply = resolver.resolve(data)
    except Exception:
        # SERVFAIL; don't fall back to ISP or plaintext DNS.
        reply = data[:2] + struct.pack("!HHHHH", 0x8182, 0, 0, 0, 0)
    if tcp:
        sock.sendall(struct.pack("!H", len(reply)) + reply)
    else:
        sock.sendto(reply, peer)


def run(args):
    deny = load_domains(args.blocklist)
    if not deny:
        raise SystemExit("adult-domain policy is empty; refusing to start (fail closed)")
    try:
        ipaddress.ip_address(args.listen)
    except ValueError as exc:
        raise SystemExit(f"listen must be an IP address: {exc}")
    resolver = Resolver(args.upstream_host, args.upstream_ip, args.upstream_port, deny, args.timeout)
    resolver.blocklist_path = args.blocklist
    threading.Thread(target=reload_policy_loop, args=(resolver,), daemon=True).start()
    udp = socket.socket(socket.AF_INET6 if ":" in args.listen else socket.AF_INET, socket.SOCK_DGRAM)
    tcp = socket.socket(socket.AF_INET6 if ":" in args.listen else socket.AF_INET, socket.SOCK_STREAM)
    for sock in (udp, tcp):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((args.listen, args.port))
    tcp.listen(32)
    threading.Thread(target=udp_loop, args=(udp, resolver), daemon=True).start()
    while True:
        conn, _ = tcp.accept()
        threading.Thread(target=tcp_loop, args=(conn, resolver), daemon=True).start()


def udp_loop(sock, resolver):
    while True:
        data, peer = sock.recvfrom(4096)
        threading.Thread(target=serve_one, args=(sock, resolver, data, peer, False), daemon=True).start()


def reload_policy_loop(resolver):
    last_mtime = resolver.blocklist_path.stat().st_mtime_ns
    while True:
        time.sleep(15)
        try:
            mtime = resolver.blocklist_path.stat().st_mtime_ns
            if mtime == last_mtime:
                continue
            updated = load_domains(resolver.blocklist_path)
            if not updated:
                continue
            with resolver.policy_lock:
                resolver.deny = updated
            last_mtime = mtime
        except (OSError, ValueError):
            # Keep the last known-good policy on a partial/manual bad update.
            continue


def tcp_loop(conn, resolver):
    try:
        with conn:
            conn.settimeout(5)
            size = struct.unpack("!H", recv_exact(conn, 2))[0]
            query = recv_exact(conn, size)
            serve_one(conn, resolver, query, None, True)
    except (OSError, struct.error):
        pass


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--listen", default="127.0.0.1")
    p.add_argument("--port", type=int, default=5353)
    p.add_argument("--upstream-host", required=True, help="DoT hostname for TLS certificate validation")
    p.add_argument("--upstream-ip", required=True, help="literal bootstrap IP address (avoids DNS recursion)")
    p.add_argument("--upstream-port", type=int, default=853)
    p.add_argument("--blocklist", type=Path, required=True)
    p.add_argument("--timeout", type=float, default=3.0)
    args = p.parse_args()
    if not 1 <= args.port <= 65535 or not 1 <= args.upstream_port <= 65535:
        p.error("ports must be 1..65535")
    try:
        ipaddress.ip_address(args.upstream_ip)
    except ValueError:
        p.error("--upstream-ip must be an IPv4 or IPv6 literal")
    run(args)


if __name__ == "__main__":
    main()
