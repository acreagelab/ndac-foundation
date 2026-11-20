"""Create a new NDAC data project from the bundled template, or add dated graph/report folders.

Usage:
    python scaffold.py new <name> [--base DIR] [--template DIR] [--date YYYY-MM-DD]
    python scaffold.py date <project_dir> [--date YYYY-MM-DD]

`new`  copies template/ (next to this file) into <base>/<name>, fills placeholders
       (<PROJECT_NAME>, <PROJECT_DIR>, <AUTHOR>, <EMAIL>), then adds graph/<date>,
       report/<date> and the docs/ subfolders. Refuses if the target already exists.
`date` only adds graph/<date> and report/<date> to an existing project.

Parent folder for new projects, first match wins:
    --base DIR  >  PROJECTS_ROOT environment variable  >  ~/Projects
"""
import argparse
import datetime as dt
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent / "template"

# Extra folders on top of the template (template's own folders are copied as-is).
EXTRA_DIRS = ["docs/specs", "docs/plans", "docs/reviews", "docs/license-register"]
DATED_PARENTS = ["graph", "report"]

# Never copy these from the template.
SKIP = shutil.ignore_patterns(".git", ".ee_auth", ".env", "__pycache__", ".pytest_cache",
                              ".venv", "venv", "*.pyc")

# Files where placeholders are replaced.
PLACEHOLDER_FILES = ["CLAUDE.md", "README.md", "SETUP.md", "PROGRESS_REPORT.md",
                     "docs/HOW_TO_RUN.md", "docs/metadata-template.meta.yaml",
                     "configs/default.yaml"]

GITIGNORE_ADDITION = """
# --- Dated figure outputs (folder structure kept via .gitkeep) ---
graph/**
!graph/**/
!graph/**/.gitkeep
"""


def default_base() -> str:
    return os.environ.get("PROJECTS_ROOT") or str(Path.home() / "Projects")


def git_config(key: str) -> str:
    try:
        out = subprocess.run(["git", "config", "--get", key], capture_output=True,
                             text=True, timeout=10)
        return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def make_dir(path: Path, created: list) -> None:
    if not path.exists():
        path.mkdir(parents=True)
        created.append(path)
    if not any(path.iterdir()):
        (path / ".gitkeep").touch()


def add_dated(root: Path, date: str, created: list) -> None:
    for parent in DATED_PARENTS:
        make_dir(root / parent / date, created)


def report(root: Path, created: list) -> None:
    print(f"Project: {root}")
    if not created:
        print("Nothing new - everything already existed.")
        return
    print("Created:")
    for c in created:
        print("  " + c.relative_to(root).as_posix() + ("/" if c.is_dir() else ""))


def cmd_new(a) -> None:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_\-]*", a.name):
        sys.exit(f"ERROR: project name '{a.name}' - use letters, digits, _ or - (no spaces).")
    template = Path(a.template)
    if not (template / "CLAUDE.md").exists():
        sys.exit(f"ERROR: template not found or has no CLAUDE.md: {template}")
    base = Path(a.base).expanduser()
    if not base.is_dir():
        sys.exit(f"ERROR: parent folder does not exist: {base} "
                 f"(create it, or pass --base / set PROJECTS_ROOT).")
    root = base / a.name
    if root.exists():
        sys.exit(f"ERROR: {root} already exists - not overwriting. "
                 f"Use 'date' mode to add dated folders to it.")

    shutil.copytree(template, root, ignore=SKIP)
    created = [root]

    author = git_config("user.name") or "TODO_AUTHOR"
    email = git_config("user.email") or "TODO_EMAIL"
    values = {"<PROJECT_NAME>": a.name, "<PROJECT_DIR>": str(root),
              "<AUTHOR>": author, "<EMAIL>": email}
    for rel in PLACEHOLDER_FILES:
        f = root / rel
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        new = text
        for key, val in values.items():
            new = new.replace(key, val)
        if new != text:
            f.write_text(new, encoding="utf-8")

    gi = root / ".gitignore"
    if gi.exists() and "graph/**" not in gi.read_text(encoding="utf-8"):
        with gi.open("a", encoding="utf-8") as fh:
            fh.write(GITIGNORE_ADDITION)

    for d in EXTRA_DIRS:
        make_dir(root / d, created)
    add_dated(root, a.date, created)
    report(root, created)
    print(f"\nTemplate copied from: {template}")
    print(f"Author filled as: {author} <{email}>"
          + ("  (set git config user.name/user.email, then fix README.md)"
             if author.startswith("TODO") or email.startswith("TODO") else ""))


def cmd_date(a) -> None:
    root = Path(a.project_dir).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"ERROR: project folder not found: {root}")
    created: list = []
    add_dated(root, a.date, created)
    report(root, created)


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new")
    n.add_argument("name")
    n.add_argument("--base", default=default_base())
    n.add_argument("--template", default=str(TEMPLATE))
    n.add_argument("--date", default=dt.date.today().isoformat())
    n.set_defaults(func=cmd_new)

    d = sub.add_parser("date")
    d.add_argument("project_dir")
    d.add_argument("--date", default=dt.date.today().isoformat())
    d.set_defaults(func=cmd_date)

    a = p.parse_args()
    dt.date.fromisoformat(a.date)  # validate
    a.func(a)


if __name__ == "__main__":
    main()
