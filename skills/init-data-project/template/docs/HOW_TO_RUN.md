# How to run: <PROJECT_NAME>

Once per session:

```powershell
conda activate TODO_ENV_NAME
cd <PROJECT_DIR>
```

Only list commands that have been run and work. Mark steps that OVERWRITE existing
outputs with **(overwrites)** in their title. Logs go to `logs\<step>_<scope>.log`.

## 1. TODO step name

```powershell
python -u subprojects/TODO/scripts/01_run.py --version v1_baseline *> logs\TODO_v1.log
Get-Content logs\TODO_v1.log -Tail 20
```

`*>` sends all output to the log. Avoid `2>&1 | Tee-Object` in Windows PowerShell 5.1:
it turns normal Python log messages into red error records. To watch a long run live,
open a second terminal and run `Get-Content logs\TODO_v1.log -Wait`.

On Linux / HPC (bash): `python -u ... 2>&1 | tee logs/TODO_v1.log`.

## 2. Compare versions

```powershell
python scripts/compare_runs.py TODO --sort <key_metric> --save
```

## On Fir (Alliance HPC)

Once per session, on a login node:

```bash
module load StdEnv/2023 python/3.12 gdal
source ~/envs/<PROJECT_NAME>/bin/activate
cd ~/projects/<PROJECT_NAME>        # wherever the project is cloned on Fir
```

Run a version as a Slurm job (commit first; outputs land in `data/outputs/...`, the job log in `logs/`):

```bash
sbatch --export=ALL,SUB=TODO,VER=v1_baseline scripts/job_template.sbatch
squeue -u $USER                     # job status
tail -f logs/ndac-run-<jobid>.out   # follow the log
```

Then compare as usual: `python scripts/compare_runs.py TODO`.

## Diagrams

```powershell
python scripts/render_diagrams.py
```

## Verify

```powershell
pytest
```
