#!/bin/bash
# Python environment on Fir / Alliance clusters. The project runs in the lab's shared image
# (pinned in scripts/fir_python), so there is nothing to build for packages the image has.
# This script installs only what the image LACKS (e.g. pytest, nbstripout) into a small
# add-on venv on top of it (~/venvs/<project>, --system-site-packages), which
# scripts/fir_python then uses automatically.
#
#   bash scripts/setup_fir_env.sh            # on a LOGIN node (needs internet for PyPI fallbacks)
#   scripts/fir_python -u script.py          # every run afterwards; no module load, no activate
#
# Packages already in the image are NOT reinstalled, even if requirements.txt pins another
# version: the image version is used and reported. All versions in use are written to
# requirements-fir.lock.txt: commit it, so runs on Fir can be reproduced.
# No conda envs (group file quota); see /project/def-kanj241/zenvs/README.md.
set -eo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
py="$root/scripts/fir_python"
image="$(sed -n 's/^IMAGE=//p' "$py")"
zenvs="${ZENVS:-/project/def-kanj241/zenvs}"
sif="$zenvs/containers/$image.sif"
extra="${FIR_ENV_DIR:-$HOME/venvs/$(basename "$root")}"
apptainer="$(command -v apptainer || echo /cvmfs/soft.computecanada.ca/easybuild/software/2023/x86-64-v3/Core/apptainer/1.2.4/bin/apptainer)"

[ -f "$sif" ] || { echo "ERROR: image not found: $sif (set IMAGE in scripts/fir_python)" >&2; exit 1; }
echo "Image: $image"

in_image() { "$zenvs/bin/$image-python" "$@"; }

missing=()
while read -r req; do
    name="${req%%[=<>!~ ]*}"
    have="$(in_image -c "import importlib.metadata as m, sys; print(m.version(sys.argv[1]))" "$name" 2>/dev/null || true)"
    if [ -n "$have" ]; then
        want="${req#*==}"
        [ "$want" != "$req" ] && [ "$want" != "$have" ] && note=" (requirements.txt pins $want)" || note=""
        echo "  image       $name $have$note"
    else
        missing+=("$req")
    fi
done < <(grep -vE '^\s*(#|$|-)' "$root/requirements.txt" | sed 's/#.*//; s/[[:space:]]*$//')

if [ ${#missing[@]} -eq 0 ]; then
    echo "Everything in requirements.txt is in the image; no add-on venv needed."
else
    unset PYTHONHOME LD_LIBRARY_PATH SSL_CERT_FILE CURL_CA_BUNDLE
    binds=; for d in /project /scratch /localscratch; do [ -d "$d" ] && binds="$binds${binds:+,}$d"; done
    in_sif() { "$apptainer" exec ${binds:+-B "$binds"} "$sif" "$@"; }
    [ -f "$extra/pyvenv.cfg" ] || in_sif python -m venv --system-site-packages "$extra"
    for req in "${missing[@]}"; do
        if in_sif "$extra/bin/pip" install -q --no-index "$req" 2>/dev/null; then
            echo "  wheelhouse  $req"
        elif in_sif "$extra/bin/pip" install -q "$req" 2>/dev/null; then
            echo "  PyPI        $req"
        else
            name="${req%%[=<>!~]*}"
            in_sif "$extra/bin/pip" install -q "$name"
            echo "  CHANGED     $req -> $(in_sif "$extra/bin/pip" show "$name" | awk '/^Version/{print $2}') (pin not available here)"
        fi
    done
    echo "Add-on venv: $extra"
fi

{ echo "# image: $image"; "$py" -m pip freeze 2>/dev/null; } > "$root/requirements-fir.lock.txt"
echo ""
echo "Recorded versions: requirements-fir.lock.txt (commit it)"
echo "Run:  scripts/fir_python -u <script.py>"
