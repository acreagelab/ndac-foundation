# <PROJECT_NAME>

TODO: one paragraph: what this project produces, for whom, and its status.

Research aim and questions: [docs/research/objectives.md](docs/research/objectives.md) ·
plan: [docs/research/plan.md](docs/research/plan.md) ·
pipeline: [docs/research/diagrams/pipeline.mmd](docs/research/diagrams/pipeline.mmd)

## Structure

| Path | Purpose |
|---|---|
| `configs/default.yaml` | Project-wide parameters (CRS, seed, paths) |
| `subprojects/<name>/` | One research question each: configs per version, scripts, notebooks |
| `src/common.py` | Shared helpers: layered config, run folders, manifests, seeding |
| `scripts/` | Project-level tools: compare runs, render diagrams, study-area map, EE check |
| `data/raw` → `interim` → `processed` → `outputs` | Data flow; raw is READ-ONLY; nothing under data/ is committed |
| `graph/<date>/`, `report/<date>/` | Dated figures and reports (not committed) |
| `notebooks/` | Exploration only (outputs stripped on commit) |
| `docs/research/` | Objectives, plan, diagrams |
| `docs/` | Data sources, experiments log, DMP, references, contributions, meetings, acknowledgement |
| `tests/` | pytest suite (`pytest`) |
| `PROGRESS_REPORT.md` | Lab notebook: decisions and results |

## Quickstart

```powershell
conda env create -f environment.yml    # once; then:
conda activate TODO_ENV_NAME
Copy-Item .env.example .env            # then fill in DATA_ROOT (and EE_PROJECT if used)
pytest
```

## Data sources and governance

Inputs and their security zones: [docs/data_sources.md](docs/data_sources.md). Every
shared dataset carries a `.meta.yaml` sidecar. Nothing leaves the secure environment
without `/export-check`.

## Acknowledgements

This work used data and facilities provided by the Nutrien Digital Agriculture Centre
(NDAC), University of Saskatchewan. See [docs/ACKNOWLEDGEMENT.md](docs/ACKNOWLEDGEMENT.md).

## Contact
<AUTHOR> — <EMAIL> — Nutrien Digital Agriculture Centre, University of Saskatchewan
