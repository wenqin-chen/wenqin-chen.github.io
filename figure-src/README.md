# figure-src — source for the portfolio figures

Self-contained tooling that builds the **Neural Quantum States** project figures. It depends only on the
bundled data here — **not** on the research repo — so the site is reproducible on its own.

## Contents
- `build_nqs_figure.py` — the plotting script.
- `figure_data.npz` — the minimal data the figure needs (~22 KB), extracted once from the research run.
- `nqs_texture_convergence_2panel.png`, `nqs_texture_banner.png` — full-resolution source plots.

## Regenerate
```
python3 build_nqs_figure.py
```
Requires `numpy`, `matplotlib`, `Pillow`. This rewrites the full-res sources here **and** the web-optimized
assets the site actually serves:
- `../assets/figures/nqs-2panel.png` — the two-panel figure on the NQS project page.
- `../assets/figures/nqs-texture.jpg` — the skyrmion-texture banner on the home-page card.

## What the figure shows
- **Left panel** — the real-space spin texture the trained network holds (a cell-D skyrmion crystal):
  colour is out-of-plane spin `m_z`, arrows are in-plane spin; the green rhombus is one magnetic cell.
- **Right panel** — the N=18 training convergence: four candidate orders (skyrmion crystal, paramagnet,
  in-plane spiral, ferromagnet), each optimized by natural-gradient (MinSR) variational Monte Carlo.

## Data provenance (`figure_data.npz`)
Extracted from the `continuum_skyrmion_nqs` production run:
- `q1`, `q2` — reciprocal lattice vectors of the magnetic cell (from `ohaus_texture.npz`).
- `g16` — the 16×16×3 measured NQS spin grid (`diagnose_N18_hires_skx.json`, `m_grid_final`, per bin-area).
- `skx` / `fluid` / `spiral` / `fm` — twist-averaged convergence curves, each anchored to its reliable `E_final`.
