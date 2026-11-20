# New project checklist

Work through this list once, then delete this file. Claude can help with each step.

1. **Fill the TODOs** in [CLAUDE.md](CLAUDE.md) (purpose, people, conda env, security zone,
   identifiers present) and [README.md](README.md). Ask your supervisor or the NDAC data
   manager for the security zone if you're unsure; don't guess it.
2. **Research context**: draft [docs/research/objectives.md](docs/research/objectives.md)
   (aim, questions, hypotheses, key metrics fixed in advance) and
   [docs/research/plan.md](docs/research/plan.md). Edit the diagrams in
   [docs/research/diagrams/](docs/research/diagrams/) and render them with
   `python scripts/render_diagrams.py` (needs Node.js).
3. **Environment**: rename the env in [environment.yml](environment.yml), then
   `conda env create -f environment.yml` and `conda activate <env>`. Put the env name in
   CLAUDE.md. Add packages to environment.yml (conda-forge) or requirements.txt (`==`).
4. **Secrets**: copy `.env.example` to `.env`; set `DATA_ROOT`, and `EE_PROJECT` if the
   project uses Earth Engine (institutional identity, never a personal Gmail).
5. **CRS**: set `crs_analysis` in [configs/default.yaml](configs/default.yaml): UTM zone
   for local work (SK = EPSG:32613), EPSG:3347 for prairie-wide statistics.
6. **Initialize git**: `powershell -ExecutionPolicy Bypass -File init_project.ps1`. It
   creates the repo, installs the NDAC push guard and the notebook output stripper, and
   checks that credentials and data are ignored. Stage files by name (never `git add .`)
   and make the first commit.
7. **Smoke test**: `pytest`. It checks layout, config, .gitignore, src/common.py and
   that the docs' links and pipeline script paths resolve.
8. **Data**: register each input in [docs/data_sources.md](docs/data_sources.md) as it
   arrives. Sidecars for shared datasets: metadata-tagger agent.
9. **First sub-project**: ask Claude "add a sub-project called <name>".
10. **People**: add yourself and collaborators to [docs/contributions.md](docs/contributions.md).
    Outputs acknowledge NDAC: [docs/ACKNOWLEDGEMENT.md](docs/ACKNOWLEDGEMENT.md).

**On Fir (Alliance HPC)** instead of steps 3, 4 and 6, on a login node:
`bash scripts/setup_fir_env.sh` (no conda on Alliance: modules + virtualenv), create `.env`
with `DATA_ROOT=/project/<group>/...`, then `bash init_project.sh`. Fill `--account` in
`scripts/job_template.sbatch`. Check with the data steward that the project's security zone
is allowed on Fir before copying data there. See CLAUDE.md, "Running on Fir".

The ndac-foundation plugin provides `/export-check`, `/adopt-project`, the NDAC data rules
skill, and the pii-scanner, metadata-tagger, repo-auditor, reviewer and researcher agents.

Standing habits: commit at the end of each work session; log decisions in
PROGRESS_REPORT.md; run `/export-check` before anything leaves the secure environment.
