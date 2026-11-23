# ndac-foundation

Ready-made project setup and Claude helpers for research at the Nutrien Digital
Agriculture Centre (NDAC), University of Saskatchewan. Install it once, then ask Claude
to start a project: you get the same folders, documents and data-safety checks as
everyone else on the team.

**You need:** VS Code with the **Claude Code** extension (signed in with your USask
account), **git** and **Python**. You don't need a GitHub account.

---

## Install on your Windows PC

Open VS Code → **Terminal → New Terminal**, then copy and paste these lines.
Nothing needs editing.

```powershell
mkdir C:\$env:USERNAME\Projects
git clone https://github.com/acreagelab/ndac-foundation C:\$env:USERNAME\Projects\ndac-foundation
powershell -ExecutionPolicy Bypass -File C:\$env:USERNAME\Projects\ndac-foundation\install.ps1
setx PROJECTS_ROOT C:\$env:USERNAME\Projects
```

**Check it worked:** close and reopen VS Code, click the **Claude** icon, type `/`.
You should see `init-data-project` and `export-check` in the list.

---

## Install on Fir (the Alliance cluster)

First connect VS Code to Fir (see [slide 3](docs/training/slide3_fir.png)). Then open
**Terminal → New Terminal** in the Fir window and paste:

```bash
cd ~
git clone https://github.com/acreagelab/ndac-foundation
bash ndac-foundation/install.sh

echo 'export PROJECTS_ROOT=/project/def-kanj241/'$USER'/Projects' >> ~/.bashrc
source ~/.bashrc
mkdir -p $PROJECTS_ROOT

sh ~/.claude/skills/fir-resources/fir_share.sh
sh ~/.claude/skills/fir-resources/fir_share.sh --check
```

**Check it worked:** the last line should say **All as intended.** Then reload VS Code
(Ctrl+Shift+P → *Developer: Reload Window*) and type `/` in the Claude panel.

Not in the `def-kanj241` group? Replace `def-kanj241` with your group's name.

### Who can see your projects on Fir

| Who | What they can do |
|---|---|
| You | Everything |
| Your PI and the data manager | Read and edit everything |
| Other team members | **Read only** (can't edit or delete), on normal projects |
| Anyone else | Nothing |

Projects that hold restricted data (field-level yield, soil, producer data, etc.) are
hidden from other team members. Tell Claude *"this project will have restricted data"*
before you copy such data in, and it will lock the project down.

---

## Start using it

Open the Claude panel and just ask:

| Ask Claude | What you get |
|---|---|
| *Start a new project called wetland_mb* | A project folder with everything set up |
| *Add a sub-project called et_mapping* | A folder for one research question |
| *Make a v2 of et_mapping that adds Sentinel-2* | A new version of the method to compare |
| *Make today's report folder* | Dated folders for figures and reports |
| */export-check this figure* | A check before anything leaves the team (no personal or farm data, NDAC acknowledged) |
| On Fir: *Run v2 of et_mapping on the cluster* | Claude picks time, memory and storage, shows you, then submits the job |

## Get updates

Windows:

```powershell
git -C C:\$env:USERNAME\Projects\ndac-foundation pull
powershell -ExecutionPolicy Bypass -File C:\$env:USERNAME\Projects\ndac-foundation\install.ps1
```

Fir:

```bash
git -C ~/ndac-foundation pull && bash ~/ndac-foundation/install.sh
```

## Help

Training slides: [docs/training/](docs/training/). Questions or errors: contact Thuan Ha
(NDAC data manager) and paste the error message.

---

## Reference

<details>
<summary>What's inside, how access works, and maintaining the plugin</summary>

### Skills and agents

| Skill | Purpose |
|---|---|
| `init-data-project` | New project, sub-project, version, dated folders (`scaffold.py`) |
| `export-check` | Pre-export disclosure control; PASS / BLOCKED per artifact |
| `adopt-project` | Bring an existing project under git and up to the baseline |
| `ndac-data-rules` | Prairie data-governance and CRS rules, applied in any project |
| `fir-resources` | On Fir: right node (login / interactive / batch) and storage (/project, /scratch, node-local disk, nearline); `fir_share.sh` sets access |

**Agents**: `pii-scanner` (identifiers, PPID/LLD, small cells, credentials),
`metadata-tagger` (`.meta.yaml` sidecars), `repo-auditor` (baseline scorecard),
`reviewer` (code, analysis, papers, slides), `researcher` (literature and policy research).
Ask e.g. *"use the reviewer agent on this chapter"*. `/adopt-project` brings an existing
project up to the baseline.

The installer copies skills to `~/.claude/skills/` and agents to `~/.claude/agents/`;
anything it replaces is backed up to `~/.claude/backups/` first.

### Access on Fir (`fir_share.sh`)

Access follows the `Security zone of inputs:` line in each project's `CLAUDE.md`:
`A_Public` / `B_Internal` (new-project default) → allocation group read-only;
`C_Limited` / `D_Restric` / `TODO` → owner, PI and data managers only. PI and allocation
come from the `/project/def-<pi>/` path; data managers are listed in
[skills/fir-resources/fir_share.conf](skills/fir-resources/fir_share.conf). Re-run after
creating a project, changing its zone, or copying data in with `cp -p` / `rsync -a` /
`tar`; `--check` reports anything out of place. Only a folder's owner can set its access.

### Project template

[skills/init-data-project/template/](skills/init-data-project/template/):

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

### Acknowledging NDAC

Every project gets `docs/ACKNOWLEDGEMENT.md` with the standard wording for papers,
theses, talks, posters, datasets and code, and `/export-check` blocks publications that
miss it. **The wording is currently a draft**: replace it with NDAC's official text in
[skills/init-data-project/template/docs/ACKNOWLEDGEMENT.md](skills/init-data-project/template/docs/ACKNOWLEDGEMENT.md).

### Running the scaffold without Claude

```
python skills/init-data-project/scaffold.py new <name> [--base DIR]
python skills/init-data-project/scaffold.py subproject <project_dir> <name>
python skills/init-data-project/scaffold.py version <project_dir> <subproject> <version> [--from V] [--description TEXT]
python skills/init-data-project/scaffold.py date <project_dir> [--subproject NAME]
```

New projects go to `~/Projects/<name>` unless `--base` or `PROJECTS_ROOT` says otherwise.
Author name and email come from `git config user.name` / `user.email`.

### Why not `/plugin install`?

USask's Claude Code policy only allows plugin marketplaces on `gitlab.usask.ca`. If NDAC
gets a group there: `/plugin marketplace add <gitlab url>` +
`/plugin install ndac-foundation@ndac-foundation` (the repo is already laid out as a
plugin; skills then appear as `ndac-foundation:<skill>`).

### Changing the plugin

Edit, test on a throwaway project (`scaffold.py new test --base <temp dir>`, then `pytest`
inside it), commit, bump `version` in `.claude-plugin/plugin.json`, push. Changes reach
teammates when they update, and affect only projects created afterwards.

</details>

## Contact

Thuan Ha — Nutrien Digital Agriculture Centre, University of Saskatchewan
