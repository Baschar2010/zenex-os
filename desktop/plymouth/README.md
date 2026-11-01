# ZENEX Plymouth themes

`zenex.plymouth`/`zenex.script` implement the desktop animation with three transparent sprites derived at one uniform scale from the canonical logo: bolt, ZENEX wordmark, and a separate blue impact glow. The script starts on black, reveals the bolt, brings the wordmark up, then uses a restrained opacity pulse until Plymouth exits. `zenex-lowram.plymouth` uses only one static logo sprite.

The `scripts/generate_boot_animation.py` generator creates the three PNGs and theme files in this directory. Add this directory to the desktop Plymouth package at `/usr/share/plymouth/themes/zenex/`, then select `zenex` for standard PCs or `zenex-lowram` for the 1 GiB profile in the desktop product's initramfs configuration. The themes are source assets only; they have not yet been installed in or run from a ZENEX desktop image.
