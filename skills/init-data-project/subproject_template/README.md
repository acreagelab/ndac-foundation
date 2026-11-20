# Sub-project: <SUBPROJECT>

| | |
|---|---|
| **Research question** | TODO: RQ id + question, from [objectives](../../docs/research/objectives.md) |
| **Owner** | <AUTHOR> |
| **Started** | <DATE> |
| **Status** | planning / running / done / dropped |
| **Current version** | v1_baseline |
| **Key metric** | TODO: fixed BEFORE running (same as in objectives.md) |

## Question and approach
TODO: one paragraph.

## Inputs
List each input and add it to [data_sources.md](../../docs/data_sources.md).
Security zone: inherits the project zone (see CLAUDE.md). If this sub-project needs data
from a different zone or different collaborators, make it a separate project instead.

## Versions
A version is a config file in [configs/](configs/), not a copied script.
- `configs/base.yaml`: settings shared by every version of this sub-project
- `configs/<version>.yaml`: only what differs from base.yaml

Create a new one with Claude ("make a v2 of <SUBPROJECT> that adds Sentinel-2") or:
`python <plugin>/skills/init-data-project/scaffold.py version . <SUBPROJECT> v2_name --from v1_baseline`
If a version needs code changes, work on a git branch and tag it when a result is reported
(`git tag <SUBPROJECT>-v2_name`).

## Run

```powershell
python subprojects/<SUBPROJECT>/scripts/01_run.py --version v1_baseline
python scripts/compare_runs.py <SUBPROJECT> --sort <metric>
```

Each run writes to `data/outputs/<SUBPROJECT>/<version>/<timestamp>_<git-sha>/`
(metrics.json, run_manifest.json, config_resolved.yaml). Runs are never overwritten.
Record results and keep/drop decisions in [experiments.md](../../docs/experiments.md).

## Notebooks
[notebooks/](notebooks/) is for exploration only. Outputs are stripped on commit
(nbstripout). Every number that gets reported comes from a script run with a manifest.
