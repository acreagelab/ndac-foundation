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

Run a version as a Slurm job (commit first). Plan it, then submit the command the plan prints:

```bash
python scripts/fir_plan.py TODO v1_baseline     # time, memory, CPUs, staging, output location
sbatch ... scripts/job_template.sbatch          # the exact command printed by fir_plan
squeue -u $USER                                 # job status
tail -f logs/<job-name>-<jobid>.out             # follow the log
```

Then compare: `python scripts/compare_runs.py TODO` (add `--root /scratch/$USER/<PROJECT_NAME>/data/outputs`
if the plan sent outputs to scratch; copy final results back to /project).

## Diagrams

```powershell
python scripts/render_diagrams.py
```

## Verify

```powershell
pytest
```
