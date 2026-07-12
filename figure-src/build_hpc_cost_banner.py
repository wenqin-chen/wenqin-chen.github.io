"""Build the hpc-cost-analytics homepage banner (2 panels).

Left: the run-cost distribution (log scale) across the 2,127-run telemetry
warehouse. Right: out-of-campaign predictions vs actual cost from the
gradient-boosted model, refit here exactly as in the public notebook
(same features, hyperparameters, and leave-campaign-out split).

Reads the public parquet of github.com/wenqin-chen/hpc-cost-analytics from a
local checkout (HPC_COST_ANALYTICS_DIR overrides); writes only
assets/figures/hpc-cost-banner.png. Uses the site palette on white.
"""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import GroupKFold, cross_val_predict

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "assets" / "figures" / "hpc-cost-banner.png"
REPO = Path(os.environ.get("HPC_COST_ANALYTICS_DIR",
                           Path.home() / "Documents" / "hpc-cost-analytics"))

INK, INK2, MUTED, LINE = "#1c1b19", "#4a4842", "#767268", "#d8d4c8"
ACCENT = "#dc3521"
SRC_COLORS = {"continuum_scf": ACCENT, "lattice_scf_v2": "#4a4842", "lattice_scf": "#a39e91"}
SRC_LABELS = {"continuum_scf": "continuum solver", "lattice_scf_v2": "lattice solver v2",
              "lattice_scf": "lattice solver v1"}

runs = pd.read_parquet(REPO / "data" / "runs.parquet")

# training table, exactly as in the public notebook
runs["is_stub"] = (runs.status == "unknown") & runs.n_iter.isna()
runs["is_censored"] = (runs.status == "max_iter") | (runs.n_iter >= runs.max_iter)
tr = runs[(runs.wall_minutes > 0) & ~runs.is_stub & ~runs.is_censored.fillna(False)].copy()
tr = tr.reset_index(drop=True)
CAT = ["source", "seed_family", "mixing", "machine"]
NUM = ["grid_k", "basis_nharm", "tol", "max_iter"]
X = tr[CAT + NUM].copy()
for c in CAT:
    X[c] = X[c].astype("category")
y = np.log(tr["wall_minutes"].values)
groups = tr["campaign"].values

hgb = HistGradientBoostingRegressor(categorical_features="from_dtype",
                                    random_state=0, max_iter=300, learning_rate=0.05)
pred = cross_val_predict(hgb, X, y, cv=GroupKFold(5), groups=groups)
tr["pred_min"] = np.exp(pred)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "text.color": INK, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.linewidth": 1.0,
})

fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.0), dpi=220)
fig.patch.set_facecolor("white")

# ---- left: cost distribution --------------------------------------------
ax = axes[0]
ax.set_facecolor("white")
timed = runs[runs.wall_minutes > 0]
bins = np.logspace(np.log10(timed.wall_minutes.min()), np.log10(timed.wall_minutes.max()), 44)
ax.hist(timed.wall_minutes, bins=bins, color=INK2, alpha=0.85, edgecolor="white", lw=0.4)
med = timed.wall_minutes.median()
ax.axvline(med, color=ACCENT, lw=2)
ax.text(med * 1.35, ax.get_ylim()[1] * 0.93, f"median {med:.1f} min",
        color=ACCENT, fontsize=10.5, weight="bold", va="top")
ax.set_xscale("log")
ax.set_xlabel("wall-clock cost (minutes, log scale)", fontsize=10.5)
ax.set_ylabel("runs", fontsize=10.5)
ax.set_title("2,127 solver runs, seconds to hours", fontsize=12, color=INK, pad=8)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

# ---- right: predicted vs actual (out-of-campaign) ------------------------
ax = axes[1]
ax.set_facecolor("white")
lims = (tr.wall_minutes.min() * 0.6, tr.wall_minutes.max() * 1.6)
ax.plot(lims, lims, ls="--", lw=1.1, color=MUTED, zorder=1)
for src, g in tr.groupby("source"):
    ax.scatter(g.wall_minutes, g.pred_min, s=11, alpha=0.5, lw=0,
               color=SRC_COLORS[src], label=SRC_LABELS[src], zorder=2)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(lims); ax.set_ylim(lims)
ax.set_xlabel("actual cost (min)", fontsize=10.5)
ax.set_ylabel("predicted cost (min)", fontsize=10.5)
ax.set_title("Predicted vs actual, unseen campaigns", fontsize=12, color=INK, pad=8)
ax.legend(frameon=False, fontsize=9, loc="upper left", handletextpad=0.1, borderaxespad=0.2)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

fig.tight_layout(w_pad=2.4)
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, facecolor="white", bbox_inches="tight")
print(f"wrote {OUT}")
