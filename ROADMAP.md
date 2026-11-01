# ZENEX implementation roadmap

## Phase 0 — project alignment (current)

- Adopt the supplied ZENEX requirements and move away from the freestanding-kernel direction.
- Define supported virtual targets and a security boundary for compatibility, DNS, and child profiles.
- Preserve exact logo source and record licenses/clearance requirements.

## Phase 1 — build capacity and pinned upstreams

- Establish a Linux build host with AOSP's current documented requirements; do not put a massive AOSP checkout on a constrained Windows system.
- Pin AOSP manifest branch and Linux desktop base/kernel revisions.
- Bring up unmodified AOSP Cuttlefish and a minimal Linux QEMU image first; save known-good build/test manifests.

## Phase 2 — ZENEX branding and first-party shell

- Integrate exact logo boot sequence, Android setup/lockscreen/launcher and PC login/desktop shell.
- Install the generated standard/low-RAM Android bootanimation ZIPs through the ZENEX product configuration and package the matching standard/low-RAM Plymouth themes into desktop initramfs images.
- Implement both mobile launcher modes and the first desktop applications.
- Build the Kotlin HOME launcher scaffold in `mobile/launcher/` in the pinned
  AOSP tree, set it as the default HOME component, then add library search,
  app ordering and accessibility/instrumentation coverage.
- Measure responsiveness and accessibility on virtual targets.
- Add low-memory desktop and Android product configurations; test 1/2 GiB PC profiles and the 2 GiB ARM64 phone target before raising minimums.

## Phase 3 — policy and security

- Remove/verify absence of Google services, telemetry, and ad identifiers/endpoints.
- Implement selected DoH/DoT, persistence, no silent provider-DNS fallback, and status UI.
- Integrate the OISD NSFW-small input and periodic update service from
  `network/dns-filter/`; validate list provenance, resolver bootstrap, firewall
  enforcement, IPv6, fail-closed behavior and license notice before image build.
- Add optional guardian profile and source-controlled policy, with realistic documented limits.
- Perform app-sandbox, SELinux, signature, secure-boot/recovery and update review.

## Phase 4 — persistence and install

- Validate encrypted persistent user data and account setup on both target families.
- Build safe PC installer for explicitly selected virtual disk; test with disposable QEMU images.
- Define mobile owner setup, update, recovery, boot-key, and per-model flashing process.

## Phase 5 — ecosystem and distribution

- Add opt-in local ZENEX Connect pairing, encrypted file/clipboard transfer, and tested accessory profiles.
- Build signed release artifacts, source/patch archives, checksums, notices, recovery docs, and per-device support matrix.
- Release only after the acceptance criteria in `SPEC.md` pass for the declared target set.

## Immediate build constraint

Official AOSP developer guidance currently calls for around 400 GB free storage and at least 64 GB RAM. This session measured about 249 GiB free on C: and 12 logical processors; Windows CIM access prevented a reliable RAM measurement. AOSP checkout/build has therefore not been started. The current workstation is below the documented storage minimum, and its memory suitability is unverified.
