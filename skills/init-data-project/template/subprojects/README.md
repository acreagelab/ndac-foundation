# Sub-projects

Each folder here is one research question that shares this project's data, code (`src/`)
and security zone. Create one by asking Claude ("add a sub-project called et_mapping"),
which runs `scaffold.py subproject`.

| Sub-project | Research question | Owner | Status |
|---|---|---|---|
| | | | |

Inside each sub-project:
- `configs/base.yaml` plus one YAML per **version** (a version is a config, not a copied script)
- `scripts/`: entry points taking `--version`
- `notebooks/`: exploration only, outputs stripped on commit

Run outputs go to `data/outputs/<subproject>/<version>/<timestamp>_<git-sha>/`, compared
with `python scripts/compare_runs.py <subproject>`, and logged in
[docs/experiments.md](../docs/experiments.md).

Make it a **separate project** instead if it needs data from a different security zone,
different collaborators, or a different data-sharing agreement.
