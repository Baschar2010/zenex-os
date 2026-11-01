#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/build-zenex.sh <desktop|aosp|all> [output-directory]

Builds a source/integration bundle for an image builder. It does not build a
Linux distribution ISO or compile AOSP; those require their respective build
trees and toolchains.

Required environment:
  ZENEX_DOT_HOST       DoT resolver hostname with a valid TLS certificate
  ZENEX_DOT_IP         Literal bootstrap IP for desktop DoT (desktop/all)
  ZENEX_PRIVATE_DNS_HOST  Optional AOSP DoT hostname; defaults to ZENEX_DOT_HOST
EOF
}

fail() { echo "build-zenex: $*" >&2; exit 2; }

target=${1:-}
[[ "$target" == desktop || "$target" == aosp || "$target" == all ]] || { usage >&2; exit 2; }
project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
out_dir=${2:-"$project_root/dist"}
[[ "$out_dir" != "$project_root" && "$out_dir" != "$project_root/.." ]] || fail "output directory cannot be the project root"
mkdir -p -- "$out_dir"
out_dir=$(cd -- "$out_dir" && pwd -P)

need_dot_host=false
need_dot_ip=false
[[ "$target" == desktop || "$target" == all ]] && { need_dot_host=true; need_dot_ip=true; }
[[ "$target" == aosp || "$target" == all ]] && need_dot_host=true
if $need_dot_host; then
  [[ -n "${ZENEX_DOT_HOST:-}" ]] || fail "set ZENEX_DOT_HOST to your selected DoT resolver hostname"
  [[ "$ZENEX_DOT_HOST" =~ ^([A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$ ]] || fail "ZENEX_DOT_HOST must be a DNS hostname"
fi
if $need_dot_ip; then
  [[ -n "${ZENEX_DOT_IP:-}" ]] || fail "set ZENEX_DOT_IP to the selected resolver's literal bootstrap IP"
  python3 - "$ZENEX_DOT_IP" <<'PY' || fail "ZENEX_DOT_IP must be a literal IPv4 or IPv6 address"
import ipaddress, sys
ipaddress.ip_address(sys.argv[1])
PY
fi
private_dns_host=${ZENEX_PRIVATE_DNS_HOST:-${ZENEX_DOT_HOST:-}}
if [[ "$target" == aosp || "$target" == all ]]; then
  [[ -n "$private_dns_host" ]] || fail "set ZENEX_PRIVATE_DNS_HOST (or ZENEX_DOT_HOST) for AOSP"
  [[ "$private_dns_host" =~ ^([A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$ ]] || fail "ZENEX_PRIVATE_DNS_HOST must be a DNS hostname"
fi

stage=$(mktemp -d "$out_dir/.zenex-${target}.XXXXXX")
cleanup() {
  case "$stage" in "$out_dir"/.zenex-${target}.*) rm -rf -- "$stage" ;; *) echo "unsafe staging path; leaving $stage" >&2 ;; esac
}
trap cleanup EXIT

copy() { mkdir -p -- "$(dirname -- "$2")"; cp -a -- "$1" "$2"; }

if [[ "$target" == desktop || "$target" == all ]]; then
  rootfs="$stage/desktop/rootfs"
  mkdir -p "$rootfs/usr/lib/zenex" "$rootfs/etc/zenex" \
    "$rootfs/etc/systemd/system/multi-user.target.wants" \
    "$rootfs/etc/systemd/resolved.conf.d" \
    "$rootfs/etc/systemd/system/systemd-resolved.service.d" \
    "$rootfs/usr/lib/sysusers.d" "$rootfs/usr/lib/tmpfiles.d" \
    "$rootfs/var/lib/zenex" "$rootfs/usr/share/plymouth/themes/zenex"
  copy "$project_root/network/dns-filter/zenex-dns-filter.py" "$rootfs/usr/lib/zenex/zenex-dns-filter.py"
  copy "$project_root/network/dns-filter/update-zenex-blocklist.py" "$rootfs/usr/lib/zenex/update-zenex-blocklist.py"
  copy "$project_root/network/dns-filter/zenex-dns-filter.service" "$rootfs/etc/systemd/system/zenex-dns-filter.service"
  copy "$project_root/network/dns-filter/zenex-blocklist-update.service" "$rootfs/etc/systemd/system/zenex-blocklist-update.service"
  copy "$project_root/network/dns-filter/zenex-blocklist-update.timer" "$rootfs/etc/systemd/system/zenex-blocklist-update.timer"
  copy "$project_root/network/dns-filter/10-zenex-resolved.conf" "$rootfs/etc/systemd/resolved.conf.d/10-zenex.conf"
  copy "$project_root/desktop/systemd/systemd-resolved.service.d/10-zenex-dns.conf" "$rootfs/etc/systemd/system/systemd-resolved.service.d/10-zenex-dns.conf"
  copy "$project_root/desktop/systemd/sysusers.d/zenex-dns.conf" "$rootfs/usr/lib/sysusers.d/zenex-dns.conf"
  copy "$project_root/desktop/systemd/tmpfiles.d/zenex-dns.conf" "$rootfs/usr/lib/tmpfiles.d/zenex-dns.conf"
  copy "$project_root/network/policy/adult-domains.txt" "$rootfs/var/lib/zenex/adult-domains.txt"
  copy "$project_root/network/policy/adult-domains.txt.provenance" "$rootfs/var/lib/zenex/adult-domains.txt.provenance"
  copy "$project_root/network/policy/OISD-LICENSE.txt" "$rootfs/usr/share/doc/zenex/OISD-LICENSE.txt"
  printf 'ZENEX_DOT_HOST=%s\nZENEX_DOT_IP=%s\n' "$ZENEX_DOT_HOST" "$ZENEX_DOT_IP" > "$rootfs/etc/zenex/dns.conf"
  ln -s /run/systemd/resolve/stub-resolv.conf "$rootfs/etc/resolv.conf"
  ln -s ../zenex-dns-filter.service "$rootfs/etc/systemd/system/multi-user.target.wants/zenex-dns-filter.service"
  ln -s ../zenex-blocklist-update.timer "$rootfs/etc/systemd/system/multi-user.target.wants/zenex-blocklist-update.timer"
  cp -a "$project_root/desktop/plymouth/." "$rootfs/usr/share/plymouth/themes/zenex/"
  cat > "$stage/desktop/README.txt" <<'EOF'
Install this rootfs overlay while building a disposable ZENEX Linux image.
It enables the DNS proxy and update timer at boot, orders systemd-resolved
after the proxy, and points the system stub resolver at the local filter.
The DoT hostname and bootstrap IP were supplied by the image builder.
Review nftables/firewall integration before claiming direct DNS bypass is blocked.
EOF
fi

if [[ "$target" == aosp || "$target" == all ]]; then
  common="$stage/aosp/device/zenex/common"
  copy "$project_root/mobile/launcher" "$common/packages/ZenexLauncher"
  copy "$project_root/mobile/policy-app" "$common/packages/ZenexPolicy"
  copy "$project_root/mobile/overlay" "$common/overlay"
  copy "$project_root/mobile/product/zenex_product.mk" "$common/zenex_product.mk"
  copy "$project_root/mobile/product/zenex_bootanimation.mk" "$common/product/zenex_bootanimation.mk"
  copy "$project_root/mobile/product/preferred-apps/zenex-home.xml" "$common/preferred-apps/zenex-home.xml"
  mkdir -p "$common/boot-animation"
  copy "$project_root/mobile/boot-animation/generated/bootanimation.zip" "$common/boot-animation/bootanimation.zip"
  copy "$project_root/mobile/boot-animation/generated/bootanimation-lowram.zip" "$common/boot-animation/bootanimation-lowram.zip"
  python3 - "$common/packages/ZenexPolicy/res/values/config.xml" "$private_dns_host" <<'PY'
from pathlib import Path
import sys
target = Path(sys.argv[1])
text = target.read_text(encoding="utf-8")
host = sys.argv[2]
if "@ZENEX_PRIVATE_DNS_HOST@" not in text:
    raise SystemExit("missing private DNS hostname template marker")
target.write_text(text.replace("@ZENEX_PRIVATE_DNS_HOST@", host), encoding="utf-8")
PY
  cat > "$common/Android.bp" <<'EOF'
// Soong discovers Android.bp recursively under this device directory.
subdirs = ["packages/ZenexLauncher", "packages/ZenexPolicy"]
EOF
  cat > "$stage/aosp/README.txt" <<'EOF'
Copy device/zenex/common into the pinned AOSP source tree and inherit
device/zenex/common/zenex_product.mk from the selected product makefile.
The product adds ZenexLauncher and ZenexPolicy, the HOME preferred activity,
framework/Settings resource overlays and standard/low-RAM bootanimation.
Provision ZenexPolicy as Device Owner during first-run setup for Private DNS
enforcement. The selected DoT hostname was supplied by the image builder.
This bundle does not compile an Android image or enroll a physical phone.
EOF
fi

cat > "$stage/BUILD-NOTES.txt" <<EOF
ZENEX $target integration bundle
Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Project source: $project_root
This archive stages existing ZENEX modules; it does not compile a Linux ISO or AOSP image.
EOF
archive="$out_dir/zenex-${target}-bundle.tar.gz"
tar -czf "$archive.tmp" -C "$stage" .
mv -f -- "$archive.tmp" "$archive"
sha256sum "$archive" > "$archive.sha256.tmp"
mv -f -- "$archive.sha256.tmp" "$archive.sha256"
echo "Created $archive"
cat "$archive.sha256"
