# <PROJECT_NAME>

TODO — one paragraph: what this project produces, for whom, and its status.

## Structure

| Path | Purpose |
|---|---|
| `configs/` | All tunable parameters (`default.yaml`) |
| `data/raw` → `interim` → `processed` → `outputs` | Data flow; raw is READ-ONLY |
| `src/` | Importable project code (`common.py`: config, seeding, run manifests) |
| `scripts/` | Entry points, numbered by stage |
| `tests/` | pytest suite (`pytest tests/ -v`) |
| `docs/` | Runbook (`HOW_TO_RUN.md`), metadata sidecar template |
| `logs/` | Runtime logs (never at project root) |
| `PROGRESS_REPORT.md` | Lab notebook — decisions and results |

## Quickstart

```powershell
conda activate TODO_ENV_NAME
pip install -r requirements.txt
Copy-Item .env.example .env   # then fill in DATA_ROOT (and EE_PROJECT if used)
pytest tests/ -v
```

## Data sources and governance

TODO — list inputs with their security zones (A_Public / B_Internal / C_Limited /
D_Restric). Every shared dataset carries a `.meta.yaml` sidecar. Nothing leaves
the secure environment without `/export-check`.

## Contact
<AUTHOR> — <EMAIL> — Nutrien Digital Agriculture Centre, University of Saskatchewan
