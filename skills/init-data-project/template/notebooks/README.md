# Notebooks (project-level exploration)

- Exploration only. Any number that is reported must come from a script run that writes a
  run manifest (see `src/common.py`).
- Outputs are stripped on commit by nbstripout, installed as a git filter by
  `init_project.ps1`. Printed tables of field-level data must never reach git.
- Name: `YYYY-MM-DD_<initials>_<topic>.ipynb`. Sub-project notebooks go in
  `subprojects/<name>/notebooks/`.
