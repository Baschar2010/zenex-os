# Build environment status

## Current Windows workstation

- 12 logical processors.
- C: has approximately 249 GiB free of approximately 476 GiB total.
- Windows CIM/WMI queries were denied in this session, so installed RAM could not be measured reliably.
- WSL invocation has intermittently returned `Wsl/E_ACCESSDENIED`; Debian WSL was usable in prior elevated build sessions, but the current AOSP Linux build path is not ready.
- Only C: is available as a fixed local volume in this session; no separate 400 GiB build volume was found.

## AOSP requirement and decision

The official [AOSP build requirements](https://source.android.com/docs/setup/start/requirements) currently call for 400 GB free disk space and at least 64 GB RAM on a 64-bit Linux build machine. The official [source setup](https://source.android.com/docs/setup/download) uses Repo and a full multi-repository checkout. This machine has less than the documented storage requirement, so a source checkout/build is intentionally not started here. Use a dedicated Linux build volume or workstation with the required capacity before syncing AOSP. This avoids a predictable failed multi-hour download and protects Windows free space.

The first mobile target is Cuttlefish, which AOSP documents as a virtual-device target. Physical-device support requires device-specific binaries and separate qualification.

## Runtime is a separate target

The PC guest's default target is 2 GiB RAM, 2 vCPUs, and a 32 GiB disposable QEMU disk on a 16 GiB Windows host. A 1 GiB/1-vCPU recovery profile is also specified. A 500 GB user disk is an installation capacity target, not a build-space target. For Android, Cuttlefish can be configured for different RAM and CPU counts; its 2 GiB guest target still needs measurement and may be constrained by host virtualization, graphics acceleration, or Windows/WSL support. Official Cuttlefish guidance says the virtual device relies on host virtualization/KVM and resource use varies with the instance profile.

Consequently the plan can target low-resource runtime devices, but this PC cannot currently perform a full local AOSP source build under official recommended requirements. A small guest profile does not reduce the amount of RAM/disk needed to compile AOSP.
