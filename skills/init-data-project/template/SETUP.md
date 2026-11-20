# New project from this template — checklist

Copy the folder, rename it, then work through this list. Delete this file when done.

1. **Rename** the folder to the project name (no spaces; e.g. `wetness_index_mb`).
2. **Fill placeholders** — search the tree for `<PROJECT_NAME>` and `TODO` and replace
   in [CLAUDE.md](CLAUDE.md), [README.md](README.md), [configs/default.yaml](configs/default.yaml),
   [PROGRESS_REPORT.md](PROGRESS_REPORT.md).
3. **Environment**: create/choose the conda env, then declare it in CLAUDE.md and pin
   dependencies in [requirements.txt](requirements.txt) (`==`, every import declared).
4. **Secrets**: copy `.env.example` → `.env`; set `DATA_ROOT`, and `EE_PROJECT` if the
   project uses Earth Engine (institutional identity — never a personal Gmail).
5. **CRS**: set `crs_analysis` in `configs/default.yaml` — UTM zone for local work
   (SK = EPSG:32613), EPSG:3347 for prairie-wide area statistics. Never EPSG:3857
   for measurement.
6. **Initialize git**: run `powershell -ExecutionPolicy Bypass -File init_project.ps1`.
   It creates the repo, installs the NDAC push guard, and verifies credential and data
   paths are ignored. Then stage explicitly (never `git add .`) and make the first commit.
7. **Smoke test**: `pytest tests/ -v` — validates layout, config, and .gitignore coverage.
8. **Sensitive data**: fill the "Sensitive data" section of CLAUDE.md honestly (identifiers
   present? zone? named producers?). If datasets land in `data/`, generate sidecars with
   the metadata-tagger agent (template: [docs/metadata-template.meta.yaml](docs/metadata-template.meta.yaml)).

This template references the agents pii-scanner, repo-auditor, reviewer, researcher and
metadata-tagger, the skills `/adopt-project` and `/export-check`, and the geospatial and
data-governance rules. These are NOT yet part of the ndac-foundation plugin. If you don't
have them installed, ask Thuan before relying on them.
Later, `/fewer-permission-prompts` can build this project's `.claude/settings.json`.

Standing habits: end each work session with a short commit; log decisions in
PROGRESS_REPORT.md; run `/export-check` before anything leaves the secure environment.
