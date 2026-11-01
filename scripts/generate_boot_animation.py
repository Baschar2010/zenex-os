#!/usr/bin/env python3
"""Generate ZENEX Android bootanimation.zip assets from the owner's exact logo."""
from __future__ import annotations

import argparse
from io import BytesIO
import math
from pathlib import Path
import zipfile

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "zenex-logo-transparent.png"
OUTPUT = ROOT / "mobile" / "boot-animation" / "generated"
WIDTH, HEIGHT, FPS = 720, 1280, 30
BLACK = (0, 0, 0)


def ease(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def render_impact(amount: float) -> Image.Image:
    """Make a separate blue/cyan light effect behind the unmodified logo pixels."""
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    cx, cy = WIDTH // 2, 610
    radius = int(84 + 330 * (1.0 - amount))
    alpha = int(245 * amount ** 0.8)
    for scale, color, opacity in (
        (1.00, (0, 92, 255), alpha),
        (0.52, (0, 180, 255), min(255, alpha)),
        (0.18, (225, 252, 255), min(255, alpha)),
    ):
        r = max(1, int(radius * scale))
        draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(*color, opacity))
    return glow.filter(ImageFilter.GaussianBlur(38))


def compose_logo(source: Image.Image, *, bolt_progress: float = 1.0,
                 title_progress: float = 1.0, pulse: float = 1.0,
                 impact: float = 0.0, bolt_opacity: float | None = None) -> Image.Image:
    """Compose crops at one shared scale so the original proportions stay exact."""
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (*BLACK, 255))
    if impact > 0:
        canvas.alpha_composite(render_impact(impact))

    src_w, src_h = source.size
    target_w = 590
    scale = target_w / src_w
    target_h = round(src_h * scale)
    left = (WIDTH - target_w) // 2
    top = (HEIGHT - target_h) // 2

    # Split only for timing; each crop uses the same scale and source pixels.
    bolt_source = source.crop((0, 0, src_w, 590))
    bolt = bolt_source.resize((target_w, round(590 * scale)), Image.Resampling.LANCZOS)
    bolt_h = bolt.height
    bolt_factor = 0.68 + 0.32 * bolt_progress
    bolt_size = (max(1, round(bolt.width * bolt_factor)), max(1, round(bolt.height * bolt_factor)))
    bolt = bolt.resize(bolt_size, Image.Resampling.LANCZOS)
    opacity = bolt_progress if bolt_opacity is None else bolt_opacity
    bolt.putalpha(bolt.getchannel("A").point(lambda a: round(a * opacity * pulse)))
    bolt_x = left + (target_w - bolt.width) // 2
    bolt_y = top + (bolt_h - bolt.height) // 2
    canvas.alpha_composite(bolt, (bolt_x, bolt_y))

    word_source = source.crop((0, 590, src_w, src_h))
    word = word_source.resize((target_w, max(1, round((src_h - 590) * scale))), Image.Resampling.LANCZOS)
    word_y = top + bolt_h + round((1.0 - title_progress) * 100)
    word.putalpha(word.getchannel("A").point(lambda a: round(a * title_progress * pulse)))
    canvas.alpha_composite(word, (left, word_y))
    return canvas.convert("RGB")


def save_frame(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=True, compress_level=9)


def write_zip(output_dir: Path, *, low_ram: bool) -> None:
    stage = output_dir / ("lowram-frames" if low_ram else "standard-frames")
    if stage.exists():
        for existing in stage.glob("*.png"):
            existing.unlink()
    stage.mkdir(parents=True, exist_ok=True)

    with Image.open(SOURCE) as opened:
        source = opened.convert("RGBA")
    (ROOT / "mobile" / "boot-animation" / "zenex-lowram.svg").write_text(
        '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 1280" preserveAspectRatio="xMidYMid meet" role="img" aria-label="ZENEX startup logo">
  <rect width="720" height="1280" fill="#000"/>
  <image href="../../assets/zenex-logo-transparent.png" x="65" y="347" width="590" height="587" preserveAspectRatio="xMidYMid meet" opacity="0">
    <animate attributeName="opacity" begin="0.15s" dur="0.18s" from="0" to="1" fill="freeze"/>
  </image>
  <style>@media (prefers-reduced-motion:reduce) { image { opacity:1 } }</style>
</svg>
''', encoding="utf-8")

    if low_ram:
        # Two identical frames make a static image that can loop without black flicker.
        final = compose_logo(source)
        save_frame(final, stage / "00000.png")
        save_frame(final, stage / "00001.png")
        desc = f"{WIDTH} {HEIGHT} {FPS}\np 0 0 part0\n"
        frames = [(stage / "00000.png", "part0/00000.png"),
                  (stage / "00001.png", "part0/00001.png")]
    else:
        # 0-30: black. 31-70: blue impact + bolt. 71-110: ZENEX wordmark rises in.
        for index in range(111):
            if index <= 30:
                frame = Image.new("RGB", (WIDTH, HEIGHT), BLACK)
            elif index <= 70:
                progress = ease((index - 31) / 39)
                frame = compose_logo(source, bolt_progress=0.24 + 0.76 * progress,
                                     bolt_opacity=0.82 + 0.18 * progress,
                                     title_progress=0.0,
                                     impact=max(0.0, 1.0 - (index - 31) / 18))
            else:
                progress = ease((index - 71) / 39)
                frame = compose_logo(source, title_progress=progress)
            save_frame(frame, stage / f"{index:05d}.png")

        # A gentle ~2-second loop while Android finishes booting.
        for index in range(60):
            phase = index / 59
            pulse = 0.975 + 0.025 * (0.5 - 0.5 * math.cos(phase * 2 * math.pi))
            frame = compose_logo(source, pulse=pulse)
            save_frame(frame, stage / f"hold-{index:05d}.png")
        desc = f"{WIDTH} {HEIGHT} {FPS}\nc 1 0 part0\np 0 0 part1\n"
        frames = [(stage / f"{index:05d}.png", f"part0/{index:05d}.png") for index in range(111)]
        frames += [(stage / f"hold-{index:05d}.png", f"part1/{index:05d}.png") for index in range(60)]

    path = output_dir / ("bootanimation-lowram.zip" if low_ram else "bootanimation.zip")
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("desc.txt", desc.encode("ascii"))
        for local, name in frames:
            archive.write(local, name)
    for local, _ in frames:
        local.unlink()
    stage.rmdir()
    print(f"Wrote {path} ({len(frames)} PNG frames, {path.stat().st_size:,} bytes)")


def write_preview(output_dir: Path) -> None:
    sample_frames = [0, 30, 31, 50, 70, 71, 90, 110]
    tile_w, tile_h = 180, 320
    sheet = Image.new("RGB", (tile_w * 4, (tile_h + 28) * 2), (14, 18, 28))
    standard = output_dir / "bootanimation.zip"
    with zipfile.ZipFile(standard) as archive:
        for index, frame_id in enumerate(sample_frames):
            name = f"part0/{frame_id:05d}.png"
            with Image.open(BytesIO(archive.read(name))) as image:
                thumb = image.convert("RGB").resize((tile_w, tile_h), Image.Resampling.LANCZOS)
            x, y = (index % 4) * tile_w, (index // 4) * (tile_h + 28)
            sheet.paste(thumb, (x, y))
            ImageDraw.Draw(sheet).text((x + 6, y + tile_h + 5), f"Standard frame {frame_id}", fill=(230, 235, 245))
    lowram = output_dir / "bootanimation-lowram.zip"
    with zipfile.ZipFile(lowram) as archive:
        with Image.open(BytesIO(archive.read("part0/00000.png"))) as image:
            thumb = image.convert("RGB").resize((tile_w, tile_h), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (0, (tile_h + 28) * 2 - tile_h))
        ImageDraw.Draw(sheet).text((6, (tile_h + 28) * 2 - 22), "Low-RAM static hold", fill=(230, 235, 245))
    sheet.save(output_dir / "bootanimation-preview.png", optimize=True)


def write_plymouth_assets() -> None:
    """Write lightweight sprite layers and script themes for the Linux desktop."""
    target = ROOT / "desktop" / "plymouth"
    target.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE) as opened:
        source = opened.convert("RGBA")
    src_w, src_h = source.size
    target_w = 620
    scale = target_w / src_w
    scaled_h = round(src_h * scale)
    bolt_h = round(590 * scale)
    bolt = source.crop((0, 0, src_w, 590)).resize((target_w, bolt_h), Image.Resampling.LANCZOS)
    word = source.crop((0, 590, src_w, src_h)).resize((target_w, scaled_h - bolt_h), Image.Resampling.LANCZOS)
    logo = source.resize((target_w, scaled_h), Image.Resampling.LANCZOS)
    bolt.save(target / "bolt.png", optimize=True)
    word.save(target / "wordmark.png", optimize=True)
    logo.save(target / "zenex-logo.png", optimize=True)

    glow_size = 420
    glow = Image.new("RGBA", (glow_size, glow_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    for radius in range(glow_size // 2, 0, -4):
        t = radius / (glow_size / 2)
        alpha = round(46 * (1 - t) ** 2)
        draw.ellipse((glow_size/2-radius, glow_size/2-radius,
                      glow_size/2+radius, glow_size/2+radius),
                     fill=(0, 105, 255, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(12))
    glow.save(target / "impact-glow.png", optimize=True)

    (target / "zenex.plymouth").write_text(
        "[Plymouth Theme]\nName=ZENEX\nDescription=ZENEX startup animation\nModuleName=script\n\n"
        "[script]\nImageDir=/usr/share/plymouth/themes/zenex\n"
        "ScriptFile=/usr/share/plymouth/themes/zenex/zenex.script\n", encoding="utf-8")
    (target / "zenex-lowram.plymouth").write_text(
        "[Plymouth Theme]\nName=ZENEX Low RAM\nDescription=Static ZENEX startup logo\nModuleName=script\n\n"
        "[script]\nImageDir=/usr/share/plymouth/themes/zenex\n"
        "ScriptFile=/usr/share/plymouth/themes/zenex/zenex-lowram.script\n", encoding="utf-8")
    (target / "zenex.script").write_text(r'''Window.SetBackgroundTopColor(0, 0, 0);
Window.SetBackgroundBottomColor(0, 0, 0);

bolt.image = Image("bolt.png");
bolt.sprite = Sprite(bolt.image);
bolt.sprite.SetZ(10);
word.image = Image("wordmark.png");
word.sprite = Sprite(word.image);
word.sprite.SetZ(11);
glow.image = Image("impact-glow.png");
glow.sprite = Sprite(glow.image);
glow.sprite.SetZ(9);

frame = 0;
fun refresh_callback() {
    frame++;
    screen_w = Window.GetWidth();
    screen_h = Window.GetHeight();
    group_h = bolt.image.GetHeight() + word.image.GetHeight();
    x = (screen_w - bolt.image.GetWidth()) / 2;
    y = (screen_h - group_h) / 2;
    bolt_y = y;
    word_y = y + bolt.image.GetHeight();
    bolt_opacity = 0;
    word_opacity = 0;
    glow_opacity = 0;

    # 0-30 black (~1 second at Plymouth's refresh cadence).
    if (frame >= 50 && frame < 117) {
        progress = (frame - 50) / 67;
        if (progress > 1) progress = 1;
        bolt_opacity = progress;
        bolt_y = y - (1 - progress) * 70;
        glow_opacity = (1 - progress) * 0.9;
    } else if (frame >= 117 && frame < 184) {
        bolt_opacity = 1;
        progress = (frame - 117) / 67;
        if (progress > 1) progress = 1;
        word_opacity = progress;
        word_y = y + bolt.image.GetHeight() + (1 - progress) * 75;
    } else if (frame >= 184) {
        bolt_opacity = 1;
        word_opacity = 1;
        pulse = 0.975 + 0.025 * (0.5 + 0.5 * Math.Cos(frame / 24));
        bolt_opacity = pulse;
        word_opacity = pulse;
    }

    bolt.sprite.SetPosition(x, bolt_y, 10);
    bolt.sprite.SetOpacity(bolt_opacity);
    word.sprite.SetPosition(x, word_y, 11);
    word.sprite.SetOpacity(word_opacity);
    glow.sprite.SetPosition((screen_w - glow.image.GetWidth()) / 2,
                            y + bolt.image.GetHeight() / 4, 9);
    glow.sprite.SetOpacity(glow_opacity);
}
Plymouth.SetRefreshFunction(refresh_callback);
''', encoding="utf-8")
    (target / "zenex-lowram.script").write_text(r'''Window.SetBackgroundTopColor(0, 0, 0);
Window.SetBackgroundBottomColor(0, 0, 0);
logo.image = Image("zenex-logo.png");
logo.sprite = Sprite(logo.image);
logo.sprite.SetZ(10);
fun refresh_callback() {
    logo.sprite.SetPosition((Window.GetWidth() - logo.image.GetWidth()) / 2,
                            (Window.GetHeight() - logo.image.GetHeight()) / 2, 10);
}
Plymouth.SetRefreshFunction(refresh_callback);
''', encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    if not SOURCE.is_file():
        raise SystemExit(f"Missing canonical transparent logo: {SOURCE}")
    write_zip(output_dir, low_ram=False)
    write_zip(output_dir, low_ram=True)
    write_preview(output_dir)
    write_plymouth_assets()


if __name__ == "__main__":
    main()
