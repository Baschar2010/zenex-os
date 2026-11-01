# ZENEX logo assets

`zenex-logo-source.png` is the exact image supplied by the owner and is retained unchanged. It is the sole canonical mark: the faceted electric-blue lightning shape, its original blue/cyan colors, and the ZENEX wordmark are all part of the logo and must not be redrawn or recolored.

`import_zenex_logo.py` creates `zenex-logo-transparent.png` for use on black or other backgrounds. It removes only the exterior neutral checkerboard and border by changing alpha; retained RGB artwork pixels remain identical to the original. The source PNG is preserved for future higher-quality extraction if needed.

`zenex-boot-animation.svg` is a lightweight vector preview. Platform boot assets are generated separately in `../mobile/boot-animation/`; the Android AOSP integration fragment selects the standard sequence or the two-frame low-RAM hold. `../mobile/boot-animation/zenex-lowram.svg` is a tiny vector fallback for SVG-capable renderers. The matching PC Plymouth theme sources are in `../desktop/plymouth/` and await packaging into the desktop image.

Older NEXUS and hand-drawing assets are historical concepts and are not ZENEX branding. Before public distribution, clear the ZENEX name and confirm redistribution rights for all source artwork; see `../BRANDING.md` in the archived prototype tree.
