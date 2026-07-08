# figure-src — source for the portfolio figures

Tooling that builds and crops the portfolio figures. The neural-quantum-states figure uses bundled data;
the Hall Crystal and condensed-matter homepage banners read local source figures from their research folders.

## Contents
- `build_nqs_figure.py` — the plotting script.
- `build_qc_tetron_crop.py` — regenerates the quantum-computing card's Tetron-panel crop from `assets/figures/qc-fig-tetron.png`.
- `build_qc_bloch_card.py` — pads the quantum-computing Bloch-sphere card crop so its rendered height matches the braiding panel.
- `build_hf_banner.py` — crops the Hall Crystal S8b texture plot and adds compact colorbars for the homepage Hartree-Fock banner.
- `build_cooper_banner.py` — combines Cooper-pair figures with `Figure-1.pdf` from the phonon-magnetism project.
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

For the quantum-computing Tetron crop:
```
python3 build_qc_tetron_crop.py
```
Requires `Pillow`. This rewrites `../assets/figures/qc-crop-tetron.png`.

For the quantum-computing Bloch-sphere card crop:
```
python3 build_qc_bloch_card.py
```
Requires `numpy` and `Pillow`. This rewrites `../assets/figures/qc-crop-bloch.png`.

For the Hartree-Fock homepage banner:
```
python3 build_hf_banner.py
```
Requires `Pillow` and reads the local Hall Crystal plot at
`~/Documents/Hall Crystal/projects/continuum_2deg_hf/figures/dilute_textures/texture_S8b.png`.
This rewrites `../assets/figures/hf-s8b-texture-banner.png`.

For the condensed-matter homepage panels:
```
python3 build_cooper_banner.py
```
Requires `Pillow` and `pdftoppm`. It reads
`~/Documents/Flat-band superconductivity/Cooper Pair/Main/Fig1.png` and
`~/Documents/Flat-band superconductivity/Cooper Pair/Main/Figure2band_fromsvg.pdf`, plus
`~/Documents/DiracPhonon/Geometric_theory/Figure-1.pdf`.
This rewrites `../assets/figures/cooper-pair-banner.png` and
`../assets/figures/chiral-phonon-banner.png`.

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
