# ZENEX low-resource targets

These are product engineering targets, not claims of current compatibility. Each needs measurements on a built artifact and hardware/virtualization validation.

## Desktop PC

### User hardware target

- 64-bit x86_64 CPU; 4 cores recommended. Two cores are the low-end target.
- **Low-end target: 2 GiB RAM and 32 GiB disk capacity** for the minimal desktop, small first-party apps, and one light workload at a time.
- **Very-low-memory fallback target: 1 GiB RAM and 16 GiB disk**, limited to a reduced desktop, no heavy browser workload, no visual effects, and one app at a time. Boot uses a two-frame static hold instead of the standard animation sequence. This profile must pass a separate performance and stability gate before being advertised.
- 16 GiB RAM and a 500 GB disk are a comfortable user target, not the minimum.
- No dedicated GPU required for basic desktop mode; software rendering must remain usable, while accelerated graphics are preferred.
- Idle memory, boot time, app launch time, update size, suspend/resume, and storage use must be measured and published.

### Windows-hosted QEMU profile

- Default guest: 2 GiB RAM, 2 vCPUs, 32 GiB sparse disposable disk, 1280x800 display.
- Low-memory test guest: 1 GiB RAM, 1 vCPU, 16 GiB sparse disk, 1024x768 display, animations/compositing disabled.
- Host test PC: 16 GiB RAM; one VM at a time. Keep at least 6 GiB available to Windows; don't build AOSP while the VM runs. If the desktop host is under memory pressure, use the 1 GiB guest profile or stop the VM.
- QEMU uses a snapshot or a newly created disposable virtual disk during development. Never attach the Windows system disk to an installer test.
- If memory pressure or software-rendering latency is unacceptable, lower guest resolution/frame rate before increasing assigned resources.

The exact QEMU flags are to be added after the Linux desktop image exists; don't point the old freestanding-kernel launcher at the new product and call it verified.

## Mobile devices

- Initial low-resource qualification target: ARM64 phone/tablet with **2 GiB physical RAM and 32 GiB storage**, AOSP-compatible boot chain, and device-specific kernel/vendor support. This is a best-effort model-by-model target, not a guarantee for arbitrary old phones.
- Very old 1 GiB or 32-bit devices are a separate legacy tier; they may need older platform versions and may have no maintainable vendor kernel/security updates. They are not promised as fully supported until a specific model passes boot, modem, camera, storage, update, and security checks.
- Android image should contain no Google services, analytics, ad identifier, or nonessential background apps. Idle RAM, cold boot, app startup, standby battery use, and storage footprint are measured on the target model.
- Use the 111-frame standard boot sequence for the normal profile and a two-frame static PNG hold for low-RAM boot. Android bootanimation.zip uses PNG frames; the SVG is a source/preview format, not an image format the native boot-animation service directly renders.
- Enable and tune Android's low-RAM process management for low-resource device builds, then validate background-app kills, app launch, and responsiveness. AOSP exposes low-RAM tuning through `ro.config.low_ram`/`lmkd`; it does not automatically make every device fit or perform well.
- A virtual Cuttlefish profile should start with 2 GiB guest RAM and the lowest supported vCPU count that passes UI performance and smoke tests. Host memory/CPU requirements are separate and may be higher.
- No blanket promise for “all phones”: support is enumerated by exact make/model, regional variant, firmware, and tested peripherals.

## Build machine versus runtime machine

Small end-user runtime targets do not imply that a full AOSP source build fits on the same PC. Current official AOSP guidance recommends 400 GB free storage and at least 64 GB RAM for development. This session found 248.9 GiB free on C: and no other fixed drive, so a full AOSP checkout and build is not being attempted here.
