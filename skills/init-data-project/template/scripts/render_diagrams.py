"""Render every Mermaid diagram (docs/research/diagrams/*.mmd) to PNG next to its source.

    python scripts/render_diagrams.py            # render all
    python scripts/render_diagrams.py pipeline   # render one (name without .mmd)

Needs Node.js (https://nodejs.org). Uses a pinned @mermaid-js/mermaid-cli via npx (first
run downloads it; later runs reuse the cache). It drives an INSTALLED Chrome or Edge when
one is found; managed university machines often block browsers downloaded into the user
profile ("spawn UNKNOWN"). Without an installed browser, puppeteer downloads Chromium
(~150 MB). Override with the BROWSER_PATH environment variable.

Rendering is LOCAL on purpose. Do not paste diagrams into online renderers
(mermaid.live, mermaid.ink, ...): a pipeline diagram reveals data sources and
security zones, and those sites send the text to an outside server.

Edit the .mmd files, never the PNGs. GitHub/GitLab and VS Code (Markdown preview with
a Mermaid extension) also render ```mermaid blocks directly.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MERMAID_CLI = "@mermaid-js/mermaid-cli@12.2.0"
ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src" / "common.py").exists())
DIAGRAMS = ROOT / "docs" / "research" / "diagrams"

BROWSER_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
]


def find_browser() -> str | None:
    if os.environ.get("BROWSER_PATH"):
        return os.environ["BROWSER_PATH"]
    return next((b for b in BROWSER_CANDIDATES if Path(b).is_file()), None)


def main() -> None:
    npx = shutil.which("npx")
    if not npx:
        sys.exit("npx not found: install Node.js (LTS) from https://nodejs.org, then re-run.")
    wanted = set(sys.argv[1:])
    sources = sorted(p for p in DIAGRAMS.glob("*.mmd") if not wanted or p.stem in wanted)
    if not sources:
        sys.exit(f"No matching .mmd files in {DIAGRAMS}")

    env = dict(os.environ)
    extra: list[str] = []
    browser = find_browser()
    with tempfile.TemporaryDirectory() as tmp:
        if browser:
            print(f"Using installed browser: {browser}")
            cfg = Path(tmp) / "puppeteer.json"
            cfg.write_text(json.dumps({"executablePath": browser, "headless": True}), encoding="utf-8")
            extra = ["-p", str(cfg)]
            env["PUPPETEER_SKIP_DOWNLOAD"] = "1"
        failed = []
        for src in sources:
            out = src.with_suffix(".png")
            cmd = [npx, "--yes", MERMAID_CLI, "-i", str(src), "-o", str(out),
                   "--backgroundColor", "white", "--scale", "2", *extra]
            print(f"Rendering {src.relative_to(ROOT)} -> {out.name}")
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            if result.returncode != 0 or not out.exists():
                failed.append(src.name)
                print(result.stderr.strip()[-2000:] or result.stdout.strip()[-2000:], file=sys.stderr)
    if failed:
        sys.exit(f"Failed: {', '.join(failed)}")
    print("Done.")


if __name__ == "__main__":
    main()
