#!/bin/bash
# Slurm job: run one VERSION of one SUB-PROJECT on Fir.
#
#   sbatch --export=ALL,SUB=et_mapping,VER=v2_add_s2 scripts/job_template.sbatch
#
# Several versions at once (one job each):
#   for v in v1_baseline v2_add_s2; do sbatch --export=ALL,SUB=et_mapping,VER=$v scripts/job_template.sbatch; done
#
# Before the first job: fill in --account, run scripts/setup_fir_env.sh on a login node,
# and commit your code (the run folder name records the git commit; "-dirty" = uncommitted).
# Compute nodes have no internet: download data (e.g. Earth Engine) on a login node first.
#
#SBATCH --account=def-TODO          # your PI's allocation, e.g. def-smith
#SBATCH --job-name=ndac-run
#SBATCH --time=01:00:00              # hh:mm:ss - ask for what you need, shorter jobs start sooner
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --output=logs/%x-%j.out      # logs/ is gitignored; submit from the project root
# #SBATCH --gpus-per-node=1          # uncomment for GPU work

set -eo pipefail   # no -u: Lmod's module command can trip over unset variables
: "${SUB:?pass SUB=<subproject> via --export}"
: "${VER:?pass VER=<version> via --export}"

cd "${SLURM_SUBMIT_DIR}"
project="$(basename "$PWD")"
module load StdEnv/2023 python/3.12 gdal          # keep in step with scripts/setup_fir_env.sh
# shellcheck disable=SC1090
source "${FIR_ENV_DIR:-$HOME/envs/$project}/bin/activate"

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-1}"
echo "Job ${SLURM_JOB_ID} on $(hostname): ${SUB} / ${VER}, ${SLURM_CPUS_PER_TASK} CPUs"

# Large inputs: copy to fast node-local disk first, e.g.
#   cp -r "$DATA_ROOT/irrigation/inputs" "$SLURM_TMPDIR/" ; export DATA_ROOT="$SLURM_TMPDIR"
python -u "subprojects/${SUB}/scripts/01_run.py" --version "${VER}"
