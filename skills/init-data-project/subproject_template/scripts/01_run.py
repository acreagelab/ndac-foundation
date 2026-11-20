"""<SUBPROJECT>: main run script. Replace the TODO block with the real analysis.

    python subprojects/<SUBPROJECT>/scripts/01_run.py --version v1_baseline

Pattern every run follows: layered config -> seed -> fresh run folder -> work ->
metrics.json + run_manifest.json. Keep reported numbers coming from runs like this one.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src" / "common.py").exists())
sys.path.insert(0, str(ROOT))

from src.common import (load_config, new_run_dir, resolve_path, seed_everything,  # noqa: E402
                        write_metrics, write_run_manifest)

SUBPROJECT = Path(__file__).resolve().parents[1].name


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--version", required=True, help="config name in configs/, e.g. v1_baseline")
    a = p.parse_args()

    cfg = load_config(subproject=SUBPROJECT, version=a.version)
    seed_everything(cfg["project"]["seed"])
    run_dir = new_run_dir(SUBPROJECT, a.version)
    inputs = [resolve_path(v) for v in (cfg.get("inputs") or {}).values()]
    try:
        shown = run_dir.relative_to(ROOT)
    except ValueError:          # run folder outside the project (node-local disk or /scratch on Fir)
        shown = run_dir
    print(f"Run folder: {shown}")

    # ---- TODO: the analysis. Read inputs, write outputs into run_dir. ----------------
    metrics: dict = {}  # e.g. {"rmse": 0.41, "bias": -0.02, "n_fields": 112}
    # ------------------------------------------------------------------------------------

    write_metrics(run_dir, metrics)
    write_run_manifest(run_dir, cfg, inputs=inputs)
    print("Done. Compare runs: python scripts/compare_runs.py " + SUBPROJECT)


if __name__ == "__main__":
    main()
