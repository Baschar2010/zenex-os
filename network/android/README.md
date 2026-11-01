# Android/AOSP DNS policy integration

The Linux systemd resolver proxy is not an Android Private DNS server. Android
Private DNS is a system-managed DNS-over-TLS client and expects a reachable
resolver hostname with a valid certificate. AOSP product integration must pick
one supported architecture:

1. **Remote DoT resolver** operated by ZENEX or selected by the owner, with the
   same blocklist and an explicit availability/privacy policy; configure the
   strict Private DNS hostname through the ZENEX Device Owner policy app during
   initial provisioning.
2. **On-device platform resolver hook** that applies the signed domain policy
   inside the privileged Android resolver before forwarding over the system's
   authenticated Private DNS transport. Keep this in AOSP product/framework
   source; don't install a normal app that claims to globally set Private DNS.

Device-owner APIs can set the global Private DNS hostname on fully managed
devices and can prevent changing the setting, but this is enrollment policy,
not capability for an ordinary launcher APK. ZENEX's setup product must reveal
the chosen host and report failure if configuration fails; never silently
fall back to cleartext or carrier DNS.

The current source scaffold is `mobile/policy-app/`; the product package and
Settings/framework overlay fragments are under `mobile/product/` and
`mobile/overlay/`. No AOSP source checkout/product image exists, so these are
not yet a built system overlay. Verify API level, provisioning ownership, DNS
transport, VPN interaction, IPv4/IPv6 and app-level encrypted DNS on each target.
