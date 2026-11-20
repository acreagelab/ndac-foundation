"""Docs stay truthful: relative links resolve, and the pipeline names only real scripts."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "data", "graph", "report", "logs", "node_modules", ".venv", "venv"}
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def _markdown_files():
    for path in ROOT.rglob("*.md"):
        if not SKIP_DIRS.intersection(path.relative_to(ROOT).parts):
            yield path


def test_relative_markdown_links_resolve():
    broken = []
    for md in _markdown_files():
        text = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8"), flags=re.S)
        for target in LINK.findall(text):
            if re.match(r"^[a-z]+:", target) or target.startswith("#") or "<" in target:
                continue
            if not (md.parent / target.split("#")[0]).exists():
                broken.append(f"{md.relative_to(ROOT)} -> {target}")
    assert not broken, "broken links:\n" + "\n".join(broken)


def test_pipeline_scripts_exist():
    diagrams = ROOT / "docs" / "research" / "diagrams"
    missing = []
    for mmd in diagrams.glob("*.mmd"):
        body = "\n".join(l for l in mmd.read_text(encoding="utf-8").splitlines()
                         if not l.lstrip().startswith("%%"))
        for script in re.findall(r"[\w./\-]+\.py\b", body):
            if not (ROOT / script).exists():
                missing.append(f"{mmd.name}: {script}")
    assert not missing, "diagram names scripts that don't exist:\n" + "\n".join(missing)
