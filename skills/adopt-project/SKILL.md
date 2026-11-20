---
name: adopt-project
description: Bring an EXISTING NDAC project (one not created from the ndac-foundation template) under version control and up to baseline hygiene, in credential-safe order (.gitignore before git init, explicit staging, no data or secrets committed, push guard installed). Use when asked to adopt, initialize, git-init, or clean up an existing project directory. For brand-new projects use init-data-project instead.
---

# Adopt an existing NDAC project

Bring ONE existing project directory up to the baseline. Order matters: the credential
steps come before git exists, so a token can never enter history.

The baseline files come from the init-data-project template in this plugin:
`<skill-dir>/../init-data-project/template/` (call it TEMPLATE below).

## Steps

1. **Audit first.** Launch the `repo-auditor` agent on the project directory and review
   its scorecard with the user before changing anything.

2. **Credential sweep: hard gate.** Glob for `.ee_auth/**`, `.ee_accounts/**`,
   `.ee_personal_account/**`, `**/credentials`, `application_default_credentials.json`,
   `*service-account*.json`, `.env`, `*key*.txt`, `*.pem`. If anything is found:
   STOP, list the paths (never the contents), and ask the user whether to relocate them
   outside the project tree before continuing. Never move, delete, or read them yourself.

3. **Write `.gitignore` BEFORE `git init`.** Start from `TEMPLATE/.gitignore`; merge with
   any existing one, never drop an existing credential pattern. Adjust data patterns per
   project only with an explicit `!` exception and a reason. Credential patterns are
   non-negotiable.

4. **Init and verify the ignore works.** `git init -b main`, then confirm:
   - `git check-ignore -v` returns a match for each credential path found in step 2
   - `git status --short` lists no `data/`, `report/`, data files, or credential paths

5. **Install the guards.** Copy `TEMPLATE/.githooks/pre-push` into the project as
   `.githooks/pre-push` and into `.git/hooks/pre-push`. It blocks pushes to non-USask
   remotes until deliberately approved with `git config ndac.pushApproved true` after
   `/export-check`. If the project has notebooks: `python -m nbstripout --install
   --attributes .gitattributes`. Copy `TEMPLATE/.claude/settings.json` (credential read
   deny rules) if the project has no `.claude/settings.json`; merge otherwise.

6. **First commit: explicit staging only.** Stage code, configs, docs, tests, and
   `.gitignore` by name. NEVER `git add .` or `git add -A`. Commit only if the user asked
   for a commit; otherwise stop after staging and report.

7. **Pin dependencies.** Create or fix `requirements.txt` (and `environment.yml` for
   conda/geospatial stacks) with exact pins covering every import actually used
   (cross-check imports vs manifest). Record which interpreter/conda env the project uses.

8. **CLAUDE.md and research docs.** Use `TEMPLATE/CLAUDE.md` as the outline. Fill in only
   what is true on disk; every path and command cited must resolve. Offer to add the
   research docs the project is missing (`docs/research/objectives.md`, `plan.md`,
   diagrams, `docs/data_sources.md`, `docs/ACKNOWLEDGEMENT.md`) from TEMPLATE.

9. **Report layout deviations; don't move files.** raw/processed mixing, root-level
   logs, in-tree venvs/zips, duplicate or `_v2`/`_final` copies of scripts: list them with
   recommendations (e.g. version configs under `subprojects/`). Moving or deleting
   requires the user's confirmation per item.

10. **Verify.** `git status` shows a clean picture, staged set contains no data/secrets,
    `pytest` passes if tests exist. Report the scorecard delta from step 1.

## Do not

- Run this across many projects in one pass: one project, reviewed, at a time
- Touch `data/raw/` (read-only, always)
- Commit or push unless explicitly asked
