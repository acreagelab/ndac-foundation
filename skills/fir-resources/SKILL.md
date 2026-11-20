---
name: fir-resources
description: Decide where work and data go on the Fir cluster (Alliance HPC) — login node vs interactive vs Slurm batch job, how much time/memory/CPU/GPU to request, and which storage (/project, /scratch, node-local $SLURM_TMPDIR, nearline, /home) — using real measurements of inputs and earlier runs. Use whenever the user is on Fir (or another Alliance cluster) and wants to run an analysis, submit a job, move or store data, handle big data or long processing, or asks where something should run or live.
---

# Fir resources: right node, right storage

Goal: heavy or long work runs as Slurm jobs sized from real measurements; data lives on the
storage that fits its size, speed need and value. Never guess cluster limits from memory:
read them from the cluster (`sinfo`, `sacct`, `diskusage_report`) or the project's
`configs/fir.yaml`.

## Where work runs

| Work | Where | How |
|---|---|---|
| Editing, Claude, git, reading docs | login node | as is |
| Downloads (Earth Engine, web data) | login node | compute nodes have no internet; download before the job |
| Quick test: a few minutes, little memory, no GPU | login node | only if `fir_plan.py` says "login node"; otherwise a small batch job |
| Debugging with real data | interactive job | `salloc --account=<acct> --time=1:00:00 --mem=8G --cpus-per-task=4` |
| Anything heavy, long, parallel or GPU | batch job | `python scripts/fir_plan.py <sub> <ver>` → its `sbatch` command |
| Many versions / years / tiles | job array or one job per version | one `sbatch` per version, or `--array` over a list |

Never start heavy computation on a login node: it slows the node for everyone and may be killed.

## Where data lives

| Data | Storage | Notes |
|---|---|---|
| Code, configs, docs (the project) | `/project/<allocation>/<user>/<project>` | backed up, group-shared |
| Raw inputs, final results | `/project/...` | backed up, permanent; register inputs in docs/data_sources.md |
| Big intermediate files, large run outputs | `/scratch/$USER/<project>` | fast, large, **NOT backed up, purged when old**; never the only copy |
| Data a job reads heavily | node-local `$SLURM_TMPDIR` | fastest; deleted at job end; use `STAGE=1` so results are copied back |
| Finished datasets to archive | nearline (tape) | cheap long-term; slow to read back |
| Python env, small personal config | `/home` | small quota |

Many small files (thousands) are slow on shared storage: bundle them (tar) before staging.
Before copying data to Fir at all: the project's security zone must be allowed there; ask
the data steward for C_Limited / D_Restric.

## Procedure for running a version

1. **Commit** the code (run folders record the commit; `-dirty` runs can't be reproduced).
2. **Plan**: `python scripts/fir_plan.py <subproject> <version>`. It measures inputs, reads
   earlier runs' real time and memory from Slurm accounting, reads the cluster time limit,
   and prints a plan plus the exact `sbatch` command.
3. **Show the plan to the user** — where it runs, time, memory, CPUs/GPUs, staging, output
   location, warnings — and **submit only after they agree**. Requests use the group's
   allocation and fair-share priority.
4. **First run of a version** (no history): suggest a small test (subset of data, short
   time), then re-plan from its measured numbers.
5. **Submit** the printed command from the project root. Report the job ID; check with
   `squeue -u $USER`; the log is `logs/<job-name>-<id>.out`.
6. **After the job**: `python scripts/compare_runs.py <subproject>` (add
   `--root <scratch>/data/outputs` if outputs went to scratch); record the result and
   keep/drop in the experiments log. If outputs are on scratch, copy final results to /project.

## Warnings to act on
- Plan exceeds the cluster time limit → split (job array over years/tiles) or checkpoint.
- An earlier run hit TIMEOUT / OUT_OF_MEMORY → the plan adds margin; also look for why.
- Outputs routed to scratch → remind the user it's purged and not backed up.
- `fir.account` still `def-TODO` → ask the user for their PI's allocation; don't invent one.
- Before big writes: `diskusage_report` to check quota (space AND file count).

## Settings
Per project: `configs/fir.yaml` (account, storage paths, defaults, margins, thresholds).
Per version: `resources: {cpus, mem_gb, gpus, time}` in the version config overrides the plan.
