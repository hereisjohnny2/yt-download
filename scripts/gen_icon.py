"""Generates the original app icon (assets/icon.png and assets/icon.ico).

Run once with `python scripts/gen_icon.py` whenever the design changes.
Requires Pillow (dev-only dependency, not needed to run the app itself).
"""

import math
import os

from PIL import Image, ImageDraw

SIZE = 512
BG_TOP = (124, 92, 255)      # #7c5cff
BG_BOTTOM = (90, 63, 214)    # #5a3fd6
NOTE_COLOR = (255, 255, 255)
ARROW_COLOR = (255, 255, 255)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")


def rounded_gradient_background(size: int) -> Image.Image:
    base = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gradient = Image.new("RGBA", (size, size))
    for y in range(size):
        t = y / (size - 1)
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
        for x in range(size):
            gradient.putpixel((x, y), (r, g, b, 255))

    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    radius = int(size * 0.22)
    mask_draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)

    base.paste(gradient, (0, 0), mask)
    return base


def draw_note_and_arrow(img: Image.Image):
    draw = ImageDraw.Draw(img)
    size = img.size[0]
    cx, cy = size * 0.5, size * 0.46

    # Musical eighth note: notehead + stem + flag (generic, original shape).
    stem_x = cx + size * 0.08
    stem_top = cy - size * 0.24
    stem_bottom = cy + size * 0.02

    head_w, head_h = size * 0.15, size * 0.115
    draw.ellipse(
        [stem_x - head_w, stem_bottom - head_h, stem_x + head_w * 0.2, stem_bottom + head_h],
        fill=NOTE_COLOR,
    )
    draw.line([(stem_x, stem_bottom), (stem_x, stem_top)], fill=NOTE_COLOR, width=int(size * 0.045))

    flag = [
        (stem_x, stem_top),
        (stem_x + size * 0.17, stem_top + size * 0.05),
        (stem_x + size * 0.14, stem_top + size * 0.18),
        (stem_x, stem_top + size * 0.11),
    ]
    draw.polygon(flag, fill=NOTE_COLOR)

    # Downward arrow underneath, signalling "download".
    arrow_cx = cx - size * 0.01
    arrow_top = cy + size * 0.1
    arrow_bottom = cy + size * 0.27
    width = int(size * 0.05)
    draw.line([(arrow_cx, arrow_top), (arrow_cx, arrow_bottom)], fill=ARROW_COLOR, width=width)
    head = size * 0.065
    draw.polygon(
        [
            (arrow_cx - head, arrow_bottom - head * 0.6),
            (arrow_cx + head, arrow_bottom - head * 0.6),
            (arrow_cx, arrow_bottom + head * 0.6),
        ],
        fill=ARROW_COLOR,
    )


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    img = rounded_gradient_background(SIZE)
    draw_note_and_arrow(img)

    png_path = os.path.join(OUT_DIR, "icon.png")
    img.save(png_path)

    ico_path = os.path.join(OUT_DIR, "icon.ico")
    sizes = [16, 24, 32, 48, 64, 128, 256]
    img.save(ico_path, sizes=[(s, s) for s in sizes])

    print(f"Wrote {png_path}")
    print(f"Wrote {ico_path}")


if __name__ == "__main__":
    main()
