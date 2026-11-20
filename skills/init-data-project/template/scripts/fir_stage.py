"""Copy a version's ${DATA_ROOT} inputs to fast node-local disk (used by job_template.sbatch).

    python scripts/fir_stage.py <subproject> <version> <dest_dir>

Keeps each input's path relative to DATA_ROOT, so after `export DATA_ROOT=<dest_dir>` the
run reads the local copies with no code change. Project-relative inputs (data/raw/...) are
left in place. Prints what it copied.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src" / "common.py").exists())
sys.path.insert(0, str(ROOT))

from src.common import data_root, load_config  # noqa: E402

PREFIX = "${DATA_ROOT}"


def stage(subproject: str, version: str, dest: Path) -> list[str]:
    cfg = load_config(subproject=subproject, version=version)
    copied = []
    for name, value in (cfg.get("inputs") or {}).items():
        text = str(value)
        if not text.startswith(PREFIX):
            print(f"  in place  {name}: {text}")
            continue
        rel = text[len(PREFIX):].lstrip("/\\")
        src, dst = data_root() / rel, dest / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        elif src.is_file():
            shutil.copy2(src, dst)
        else:
            raise FileNotFoundError(f"input '{name}' not found: {src}")
        copied.append(rel)
        print(f"  staged    {name}: {rel}")
    return copied


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    stage(sys.argv[1], sys.argv[2], Path(sys.argv[3]))
