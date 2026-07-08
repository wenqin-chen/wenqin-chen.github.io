# figure-src — source for the portfolio figures

Tooling that builds and crops the portfolio figures. The neural-quantum-states figure uses bundled data;
the Hall Crystal and condensed-matter homepage banners read local source figures from their research folders.

## Contents
- `build_nqs_figure.py` — the plotting script.
- `build_qc_tetron_crop.py` — regenerates the quantum-computing card's Tetron-panel crop from `assets/figures/qc-fig-tetron.png`.
- `build_qc_bloch_card.py` — pads the quantum-computing Bloch-sphere card crop so its rendered height matches the braiding panel.
- `build_hf_banner.py` — crops the Hall Crystal S8b texture plot and adds compact colorbars for the homepage Hartree-Fock banner (superseded on the homepage by the SCF trio below; kept for reuse).
- `build_scf_figures.py` — rebuilds the three SCF-method figures on the Hartree-Fock banner (flowchart, convergence, seed→SkX textures) from `scf_figure_data.npz`. Site edits vs. the deck originals: the flowchart is redrawn fully generic (order parameter m, H[m] = H₀ + V[m] — no lattice-specific Hamiltonian); convergence title is just "SCF convergence" with the tolerance annotation removed; the textures suptitle is removed.
- `extract_scf_data.py` — one-shot that regenerates `scf_figure_data.npz` by re-running the anchor-cell canted-Néel SCF (n=0.05, α=1.4, A=0.3, L=9, p=2, I/Ic=1.045, tol=1e-5, κ_nk=24) with the research solver in `~/Documents/Hall Crystal/projects/` (read-only; ~13 min serial).
- `build_cooper_banner.py` — combines Cooper-pair figures with `Figure-1.pdf` from the phonon-magnetism project.
- `figure_data.npz` — the minimal data the figure needs (~22 KB), extracted once from the research run.
- `scf_figure_data.npz` — the SCF-figure data (~4 KB): site positions, seed + converged textures, per-iteration residual and free-energy histories (29 iterations, final residual 1.0e-5, F/site −0.4387).
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

For the Hartree-Fock homepage banner (the SCF-method trio):
```
python3 build_scf_figures.py
```
Requires `numpy` + `matplotlib`; fully self-contained (reads only `scf_figure_data.npz`).
This rewrites `../assets/figures/hf-scf-flowchart.png`, `hf-scf-convergence.png`,
and `hf-scf-textures.png`. To re-extract the data from a fresh solver run
(only needed if the run recipe changes), `python3 extract_scf_data.py` —
that one does read the research repo.

The older single-image banner:
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
