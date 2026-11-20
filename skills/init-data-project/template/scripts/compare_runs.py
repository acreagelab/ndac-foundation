"""Collect metrics.json from every run of a sub-project into one comparison table.

    python scripts/compare_runs.py et_mapping
    python scripts/compare_runs.py et_mapping --sort rmse --save

Reads data/outputs/<subproject>/<version>/<run>/metrics.json (+ run_manifest.json) and
prints one row per run. --save writes report/<today>/<subproject>/run_comparison.csv.
Use the table to fill the "Key metric result" and "Decision" columns in docs/experiments.md.
Runs flagged dirty were made from uncommitted code: re-run before reporting them.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src" / "common.py").exists())
sys.path.insert(0, str(ROOT))

from src.common import ROOT as PROJECT_ROOT  # noqa: E402


def collect(subproject: str, outputs: Path) -> list[dict]:
    rows = []
    for metrics_file in sorted((outputs / subproject).glob("*/*/metrics.json")):
        run_dir = metrics_file.parent
        row = {"version": run_dir.parent.name, "run": run_dir.name}
        manifest = run_dir / "run_manifest.json"
        if manifest.exists():
            m = json.loads(manifest.read_text(encoding="utf-8"))
            git = m.get("git") or {}
            row["git_sha"] = (git.get("sha") or "")[:7]
            row["dirty"] = git.get("dirty")
            row["seed"] = m.get("seed")
            if m.get("slurm"):
                row["job"] = m["slurm"].get("job_id")
        metrics = json.loads(metrics_file.read_text(encoding="utf-8"))
        for key, val in metrics.items():
            row[key] = val if not isinstance(val, (dict, list)) else json.dumps(val)
        rows.append(row)
    return rows


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("subproject")
    p.add_argument("--sort", help="metric to sort by (ascending)")
    p.add_argument("--desc", action="store_true", help="sort descending")
    p.add_argument("--save", action="store_true", help="write report/<today>/<subproject>/run_comparison.csv")
    p.add_argument("--root", action="append",
                   help="extra run root to include (repeatable), e.g. /scratch/$USER/<project>/data/outputs")
    a = p.parse_args()

    rows = collect(a.subproject, PROJECT_ROOT / "data" / "outputs")
    for extra in a.root or []:
        rows += collect(a.subproject, Path(extra))
    if not rows:
        sys.exit(f"No runs with metrics.json under data/outputs/{a.subproject}/")
    cols: list[str] = []
    for r in rows:
        cols += [k for k in r if k not in cols]
    if a.sort:
        rows.sort(key=lambda r: (r.get(a.sort) is None, r.get(a.sort)), reverse=a.desc)

    widths = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in cols}
    print("  ".join(c.ljust(widths[c]) for c in cols))
    print("  ".join("-" * widths[c] for c in cols))
    for r in rows:
        print("  ".join(str(r.get(c, "")).ljust(widths[c]) for c in cols))
    if any(r.get("dirty") for r in rows):
        print("\nNOTE: dirty=True runs used uncommitted code; re-run from a commit before reporting.")

    if a.save:
        out = PROJECT_ROOT / "report" / dt.date.today().isoformat() / a.subproject / "run_comparison.csv"
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
        print(f"\nSaved: {out.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
