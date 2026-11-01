# Repo local manifest for ZENEX

`local_manifest.xml` declares `vendor/zenex` as a local Repo project. Because
the project is already inside the checkout, define the local remote in the
manifest used for the checkout (or include this stanza there):

```xml
<remote name="local" fetch=".." />
```

Repo local manifests are normally placed in `.repo/local_manifests/`; copy this
file there after `repo init`. The local remote's `fetch=".."` resolves the
project name `local/zenex` to the checkout's `vendor/zenex` directory. Validate
with `repo sync -l vendor/zenex` in an initialized source tree. This file does
not pin or fetch upstream AOSP/LineageOS. Choose and pin a supported Android
manifest branch separately before syncing external projects.

## Redmi Note 14 Pro 5G Global

For the Global model 24090RA29G (`malachite`) on LineageOS 23.2, initialize
the upstream checkout and copy the device manifest:

```sh
repo init -u https://github.com/LineageOS/android.git -b lineage-23.2 --git-lfs
mkdir -p .repo/local_manifests
cp /path/to/zenex-os/manifest/local_manifest_malachite.xml \
  .repo/local_manifests/zenex_malachite.xml
repo sync -c --no-clone-bundle --no-tags -j2
```

Obtain the vendor files from firmware/device that you are entitled to use,
then run the device tree's documented `extract-files.sh` procedure or place
the extracted files in `vendor/xiaomi/malachite`. Do not add proprietary
blobs to this repository. Verify `vendor/xiaomi/malachite/BoardConfigVendor.mk`
exists before building. Then run:

```sh
source build/envsetup.sh
lunch lineage_malachite bp2a userdebug
m bacon -j2
```

This is a community device tree, not an official Xiaomi/LineageOS target. The
local manifest does not brand LineageOS as ZENEX and does not make a ROM safe
to flash on any other model or region.
