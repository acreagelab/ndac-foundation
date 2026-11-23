#!/bin/sh
# Install (or update) ndac-foundation as personal Claude Code skills and agents
# on Linux / macOS / HPC.   sh install.sh      (update: git pull, then run again)
# Replaced items are moved to ~/.claude/backups/ndac-foundation-<timestamp>/ first.
set -e
repo=$(cd "$(dirname "$0")" && pwd)
claude="$HOME/.claude"
backup="$claude/backups/ndac-foundation-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$claude/skills" "$claude/agents"

install_item() {  # $1 = source path, $2 = destination dir
    name=$(basename "$1")
    if [ -e "$2/$name" ]; then
        mkdir -p "$backup/$(basename "$2")"
        mv "$2/$name" "$backup/$(basename "$2")/$name"
        echo "  replaced $name (old copy backed up)"
    else
        echo "  added    $name"
    fi
    cp -R "$1" "$2/$name"
}

echo "Skills -> $claude/skills"
for d in "$repo"/skills/*/; do install_item "${d%/}" "$claude/skills"; done
echo "Agents -> $claude/agents"
for f in "$repo"/agents/*.md; do install_item "$f" "$claude/agents"; done
chmod +x "$claude/skills/init-data-project/template/.githooks/pre-push" 2>/dev/null || true
chmod +x "$claude/skills/fir-resources/fir_share.sh" 2>/dev/null || true

echo ""
echo "ndac-foundation installed."
[ -d "$backup" ] && echo "Backups of replaced items: $backup"
echo "Restart Claude Code, then type / and look for init-data-project, export-check."
