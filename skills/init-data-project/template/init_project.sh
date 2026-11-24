#!/bin/bash
# One-time initialization on Linux / Fir (bash version of init_project.ps1). Safe to re-run.
#   bash init_project.sh
set -u
root="$(cd "$(dirname "$0")" && pwd)"
cd "$root"

if [ -d .git ]; then
    echo "Git repo already initialized - skipping init."
else
    git init -b main
fi

# NDAC push guard: blocks pushes to non-USask remotes until deliberately approved
# (git config ndac.pushApproved true - only after /export-check).
if [ -f .githooks/pre-push ]; then
    cp .githooks/pre-push .git/hooks/pre-push && chmod +x .git/hooks/pre-push
    echo "Push guard installed."
else
    echo "WARNING: .githooks/pre-push not found - install the push guard manually."
fi

# Notebook outputs (printed tables, plots of field data) must not reach git.
py=python
[ -x scripts/fir_python ] && [ -d "${ZENVS:-/project/def-kanj241/zenvs}" ] && py=scripts/fir_python
if $py -m nbstripout --version >/dev/null 2>&1; then
    $py -m nbstripout --install --attributes .gitattributes
    echo "nbstripout installed: notebook outputs are stripped on commit."
else
    echo "WARNING: nbstripout not found - on Fir run scripts/setup_fir_env.sh, elsewhere activate the project env, then re-run."
fi

echo ""
echo "check-ignore verification (each line below = protected):"
git check-ignore -v .env .ee_auth/credentials data/raw/sample.tif logs/run.log \
    report/2026-01-01/table.csv fields.shp model.pkl slurm-123.out \
    || echo "WARNING: some paths are NOT ignored - fix .gitignore before committing."

echo ""
echo "Untracked files:"
git status --short

echo ""
echo "Next steps:"
echo "  1. Review the list above; stage explicitly by name (never 'git add .')"
echo "  2. git commit for the initial baseline"
echo "  3. pytest"
echo "  4. Work through SETUP.md, then delete it"
