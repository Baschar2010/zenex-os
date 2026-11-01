# ZENEX network policy prototype

`zenex-dns-filter.py` is a dependency-free local DNS policy proxy. It serves
loopback UDP and TCP, rejects exact blocked domains and their subdomains, and
forwards allowed DNS queries over authenticated DNS-over-TLS. Upstream errors
return SERVFAIL; it never falls back to plaintext or ISP DNS.

The DoT endpoint is configured as both a hostname and literal bootstrap IP.
The socket connects to the literal address while TLS validates the configured
hostname, preventing a resolver recursion loop when ordinary DNS points back to
the local filter.

## Integration contract

1. Install a reviewed policy at `/var/lib/zenex/adult-domains.txt` (the repository
   includes an OISD snapshot under `network/policy/`) owned by `zenex-dns`. The packaged snapshot is
   the boot-time baseline; the timer refreshes it later. Empty policy is rejected.
   A privileged installer creates a locked `zenex-dns` account, creates
   `/var/lib/zenex`, and installs the script as `/usr/lib/zenex/zenex-dns-filter.py`.
2. Configure the system resolver to use `127.0.0.1:5353` (including TCP),
   preserve loopback access, and block outbound UDP/TCP port 53 for all other
   processes. Permit the service's outbound TCP 853 only. IPv6 must receive
   equivalent rules; no direct DNS escape route is allowed.
3. Configure `/etc/zenex/dns.conf` with an explicitly selected resolver hostname
   and literal bootstrap IP. Validate both before enabling the service; do not
   silently select a vendor resolver.
4. Android should implement the same deny policy through a supported Private
   DNS/VPN or platform resolver integration; this Linux systemd proxy cannot
   simply be dropped into Android.

Enable the Linux units only after the initial list and explicit resolver config
are installed: `systemctl enable --now zenex-dns-filter.service zenex-blocklist-update.timer`.
The updater refreshes at boot and every 12 hours, validates before replacing,
and the daemon reloads a changed list in the background.

This prototype is not a production content classifier. The included OISD data
snapshot and its GPL-3.0 license notice are under `network/policy/`; review the
upstream terms and attribution before distributing a system image. The updater
uses HTTPS and local provenance hashes but the upstream currently supplies no
signature verification in this integration. Domain filtering cannot stop direct-IP access, arbitrary VPNs, encrypted
client DNS, newly registered domains, or explicit content hosted on allowed
domains. A guardian profile must separately restrict VPN/app installation and
settings, with signed boot policy; even then a device owner can replace the OS.

## Firewall policy sketch (nftables)

Integrators should generate rules in a dedicated table and test resolver startup
ordering before enabling them. Do not flush or replace the host firewall from a
package install. A matching systemd-resolved drop-in is in
`10-zenex-resolved.conf`. The policy should allow loopback DNS, permit only the service
UID to connect to the selected resolver on TCP/853, and reject all other port
53/853 traffic (plus equivalent IPv6 traffic). This repository deliberately
does not ship an unconditional firewall script that could lock an existing host
out of DNS/network access.

## Current status

Source module and list snapshot only. It is not installed or wired to a product
image. Run protocol tests and a security review before integration.
