---
name: init-data-project
description: Create a new NDAC data project from the bundled template (CLAUDE.md, src, configs, data/raw|interim|processed|outputs, logs, scripts, tests, docs, NDAC push guard) plus dated graph/<date> and report/<date> folders; or add today's dated graph/report folders to an existing project. Use when the user asks to start, set up, init, or bootstrap a new project, or asks for a new dated report or graph folder.
---

# Init Data Project

A new project is a copy of `template/` (in the same folder as this file) plus the extra
folders below. To change what every new project gets, edit `template/` in the
ndac-foundation repo and push it. Teammates receive the change when they update the plugin.

## Layout produced

```
<projects-root>/<name>/
├── (everything in template/: CLAUDE.md, README.md, SETUP.md, PROGRESS_REPORT.md,
│    configs/, data/{raw,interim,processed,outputs}/, logs/, scripts/, src/, tests/,
│    docs/, .githooks/pre-push, .gitignore, .env.example, requirements.txt, init_project.ps1)
├── graph/YYYY-MM-DD/      # figures, one folder per date (gitignored contents)
├── report/YYYY-MM-DD/     # reports, one folder per date
└── docs/specs/ plans/ reviews/ license-register/   # used by the USask skills
```

`<projects-root>` is, first match wins: `--base DIR`, the `PROJECTS_ROOT` environment
variable, or `~/Projects`.

## How to run

The bundled script is `scaffold.py`, in the same folder as this file.

**New project**
1. Get the project name from the user. Use letters, digits, `_` or `-` with no spaces,
   e.g. `irrigation_SK`. If they didn't give one, ask.
2. Confirm where it should go. Show the resolved `<projects-root>` and ask if the user
   hasn't said. Then run `python "<skill-dir>/scaffold.py" new <name>`, adding
   `--base <dir>` when needed.
   - The script refuses if `<projects-root>/<name>` already exists. Never delete or
     overwrite an existing project to get around this.
   - It fills `<AUTHOR>` / `<EMAIL>` from `git config user.name` / `user.email`. If it
     reports TODO values, tell the user to set those and fix README.md.
3. Show the user the "Created:" list.
4. Offer to run the template's own init step, which runs `git init`, installs the NDAC
   push guard from `.githooks/pre-push`, and checks that `.gitignore` protects
   credentials and data:
   `powershell -ExecutionPolicy Bypass -File "<project_dir>\init_project.ps1"`
   Run it only if the user agrees.
5. Remind the user to fill the CLAUDE.md TODOs: purpose, conda env, the input security zone
   (A_Public / B_Internal / C_Limited / D_Restric) and the identifiers present. Ask for the
   security zone; don't guess it. Then work through `SETUP.md`.

**Dated folders for today (existing project)**
- Run `python "<skill-dir>/scaffold.py" date "<project_dir>"`. Add `--date YYYY-MM-DD` for
  another date. Default to the current working directory when the user is inside a project.

## Conventions afterwards

- Save figures to `graph/<run-date>/` and reports to `report/<run-date>/`. Never overwrite an
  earlier date's folder.
- Everything in the project's CLAUDE.md applies: `data/raw` is read-only, stage files by name,
  and nothing leaves the secure environment without an export check.
