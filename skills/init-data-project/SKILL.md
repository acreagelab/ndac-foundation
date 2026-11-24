---
name: init-data-project
description: Create and grow NDAC research projects from the bundled template — new project (CLAUDE.md, research objectives/plan/pipeline diagrams, data-source register, DMP, acknowledgement, src, configs, data/raw|interim|processed|outputs, tests, push guard), new sub-project, new version of a sub-project's method, or today's dated graph/report folders. Use when the user asks to start, set up, init or bootstrap a project; add a sub-project, study or experiment; make a new version/variant of an analysis; or asks for a new dated report or graph folder.
---

# Init Data Project

The bundled script is `scaffold.py` and the templates are `template/` (projects) and
`subproject_template/` (sub-projects), all in the same folder as this file. To change
what every new project gets, edit them in the ndac-foundation repo and push; teammates
get the change when they update the plugin. Existing projects are not touched.

## Concepts (explain briefly if the user seems unsure)
- **Project**: one dataset family, one security zone, one team. `<projects-root>/<name>/`
- **Sub-project**: one research question inside a project, sharing its data and code.
  `subprojects/<name>/`. If it needs data from another security zone, different
  collaborators or a different data-sharing agreement, make a separate project instead.
- **Version**: one variant of a sub-project's method = one config file
  `subprojects/<name>/configs/<version>.yaml` holding only what differs from `base.yaml`.
  Never copy scripts to make versions. Code changes for a version go on a git branch.
- **Run**: one execution of a version, in `data/outputs/<sub>/<version>/<time>_<sha>/`,
  never overwritten.

## New project
1. Get the project name: letters, digits, `_` or `-`, no spaces (e.g. `irrigation_SK`).
   If not given, ask.
2. Resolve `<projects-root>`: `--base DIR`, else the `PROJECTS_ROOT` environment
   variable, else `~/Projects`. Show it and confirm with the user if they haven't said
   where. On Fir it must be `/project/<allocation>/<user>/Projects`; if `PROJECTS_ROOT` is
   the user's top folder (no `/Projects`), stop and help fix `~/.bashrc` first (the script
   refuses that path too). Run `python "<skill-dir>/scaffold.py" new <name>` (add `--base <dir>` if needed).
   - On Fir it then runs `fir_share.sh` on the new project: B_Internal, so the allocation
     group can read it (not change it); PI and data managers get read/write. Tell the user
     this before running. If C_Limited / D_Restric data is expected from the start, add
     `--no-share`, raise the zone in CLAUDE.md, then run `fir_share.sh` on the project.
   - The script refuses if the folder exists. Never delete or overwrite a project to get
     around this.
   - `<AUTHOR>`/`<EMAIL>` come from `git config user.name`/`user.email`. If it reports
     TODO values, tell the user to set them and fix README.md and docs/.
3. Show the "Created:" list.
4. Offer to run `powershell -ExecutionPolicy Bypass -File "<project_dir>\init_project.ps1"`
   (git init, NDAC push guard, notebook output stripping, ignore checks). Only if the user
   agrees. On Linux / Fir use `bash "<project_dir>/init_project.sh"` instead.
   - Python on Fir is automatic: the script pins the newest lab image from
     `/project/def-kanj241/zenvs` in `scripts/fir_python` and makes it VS Code's interpreter.
     Run everything as `scripts/fir_python ...`; never create a conda env or a full venv.
     Run `bash scripts/setup_fir_env.sh` once (before `init_project.sh`) to add what the image
     lacks (pytest, nbstripout) as a small add-on venv.
   Heavy runs on Fir go through `scripts/job_template.sbatch`; see the project's CLAUDE.md,
   "Running on Fir". If the user is on Fir, remind them to confirm with the data steward that
   the project's security zone is allowed there before copying data.
5. Remind the user of the first steps, in this order, and offer to help with each:
   - CLAUDE.md TODOs: purpose, people (data steward), environment, input security zone
     (A_Public / B_Internal / C_Limited / D_Restric), identifiers present. The zone starts
     as B_Internal (NDAC default for a new project); ask whether C_Limited / D_Restric data
     is expected and, if so, raise it now, before that data arrives.
   - On Fir: access was set by the script (B_Internal: PI read/write, group read-only). If
     it printed "Access not set", offer `sh ~/.claude/skills/fir-resources/fir_share.sh
     "<project_dir>"`; until it runs, the project is private to its owner and PI.
   - `docs/research/objectives.md`: aim, research questions, hypotheses, and the key metric
     for each, fixed before analysis. Then `plan.md` and the diagrams.
   - Then `SETUP.md`.
6. Mention that outputs must acknowledge NDAC (`docs/ACKNOWLEDGEMENT.md`).

## New sub-project
- Run `python "<skill-dir>/scaffold.py" subproject "<project_dir>" <name>` (default
  project_dir: the current working directory when inside a project).
- Then help fill `subprojects/<name>/README.md` (research question from objectives.md,
  key metric) and `configs/base.yaml`, and add the sub-project to `subprojects/README.md`
  and to the pipeline diagram.

## New version
- Run `python "<skill-dir>/scaffold.py" version "<project_dir>" <subproject> <version>
  [--from <parent_version>] [--description "what changes"] [--hypothesis H1]`.
  Version names: short and descriptive, e.g. `v2_add_sentinel2`.
- Then edit the new YAML so it lists only what differs. If the change needs code, suggest
  a git branch. The script adds a row to `docs/experiments.md`; after runs, help fill the
  result from `python scripts/compare_runs.py <subproject>` and record keep/drop.

## Dated folders
- `python "<skill-dir>/scaffold.py" date "<project_dir>" [--subproject <name>] [--date YYYY-MM-DD]`.

## Diagrams
- Sources: `docs/research/diagrams/*.mmd` (Mermaid). After editing, render PNGs with
  `python scripts/render_diagrams.py` (needs Node.js; renders locally). Never send
  diagrams to online renderers; they can reveal data sources and security zones.
- When a pipeline step gets a script, put its path in the node label; `pytest` checks
  that every script named in the diagrams exists.

## Conventions afterwards
- Figures to `graph/<run-date>/[<subproject>/]`, reports to `report/<run-date>/[<subproject>/]`;
  never overwrite an earlier date's folder. Both are gitignored.
- Everything in the project's CLAUDE.md applies: `data/raw` read-only, stage files by name,
  register inputs in `docs/data_sources.md`, acknowledge NDAC, and run `/export-check`
  before anything leaves the secure environment.
