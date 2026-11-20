# One-time initialization for a project created from the ndac-foundation template.
# Run AFTER filling .env (see SETUP.md). Safe to re-run.
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

if (Test-Path (Join-Path $root ".git")) {
    Write-Host "Git repo already initialized - skipping init."
} else {
    git -C $root init -b main | Out-Host
}

# NDAC push guard: blocks pushes to non-USask remotes until deliberately approved
# (git config ndac.pushApproved true - only after /export-check).
$guard = Join-Path $root ".githooks\pre-push"   # shipped with the template
if (Test-Path $guard) {
    Copy-Item $guard -Destination (Join-Path $root ".git\hooks\pre-push") -Force
    Write-Host "Push guard installed."
} else {
    Write-Host "WARNING: push guard not found at $guard - install it manually."
}

# Notebook outputs (printed tables, plots of field data) must not reach git.
$ErrorActionPreference = "Continue"
python -m nbstripout --version *> $null
if ($LASTEXITCODE -eq 0) {
    Push-Location $root
    python -m nbstripout --install --attributes .gitattributes
    Pop-Location
    Write-Host "nbstripout installed: notebook outputs are stripped on commit."
} else {
    Write-Host "WARNING: nbstripout not found - activate the project env (it is in requirements.txt) and re-run this script."
}

Write-Host ""
Write-Host "check-ignore verification (each line below = protected):"
git -C $root check-ignore -v .env .ee_auth/credentials data/raw/sample.tif logs/run.log report/2026-01-01/table.csv fields.shp model.pkl
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: some paths are NOT ignored - fix .gitignore before committing."
}

Write-Host ""
Write-Host "Untracked files:"
git -C $root status --short

Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Review the list above; stage explicitly by name (never 'git add .')"
Write-Host "  2. git commit for the initial baseline"
Write-Host "  3. pytest"
Write-Host "  4. Work through SETUP.md, then delete it"
