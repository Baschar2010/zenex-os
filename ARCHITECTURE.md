# ZENEX architecture

```text
Shared ZENEX identity and policy
├── Brand assets and design tokens
├── privacy, DNS, child-profile, release policy
├── ZENEX Connect protocol specification
├── ZENEX Mobile
│   └── AOSP → ZENEX product configuration → Cuttlefish/device image
└── ZENEX Desktop
    └── Linux kernel + base user space → ZENEX shell/services → QEMU ISO/installer
```

## Platform separation

### Mobile build

Track an explicit AOSP manifest branch and device target. Keep ZENEX changes in product makefiles, overlays, resource packages, first-party apps, sepolicy changes, and narrowly scoped framework changes. Build Cuttlefish first; do not claim a physical-device image until vendor/device binaries, bootloader unlock requirements, verified boot keys, radio firmware, camera, sensors, suspend, and update path are tested for that model.

Android's app sandbox is based on unique app UIDs and kernel-enforced process/data isolation. ZENEX should use those platform controls and SELinux; a separate "Google sandbox" label alone is not a security boundary.

### Desktop build

Track a stable Linux kernel and a minimal, auditable user-space. Package the ZENEX shell and policy services as first-party components. QEMU x86_64 is the first hardware contract. Keep source builds separate from Windows user files and boot/install tests attached only to disposable QEMU disks.

## Shared policy services

- DNS manager owns the platform resolver configuration, resolver certificate validation, status and fail-closed behavior. Desktop implementation uses Linux network-management interfaces; Android implementation uses supported Android private-DNS/VPN APIs or narrowly scoped framework changes. Never silently substitute another resolver.
- Child-profile policy is enforced by OS permissions, package management, network policy and verified system configuration. Domain lists are not a complete classifier and must not be marketed as absolute content filtering.
- Optional compatibility packages remain absent from the base product. Require explicit package provenance, signing, SELinux/UID review, network denial by default, and independent revocation.

## Security boundaries

Trust starts at the device boot chain. Release images must be signed. Development devices may use owner-authorized keys; recovery and bootloader-unlock behavior must be explicit. A user with physical ownership and authority to replace boot keys can install a different operating system, so no open-source software can guarantee an unmodifiable policy against that owner.

## Build reproducibility

Use a checked-in manifest/pin file per platform. Record upstream revision, local patch hashes, toolchain, build command, generated artifact hash, and test results. Upstream source trees should not be copied into this repository; use Repo manifests/workspaces and keep ZENEX-owned patches separate.
