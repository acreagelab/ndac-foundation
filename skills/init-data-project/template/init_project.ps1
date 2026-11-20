# One-time initialization for a project created from the ndac-foundation template.
# Run AFTER renaming the folder and filling .env (see SETUP.md).
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

if (Test-Path (Join-Path $root ".git")) {
    Write-Host "Git repo already initialized - skipping init."
} else {
    git -C $root init | Out-Host
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

Write-Host ""
Write-Host "check-ignore verification (each line below = protected):"
git -C $root check-ignore -v .env .ee_auth/credentials data/raw/sample.tif logs/run.log
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
Write-Host "  3. pytest tests/ -v"
Write-Host "  4. Work through SETUP.md, then delete it"
