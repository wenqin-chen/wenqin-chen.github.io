"""Build the Hartree-Fock homepage banner from the Hall Crystal texture plot.

The source plot is the full scientific S8b texture figure. For the homepage card
we keep axes, tick numbers, and compact colorbars, while removing the suptitle
and panel titles so the banner stays readable at small size. The homepage banner
uses the original charge-density and spin-direction colors from the source plot.
"""

from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets" / "figures"
OUTPUT = ASSETS / "hf-s8b-texture-banner.png"

DEFAULT_HF_DIR = (
    Path.home()
    / "Documents"
    / "Hall Crystal"
    / "projects"
    / "continuum_2deg_hf"
)
HF_DIR = Path(os.environ.get("HALL_CRYSTAL_HF_DIR", DEFAULT_HF_DIR))
SOURCE = HF_DIR / "figures" / "dilute_textures" / "texture_S8b.png"

# Pixel crops in the rendered source image. Each crop keeps one axes box plus
# tick labels and axis labels, while excluding titles and source colorbars.
PANEL_CROPS = [
    (0, 136, 462, 815),
    (890, 136, 1355, 815),
]
COLORBAR_CROPS = [
    (500, 186, 524, 702),
    (1393, 186, 1417, 702),
]
PANEL_GAP = 18
BAR_GAP = 10
BAR_WIDTH = 14
BAR_LABEL_GAP = 7
BAR_TEXT_WIDTH = 48
BAR_TOP = 22
BAR_BOTTOM = 608

BLACK = (20, 20, 20)


def font(size: int):
    for path in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/Library/Fonts/Arial.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def draw_colorbar(
    block: Image.Image,
    source_bar: Image.Image,
    x: int,
    top: int,
    bottom: int,
    ticks: list[tuple[float, str]],
    tick_font,
) -> None:
    draw = ImageDraw.Draw(block)
    height = bottom - top
    bar = source_bar.resize((BAR_WIDTH, height), Image.Resampling.BICUBIC)
    block.paste(bar, (x, top))

    draw.rectangle([x, top, x + BAR_WIDTH - 1, bottom - 1], outline=BLACK, width=1)
    for t, label in ticks:
        y = round(bottom - t * height)
        draw.line([(x + BAR_WIDTH, y), (x + BAR_WIDTH + 4, y)], fill=BLACK, width=1)
        bbox = draw.textbbox((0, 0), label, font=tick_font)
        text_y = y - (bbox[3] - bbox[1]) / 2
        draw.text((x + BAR_WIDTH + BAR_LABEL_GAP, text_y), label, font=tick_font, fill=BLACK)


def panel_block(
    panel: Image.Image,
    source_bar: Image.Image,
    ticks: list[tuple[float, str]],
    tick_font,
) -> Image.Image:
    block_width = panel.width + BAR_GAP + BAR_WIDTH + BAR_LABEL_GAP + BAR_TEXT_WIDTH
    block = Image.new("RGB", (block_width, panel.height), "white")
    block.paste(panel, (0, 0))
    draw_colorbar(block, source_bar, panel.width + BAR_GAP, BAR_TOP, BAR_BOTTOM, ticks, tick_font)
    return block


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Missing source texture plot: {SOURCE}")

    source = Image.open(SOURCE).convert("RGB")
    panels = [source.crop(crop) for crop in PANEL_CROPS]
    colorbars = [source.crop(crop) for crop in COLORBAR_CROPS]
    tick_font = font(22)
    blocks = [
        panel_block(panels[0], colorbars[0], [(0.0, "0"), (0.5, "3"), (1.0, "6")], tick_font),
        panel_block(panels[1], colorbars[1], [(0.0, "-1"), (0.5, "0"), (1.0, "1")], tick_font),
    ]

    width = sum(block.width for block in blocks) + PANEL_GAP * (len(blocks) - 1)
    height = max(block.height for block in blocks)
    banner = Image.new("RGB", (width, height), "white")

    x = 0
    for block in blocks:
        banner.paste(block, (x, 0))
        x += block.width + PANEL_GAP

    ASSETS.mkdir(parents=True, exist_ok=True)
    banner.save(OUTPUT, optimize=True)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
