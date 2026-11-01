# ZENEX OS product specification

This document translates the owner's 2026-10-27 requirements into implementation and verification criteria. `ZENEX` and the exact supplied logo image are the current brand.

## 1. Product targets

### ZENEX Mobile

- Use Android Open Source Project (AOSP), not an independently written mobile kernel.
- First target: AOSP Cuttlefish virtual device. Each real phone/tablet needs an individually supported device target and its required vendor components.
- Low-resource runtime target: ARM64 phone with 2 GiB physical RAM and 32 GiB storage, without Google services or bundled third-party apps. A 1 GiB or 32-bit legacy phone is a separate best-effort tier and requires model-specific validation.
- Ship no Google Mobile Services, Play Services, Google apps, Google tracking/analytics, or manufacturer carrier bloatware.
- Provide a ZENEX setup wizard, lock screen, launcher, settings, and boot animation.

### ZENEX Desktop

- Use an upstream Linux kernel with a ZENEX desktop and system services. Do not reuse the old freestanding `work/nexus-os` prototype as the product foundation.
- First target: QEMU x86_64. The ISO boots, installs only to a selected virtual disk, creates an account, persists user files, and shuts down cleanly.
- Low-resource runtime target: PC with 2 GiB RAM and a 32 GB disk for a minimal desktop. A restricted rescue/very-low-memory mode targets 1 GiB RAM and 16 GB disk; 16 GiB RAM and a 500 GB disk should run the full desktop comfortably after qualification.
- PC interface: polished desktop shell, app launcher, system tray, settings, terminal, file manager, text editor, and browser choice documented by package and license.

The mobile and desktop products share brand assets, design tokens, user-facing privacy policy, DNS policy, and ZENEX Connect specifications. Kernel, driver, packaging, and device support stay platform-specific.

## 2. Branding and boot

- Use the owner-provided PNG as the exact master: preserve lightning silhouette, blue/cyan hues, facets, and `ZENEX` wordmark.
- Keep the source artwork unchanged. Derived assets may only remove the baked checkerboard/background or scale uniformly; they must not redraw, recolor, distort, or replace the wordmark.
- Boot sequence: 720×1280 Android standard profile at 30 fps: frames 0–30 black, 31–70 blue impact/lightning, 71–110 wordmark rise, then a gentle loop until boot completes. The 1 GiB profile uses a two-frame static hold rather than a large sequence. Desktop Linux follows the same timing via a separate Plymouth theme.
- The logo and name appear throughout product boot and UI. They may be replaced only through a deliberate source/configuration change and rebuild, subject to normal device-owner control; do not misrepresent an ordinary software setting as tamper-proof.

## 3. Android/UI

- AOSP-derived ZENEX launcher offers two user-selectable layouts: Android-style grid/widgets/app drawer and iOS-inspired grid/app library/control center.
- Both modes share accessibility, keyboard/screen-reader support, consistent typography and icon sizing, reduced-motion controls, and responsive phone/tablet layouts.
- No ads, sponsored recommendations, system advertising popups, or promotional notifications.
- Android app sandbox and permission controls remain enabled. App-to-app data, contacts, location, microphone, camera, and diagnostics require platform-enforced access grants.

## 4. Compatibility sandbox

- Optional compatibility services are absent from the base image. If later provided, install them as explicitly identified, independently updateable packages in the Android application sandbox.
- Default network access is denied for compatibility packages until the owner grants it. Capabilities (location, contacts, files, logs) remain denied unless individually granted through platform permission mechanisms.
- Do not describe a compatibility layer as isolated merely because it is labeled a sandbox. Test process identity, SELinux domain, UID separation, data paths, IPC permissions, network policy, and permission revocation.
- Compatibility must not require Google code in the core image. Document proprietary components and their licenses before distribution.

## 5. Network and privacy

- Ship no telemetry, ads, device identifiers for analytics, or hidden app network access.
- Provide system-wide configurable DoH/DoT with certificate validation and a visible resolver status. Persist and respect the user's configured resolver; never silently fall back to provider DNS. If the endpoint is unavailable, fail closed for DNS and explain the failure.
- Any DNS/domain filter is supplemental: HTTPS, alternate resolvers, VPNs, direct IPs, and newly created domains limit domain-blocking guarantees. Do not claim that DNS alone blocks all trackers or explicit content.
- Network activity must be attributable to a system service or user-approved app; expose connection permissions and a local audit view without collecting telemetry.

## 6. Child profile and adult-content policy

- Provide an optional child profile controlled by a guardian PIN. App installation/removal, account changes, network-policy edits, and restricted settings require guardian authorization.
- A source-controlled restrictive policy can deny known adult-content domains and apply safe search where supported; users cannot disable the policy through ordinary child-profile settings or developer toggles.
- Enforcement is only as strong as the verified boot chain, signed system image, recovery policy, network path, and curated blocklists. An owner who can unlock the bootloader, replace the image, use an unmanaged VPN, or alter the network can bypass controls. Never claim universal or mathematically unbreakable content classification.
- Do not inspect TLS content or collect browsing histories for this feature. Provide local policy status and minimal, local-only troubleshooting data.

## 7. ZENEX Connect

- Later milestone: local-network device discovery and end-to-end encrypted clipboard/file/notification relay, with no cloud dependency.
- Pairing is explicit, uses authenticated device keys and user confirmation, has per-feature permissions and revocation, and rejects unauthenticated peers.
- Bluetooth support is device/profile specific; "universal compatibility" is not claimed without interoperability testing.

## 8. Release acceptance

- Reproducible source manifest, pinned upstream revisions, license notices, checksums, and documented build environment.
- Mobile and desktop artifacts boot in their supported virtual targets. Real-hardware support is declared per tested model.
- Setup creates an owner account and recovery path; ordinary users cannot obtain system privileges accidentally.
- Files survive restart on the virtual disk; the installer never writes an unrelated host disk.
- Privacy review finds no Google service dependency, telemetry, advertising identifier, plaintext DNS fallback, or unapproved background network client.
- App isolation, DNS failure behavior, child-profile policy, boot integrity, updates, rollback, and recovery have explicit tests.
- Branding, boot animation, layout, performance, accessibility, and pointer input are visually/behaviorally verified in QEMU/Cuttlefish.

No artifact is called a complete release until all relevant platform-specific acceptance criteria pass.
