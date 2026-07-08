"""One-shot: regenerate the anchor-cell canted-Neel SCF run and export the
figure data for the portfolio site (figure-src/scf_figure_data.npz).

Reads the research repo READ-ONLY (imports + one JSON); writes only into the
website folder. Recipe mirrors _oneshot_phase5_stage4_competing_seeds.py:
(n=0.05, alpha=1.4, A=0.3), L=9, p=2, I/Ic=1.045, canted_neel seed
(A=0.3, S_z0=0, p=2), Pulay mixing, tol=1e-5.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path("/Users/wenqinchen/Documents/Hall Crystal/projects")
SOC = REPO / "hubbard_skyrmion_soc"
HUB = REPO / "hubbard_model"
for p in (str(SOC), str(HUB)):
    if p not in sys.path:
        sys.path.insert(0, p)

from hubbard_meanfield import MagneticSupercell  # noqa: E402
from hubbard_unrestricted_meanfield import self_consistent_solve  # noqa: E402
from cell_params import params_for_cell  # noqa: E402
from texture_seeds_skx import canted_neel_skx  # noqa: E402

OUT = Path("/Users/wenqinchen/Documents/Job application/wenqinchen98.github.io/figure-src/scf_figure_data.npz")

CELL_N, CELL_ALPHA, CELL_A = 0.05, 1.4, 0.3
L, P_TRIAD, I_OVER_IC = 9, 2, 1.045
KAPPA_NK, TOL, MAX_ITER, WORKERS = 24, 1.0e-5, 200, 1

# --- I from the Stage-1 Lindhard scan (same interpolation as the driver) ---
stage1 = json.loads((SOC / "meanfield_outputs" / "phase5_stage1_lindhard_scan.json").read_text())
row = next(r for r in stage1["results"]
           if abs(r["n"] - CELL_N) < 1e-9 and abs(r["alpha"] - CELL_ALPHA) < 1e-9)
s_target = P_TRIAD / L  # 2/9
chi_at_Q = float(np.interp(s_target, np.asarray(row["s_grid"], float),
                           np.asarray(row["chi_zz_diagnostic"]["chi_M_radial"], float)))
Ic_at_Q = 1.0 / (2.0 * chi_at_Q)
I_cell = I_OVER_IC * Ic_at_Q
print(f"chi(Q=2/9) = {chi_at_Q:.6f}  ->  I = 1.045 * Ic = {I_cell:.6f}")

supercell = MagneticSupercell(L, L)
params = params_for_cell(alpha=CELL_ALPHA, A=CELL_A)
seed = canted_neel_skx(supercell, A=0.3, S_z0=0.0, p=P_TRIAD)

t0 = time.time()
scf = self_consistent_solve(
    seed, params, supercell,
    coupling_I=I_cell, kappa_nk=KAPPA_NK, twist_grid=1,
    fixed_filling=CELL_N, mixing="pulay", mixing_alpha=0.5,
    tol=TOL, max_iter=MAX_ITER, workers=WORKERS,
)
dt = time.time() - t0
res = np.asarray(scf["residual_history"], float)
ene = np.asarray(scf["energy_history"], float)
print(f"SCF: {scf['status']} in {len(res)} iters ({dt:.0f}s); "
      f"final residual {res[-1]:.2e}, F/site {ene[-1]:.6f}")

OUT.parent.mkdir(parents=True, exist_ok=True)
np.savez_compressed(
    OUT,
    positions=supercell.site_positions_cartesian(),
    seed=seed,
    converged=np.asarray(scf["S_converged"], float),
    residual_history=res,
    energy_history=ene,
    meta=np.array([CELL_N, CELL_ALPHA, CELL_A, I_cell, KAPPA_NK, TOL], float),
)
print(f"wrote {OUT}  ({OUT.stat().st_size/1024:.0f} KB)")
