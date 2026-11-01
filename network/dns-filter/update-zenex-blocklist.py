#!/usr/bin/env python3
"""Fetch and validate the OISD NSFW-small list before atomic activation."""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import tempfile
import urllib.request
from urllib.parse import urlsplit
from datetime import datetime, timezone
from pathlib import Path

SOURCE = "https://raw.githubusercontent.com/sjhgvr/oisd/main/domainswild2_nsfw_small.txt"
LICENSE = "https://github.com/sjhgvr/oisd/blob/main/LICENSE"
DOMAIN = re.compile(r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(?:\.(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))*$", re.I)


def clean(raw: bytes, min_entries: int, source: str = SOURCE, license_url: str = LICENSE) -> tuple[bytes, int]:
    if len(raw) > 32 * 1024 * 1024:
        raise ValueError("source exceeds 32 MiB safety limit")
    text = raw.decode("utf-8-sig")
    result: set[str] = set()
    for line in text.splitlines():
        value = line.strip().lower().rstrip(".")
        if not value or value.startswith("#"):
            continue
        if not DOMAIN.fullmatch(value):
            raise ValueError(f"unexpected non-domain row: {value[:100]!r}")
        result.add(value)
    if len(result) < min_entries:
        raise ValueError(f"only {len(result)} valid entries; refusing to replace current list")
    return ("# Source: " + source + "\n# License: " + license_url + "\n" + "\n".join(sorted(result)) + "\n").encode(), len(result)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url", default=SOURCE)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--min-entries", type=int, default=1000)
    p.add_argument("--timeout", type=float, default=20)
    p.add_argument("--max-bytes", type=int, default=32 * 1024 * 1024)
    args = p.parse_args()
    if urlsplit(args.url).scheme != "https" or not urlsplit(args.url).hostname:
        p.error("the blocklist source must be an HTTPS URL")
    request = urllib.request.Request(args.url, headers={"User-Agent": "ZENEX-blocklist-updater/1.0"})
    if args.min_entries < 1 or args.max_bytes < 1024 or args.timeout <= 0:
        p.error("min-entries, max-bytes and timeout must be positive safety limits")
    with urllib.request.urlopen(request, timeout=args.timeout) as response:
        if response.status != 200:
            raise SystemExit(f"source returned HTTP {response.status}")
        data = response.read(args.max_bytes + 1)
    if len(data) > args.max_bytes:
        raise SystemExit(f"source exceeds configured {args.max_bytes}-byte limit")
    safe, count = clean(data, args.min_entries, args.url, LICENSE)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".zenex-list-", dir=args.output.parent)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(safe)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temp_name, 0o644)
        os.replace(temp_name, args.output)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    digest = hashlib.sha256(safe).hexdigest()
    stamp = datetime.now(timezone.utc).isoformat()
    provenance = args.output.with_suffix(args.output.suffix + ".provenance")
    metadata = f"source={args.url}\nlicense={LICENSE}\nupdated={stamp}\nentries={count}\nsha256={digest}\n"
    meta_fd, meta_name = tempfile.mkstemp(prefix=".zenex-meta-", dir=provenance.parent)
    try:
        with os.fdopen(meta_fd, "w", encoding="utf-8") as output:
            output.write(metadata)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(meta_name, 0o644)
        os.replace(meta_name, provenance)
    finally:
        if os.path.exists(meta_name):
            os.unlink(meta_name)
    print(f"Installed {count} domains; sha256={digest}")


if __name__ == "__main__":
    main()
