"""NDAC project scaffolding: new projects, sub-projects, versions, dated folders.

Usage:
    python scaffold.py new <name> [--base DIR] [--template DIR] [--date YYYY-MM-DD]
    python scaffold.py subproject <project_dir> <name>
    python scaffold.py version <project_dir> <subproject> <name> [--from VERSION]
                       [--description TEXT] [--hypothesis TEXT]
    python scaffold.py date <project_dir> [--subproject NAME] [--date YYYY-MM-DD]

`new`        copies template/ into <base>/<name>, fills placeholders (<PROJECT_NAME>,
             <PROJECT_DIR>, <AUTHOR>, <EMAIL>, <DATE>), adds graph/<date>, report/<date>
             and the docs/ subfolders. Refuses if the target already exists.
`subproject` copies subproject_template/ into <project>/subprojects/<name> and adds its
             section to docs/experiments.md. Refuses if it exists.
`version`    copies an existing version config (default: the newest) to <name>.yaml with
             a fresh `version:` header, and adds a row to docs/experiments.md.
`date`       adds graph/<date> and report/<date> (optionally /<subproject>) folders.

Parent folder for new projects, first match wins:
    --base DIR  >  PROJECTS_ROOT environment variable  >  ~/Projects
Standard library only, so it runs with any Python 3.9+.
"""
import argparse
import datetime as dt
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "template"
SUBPROJECT_TEMPLATE = HERE / "subproject_template"

EXTRA_DIRS = ["docs/specs", "docs/plans", "docs/reviews", "docs/license-register"]
DATED_PARENTS = ["graph", "report"]
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".cff", ".mmd", ".bib", ".txt", ".py", ".toml"}
NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_\-]*")

SKIP = shutil.ignore_patterns(".git", ".ee_auth", ".env", "__pycache__", ".pytest_cache",
                              ".venv", "venv", "*.pyc", "node_modules")

GITIGNORE_ADDITION = """
# --- Dated figure outputs (folder structure kept via .gitkeep) ---
graph/**
!graph/**/
!graph/**/.gitkeep
"""

EXPERIMENTS_HEADER = (
    "| Version | Parent | Hypothesis | What changed | Key metric result | Decision | Date |\n"
    "|---|---|---|---|---|---|---|\n"
)


# ----------------------------------------------------------------------- helpers
def today() -> str:
    return dt.date.today().isoformat()


def default_base() -> str:
    return os.environ.get("PROJECTS_ROOT") or str(Path.home() / "Projects")


def git_config(key: str) -> str:
    try:
        out = subprocess.run(["git", "config", "--get", key], capture_output=True,
                             text=True, timeout=10)
        return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def check_name(name: str, what: str) -> None:
    if not NAME_RE.fullmatch(name):
        sys.exit(f"ERROR: {what} name '{name}' - use letters, digits, _ or - (no spaces).")


def fill_placeholders(root: Path, values: dict) -> None:
    for f in root.rglob("*"):
        if not f.is_file() or f.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new = text
        for key, val in values.items():
            new = new.replace(key, val)
        if new != text:
            f.write_text(new, encoding="utf-8")


def make_dir(path: Path, created: list) -> None:
    if not path.exists():
        path.mkdir(parents=True)
        created.append(path)
    if not any(path.iterdir()):
        (path / ".gitkeep").touch()


def report(root: Path, created: list) -> None:
    print(f"Project: {root}")
    if not created:
        print("Nothing new - everything already existed.")
        return
    print("Created:")
    for c in created:
        rel = c.relative_to(root).as_posix() if c != root else "."
        print("  " + rel + ("/" if c.is_dir() else ""))


def project_root(path: str) -> Path:
    root = Path(path).expanduser().resolve()
    if not (root / "src" / "common.py").exists():
        sys.exit(f"ERROR: {root} is not an NDAC project (no src/common.py).")
    return root


def author() -> tuple:
    return git_config("user.name") or "TODO_AUTHOR", git_config("user.email") or "TODO_EMAIL"


def experiments_add(root: Path, subproject: str, row: str = "") -> None:
    """Ensure a '## <subproject>' section exists in docs/experiments.md; append a row."""
    path = root / "docs" / "experiments.md"
    text = path.read_text(encoding="utf-8") if path.exists() else "# Experiments log\n"
    lines = text.rstrip("\n").split("\n")
    heading = f"## {subproject}"
    if heading not in lines:
        lines += ["", heading, "", *EXPERIMENTS_HEADER.rstrip("\n").split("\n")]
    if row:
        start = lines.index(heading)
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
        last_row = max(i for i in range(start, end) if lines[i].startswith("|"))
        lines.insert(last_row + 1, row)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ------------------------------------------------------------------------ commands
def cmd_new(a) -> None:
    check_name(a.name, "project")
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

    name, email = author()
    fill_placeholders(root, {"<PROJECT_NAME>": a.name, "<PROJECT_DIR>": str(root),
                             "<AUTHOR>": name, "<EMAIL>": email, "<DATE>": a.date})

    gi = root / ".gitignore"
    if gi.exists() and "graph/**" not in gi.read_text(encoding="utf-8"):
        with gi.open("a", encoding="utf-8") as fh:
            fh.write(GITIGNORE_ADDITION)

    for d in EXTRA_DIRS:
        make_dir(root / d, created)
    for parent in DATED_PARENTS:
        make_dir(root / parent / a.date, created)
    report(root, created)
    print(f"\nTemplate copied from: {template}")
    print(f"Author filled as: {name} <{email}>"
          + ("  (set git config user.name/user.email, then fix README.md and docs/)"
             if name.startswith("TODO") or email.startswith("TODO") else ""))


def cmd_subproject(a) -> None:
    root = project_root(a.project_dir)
    check_name(a.name, "sub-project")
    target = root / "subprojects" / a.name
    if target.exists():
        sys.exit(f"ERROR: {target} already exists - not overwriting.")
    shutil.copytree(SUBPROJECT_TEMPLATE, target, ignore=SKIP)
    name, _ = author()
    fill_placeholders(target, {"<SUBPROJECT>": a.name, "<AUTHOR>": name, "<DATE>": today()})
    experiments_add(root, a.name,
                    f"| v1_baseline | base | TODO | Baseline | | | {today()} |")
    print(f"Created sub-project: {target.relative_to(root).as_posix()}/")
    for f in sorted(target.rglob("*")):
        if f.is_file():
            print("  " + f.relative_to(root).as_posix())
    print("Added section to docs/experiments.md")


def _newest_version(cdir: Path) -> str:
    versions = sorted((p for p in cdir.glob("*.yaml") if p.stem != "base"),
                      key=lambda p: p.stat().st_mtime)
    if not versions:
        sys.exit(f"ERROR: no version configs in {cdir}")
    return versions[-1].stem


def _yaml_str(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def cmd_version(a) -> None:
    root = project_root(a.project_dir)
    check_name(a.subproject, "sub-project")
    check_name(a.name, "version")
    if a.name == "base":
        sys.exit("ERROR: 'base' is reserved for the shared sub-project config.")
    cdir = root / "subprojects" / a.subproject / "configs"
    if not cdir.is_dir():
        sys.exit(f"ERROR: sub-project not found: {cdir.parent}")
    target = cdir / f"{a.name}.yaml"
    if target.exists():
        sys.exit(f"ERROR: {target} already exists - not overwriting.")
    parent = a.from_version or _newest_version(cdir)
    check_name(parent, "parent version")
    src = cdir / f"{parent}.yaml"
    if not src.exists():
        sys.exit(f"ERROR: parent version not found: {src}")

    header = [
        "version:",
        f"  name: {a.name}",
        f"  parent: {parent}",
        f"  hypothesis: {a.hypothesis or 'TODO'}",
        f"  description: {_yaml_str(a.description or 'TODO: what changed vs ' + parent)}",
        f"  created: {today()}",
    ]
    body, skipping = [], False
    for line in src.read_text(encoding="utf-8").splitlines():
        if line.startswith("version:"):
            skipping = True
            continue
        if skipping and (line.startswith((" ", "\t")) or not line.strip()):
            continue
        skipping = False
        body.append(line)
    comments = [l for l in body if l.startswith("#") and body.index(l) < 3]
    rest = [l for l in body if l not in comments]
    target.write_text("\n".join(comments + header + [""] + rest).rstrip("\n") + "\n",
                      encoding="utf-8")
    experiments_add(root, a.subproject,
                    f"| {a.name} | {parent} | {a.hypothesis or 'TODO'} | "
                    f"{(a.description or 'TODO').replace('|', '/')} | | | {today()} |")
    print(f"Created version: {target.relative_to(root).as_posix()} (copied from {parent})")
    print(f"Edit it to change only what differs, then run:\n"
          f"  python subprojects/{a.subproject}/scripts/01_run.py --version {a.name}")


def cmd_date(a) -> None:
    root = Path(a.project_dir).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"ERROR: project folder not found: {root}")
    created: list = []
    for parent in DATED_PARENTS:
        path = root / parent / a.date
        if a.subproject:
            check_name(a.subproject, "sub-project")
            path = path / a.subproject
        make_dir(path, created)
    report(root, created)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new")
    n.add_argument("name")
    n.add_argument("--base", default=default_base())
    n.add_argument("--template", default=str(TEMPLATE))
    n.add_argument("--date", default=today())
    n.set_defaults(func=cmd_new)

    s = sub.add_parser("subproject")
    s.add_argument("project_dir")
    s.add_argument("name")
    s.set_defaults(func=cmd_subproject, date=today())

    v = sub.add_parser("version")
    v.add_argument("project_dir")
    v.add_argument("subproject")
    v.add_argument("name")
    v.add_argument("--from", dest="from_version")
    v.add_argument("--description")
    v.add_argument("--hypothesis")
    v.set_defaults(func=cmd_version, date=today())

    d = sub.add_parser("date")
    d.add_argument("project_dir")
    d.add_argument("--subproject")
    d.add_argument("--date", default=today())
    d.set_defaults(func=cmd_date)

    a = p.parse_args()
    dt.date.fromisoformat(a.date)  # validate
    a.func(a)


if __name__ == "__main__":
    main()
