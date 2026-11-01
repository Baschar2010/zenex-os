#!/usr/bin/env python3
"""Make only the neutral checkerboard around the supplied ZENEX logo transparent.

All RGB values of retained artwork are preserved exactly from the source PNG.
"""
from collections import deque
from pathlib import Path
from PIL import Image

ASSETS = Path(__file__).resolve().parent
SOURCE = ASSETS / "zenex-logo-source.png"
OUTPUT = ASSETS / "zenex-logo-transparent.png"

def is_neutral_background(rgb: tuple[int, int, int]) -> bool:
    low, high = min(rgb), max(rgb)
    light_checker_or_border = high - low <= 110 and (sum(rgb) // 3 >= 138 or sum(rgb) // 3 <= 90)
    return light_checker_or_border

def main() -> None:
    source = Image.open(SOURCE).convert("RGBA")
    width, height = source.size
    pixels = list(source.get_flattened_data())
    transparent = bytearray(width * height)
    queue: deque[int] = deque()

    def add_if_background(index: int) -> None:
        if transparent[index]:
            return
        r, g, b, _ = pixels[index]
        if is_neutral_background((r, g, b)):
            transparent[index] = 1
            queue.append(index)

    for x in range(width):
        add_if_background(x)
        add_if_background((height - 1) * width + x)
    for y in range(height):
        add_if_background(y * width)
        add_if_background(y * width + width - 1)

    while queue:
        index = queue.popleft()
        x = index % width
        if x:
            add_if_background(index - 1)
        if x + 1 < width:
            add_if_background(index + 1)
        if index >= width:
            add_if_background(index - width)
        if index + width < width * height:
            add_if_background(index + width)

    output = source.copy()
    output_pixels = pixels.copy()
    for index, is_background in enumerate(transparent):
        if is_background:
            r, g, b, _ = output_pixels[index]
            output_pixels[index] = (r, g, b, 0)
    output.putdata(output_pixels)
    output.save(OUTPUT, optimize=True)
    kept = sum(1 for flag in transparent if not flag)
    print(f"Imported {SOURCE.name} unchanged; made only exterior neutral background transparent ({kept} opaque pixels).")

if __name__ == "__main__":
    main()
