# ndac-foundation

Claude Code plugin for research projects at the Nutrien Digital Agriculture Centre (NDAC),
University of Saskatchewan. It gives every team member the same project layout, research
documents, data-governance checks and Claude helpers.

## Install (once per person)

You need: **git**, **VS Code** with the **Claude Code** extension (signed in with your
USask account), and **Python**. No GitHub account is needed to install.

**Windows** (in a VS Code terminal; replace `<NSID>` with yours):

```powershell
mkdir C:\<NSID>\Projects
git clone https://github.com/thuanhavan/ndac-foundation C:\<NSID>\Projects\ndac-foundation
powershell -ExecutionPolicy Bypass -File C:\<NSID>\Projects\ndac-foundation\install.ps1
setx PROJECTS_ROOT C:\<NSID>\Projects
```

Restart VS Code, open the Claude panel, type `/` and check that `init-data-project` and
`export-check` are listed.

**Linux / HPC:** `git clone ... ~/ndac-foundation && sh ~/ndac-foundation/install.sh`

**Update:** `git -C C:\<NSID>\Projects\ndac-foundation pull`, then run `install.ps1` again.

The installer copies the skills into `~/.claude/skills/` and the agents into
`~/.claude/agents/`. Anything it replaces is backed up first to `~/.claude/backups/`.

Why not `/plugin install`? USask's Claude Code policy only allows plugin marketplaces on
`gitlab.usask.ca`. If NDAC gets a group there, the plugin can move and install with
`/plugin marketplace add <gitlab url>` + `/plugin install ndac-foundation@ndac-foundation`;
the repo is already laid out as a plugin. Skills then appear as `ndac-foundation:<skill>`.

## What you can ask Claude

| Ask | What happens |
|---|---|
| "start a new project called wetland_mb" | Creates the project from the template (below) |
| "add a sub-project called et_mapping" | `subprojects/et_mapping/` with configs, run script, notebooks; section in the experiments log |
| "make a v2 of et_mapping that adds Sentinel-2" | New version config copied from the latest one + experiments-log row |
| "make today's report folder for et_mapping" | `graph/<date>/et_mapping/`, `report/<date>/et_mapping/` |
| "/export-check this figure / table / repo" | Disclosure check: identifiers, small cells, zone crossing, NDAC acknowledgement |
| "/adopt-project on C:\...\old_project" | Brings an existing project up to the baseline, credential-safe |
| "use the pii-scanner / reviewer / repo-auditor / metadata-tagger / researcher agent on ..." | Specialist checks (see below) |

## What's inside

**Skills**

| Skill | Purpose |
|---|---|
| `init-data-project` | New project, sub-project, version, dated folders (`scaffold.py`) |
| `export-check` | Pre-export disclosure control; PASS / BLOCKED per artifact |
| `adopt-project` | Bring an existing project under git and up to the baseline |
| `ndac-data-rules` | Prairie data-governance and CRS rules, applied in any project |

**Agents**: `pii-scanner` (identifiers, PPID/LLD, small cells, credentials),
`metadata-tagger` (`.meta.yaml` sidecars), `repo-auditor` (baseline scorecard),
`reviewer` (code, analysis, papers, slides), `researcher` (literature and policy research).

**Project template** ([skills/init-data-project/template/](skills/init-data-project/template/)):

```
<project>/
├── CLAUDE.md                 rules + research context Claude reads every session
├── docs/research/            objectives.md (RQs, hypotheses, key metrics fixed in advance),
│   └── diagrams/             plan.md, pipeline / Gantt / concept diagrams (Mermaid → PNG)
├── docs/                     data_sources.md, experiments.md, DMP.md, references.bib,
│                             contributions.md (CRediT), meetings/, ACKNOWLEDGEMENT.md
├── subprojects/<name>/       one research question each; configs/<version>.yaml per variant
├── src/common.py             layered config, run folders, run manifests, seeding
├── scripts/                  compare_runs, render_diagrams, plot_study_area, verify_ee
├── data/raw → interim → processed → outputs     (never committed)
├── graph/<date>/, report/<date>/                (never committed)
├── notebooks/                exploration only; outputs stripped on commit
├── tests/                    layout, .gitignore, src/common.py, doc links
├── environment.yml, requirements.txt, pyproject.toml
├── .githooks/pre-push        NDAC push guard (blocks non-USask remotes until approved)
└── .claude/settings.json     stops Claude from reading credential files
```

## Acknowledging NDAC

Every project gets `docs/ACKNOWLEDGEMENT.md` with the standard wording for papers,
theses, talks, posters, datasets and code, and `/export-check` blocks publications that
miss it. **The wording is currently a draft**: replace it with NDAC's official text in
[skills/init-data-project/template/docs/ACKNOWLEDGEMENT.md](skills/init-data-project/template/docs/ACKNOWLEDGEMENT.md).

## Running the script without Claude

```
python skills/init-data-project/scaffold.py new <name> [--base DIR]
python skills/init-data-project/scaffold.py subproject <project_dir> <name>
python skills/init-data-project/scaffold.py version <project_dir> <subproject> <version> [--from V] [--description TEXT]
python skills/init-data-project/scaffold.py date <project_dir> [--subproject NAME]
```

New projects go to `~/Projects/<name>` unless `--base` or the `PROJECTS_ROOT` environment
variable says otherwise. Author name and email come from `git config user.name` / `user.email`.

## Changing the plugin

Edit, test on a throwaway project (`scaffold.py new test --base <temp dir>`, then `pytest`
inside it), commit, bump `version` in `.claude-plugin/plugin.json`, push. Changes reach
teammates when they update the plugin, and affect only projects created afterwards.

## Contact

Thuan Ha — Nutrien Digital Agriculture Centre, University of Saskatchewan
