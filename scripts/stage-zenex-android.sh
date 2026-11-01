#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "Usage: $0 <zenex-source-root> <android-source-root> <base-product-makefile>" >&2
  exit 2
fi

ZENEX_ROOT=$(realpath "$1")
ANDROID_ROOT=$(realpath "$2")
BASE_PRODUCT=$3
COMMON="$ANDROID_ROOT/device/zenex/common"
MODULES="$ANDROID_ROOT/vendor/zenex/apps"
ZENEX_PRIVATE_DNS_HOST=${ZENEX_PRIVATE_DNS_HOST:-family.adguard-dns.com}
ZENEX_DOT_BOOTSTRAP_IP=${ZENEX_DOT_BOOTSTRAP_IP:-94.140.14.15}

for required in \
  "$ZENEX_ROOT/mobile/launcher/Android.bp" \
  "$ZENEX_ROOT/mobile/policy-app/Android.bp" \
  "$ZENEX_ROOT/mobile/product/zenex_product.mk" \
  "$ZENEX_ROOT/mobile/boot-animation/generated/bootanimation.zip" \
  "$ZENEX_ROOT/mobile/boot-animation/generated/bootanimation-lowram.zip" \
  "$ZENEX_ROOT/mobile/overlay/frameworks/base/core/res/res/values/config.xml" \
  "$ZENEX_ROOT/mobile/overlay/packages/apps/Settings/res/values/config.xml"; do
  test -f "$required" || { echo "Missing ZENEX build input: $required" >&2; exit 1; }
done

test -f "$ANDROID_ROOT/$BASE_PRODUCT" || { echo "Missing base product makefile: $BASE_PRODUCT" >&2; exit 1; }

mkdir -p "$MODULES/launcher" "$MODULES/policy-app" \
  "$COMMON/boot-animation" "$COMMON/overlay" "$COMMON/preferred-apps" "$COMMON/product" "$COMMON/dns"
cp -a "$ZENEX_ROOT/mobile/launcher/." "$MODULES/launcher/"
cp -a "$ZENEX_ROOT/mobile/policy-app/." "$MODULES/policy-app/"
cp -a "$ZENEX_ROOT/mobile/overlay/." "$COMMON/overlay/"
cp -a "$ZENEX_ROOT/mobile/boot-animation/generated/bootanimation.zip" "$COMMON/boot-animation/"
cp -a "$ZENEX_ROOT/mobile/boot-animation/generated/bootanimation-lowram.zip" "$COMMON/boot-animation/"
cp -a "$ZENEX_ROOT/mobile/product/." "$COMMON/product/"
cp -a "$ZENEX_ROOT/mobile/product/preferred-apps/zenex-home.xml" "$COMMON/preferred-apps/"

# Use the already selected family-safe DoT hostname in the compiled DPC resource.
sed "s|@ZENEX_PRIVATE_DNS_HOST@|$ZENEX_PRIVATE_DNS_HOST|g" \
  "$MODULES/policy-app/res/values/config.xml" > "$MODULES/policy-app/res/values/config.xml.tmp"
mv "$MODULES/policy-app/res/values/config.xml.tmp" "$MODULES/policy-app/res/values/config.xml"

python3 - "$COMMON/dns/dot-provider.json" <<'PY'
import ipaddress
import json
import os
import re
import sys

host = os.environ.get("ZENEX_PRIVATE_DNS_HOST", "family.adguard-dns.com")
bootstrap = os.environ.get("ZENEX_DOT_BOOTSTRAP_IP", "94.140.14.15")
if not re.fullmatch(r"(?i)(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", host):
    raise SystemExit("Invalid ZENEX_PRIVATE_DNS_HOST")
ipaddress.IPv4Address(bootstrap)
with open(sys.argv[1], "w", encoding="utf-8") as stream:
    json.dump({"transport": "dot", "hostname": host, "bootstrap_ip": bootstrap}, stream, indent=2)
    stream.write("\n")
PY

INCLUDE_LINE='include device/zenex/common/product/zenex_product.mk'
if ! grep -Fqx "$INCLUDE_LINE" "$ANDROID_ROOT/$BASE_PRODUCT"; then
  printf '\n# ZENEX product integration\n%s\n' "$INCLUDE_LINE" >> "$ANDROID_ROOT/$BASE_PRODUCT"
fi

echo "Staged ZENEX launcher, policy app, overlays, preferred HOME, and boot-animation profiles."
echo "Note: the Android DNS filter is not an in-tree resolver implementation; the DPC only configures strict DoT after Device Owner enrollment."
