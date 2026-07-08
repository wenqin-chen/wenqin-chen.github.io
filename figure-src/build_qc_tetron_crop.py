"""Build the quantum-computing Tetron card crop.

The source paper figure has neighboring-panel text clipped into the top edge of
the Tetron panel. Keep the cleanup rectangles tight so they do not overlap the
G1/G2 gate labels in the device drawing.
"""

from pathlib import Path

from PIL import Image, ImageDraw


HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets" / "figures"

SOURCE = ASSETS / "qc-fig-tetron.png"
OUTPUT = ASSETS / "qc-crop-tetron.png"

# Left, top, right, bottom in SOURCE pixel coordinates.
TETRON_CROP = (20, 496, 1210, 884)

# Rectangles in cropped-image coordinates. These remove the panel letter and
# clipped labels from neighboring panels without touching the device labels.
CLEANUP_RECTS = [
    (45, 0, 125, 52),    # panel label "(d)"
    (400, 0, 520, 9),    # clipped tick/label from the panel above
    (860, 0, 982, 34),   # clipped "Vx(Delta)" label from the panel above
]


def main() -> None:
    image = Image.open(SOURCE).convert("RGB")
    crop = image.crop(TETRON_CROP)
    draw = ImageDraw.Draw(crop)

    for rect in CLEANUP_RECTS:
        draw.rectangle(rect, fill="white")

    crop.save(OUTPUT)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
