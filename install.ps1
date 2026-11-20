# Install (or update) ndac-foundation as personal Claude Code skills and agents.
#
#   git clone https://github.com/thuanhavan/ndac-foundation C:\<NSID>\Projects\ndac-foundation
#   powershell -ExecutionPolicy Bypass -File C:\<NSID>\Projects\ndac-foundation\install.ps1
#
# Update later:  git -C <repo> pull ; then run this script again.
#
# Copies skills/* to ~/.claude/skills/ and agents/*.md to ~/.claude/agents/. Anything it
# replaces is first moved to ~/.claude/backups/ndac-foundation-<timestamp>/, so nothing
# is lost. Only folders/files with the same names as this repo's are touched.
$ErrorActionPreference = "Stop"
$repo   = $PSScriptRoot
$claude = Join-Path $HOME ".claude"
$stamp  = Get-Date -Format "yyyyMMdd-HHmmss"
$backup = Join-Path $claude "backups\ndac-foundation-$stamp"

function Install-Item($source, $destDir) {
    $name = Split-Path $source -Leaf
    $dest = Join-Path $destDir $name
    if (Test-Path $dest) {
        $bdir = Join-Path $backup (Split-Path $destDir -Leaf)
        New-Item -ItemType Directory -Force $bdir | Out-Null
        Move-Item $dest (Join-Path $bdir $name)
        Write-Host "  replaced $name (old copy backed up)"
    } else {
        Write-Host "  added    $name"
    }
    Copy-Item $source $dest -Recurse
}

$skillsDir = Join-Path $claude "skills"
$agentsDir = Join-Path $claude "agents"
New-Item -ItemType Directory -Force $skillsDir, $agentsDir | Out-Null

Write-Host "Skills -> $skillsDir"
Get-ChildItem (Join-Path $repo "skills") -Directory | ForEach-Object { Install-Item $_.FullName $skillsDir }
Write-Host "Agents -> $agentsDir"
Get-ChildItem (Join-Path $repo "agents") -Filter *.md | ForEach-Object { Install-Item $_.FullName $agentsDir }

$version = (Get-Content (Join-Path $repo ".claude-plugin\plugin.json") -Raw | ConvertFrom-Json).version
Write-Host ""
Write-Host "ndac-foundation $version installed."
if (Test-Path $backup) { Write-Host "Backups of replaced items: $backup" }
Write-Host "Restart Claude Code (or reload the VS Code window), then type / and look for"
Write-Host "init-data-project, export-check, adopt-project, ndac-data-rules, fir-resources."
