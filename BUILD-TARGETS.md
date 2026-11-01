# ZENEX multi-platform build

## Supported workflow outputs

| Platform | Source | Build target | Output |
|---|---|---|---|
| ARM64 phones/tablets | AOSP `android-latest-release` | `gsi_arm64-userdebug` | `system.img.gz` |
| x86-64 PC/laptop | Android-x86 `r-x86` | `android_x86_64-userdebug`, then `iso_img` | bootable ISO |

The requested `aosp_arm64-userdebug` is not AOSP's generic-system-image target. AOSP documents `gsi_arm64-userdebug` for a 64-bit ARM GSI. A GSI is a system partition for compatible Project Treble devices; it does not include the device's boot/vendor firmware and is not guaranteed to boot on every ARM phone.

The official Android-x86 source instructions currently describe `r-x86` as based on Android 11. This output is a compatibility preview, not a current security release. It should not be used as a daily-driver security OS.

## ZENEX staging

`scripts/stage-zenex-android.sh` stages the Kotlin HOME app and Device Policy app, product overlays, preferred HOME entry and the standard/low-RAM boot animations, then includes `device/zenex/common/product/zenex_product.mk` from the target product makefile. The DoT hostname is compiled as `family.adguard-dns.com`, chosen earlier in this project.

The policy app applies strict Private DNS only after Device Owner enrollment on a freshly provisioned device. The Android package does not currently run the OISD blocklist as a local system resolver, and release outputs must not be described as enforcing OISD filtering. `ZENEX_LOW_RAM_PROFILE` defaults to the normal animation; set it in the product configuration for the static 1-GB animation when qualifying a low-memory device.

## GitHub runner requirements

The workflow now uses `ubuntu-latest` and only attempts the ARM64 GSI. It checks capacity before downloading source. GitHub lists 14 GB SSD and 8 GB RAM for standard private-repository Linux runners (16 GB RAM for public repositories); AOSP requires about 400 GB free disk and at least 64 GB RAM. The preflight therefore stops on standard hosted runners, avoiding a long failed sync. Cleanup cannot recover the missing hundreds of GB. A complete build needs a runner with substantially larger limits.

## Run and release

After pushing the repository, use **Actions → ZENEX multi-platform builds → Run workflow** to run the GSI build check. Or start it from PowerShell with GitHub CLI:

```powershell
gh workflow run build.yml --ref main -f build_gsi_arm64=true
```

After a successful GSI build, a version tag creates an experimental GitHub Release:

```powershell
git tag v0.1.0-preview.1
git push origin v0.1.0-preview.1
```

The GSI is gzip-compressed and gets a SHA-256 file. It is not cryptographically signed with a ZENEX production key, is not certified, and has no universal device-specific flashing instructions. Android-x86 remains deferred.

## Older Redmi profile

The Redmi Note 14 Pro 5G Global profile (`24090RA29G`, `malachite`) remains documented separately in `device/targets.example.json` and `manifest/local_manifest_malachite.xml`. It is not part of the current GSI job. A model-specific ROM would need its own firmware/blob and legal review.
