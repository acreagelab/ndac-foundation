"""Shared project helpers: config layering, paths, seeding, run folders, run manifests.

Typical use inside a sub-project script:

    cfg = load_config(subproject="et_mapping", version="v2_add_sentinel2")
    seed_everything(cfg["project"]["seed"])
    run_dir = new_run_dir("et_mapping", "v2_add_sentinel2")
    ...  # do the work
    write_metrics(run_dir, {"rmse": 0.41})
    write_run_manifest(run_dir, cfg, inputs=[resolve_path("data/raw/fields.gpkg")])
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import platform
import random
import re
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

import numpy as np
import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_\-]*")


# --------------------------------------------------------------------------- paths
def data_root() -> Path:
    """Shared-drive root from .env. Never hardcode drive paths in code or configs."""
    value = os.environ.get("DATA_ROOT", "").strip()
    if not value:
        raise RuntimeError("DATA_ROOT is not set: copy .env.example to .env and fill it in.")
    return Path(value)


def resolve_path(value: str | Path) -> Path:
    """Turn a config path into an absolute Path.

    - "${DATA_ROOT}/irrigation/fields.gpkg" -> under the shared drive (DATA_ROOT in .env)
    - "data/raw/fields.gpkg"                -> relative to the project root
    - absolute paths are returned unchanged (avoid them in configs)
    """
    text = str(value)
    if "${DATA_ROOT}" in text:
        text = text.replace("${DATA_ROOT}", str(data_root()))
    path = Path(text).expanduser()
    return path if path.is_absolute() else ROOT / path


def subproject_dir(subproject: str) -> Path:
    _check_name(subproject, "sub-project")
    path = ROOT / "subprojects" / subproject
    if not path.is_dir():
        raise FileNotFoundError(f"sub-project not found: {path}")
    return path


# -------------------------------------------------------------------------- config
def deep_merge(base: dict, override: dict) -> dict:
    """Return base updated by override; nested dicts merge, everything else replaces."""
    out = copy.deepcopy(base)
    for key, val in (override or {}).items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], val)
        else:
            out[key] = copy.deepcopy(val)
    return out


def _read_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream) or {}


def load_config(path: str | Path | None = None, *, subproject: str | None = None,
                version: str | None = None) -> dict:
    """Load layered config: configs/default.yaml -> sub-project base.yaml -> version yaml.

    load_config()                                         project defaults only
    load_config(subproject="et_mapping")                  + subprojects/et_mapping/configs/base.yaml
    load_config(subproject="et_mapping", version="v2_x")  + .../configs/v2_x.yaml
    load_config("configs/other.yaml")                     one explicit file, no layering

    The files used are listed, in order, under cfg["_sources"].
    """
    if path is not None:
        p = resolve_path(path)
        cfg = _read_yaml(p)
        cfg["_sources"] = [str(p)]
        return cfg

    layers = [ROOT / "configs" / "default.yaml"]
    if subproject:
        cdir = subproject_dir(subproject) / "configs"
        if (cdir / "base.yaml").exists():
            layers.append(cdir / "base.yaml")
        if version:
            _check_name(version, "version")
            vfile = cdir / f"{version}.yaml"
            if not vfile.exists():
                known = sorted(p.stem for p in cdir.glob("*.yaml") if p.stem != "base")
                raise FileNotFoundError(f"version '{version}' not found in {cdir}. Known: {known}")
            layers.append(vfile)
    elif version:
        raise ValueError("version given without subproject")

    cfg: dict = {}
    for layer in layers:
        cfg = deep_merge(cfg, _read_yaml(layer))
    cfg["_sources"] = [str(p) for p in layers]
    return cfg


# ------------------------------------------------------------------------- seeding
def seed_everything(seed: int, deterministic: bool = False) -> None:
    """Seed random, numpy and torch (+CUDA) together, never torch alone.

    deterministic=True also asks PyTorch for deterministic algorithms (slower; some ops
    only warn). PYTHONHASHSEED only affects *new* Python processes, so it is set here for
    subprocesses and workers; set it in the shell too if you need hash-stable ordering.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
    except ImportError:
        return
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if deterministic:
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
        torch.use_deterministic_algorithms(True, warn_only=True)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


# ----------------------------------------------------------------------------- git
def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                             text=True, check=False, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def git_state() -> dict:
    """Commit SHA plus whether tracked files had uncommitted changes.

    A result produced from uncommitted code cannot be reproduced from the SHA alone,
    so 'dirty' is recorded in the manifest and shown in run-folder names.
    """
    sha = _git("rev-parse", "HEAD")
    if sha is None:
        return {"sha": None, "dirty": None, "branch": None}
    status = _git("status", "--porcelain", "--untracked-files=no") or ""
    return {"sha": sha, "dirty": bool(status), "branch": _git("rev-parse", "--abbrev-ref", "HEAD")}


# ------------------------------------------------------------------------ run dirs
def _check_name(name: str, what: str) -> None:
    if not _NAME.fullmatch(name or ""):
        raise ValueError(f"invalid {what} name '{name}': use letters, digits, _ or -")


def new_run_dir(subproject: str, version: str, root: str | Path | None = None) -> Path:
    """Create a fresh, never-reused folder for one run:

        data/outputs/<subproject>/<version>/<YYYY-MM-DDTHHMMSS>_<sha7>[-dirty]/

    Re-running the same version makes a new folder, so runs never overwrite each other.
    """
    _check_name(subproject, "sub-project")
    _check_name(version, "version")
    base = resolve_path(root) if root else ROOT / "data" / "outputs"
    git = git_state()
    tag = (git["sha"] or "nogit")[:7] + ("-dirty" if git["dirty"] else "")
    stamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    parent = base / subproject / version
    parent.mkdir(parents=True, exist_ok=True)
    for n in range(100):
        name = f"{stamp}_{tag}" + (f"_{n}" if n else "")
        try:
            (parent / name).mkdir()
            return parent / name
        except FileExistsError:
            continue
    raise RuntimeError(f"could not create a unique run folder under {parent}")


# ---------------------------------------------------------------------- manifests
def sha256_file(path: str | Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def _describe_input(path: Path) -> dict:
    if path.is_file():
        return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
    if path.is_dir():
        files = sorted(p for p in path.rglob("*") if p.is_file())
        h = hashlib.sha256()
        for f in files:
            h.update(f.relative_to(path).as_posix().encode())
            h.update(sha256_file(f).encode())
        return {"path": str(path), "files": len(files), "sha256_tree": h.hexdigest()}
    return {"path": str(path), "missing": True}


def _requirement_versions() -> dict:
    """Installed versions of the packages declared in requirements.txt."""
    req = ROOT / "requirements.txt"
    names = []
    if req.exists():
        for line in req.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line and not line.startswith("-"):
                names.append(re.split(r"[=<>!~\[; ]", line, maxsplit=1)[0])
    found = {}
    for name in names:
        try:
            found[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            found[name] = "not installed"
    return found


def write_run_manifest(
    out_dir: str | Path,
    config: dict | str | Path | None = None,
    seed: int | None = None,
    inputs: list[str | Path] | None = None,
    extra: dict | None = None,
    config_path: str | Path | None = None,  # backwards compatibility
) -> Path:
    """Write run_manifest.json (+ config_resolved.yaml) next to metrics/model outputs.

    Records: time, git SHA + dirty flag, Python/platform, package versions, the merged
    config and SHA-256 of every config layer, and SHA-256 of each input file/folder.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if config is None and config_path is not None:
        config = config_path
    if config is None:
        config = load_config()
    elif not isinstance(config, dict):
        config = load_config(config)

    sources = [Path(s) for s in config.get("_sources", [])]
    clean_cfg = {k: v for k, v in config.items() if k != "_sources"}
    if seed is None:
        seed = (clean_cfg.get("project") or {}).get("seed")

    manifest = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git": git_state(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "packages": _requirement_versions(),
        "seed": seed,
        "config_layers": [{"path": str(s), "sha256": sha256_file(s)} for s in sources if s.exists()],
        "inputs": [_describe_input(resolve_path(p)) for p in (inputs or [])],
        "command": " ".join(sys.argv),
    }
    if extra:
        manifest.update(extra)
    if manifest["git"]["dirty"]:
        print("WARNING: run made with uncommitted changes; commit before reporting results.",
              file=sys.stderr)

    (out_dir / "config_resolved.yaml").write_text(
        yaml.safe_dump(clean_cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
    path = out_dir / "run_manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


def write_metrics(out_dir: str | Path, metrics: dict) -> Path:
    """Write metrics.json; scripts/compare_runs.py collects these across runs."""
    path = Path(out_dir) / "metrics.json"
    path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return path
