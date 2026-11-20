"""Shared project helpers: config, DATA_ROOT, seeding, run manifests."""
from __future__ import annotations

import hashlib
import json
import os
import random
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def data_root() -> Path:
    """Shared-drive root from .env — never hardcode Z:\\ paths in code or configs."""
    value = os.environ.get("DATA_ROOT", "").strip()
    if not value:
        raise RuntimeError("DATA_ROOT is not set — copy .env.example to .env and fill it in.")
    return Path(value)


def load_config(path: str | Path | None = None) -> dict:
    path = Path(path) if path else ROOT / "configs" / "default.yaml"
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def seed_everything(seed: int) -> None:
    """Seed random, numpy, and torch (+CUDA) together — never torch alone."""
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def write_run_manifest(
    out_dir: str | Path,
    config_path: str | Path | None = None,
    seed: int | None = None,
    extra: dict | None = None,
) -> Path:
    """Write run provenance next to metrics/models so results trace back to code + config."""
    config_path = Path(config_path) if config_path else ROOT / "configs" / "default.yaml"
    git = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=False,
    )
    manifest = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_sha": git.stdout.strip() if git.returncode == 0 else "not-a-repo",
        "config": str(config_path),
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "seed": seed,
    }
    if extra:
        manifest.update(extra)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "run_manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path
