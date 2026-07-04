# wenqinchen98.github.io

Personal portfolio — **Wenqin Chen**. Static site (plain HTML/CSS/JS, **no build step**), served by GitHub Pages at <https://wenqinchen98.github.io>.

## Structure
- `index.html` — home (hero · projects · about · publications)
- `projects/*.html` — one page per project (NQS, Hartree–Fock, Cooper pairs, Dirac phonon)
- `assets/css/style.css` — all styles (vermilion accent, serif/sans, dark mode)
- `assets/js/main.js` — theme toggle
- `assets/figures/` — project figures
- `assets/Wenqin_Chen_Resume.pdf` — résumé

## Deploy (GitHub Pages, free)
1. Create a public repo named exactly `wenqinchen98.github.io`.
2. `git push` this folder to its `main` branch.
3. Repo → Settings → Pages → Source: **Deploy from a branch** → `main` / `/ (root)`.
4. Live at `https://wenqinchen98.github.io` within a minute. `.nojekyll` disables Jekyll so every file is served as-is.

## Preview locally
No dependencies needed:
```
cd wenqinchen98.github.io
python3 -m http.server 8000
# open http://localhost:8000
```

## Editing
Hand-written HTML/CSS — no framework. To add a project: copy a file in `projects/`, drop a figure in `assets/figures/`, add a card to `index.html`.

## To-do before it goes fully live
- Flip each project's **"Code — coming soon"** button to the real GitHub URL once the repos are public.
- (Optional) custom domain: add a `CNAME` file containing the domain + configure DNS.
