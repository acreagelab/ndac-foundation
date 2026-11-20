# CLAUDE.md: <PROJECT_NAME>

## Purpose
TODO: one or two lines: what this project produces and for whom.

## People
- Lead / owner: <AUTHOR>
- Data steward (approves zone crossings and exports): TODO name, NDAC data manager by default
- Supervisor / PI: TODO

## Research context (read at the start of each session)
- Aim, questions, hypotheses and fixed key metrics: [docs/research/objectives.md](docs/research/objectives.md)
- Milestones and risks: [docs/research/plan.md](docs/research/plan.md)
- Pipeline: [docs/research/diagrams/pipeline.mmd](docs/research/diagrams/pipeline.mmd). Update it when a
  step is added or renamed, then `python scripts/render_diagrams.py`
- Results and keep/drop decisions per version: [docs/experiments.md](docs/experiments.md)
- Don't change a key metric after seeing results; if it must change, log why in PROGRESS_REPORT.md

## Environment
- Conda env `TODO` from [environment.yml](environment.yml) (Python 3.12, geospatial stack from conda-forge)
- Pure-Python pins in [requirements.txt](requirements.txt) (`==`; every import declared)
- Tests: `pytest` (config in pyproject.toml)

## How to run
TODO: only commands verified to work, in order. Keep [docs/HOW_TO_RUN.md](docs/HOW_TO_RUN.md) current.

## Layout
- `subprojects/<name>/`: one research question each; `configs/base.yaml` + one YAML per
  **version** (a version is a config, not a copied script); scripts take `--version`
- `src/common.py`: `load_config(subproject=, version=)`, `new_run_dir`, `write_metrics`,
  `write_run_manifest`, `seed_everything`, `resolve_path`
- Runs: `data/outputs/<subproject>/<version>/<timestamp>_<git-sha>/`, never overwritten;
  compare with `python scripts/compare_runs.py <subproject>`
- Figures: `graph/<date>/[<subproject>/]`; reports: `report/<date>/[<subproject>/]`; never
  overwrite an earlier date's folder. Both are gitignored.
- `notebooks/` and `subprojects/*/notebooks/`: exploration only; outputs stripped on commit

## Data
- Flow: `data/raw` (READ-ONLY, never modified) → `data/interim` → `data/processed` → `data/outputs`
- Shared-drive root comes from `DATA_ROOT` in `.env`; in configs write `${DATA_ROOT}/...`.
  No hardcoded drive letters or `C:\Users\...` paths in code or configs
- Every input is registered in [docs/data_sources.md](docs/data_sources.md) when it arrives
- Security zone of inputs: TODO (`A_Public` / `B_Internal` / `C_Limited` / `D_Restric`;
  order D > C > B > A). Writing output to a LOWER zone than its input is declassification:
  it needs a justification in the dataset's `.meta.yaml` and the data steward's sign-off first.
- Every shared dataset gets a `.meta.yaml` sidecar (metadata-tagger agent;
  template [docs/metadata-template.meta.yaml](docs/metadata-template.meta.yaml))

## Geospatial
- Analysis CRS: `configs/default.yaml → project.crs_analysis`. Measurement (buffers, areas,
  distances, zonal stats) only in a projected metric CRS: prairie-wide EPSG:3347; local UTM
  (AB 32611/32612, SK 32613, MB 32614). Never EPSG:3857 (~1.66× area distortion at 53°N).
- Reproject BEFORE buffering; buffer distance is in CRS units
- Shapely 2.x: `union_all()`, not `unary_union`. Shapefile DBF names truncate at 10 chars:
  verify join keys after any shapefile write. Write CRS and nodata on every raster output.

## Running on Fir (Alliance HPC; delete this section if unused)
- Environment: no conda on Alliance. `bash scripts/setup_fir_env.sh` once on a login node
  (modules + virtualenv in `~/envs/<project>`); it records versions in `requirements-fir.lock.txt`
- Setup: `bash init_project.sh` (bash version of init_project.ps1)
- Claude and light work (editing, small tests, downloads) on the LOGIN node; anything heavy
  goes through Slurm: `sbatch --export=ALL,SUB=<subproject>,VER=<version> scripts/job_template.sbatch`
- Compute nodes have no internet: download data (incl. Earth Engine) on a login node first
- `DATA_ROOT` on Fir points to `/project/<group>/...` (backed up) or `/scratch/$USER/...`
  (fast, NOT backed up, purged when old). Never keep the only copy of anything in /scratch
- Before putting data on Fir, confirm with the data steward that its security zone is
  allowed there (`C_Limited` / `D_Restric` usually needs explicit approval)
- Commit before submitting jobs: run folders record the git commit; `-dirty` runs can't be reproduced

## Earth Engine (delete this section if unused)
- Project ID comes from `EE_PROJECT` in `.env`; never hardcoded, never a personal Gmail
- Default auth: ambient `earthengine authenticate` under the institutional identity
- Optional per-project identity isolation: `import scripts.ee_config` BEFORE `import ee`
  redirects credentials into `./.ee_auth/`. That directory then holds a LIVE OAuth token:
  it is gitignored and read-blocked; never read, print, or copy anything under it.
- Sanity check: `python scripts/verify_ee.py`

## Sensitive data
- Identifiers present: TODO (PPID / LLD / field boundaries / operator names / none)
- PPID and legal land descriptions (quarter/section/township/range/meridian) are DIRECT
  identifiers, in tables and in shapefile DBF attributes. So are field boundaries joined to
  parcel layers and coordinates finer than the provider publishes.
- Field- or operator-level measurements (yield, soil EC, per-field sensors) are C_Limited
  minimum; aggregate to RM/ecodistrict and suppress cells backed by < 5 farms before release
- Indigenous-community or interview data: de-identify at ingest, before `data/raw/`, and
  flag for governance review (OCAP®/CARE) regardless
- Credentials (`.env` values, `.ee_auth/`, `**/credentials`, `*service-account*.json`, `*.pem`):
  never read, print or copy; report paths only. Read access is denied in `.claude/settings.json`.
- Run `/export-check` before ANY artifact leaves the secure environment (email, GitHub,
  presentation, chat paste). Publishing a repo additionally requires the push-guard
  override (`git config ndac.pushApproved true`), only after `/export-check`.

## Acknowledgement
Every paper, thesis, talk, poster, report, shared dataset and published repo acknowledges
NDAC data and facilities: wording in [docs/ACKNOWLEDGEMENT.md](docs/ACKNOWLEDGEMENT.md).
Record contributors in [docs/contributions.md](docs/contributions.md).

## Reproducibility
- Seed `random` + `numpy` + `torch` together (`seed_everything`), seed value from config
- Every reported number comes from a run with `metrics.json` + `run_manifest.json`; runs
  marked `-dirty` used uncommitted code: re-run from a commit before reporting
- Code changes for a version: git branch, tag `<subproject>-<version>` when reported
- `test_*.py` is reserved for real pytest tests; name experiments `experiment_*.py`
- Log what/why/next in [PROGRESS_REPORT.md](PROGRESS_REPORT.md); commit at the end of each session

## Rules
- Cite only paths and commands that resolve on disk; update this file when structure changes
- Stage files by name; never `git add .`
