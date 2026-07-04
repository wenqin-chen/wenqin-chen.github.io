"""Build the Neural-Quantum-States portfolio figures — SELF-CONTAINED.

Reads only the bundled `figure_data.npz` in this folder (no dependency on the research repo) and writes:
  here:            nqs_texture_convergence_2panel.png , nqs_texture_banner.png   (full-resolution sources)
  ../assets/figures:  nqs-2panel.png (web, 2000px)  ,  nqs-texture.jpg (card, 1000px)

Two panels, replotted from the raw run data (never cropped from an old PNG):
  LEFT  — the real-space spin texture the trained NQS holds (cell-D skyrmion crystal): colour = out-of-plane
          spin m_z, arrows = in-plane spin; colourbar + x/y axes in Bohr + 'skyrmion core' / 'magnetic cell'.
  RIGHT — the N=18 training convergence: four candidate orders (skyrmion crystal, paramagnet, in-plane spiral,
          ferromagnet), running-average variational energy vs MinSR step.

Provenance of figure_data.npz (extracted once from the continuum_skyrmion_nqs research run; see README.md):
  q1,q2  — reciprocal lattice vectors of the magnetic cell (ohaus_texture.npz)
  g16    — 16x16x3 measured NQS spin grid, m_grid_final / bin-area (diagnose_N18_hires_skx.json)
  skx/fluid/spiral/fm — twist-averaged convergence curves, each anchored to its reliable E_final.

Run:  python3 build_nqs_figure.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.abspath(os.path.join(HERE, "..", "assets", "figures"))

D = np.load(os.path.join(HERE, "figure_data.npz"))
q1, q2, g16 = D["q1"], D["q2"], D["g16"]
skx, fluid, spiral, fm = D["skx"], D["fluid"], D["spiral"], D["fm"]
A_mag = 2 * np.pi * np.linalg.inv(np.array([q1, q2])); a1, a2 = A_mag[:, 0], A_mag[:, 1]
A_sc = A_mag @ np.array([[2, -2], [2, 4]])          # N=18 simulation supercell (12 magnetic cells)


def texture_on(xs, ys):
    """Trig-interpolate the periodic 16x16 NQS spin field onto a real-space window."""
    X, Y = np.meshgrid(xs, ys, indexing="xy"); R = np.stack([X, Y], axis=-1)
    UV = R @ np.linalg.inv(A_sc).T
    k = np.fft.fftfreq(16) * 16
    ph_u = np.exp(2j * np.pi * (UV[..., 0, None] - 0.5 / 16) * k)
    ph_v = np.exp(2j * np.pi * (UV[..., 1, None] - 0.5 / 16) * k)
    m = np.zeros(X.shape + (3,))
    for c in range(3):
        F = np.fft.fft2(g16[..., c])
        m[..., c] = np.real(np.einsum("...u,uv,...v->...", ph_u, F, ph_v)) / 16 ** 2
    return X, Y, m


def runavg(y, w=15): return np.convolve(y, np.ones(w) / w, mode="valid")

C_SKX, C_FL, C_SP, C_FM = "#6a4c93", "#2e86ab", "#e08a3c", "#3a7d34"
vmax = float(np.abs(g16[..., 2]).max())
plt.rcParams.update({"font.size": 11, "axes.linewidth": 0.9})

# ==================== two-panel portfolio figure ====================
fig = plt.figure(figsize=(14.2, 6.1), constrained_layout=True)
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.13])
axA = fig.add_subplot(gs[0, 0]); axB = fig.add_subplot(gs[0, 1])

# ---- Panel A: spin texture ----
xs = np.linspace(-0.5, 15.5, 340); ys = np.linspace(-0.5, 15.5, 340)
X, Y, m = texture_on(xs, ys); mx, my, mz = m[..., 0], m[..., 1], m[..., 2]
pc = axA.pcolormesh(X, Y, mz, cmap="RdBu_r", vmin=-vmax, vmax=vmax, shading="gouraud", zorder=1)
qs = 13; vxy = float(np.hypot(mx, my).max())
axA.quiver(X[::qs, ::qs], Y[::qs, ::qs], mx[::qs, ::qs], my[::qs, ::qs], color="k",
           scale=vxy / 0.05, width=0.0034, alpha=0.82, pivot="mid", zorder=3)
o = np.array([2.2, 0.6]); cell = np.array([o, o + a1, o + a1 + a2, o + a2, o])
axA.plot(cell[:, 0], cell[:, 1], color="#00a651", lw=2.4, ls="--", alpha=0.95, zorder=4)
axA.set_aspect("equal"); axA.set_xlim(xs.min(), xs.max()); axA.set_ylim(ys.min(), ys.max())
axA.set_xlabel("$x$  (Bohr radii)"); axA.set_ylabel("$y$  (Bohr radii)")
axA.set_title("Spin texture from the trained network", fontweight="bold", fontsize=12.5, pad=9)
cb = fig.colorbar(pc, ax=axA, fraction=0.046, pad=0.03)
cb.set_ticks([-vmax, 0, vmax]); cb.set_ticklabels([f"$-${vmax:.3f}", "0", f"{vmax:.3f}"])
cb.set_label("out-of-plane spin  $m_z$", fontsize=10, labelpad=6)
cb.ax.yaxis.set_label_position("left")   # keep the label on the texture side of the bar, clear of Panel B
axA.text(o[0] + 0.5 * (a1[0] + a2[0]), o[1] + 0.5 * (a1[1] + a2[1]), "magnetic\ncell",
         ha="center", va="center", fontsize=9.5, fontweight="bold", zorder=6,
         bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="k", alpha=0.82))
sel = (X > 1.0) * (X < 7.0) * (Y > 8.5) * (Y < 13.5)
i, j = np.unravel_index(np.argmax(np.where(sel, mz, -1e9)), X.shape)
axA.annotate("skyrmion core", xy=(X[i, j], Y[i, j]), xytext=(0.0, 14.4), textcoords="data",
             fontsize=9.5, fontweight="bold", ha="left", va="center", zorder=6,
             arrowprops=dict(arrowstyle="->", color="white", lw=2.2),
             bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="0.4", alpha=0.92))

# ---- Panel B: training convergence ----
for y, col, lab, lw, z in [(skx, C_SKX, "skyrmion crystal", 2.5, 6), (fluid, C_FL, "paramagnet", 2.5, 6),
                           (spiral, C_SP, "in-plane spiral", 2.3, 5), (fm, C_FM, "ferromagnet", 2.1, 4)]:
    axB.plot(np.arange(len(y)), y, color=col, lw=0.6, alpha=0.16, zorder=z - 1)
    ra = runavg(y); axB.plot(np.arange(len(ra)) + 7, ra, color=col, lw=lw, label=lab, zorder=z)
axB.set_xlim(0, 600); axB.set_ylim(-13.95, -13.0); axB.grid(alpha=0.2)
axB.axhspan(-13.881, -13.861, color="#c1121f", alpha=0.18, zorder=0)   # skyrmion crystal <-> paramagnet tie
axB.set_xlabel("optimization step  (MinSR)")
axB.set_ylabel(r"variational energy  $\langle H\rangle$  (Ha)")
axB.yaxis.set_label_position("right"); axB.yaxis.tick_right()   # mirror layout keeps the middle gap clean
axB.legend(loc="upper right", fontsize=10, framealpha=0.96)
axB.set_title("Training convergence, 18 electrons", fontweight="bold", fontsize=12.5, pad=9)

out2 = os.path.join(HERE, "nqs_texture_convergence_2panel.png")
fig.savefig(out2, dpi=200, bbox_inches="tight"); plt.close(fig)

# ==================== standalone landscape texture banner (card) ====================
bx = np.linspace(0.0, 26.0, 560); by = np.linspace(0.0, 14.6, 315)
Xb, Yb, mb = texture_on(bx, by); mbx, mby, mbz = mb[..., 0], mb[..., 1], mb[..., 2]
figb = plt.figure(figsize=(8.0, 8.0 * 14.6 / 26.0)); axb = figb.add_axes([0, 0, 1, 1]); axb.axis("off")
axb.pcolormesh(Xb, Yb, mbz, cmap="RdBu_r", vmin=-vmax, vmax=vmax, shading="gouraud")
qb = 12
axb.quiver(Xb[::qb, ::qb], Yb[::qb, ::qb], mbx[::qb, ::qb], mby[::qb, ::qb], color="k",
           scale=float(np.hypot(mbx, mby).max()) / 0.05, width=0.0026, alpha=0.8, pivot="mid")
axb.set_xlim(bx.min(), bx.max()); axb.set_ylim(by.min(), by.max())
outb = os.path.join(HERE, "nqs_texture_banner.png")
figb.savefig(outb, dpi=180); plt.close(figb)

# ==================== web-optimized assets ====================
im2 = Image.open(out2).convert("RGB")
im2 = im2.resize((2000, round(im2.height * 2000 / im2.width)), Image.LANCZOS)
im2.save(os.path.join(ASSETS, "nqs-2panel.png"), optimize=True)
imb = Image.open(outb).convert("RGB")
imb = imb.resize((1000, round(imb.height * 1000 / imb.width)), Image.LANCZOS)
imb.save(os.path.join(ASSETS, "nqs-texture.jpg"), quality=90, optimize=True, progressive=True)

print("FIG_DONE")
print("  sources:", out2, "|", outb)
print("  web:    ", os.path.join(ASSETS, "nqs-2panel.png"), "|", os.path.join(ASSETS, "nqs-texture.jpg"))
print("  vmax(mz)=%.4f  core@(%.1f,%.1f)  plateaus skx/fluid/spiral/fm = %.3f/%.3f/%.3f/%.3f"
      % (vmax, X[i, j], Y[i, j], runavg(skx)[-10:].mean(), runavg(fluid)[-10:].mean(),
         runavg(spiral)[-10:].mean(), runavg(fm)[-10:].mean()))
