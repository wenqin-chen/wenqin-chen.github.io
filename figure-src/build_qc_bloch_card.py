"""Pad the quantum-computing Bloch-sphere card crop.

The braiding and Bloch panels sit in equal-width grid columns on the homepage.
The Bloch crop is nearly square, so it renders taller than the braiding crop.
This script adds horizontal white padding to the Bloch crop so its aspect ratio
matches the braiding panel without cropping the sphere.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets" / "figures"
BLOCH = ASSETS / "qc-crop-bloch.png"
BRAIDING = ASSETS / "qc-crop-braiding.png"


def content_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    arr = np.asarray(image.convert("RGB"))
    # Ignore pure/near-white padding, but keep anti-aliased labels and sphere lines.
    mask = np.any(arr < 248, axis=2)
    ys, xs = np.where(mask)
    if len(xs) == 0 or len(ys) == 0:
        return (0, 0, image.width, image.height)
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def main() -> None:
    bloch = Image.open(BLOCH).convert("RGB")
    braiding = Image.open(BRAIDING).convert("RGB")

    content = bloch.crop(content_bbox(bloch))
    target_ratio = braiding.width / braiding.height
    target_width = max(content.width, math.ceil(content.height * target_ratio))

    output = Image.new("RGB", (target_width, content.height), "white")
    output.paste(content, ((target_width - content.width) // 2, 0))
    output.save(BLOCH, optimize=True)
    print(f"Wrote {BLOCH} ({output.width}x{output.height})")


if __name__ == "__main__":
    main()
