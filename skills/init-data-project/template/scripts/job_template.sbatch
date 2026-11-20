#!/bin/bash
# Slurm job: run one VERSION of one SUB-PROJECT on Fir.
#
# Normally you don't call this directly: ask Claude, or run
#   python scripts/fir_plan.py <subproject> <version>
# which measures inputs and earlier runs, then prints the right sbatch command, e.g.
#   sbatch --account=def-x --time=01:15:00 --mem=12G --cpus-per-task=4 \
#          --export=ALL,SUB=et_mapping,VER=v2_add_s2,STAGE=1 scripts/job_template.sbatch
#
# Options passed through --export:
#   SUB, VER       required: sub-project and version config
#   STAGE=1        copy ${DATA_ROOT} inputs to the node's local disk ($SLURM_TMPDIR) and
#                  write the run there; results are copied to OUTPUT_ROOT when the job ends,
#                  fails, or is about to hit its time limit
#   OUTPUT_ROOT    where run folders end up (default: <project>/data/outputs; use /scratch for big outputs)
#
# Before the first job: set fir.account in configs/fir.yaml, run scripts/setup_fir_env.sh on a
# login node, and commit (the run folder records the git commit; "-dirty" = uncommitted).
# Compute nodes have no internet: download data (e.g. Earth Engine) on a login node first.
#
#SBATCH --account=def-TODO          # overridden by fir_plan's --account
#SBATCH --job-name=ndac-run
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --output=logs/%x-%j.out      # logs/ is gitignored; submit from the project root
#SBATCH --signal=B:USR1@600          # warning 10 min before the time limit -> save results

set -eo pipefail   # no -u: Lmod's module command can trip over unset variables
: "${SUB:?pass SUB=<subproject> via --export}"
: "${VER:?pass VER=<version> via --export}"

cd "${SLURM_SUBMIT_DIR}"
project_dir="$PWD"
project="$(basename "$PWD")"
module load StdEnv/2023 python/3.12 gdal          # keep in step with scripts/setup_fir_env.sh
# shellcheck disable=SC1090
source "${FIR_ENV_DIR:-$HOME/envs/$project}/bin/activate"

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-1}"
OUTPUT_ROOT="${OUTPUT_ROOT:-$project_dir/data/outputs}"
echo "Job ${SLURM_JOB_ID} on $(hostname): ${SUB} / ${VER}, ${SLURM_CPUS_PER_TASK:-?} CPUs, STAGE=${STAGE:-0}"
echo "Outputs -> ${OUTPUT_ROOT}"

copied_back=0
copy_back() {
    if [ "${STAGE:-0}" = 1 ] && [ "$copied_back" = 0 ] && [ -d "${RUNS_ROOT:-}" ]; then
        mkdir -p "$OUTPUT_ROOT"
        cp -r "$RUNS_ROOT"/. "$OUTPUT_ROOT"/ && copied_back=1
        echo "Results copied from local disk to ${OUTPUT_ROOT}"
    fi
}
trap copy_back EXIT
trap 'echo "Time limit close: saving results"; copy_back; kill -TERM "$pid" 2>/dev/null; exit 124' USR1

if [ "${STAGE:-0}" = 1 ]; then
    : "${SLURM_TMPDIR:?STAGE=1 needs node-local disk (SLURM_TMPDIR)}"
    echo "Staging inputs to ${SLURM_TMPDIR}"
    python -u scripts/fir_stage.py "$SUB" "$VER" "$SLURM_TMPDIR/data_root"
    export DATA_ROOT="$SLURM_TMPDIR/data_root"
    export RUNS_ROOT="$SLURM_TMPDIR/runs"
else
    export RUNS_ROOT="$OUTPUT_ROOT"
fi

# Run in the background and wait, so the USR1 warning can be handled while Python runs.
python -u "subprojects/${SUB}/scripts/01_run.py" --version "${VER}" &
pid=$!
wait "$pid"
