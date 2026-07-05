# Angela-Ye

## Cursor Cloud specific instructions

### Repository state (important, non-obvious)

The default branch (`main`) is currently a **placeholder** — it contains only `README.md`
and `LICENSE`. There is **no application code, no dependency manifest, no tests, and no
build/lint/run targets** on `main`. As a result there is nothing to build, lint, test, or
run from `main` yet.

The intended application — an e‑commerce TikTok video translation / makeup‑transform tool
(Python) — currently lives only in **unmerged feature branches**:

- `cursor/translate-and-transform-e-commerce-tiktok-videos-2ad3` (Flask `app.py`, Docker, `requirements.txt`)
- `cursor/translate-and-transform-e-commerce-tiktok-videos-56e9` (`app/` package + `cli.py`)
- `cursor/translate-and-transform-e-commerce-tiktok-videos-e849` (`src/process_video.py`)
- `cursor/translate-and-transform-e-commerce-tiktok-videos-eaf1` (Flask `app.py` + `templates/`)

Each of those branches carries its own `requirements.txt` and README with setup/run
instructions. Consult the specific branch's README before running its code.

### Tooling available in the environment

- Python `3.12` (`python3`, `pip3`)
- Node.js `22`

### Update script behavior

The startup update script installs Python dependencies **only if** a `requirements.txt`
exists at the repo root (it is a no‑op on `main`, which has none). When the app code is
merged into `main` (with a root `requirements.txt`), the update script will begin
installing those dependencies automatically. If a merged branch uses a different manifest
location or package manager, update the startup script accordingly.
