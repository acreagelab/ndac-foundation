# CLAUDE.md — <PROJECT_NAME>

## Purpose
TODO — one or two lines: what this project produces and for whom.

## Environment
- Interpreter: conda env `TODO` (Python 3.11+)
- Install: `pip install -r requirements.txt` (pinned `==`; every import declared)

## How to run
TODO — only commands verified to work, in order. Keep [docs/HOW_TO_RUN.md](docs/HOW_TO_RUN.md) current.

## Data
- Layout: `data/raw` (READ-ONLY, never modified) → `data/interim` → `data/processed` → `data/outputs`
- Shared-drive root comes from `DATA_ROOT` in `.env` — no hardcoded `Z:\` paths in code or configs
- Security zone of inputs: TODO (`A_Public` / `B_Internal` / `C_Limited` / `D_Restric`).
  Writing output to a LOWER zone than its input requires documented justification and Thuan's sign-off.
- Analysis CRS: `configs/default.yaml → project.crs_analysis`. Metric CRS for all measurement;
  never EPSG:3857 for buffers, areas, or zonal stats.
- Every shared dataset gets a `.meta.yaml` sidecar (metadata-tagger agent;
  template in [docs/metadata-template.meta.yaml](docs/metadata-template.meta.yaml)).

## Earth Engine (delete this section if unused)
- Project ID comes from `EE_PROJECT` in `.env` — never hardcoded, never a personal Gmail
- Default auth: ambient `earthengine authenticate` under the institutional identity
- Optional per-project identity isolation: `import scripts.ee_config` BEFORE `import ee`
  redirects credentials into `./.ee_auth/`. That directory then holds a LIVE OAuth token:
  it is gitignored and read-blocked — never read, print, or copy anything under it.
- Sanity check: `python scripts/verify_ee.py`

## Sensitive data
- Identifiers present: TODO (PPID / LLD / field boundaries / operator names / none)
- Field- or operator-level measurements (yield, soil EC, per-field sensors) are C_Limited
  minimum; aggregate to RM/ecodistrict and suppress cells backed by < 5 farms before release
- Run `/export-check` before ANY artifact leaves the secure environment
  (email, GitHub, presentation, chat paste). Publishing a repo additionally requires the
  push-guard override (`git config ndac.pushApproved true`) — only after `/export-check`.

## Reproducibility
- `from src.common import seed_everything, load_config, write_run_manifest`
- Seed `random` + `numpy` + `torch` together (`seed_everything`), seed value from config
- Write a run manifest next to every metrics/model output (`write_run_manifest`)
- `test_*.py` is reserved for real pytest tests; name experiments `experiment_*.py`
- Log what/why/next in [PROGRESS_REPORT.md](PROGRESS_REPORT.md); commit at the end of each session

## Rules
- Cite only paths and commands that resolve on disk; update this file when structure changes
