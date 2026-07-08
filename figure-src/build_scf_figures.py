"""Rebuild the three SCF-method figures for the mean-field project banner.

Self-contained (numpy + matplotlib + scf_figure_data.npz only — no dependency
on the research repo). The data file was extracted once from a canted-Neel
anchor-cell run (n=0.05, alpha=1.4, A=0.3, L=9, p=2, I/Ic=1.045, tol=1e-5)
of the hubbard_skyrmion_soc mean-field solver.

Outputs (overwrites the banner images):
    ../assets/figures/hf-scf-flowchart.png     SCF algorithm flowchart
    ../assets/figures/hf-scf-convergence.png   residual + free-energy history
    ../assets/figures/hf-scf-textures.png      initial seed -> converged SkX

Site edits vs. the original deck versions (2026-07-07):
    - convergence: title is just "SCF convergence" (cell parameters dropped);
      the orange "tolerance 10^-5" dashed line + label are removed.
    - textures: the "in-plane seed self-consistently grows out-of-plane
      cores" suptitle is removed.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon

HERE = Path(__file__).resolve().parent
DATA = np.load(HERE / "scf_figure_data.npz")
OUTDIR = HERE.parent / "assets" / "figures"

# ---- deck palette ----------------------------------------------------------
INK = "#16324f"        # dark navy (text, arrows, residual curve)
TEAL = "#2e6f8e"       # free-energy curve / saddle box
ORANGE = "#e87d2f"     # seed box / "no" branch
GREEN = "#2f7d32"      # mix-and-update box
BOX_BG = "#ffffff"
SZ_CMAP = LinearSegmentedColormap.from_list(
    "deck_diverging", ["#2e6f8e", "#f7f6f2", "#e98a4e"]
)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Arial", "DejaVu Sans"],
    "mathtext.fontset": "dejavusans",
})


# ===========================================================================
# 1. SCF algorithm flowchart
# ===========================================================================
def build_flowchart(path: Path) -> None:
    fig = plt.figure(figsize=(9.0, 10.4), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 116)
    ax.axis("off")

    def box(cx, cy, w, h, edge, face, lines, lw=2.6):
        ax.add_patch(FancyBboxPatch(
            (cx - w / 2, cy - h / 2), w, h,
            boxstyle="round,pad=0.6,rounding_size=1.2",
            edgecolor=edge, facecolor=face, linewidth=lw, zorder=3,
        ))
        n = len(lines)
        for i, (txt, kw) in enumerate(lines):
            dy = (n - 1) / 2.0 - i
            gap = h / (n + 0.2) if n > 1 else 0.0
            ax.text(cx, cy + dy * gap, txt, ha="center", va="center",
                    zorder=4, **kw)

    bold = dict(fontsize=15.5, fontweight="bold", color=INK)
    math = dict(fontsize=13.5, color=INK)

    cx = 38.0  # main column
    y_seed, y_ham, y_diag, y_spin, y_conv, y_saddle = 108.5, 92, 75.5, 60, 39, 12.5
    cx_mix, y_mix = 78.0, 68.0

    box(cx, y_seed, 40, 6.4, ORANGE, "#fdebd8",
        [(r"Initial spin texture  $S^{\,0}$", bold)])
    box(cx, y_ham, 46, 9.6, INK, BOX_BG, [
        ("Build mean-field Hamiltonian", bold),
        (r"$H[S] = H_t + H_R - \sum_i S_i \cdot \sigma_i - A\,(S_i^z)^2$", math),
    ])
    box(cx, y_diag, 46, 6.4, INK, BOX_BG,
        [(r"Diagonalize over the $k$-grid", bold)])
    box(cx, y_spin, 46, 9.6, INK, BOX_BG, [
        ("Compute new spin field", bold),
        (r"$T[S] = I\,\langle \sigma_i \rangle$", math),
    ])
    box(cx, y_saddle, 46, 9.6, TEAL, "#ddeef5", [
        ("Saddle point", dict(fontsize=15.5, fontweight="bold", color=TEAL)),
        (r"$S^{\star} = T[S^{\star}]\;\rightarrow\;$texture, $F$, $\mu$, $\sigma_{xy}$", math),
    ])
    box(cx_mix, y_mix, 30, 9.6, GREEN, "#ecf5ec", [
        ("Mix and update", dict(fontsize=15.5, fontweight="bold", color=GREEN)),
        (r"$S \leftarrow (1-\alpha)S + \alpha\,T[S]$", math),
    ])

    # decision diamond
    dw, dh = 24.5, 10.5
    ax.add_patch(Polygon(
        [(cx - dw, y_conv), (cx, y_conv + dh), (cx + dw, y_conv), (cx, y_conv - dh)],
        closed=True, edgecolor=INK, facecolor="#eef2f5", linewidth=2.6, zorder=3,
    ))
    ax.text(cx, y_conv + 2.6, "converged?", ha="center", va="center", zorder=4, **bold)
    ax.text(cx, y_conv - 2.6, r"$\|T[S]-S\|_2/\sqrt{N_c} < 10^{-5}$",
            ha="center", va="center", zorder=4, **math)

    def arrow(p0, p1, color=INK, connectionstyle=None):
        ax.add_patch(FancyArrowPatch(
            p0, p1, arrowstyle="-|>", mutation_scale=26,
            linewidth=2.6, color=color, zorder=2,
            connectionstyle=connectionstyle or "arc3,rad=0",
            shrinkA=0, shrinkB=0,
        ))

    arrow((cx, y_seed - 3.8), (cx, y_ham + 5.6))
    arrow((cx, y_ham - 5.6), (cx, y_diag + 3.9))
    arrow((cx, y_diag - 3.9), (cx, y_spin + 5.6))
    arrow((cx, y_spin - 5.6), (cx, y_conv + dh + 0.6))
    arrow((cx, y_conv - dh - 0.6), (cx, y_saddle + 5.6))
    # no -> mix -> back to Hamiltonian (right-angle path)
    ax.plot([cx + dw + 0.6, cx_mix], [y_conv, y_conv], color=INK, lw=2.6, zorder=2)
    arrow((cx_mix, y_conv), (cx_mix, y_mix - 5.6))
    ax.plot([cx_mix, cx_mix], [y_mix + 5.6, y_ham], color=INK, lw=2.6, zorder=2)
    arrow((cx_mix, y_ham), (cx + 23.8, y_ham))
    ax.text(cx + dw + 3.0, y_conv + 2.2, "no", color=ORANGE,
            fontsize=15, fontweight="bold")
    ax.text(cx + 2.2, (y_conv - dh + y_saddle + 5.6) / 2, "yes", color=GREEN,
            fontsize=15, fontweight="bold")

    ax.text(50, 2.2,
            r"fixed point  $S^{\star} = T[S^{\star}]$   $\Leftrightarrow$   "
            r"stationary point of $F[\{S_i\}]$  —  the saddle we solve for",
            ha="center", va="center", fontsize=13, style="italic", color=INK)

    fig.savefig(path, facecolor="white")
    plt.close(fig)


# ===========================================================================
# 2. SCF convergence (residual + free energy)
#    Site edit: title is just "SCF convergence"; no tolerance annotation.
# ===========================================================================
def build_convergence(path: Path) -> None:
    res = DATA["residual_history"]
    ene = DATA["energy_history"]
    it = np.arange(1, len(res) + 1)

    fig, ax = plt.subplots(figsize=(7.05, 5.05), dpi=156)
    ax.semilogy(it, res, "-o", color=INK, markersize=5.2, linewidth=1.8, zorder=3)
    ax.set_xlabel("SCF iteration", fontsize=15)
    ax.set_ylabel(r"residual  $\|T[S]-S\|_2/\sqrt{N_c}$", fontsize=15, color=INK)
    ax.tick_params(labelsize=13)
    ax.set_title("SCF convergence", fontsize=17, color=INK, pad=12)

    ax2 = ax.twinx()
    ax2.plot(it, ene, "-", color=TEAL, linewidth=1.8, zorder=2)
    ax2.set_ylabel(r"free energy  $F$  (per site)", fontsize=15, color=TEAL)
    ax2.tick_params(labelsize=13, colors=TEAL)
    for s in ("top",):
        ax.spines[s].set_visible(False)
        ax2.spines[s].set_visible(False)
    ax2.spines["right"].set_color(TEAL)

    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


# ===========================================================================
# 3. initial seed -> converged texture
#    Site edit: no suptitle.
# ===========================================================================
def _texture_panel(ax, positions, texture, title):
    sz = texture[:, 2]
    norm = TwoSlopeNorm(vmin=-0.7, vcenter=0.0, vmax=0.7)
    for (x, y), z in zip(positions, sz):
        ax.add_patch(Circle((x, y), 0.30, facecolor=SZ_CMAP(norm(z)),
                            edgecolor=INK, linewidth=0.9, zorder=2))
    inplane = np.hypot(texture[:, 0], texture[:, 1])
    # longest arrow ~1.0 lattice constants, drawn thick, so the in-plane
    # winding stays readable at banner size
    scale = float(inplane.max()) if inplane.max() > 1e-9 else 1.0
    ax.quiver(positions[:, 0], positions[:, 1], texture[:, 0], texture[:, 1],
              angles="xy", scale_units="xy", scale=scale, pivot="middle",
              color=INK, width=0.0095, headwidth=3.8, headlength=4.6,
              headaxislength=4.1, zorder=3)
    ax.set_aspect("equal")
    ax.set_xlim(positions[:, 0].min() - 0.9, positions[:, 0].max() + 0.9)
    ax.set_ylim(positions[:, 1].min() - 1.1, positions[:, 1].max() + 1.6)
    ax.axis("off")
    ax.set_title(title, fontsize=27, color=INK, pad=10)
    return norm


def build_textures(path: Path) -> None:
    positions = DATA["positions"]
    fig = plt.figure(figsize=(16.0, 7.6), dpi=100)
    ax_l = fig.add_axes([0.015, 0.04, 0.40, 0.86])
    ax_r = fig.add_axes([0.50, 0.04, 0.40, 0.86])
    _texture_panel(ax_l, positions, DATA["seed"], "initial")
    norm = _texture_panel(ax_r, positions, DATA["converged"], "converged")

    # SCF arrow between the panels
    fig.text(0.4535, 0.57, "SCF", ha="center", fontsize=27,
             fontweight="bold", color=INK)
    arr = FancyArrowPatch((0.426, 0.48), (0.481, 0.48),
                          transform=fig.transFigure, arrowstyle="-|>",
                          mutation_scale=32, linewidth=2.8, color="#4a5b6e")
    fig.add_artist(arr)

    cax = fig.add_axes([0.925, 0.29, 0.013, 0.36])
    sm = plt.cm.ScalarMappable(cmap=SZ_CMAP, norm=norm)
    cbar = fig.colorbar(sm, cax=cax, ticks=[-0.7, 0.0, 0.7])
    cbar.ax.tick_params(labelsize=16)
    cbar.set_label(r"$S_z$", fontsize=21, rotation=0, labelpad=14, color=INK)

    fig.savefig(path, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    OUTDIR.mkdir(parents=True, exist_ok=True)
    build_flowchart(OUTDIR / "hf-scf-flowchart.png")
    build_convergence(OUTDIR / "hf-scf-convergence.png")
    build_textures(OUTDIR / "hf-scf-textures.png")
    for name in ("hf-scf-flowchart.png", "hf-scf-convergence.png",
                 "hf-scf-textures.png"):
        p = OUTDIR / name
        print(f"{name}: {p.stat().st_size // 1024} KB")
