# ndac-foundation

Claude Code plugin for Nutrien Digital Agriculture Centre (NDAC) projects.

## What's inside

| Skill | What it does |
|---|---|
| `ndac-foundation:init-data-project` | Creates a new project from the NDAC template, or adds today's `graph/<date>` and `report/<date>` folders to an existing project |

The template is in [skills/init-data-project/template/](skills/init-data-project/template/).
It sets up the data flow (`data/raw` read-only, then `interim`, `processed`, `outputs`),
reproducibility helpers (`src/common.py`), Earth Engine config, `.gitignore` protection for
credentials and data, and the NDAC push guard (`.githooks/pre-push`), which blocks pushes to
non-USask remotes until someone deliberately approves them.

## Install (once per person)

The repo is private: ask Thuan for access on GitHub first, and make sure git can
authenticate to GitHub (for example via Git Credential Manager). Then, in Claude Code:

```
/plugin marketplace add https://github.com/thuanhavan/ndac-foundation
/plugin install ndac-foundation@ndac-foundation
```

Get updates with `/plugin marketplace update ndac-foundation`.

## Use

Ask Claude: *"start a new project called wetland_mb"*, or *"make today's report folder"*.

New projects go to `~/Projects/<name>` by default. To use another folder, set the
`PROJECTS_ROOT` environment variable or tell Claude where to put the project.
`README.md` and the metadata template are filled in with your
`git config user.name` / `user.email`.

You can also run the script without Claude:

```
python skills/init-data-project/scaffold.py new <name> [--base DIR]
python skills/init-data-project/scaffold.py date <project_dir>
```

## Changing the template

Edit files under `skills/init-data-project/template/`, then commit and push. The change
only affects projects created after it. Existing projects are not touched.

## Not yet included

The template refers to `/export-check`, `/adopt-project` and the metadata-tagger,
pii-scanner, repo-auditor, reviewer and researcher agents. These still live in individual
setups and are candidates to add here.

## Contact

Thuan Ha — Nutrien Digital Agriculture Centre, University of Saskatchewan
