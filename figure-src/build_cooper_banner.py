"""Build the condensed-matter homepage panels from Cooper-pair and phonon figures.

The Cooper-pair panel combines Fig1 with panel (d) from Figure2band_fromsvg.pdf.
The Chiral-phonon panel renders Figure-1.pdf from the phonon-magnetism project.
The source files are read from local research folders, but only website assets
under assets/figures are written.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image, ImageChops, ImageDraw


HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets" / "figures"
COOPER_OUTPUT = ASSETS / "cooper-pair-banner.png"
PHONON_OUTPUT = ASSETS / "chiral-phonon-banner.png"

DEFAULT_COOPER_DIR = (
    Path.home()
    / "Documents"
    / "Flat-band superconductivity"
    / "Cooper Pair"
    / "Main"
)
COOPER_DIR = Path(os.environ.get("COOPER_PAIR_FIGURE_DIR", DEFAULT_COOPER_DIR))
FIG1 = COOPER_DIR / "Fig1.png"
FIG2_PDF = COOPER_DIR / "Figure2band_fromsvg.pdf"

DEFAULT_PHONON_DIR = Path.home() / "Documents" / "DiracPhonon" / "Geometric_theory"
PHONON_DIR = Path(os.environ.get("DIRAC_PHONON_FIGURE_DIR", DEFAULT_PHONON_DIR))
PHONON_PDF = PHONON_DIR / "Figure-1.pdf"

PDF_DPI = 240
PHONON_PDF_DPI = 360
PANEL_D_CROP = (90, 600, 1500, 1885)
PANEL_D_LABEL_MASK = (0, 0, 170, 145)
FIG1_THRESHOLD = 12
FIG1_CROP_PAD = (30, 25, 30, 20)
PANEL_HEIGHT = 760
V_PAD = 20                   # top/bottom padding of both panels
COOPER_SIDE_PAD = 150        # left/right whitespace of the Cooper panel
PANEL_GAP = 130              # whitespace between Fig1 and panel (d)
PHONON_SIDE_FRACTION = 0.14  # phonon whitespace on each side (of canvas width)


def flatten_to_white(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    background.alpha_composite(rgba)
    return background.convert("RGB")


def crop_nonwhite(image: Image.Image) -> Image.Image:
    background = Image.new("RGB", image.size, "white")
    diff = ImageChops.difference(image, background)
    mask = diff.convert("L").point(lambda pixel: 255 if pixel > FIG1_THRESHOLD else 0)
    bbox = mask.getbbox()
    if bbox is None:
        return image

    left_pad, top_pad, right_pad, bottom_pad = FIG1_CROP_PAD
    left = max(0, bbox[0] - left_pad)
    top = max(0, bbox[1] - top_pad)
    right = min(image.width, bbox[2] + right_pad)
    bottom = min(image.height, bbox[3] + bottom_pad)
    return image.crop((left, top, right, bottom))


def resize_to_height(image: Image.Image, height: int) -> Image.Image:
    width = round(image.width * height / image.height)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def resize_to_width(image: Image.Image, width: int) -> Image.Image:
    height = round(image.height * width / image.width)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def render_pdf_page(pdf_path: Path, dpi: int) -> Image.Image:
    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm is None:
        raise RuntimeError("pdftoppm is required to render source PDFs")

    with TemporaryDirectory() as tmpdir:
        prefix = Path(tmpdir) / "figure"
        subprocess.run(
            [pdftoppm, "-png", "-singlefile", "-r", str(dpi), str(pdf_path), str(prefix)],
            check=True,
        )
        return Image.open(prefix.with_suffix(".png")).convert("RGB")


def main() -> None:
    if not FIG1.exists():
        raise FileNotFoundError(f"Missing source figure: {FIG1}")
    if not FIG2_PDF.exists():
        raise FileNotFoundError(f"Missing source PDF: {FIG2_PDF}")
    if not PHONON_PDF.exists():
        raise FileNotFoundError(f"Missing source PDF: {PHONON_PDF}")

    fig1 = crop_nonwhite(flatten_to_white(Image.open(FIG1)))
    panel_d = render_pdf_page(FIG2_PDF, PDF_DPI).crop(PANEL_D_CROP)
    ImageDraw.Draw(panel_d).rectangle(PANEL_D_LABEL_MASK, fill="white")
    phonon = render_pdf_page(PHONON_PDF, PHONON_PDF_DPI)

    panels = [resize_to_height(fig1, PANEL_HEIGHT), resize_to_height(panel_d, PANEL_HEIGHT)]
    content_width = sum(panel.width for panel in panels) + PANEL_GAP

    width = content_width + COOPER_SIDE_PAD * 2
    cooper_panel = Image.new("RGB", (width, PANEL_HEIGHT + V_PAD * 2), "white")

    x = COOPER_SIDE_PAD
    for panel in panels:
        cooper_panel.paste(panel, (x, V_PAD))
        x += panel.width + PANEL_GAP

    phonon_side = round(width * PHONON_SIDE_FRACTION)
    phonon = resize_to_width(phonon, width - 2 * phonon_side)
    phonon_panel = Image.new("RGB", (width, phonon.height + V_PAD * 2), "white")
    phonon_panel.paste(phonon, (phonon_side, V_PAD))

    ASSETS.mkdir(parents=True, exist_ok=True)
    cooper_panel.save(COOPER_OUTPUT, optimize=True)
    phonon_panel.save(PHONON_OUTPUT, optimize=True)
    print(f"Wrote {COOPER_OUTPUT}")
    print(f"Wrote {PHONON_OUTPUT}")


if __name__ == "__main__":
    main()
