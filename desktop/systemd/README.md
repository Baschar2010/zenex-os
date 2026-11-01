# Linux boot-time DNS wiring

The desktop integration bundle stages these files into a Linux image rootfs:

- `zenex-dns-filter.service` is enabled under `multi-user.target` and starts
  before `systemd-resolved`.
- A `systemd-resolved.service` drop-in requires the filter service.
- `resolved.conf.d/10-zenex.conf` routes `~.` to `127.0.0.1:5353`, enables the
  local stub, and clears the built-in fallback resolver list.
- `/etc/resolv.conf` points at systemd-resolved's local stub.
- sysusers/tmpfiles create the unprivileged daemon account and writable policy
  directory; the OISD baseline is present before first boot.
- The update timer is linked into `multi-user.target.wants`.

`scripts/build-zenex.sh desktop` stages this as a rootfs overlay and inserts the
builder-selected DoT hostname and bootstrap IP. If the upstream is unavailable,
the filter returns SERVFAIL; it does not switch to plaintext DNS. This resolver
setup alone cannot prevent an application from deliberately querying a public
DNS IP, using its own DoH client, or using a VPN. Add and audit a platform
firewall policy before advertising those bypass paths as blocked.
