#!/bin/bash
# Create (or update) this project's Python environment on Fir / Alliance clusters.
# Alliance does not support conda: this uses environment modules + a virtualenv, and
# installs from the Alliance wheelhouse (--no-index) where possible.
#
#   bash scripts/setup_fir_env.sh            # on a LOGIN node (needs internet for fallbacks)
#   source ~/envs/<project>/bin/activate     # every session afterwards
#
# Edit MODULES if the project needs other versions: `module spider python`, `module spider gdal`.
# Check a package in the wheelhouse:  avail_wheels geopandas
# The installed versions are written to requirements-fir.lock.txt: commit it, so runs on
# Fir can be reproduced (Fir versions may differ from the laptop pins in requirements.txt).
set -eo pipefail   # no -u: Lmod's module command can trip over unset variables

MODULES="StdEnv/2023 python/3.12 gdal"
EXTRA="geopandas matplotlib"            # geospatial packages (on the laptop these come from environment.yml)

root="$(cd "$(dirname "$0")/.." && pwd)"
project="$(basename "$root")"
env_dir="${FIR_ENV_DIR:-$HOME/envs/$project}"

if ! command -v module >/dev/null 2>&1; then
    echo "ERROR: 'module' not found. Run this on a Fir / Alliance login node." >&2
    exit 1
fi

module load $MODULES
echo "Modules: $MODULES"

if [ ! -d "$env_dir" ]; then
    virtualenv --no-download "$env_dir"
fi
# shellcheck disable=SC1091
source "$env_dir/bin/activate"
pip install --no-index --upgrade pip >/dev/null

install_one() {   # try the Alliance wheelhouse first, then PyPI
    if pip install --no-index "$1" >/dev/null 2>&1; then
        echo "  wheelhouse  $1"
    elif pip install "$1" >/dev/null 2>&1; then
        echo "  PyPI        $1"
    else
        # exact pin unavailable on this cluster: take the nearest version, and say so
        name="${1%%[=<>!~]*}"
        pip install --no-index "$name" >/dev/null 2>&1 || pip install "$name" >/dev/null
        echo "  CHANGED     $1 -> $(pip show "$name" | awk '/^Version/{print $2}') (pin not available here)"
    fi
}

echo "Installing requirements.txt:"
grep -vE '^\s*(#|$|-)' "$root/requirements.txt" | sed 's/#.*//' | while read -r req; do install_one "$req"; done
echo "Installing extras ($EXTRA):"
for req in $EXTRA; do install_one "$req"; done

pip freeze > "$root/requirements-fir.lock.txt"
echo ""
echo "Environment: $env_dir"
echo "Recorded versions: requirements-fir.lock.txt (commit it)"
echo "Each session:  module load $MODULES && source $env_dir/bin/activate"
