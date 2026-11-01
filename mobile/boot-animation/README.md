# ZENEX boot-animation assets

`generated/bootanimation.zip` is the standard AOSP animation at 720×1280 and 30 fps. It contains 111 intro frames: 0–30 black, 31–70 the blue impact and exact supplied lightning crop, 71–110 the exact supplied wordmark rising in. A 60-frame, two-second low-amplitude pulse then holds until the Android boot-animation service is told that boot has completed and the lock/setup screen can appear.

`generated/bootanimation-lowram.zip` contains two identical static logo frames and loops them without black flicker or animation. The Android native boot-animation service reads PNG sequences; it does not natively render SVG, so this is the low-memory native fallback. `zenex-lowram.svg` is the equivalent tiny two-state SVG for a renderer that supports SVG. `zenex_bootanimation.mk` selects the low-RAM asset only when a product configuration sets `ZENEX_LOW_RAM_PROFILE=true`; the variable is explicit and is not guessed from guest or host RAM. Use the static profile for a qualified 1 GiB target. A 2 GiB target uses the standard animation unless measured graphics/memory pressure justifies opting into the static profile.

Generate the assets with:

```sh
python3 scripts/generate_boot_animation.py
```

The generator derives all logo pixels from `assets/zenex-logo-transparent.png`, preserves the source colors, and uses one uniform scale for both logo sections. It creates PNG frames temporarily and removes those intermediate frames after writing the ZIPs. `generated/bootanimation-preview.png` is a contact sheet for visual review.

The makefile fragment is prepared for an AOSP product tree but has not yet been included in or built against an AOSP checkout. Copy the generated ZIPs to `device/zenex/common/boot-animation/` in that tree and include the fragment from the ZENEX product makefile. The Linux desktop's matching lightweight Plymouth theme source is in `../../desktop/plymouth/`; it has not yet been installed into a desktop image.
