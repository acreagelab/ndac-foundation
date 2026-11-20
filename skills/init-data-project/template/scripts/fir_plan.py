"""Plan where and how to run a sub-project version on Fir: node, resources, storage.

    python scripts/fir_plan.py et_mapping v2_add_s2          # human-readable plan + sbatch command
    python scripts/fir_plan.py et_mapping v2_add_s2 --json   # machine-readable

It looks at:
  - the version's inputs (size, file count) from its config,
  - how long and how much memory earlier runs ACTUALLY used (run manifests -> sacct),
  - the cluster's time limit (sinfo), and configs/fir.yaml (account, storage, thresholds),
  - optional per-version `resources:` overrides in the version config,
and recommends: login node / interactive / batch job, --time, --mem, --cpus, GPUs,
whether to stage inputs to the node's local disk, and where outputs should go.

It never submits anything. Claude shows the plan and submits only after you agree.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src" / "common.py").exists())
sys.path.insert(0, str(ROOT))

from src.common import load_config, resolve_path  # noqa: E402

GB = 1024 ** 3


# ----------------------------------------------------------------------- parsing
def parse_slurm_time(text: str | None) -> int | None:
    """'1-02:03:04', '02:03:04', '03:04', '45' (minutes) -> seconds. UNLIMITED/blank -> None."""
    if not text or text.strip().upper() in {"UNLIMITED", "INVALID", "NONE", "PARTITION_LIMIT"}:
        return None
    text = text.strip()
    days = 0
    if "-" in text:
        d, text = text.split("-", 1)
        days = int(d)
    parts = [float(p) for p in text.split(":")]
    if len(parts) == 1:          # minutes
        h, m, s = 0, parts[0], 0
    elif len(parts) == 2:        # mm:ss
        h, m, s = 0, parts[0], parts[1]
    else:
        h, m, s = parts[-3:]
    return int(days * 86400 + h * 3600 + m * 60 + s)


def format_slurm_time(seconds: int) -> str:
    days, rem = divmod(int(seconds), 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    return (f"{days}-" if days else "") + f"{h:02d}:{m:02d}:{s:02d}"


def parse_mem(text: str | None) -> int | None:
    """sacct memory ('123456K', '2.5G', '800M') -> bytes."""
    if not text:
        return None
    m = re.fullmatch(r"([\d.]+)([KMGT]?)", text.strip().upper())
    if not m:
        return None
    mult = {"": 1, "K": 1024, "M": 1024 ** 2, "G": GB, "T": 1024 ** 4}[m.group(2)]
    return int(float(m.group(1)) * mult)


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{int(n)} B"
        n /= 1024
    return f"{n:.1f} TB"


# ------------------------------------------------------------------- measuring
def measure_inputs(cfg: dict) -> list[dict]:
    """Size and file count of every path under the config's `inputs:`."""
    out = []
    for name, value in (cfg.get("inputs") or {}).items():
        item = {"name": name, "config": str(value), "on_data_root": "${DATA_ROOT}" in str(value)}
        try:
            path = resolve_path(value)
        except RuntimeError as err:          # DATA_ROOT not set
            item.update(exists=False, error=str(err))
            out.append(item)
            continue
        item["path"] = str(path)
        if path.is_file():
            item.update(exists=True, bytes=path.stat().st_size, files=1)
        elif path.is_dir():
            files = [p for p in path.rglob("*") if p.is_file()]
            item.update(exists=True, bytes=sum(p.stat().st_size for p in files), files=len(files))
        else:
            item.update(exists=False)
        out.append(item)
    return out


def dir_bytes(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def run_roots(fir: dict) -> list[Path]:
    roots = [ROOT / "data" / "outputs"]
    scratch = (fir.get("storage") or {}).get("scratch")
    if scratch and "TODO" not in scratch:
        roots.append(Path(os.path.expandvars(scratch)) / "data" / "outputs")
    return roots


def past_runs(subproject: str, version: str, roots: list[Path]) -> list[dict]:
    """Earlier runs of this sub-project (all versions) from their manifests."""
    runs = []
    for root in roots:
        for manifest in sorted((root / subproject).glob("*/*/run_manifest.json")):
            try:
                m = json.loads(manifest.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            runs.append({"version": manifest.parent.parent.name, "dir": str(manifest.parent),
                         "job_id": (m.get("slurm") or {}).get("job_id"),
                         "output_bytes": dir_bytes(manifest.parent)})
    return runs


def sacct_stats(job_ids: list[str]) -> dict[str, dict]:
    """Real elapsed time and peak memory per job, from Slurm accounting (empty off-cluster)."""
    if not job_ids or not shutil.which("sacct"):
        return {}
    cmd = ["sacct", "-n", "-P", "-j", ",".join(job_ids),
           "--format=JobID,State,Elapsed,MaxRSS,AllocCPUS,ReqMem"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return {}
    return parse_sacct(out)


def parse_sacct(out: str) -> dict[str, dict]:
    """Parse `sacct -n -P --format=JobID,State,Elapsed,MaxRSS,AllocCPUS,ReqMem` output.

    The job line carries the final state; its steps (.batch, .extern, .0) carry MaxRSS.
    """
    stats: dict[str, dict] = {}
    for line in out.splitlines():
        job, state, elapsed, maxrss, cpus, _ = (line.split("|") + [""] * 6)[:6]
        base = job.split(".")[0]
        s = stats.setdefault(base, {"state": None, "elapsed": 0, "maxrss": 0, "cpus": None})
        if job == base:
            s["state"], s["cpus"] = state, cpus
        s["elapsed"] = max(s["elapsed"], parse_slurm_time(elapsed) or 0)
        s["maxrss"] = max(s["maxrss"], parse_mem(maxrss) or 0)
    return stats


def cluster_max_walltime(fir: dict) -> int | None:
    if fir.get("max_walltime"):
        return parse_slurm_time(str(fir["max_walltime"]))
    if not shutil.which("sinfo"):
        return None
    try:
        out = subprocess.run(["sinfo", "-h", "-o", "%l"], capture_output=True, text=True,
                             timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    limits = [parse_slurm_time(x) for x in out.split()]
    limits = [x for x in limits if x]
    return max(limits) if limits else None


# --------------------------------------------------------------------- planning
def make_plan(subproject: str, version: str, cfg: dict, fir: dict, inputs: list[dict],
              history: list[dict], stats: dict[str, dict], max_wall: int | None) -> dict:
    d = fir.get("defaults") or {}
    margin = fir.get("margins") or {}
    th = fir.get("thresholds") or {}
    res = cfg.get("resources") or {}
    notes: list[str] = []
    warnings: list[str] = []

    in_bytes = sum(i.get("bytes", 0) for i in inputs)
    in_files = sum(i.get("files", 0) for i in inputs)
    missing = [i["name"] for i in inputs if not i.get("exists")]
    if missing:
        warnings.append(f"inputs not found here: {', '.join(missing)} (sizes unknown; check paths/DATA_ROOT)")

    # history: same version first, else any version of the sub-project
    same = [h for h in history if h["version"] == version and h.get("job_id") in stats]
    pool = same or [h for h in history if h.get("job_id") in stats]
    measured = [stats[h["job_id"]] for h in pool]
    ok = [s for s in measured if (s["state"] or "").startswith("COMPLETED")]
    failed = [s for s in measured if s["state"] and not s["state"].startswith("COMPLETED")]
    basis = ok or measured

    if basis:
        t_used = max(s["elapsed"] for s in basis)
        m_used = max(s["maxrss"] for s in basis)
        time_s = max(15 * 60, math.ceil(t_used * float(margin.get("time", 1.5)) / 900) * 900)
        mem_gb = max(2, math.ceil(m_used * float(margin.get("mem", 1.3)) / GB))
        src = "this version" if same else "other versions of this sub-project"
        notes.append(f"based on {len(basis)} earlier run(s) of {src}: longest {format_slurm_time(t_used)}, "
                     f"peak memory {human(m_used)}")
        if any((s["state"] or "").startswith(("TIMEOUT", "OUT_OF_MEMORY")) for s in failed):
            warnings.append("an earlier run hit its time or memory limit; the request below adds margin, "
                            "but check whether the job needs splitting or checkpointing")
        first_run = False
    else:
        time_s = parse_slurm_time(str(d.get("time", "01:00:00")))
        mem_gb = int(d.get("mem_gb", 8))
        first_run = True
        notes.append("no measured history yet: these are starting values. Make the first run a SMALL "
                     "test (subset of data), then plan again from its real numbers")

    cpus = int(res.get("cpus", d.get("cpus", 4)))
    gpus = int(res.get("gpus", d.get("gpus", 0)))
    if "time" in res:
        time_s = parse_slurm_time(str(res["time"]))
    if "mem_gb" in res:
        mem_gb = int(res["mem_gb"])

    if max_wall and time_s > max_wall:
        warnings.append(f"needs {format_slurm_time(time_s)} but the cluster limit is "
                        f"{format_slurm_time(max_wall)}: split the work (job array over years/tiles) "
                        f"or add checkpointing so the job can resume")
        time_s = max_wall

    stage = in_bytes >= float(th.get("stage_input_gb", 1)) * GB or in_files >= int(th.get("stage_many_files", 1000))
    if stage:
        notes.append(f"inputs {human(in_bytes)} in {in_files} file(s): copy to the node's local disk "
                     f"first (STAGE=1); results are copied back when the job ends")
        if not all(i.get("on_data_root") for i in inputs if i.get("exists")):
            warnings.append("only ${DATA_ROOT}/... inputs are staged; project-relative inputs are read in place")
    if in_files >= int(th.get("stage_many_files", 1000)):
        notes.append("many small files: consider bundling them (tar/zip) - much faster to copy and read")

    out_hist = [h["output_bytes"] for h in history if h["version"] == version] or \
               [h["output_bytes"] for h in history]
    big_out = bool(out_hist) and max(out_hist) >= float(th.get("scratch_output_gb", 50)) * GB
    storage = fir.get("storage") or {}
    if big_out and storage.get("scratch") and "TODO" not in storage["scratch"]:
        output_root = os.path.expandvars(storage["scratch"]) + "/data/outputs"
        warnings.append(f"earlier runs wrote up to {human(max(out_hist))}: outputs go to scratch "
                        f"({output_root}), which is NOT backed up and is purged - copy final results "
                        f"to /project when done")
    else:
        output_root = None   # job default: <project>/data/outputs

    tiny = (not first_run and time_s <= int(th.get("login_max_minutes", 10)) * 60 * 1.5
            and mem_gb <= int(th.get("login_max_mem_gb", 4)) and gpus == 0 and not stage)
    where = "login node (quick test only)" if tiny else "batch job (sbatch)"
    if first_run:
        where = "batch job (sbatch) - small test run first"

    account = fir.get("account", "def-TODO")
    if "TODO" in str(account):
        warnings.append("set fir.account in configs/fir.yaml (your PI's allocation, e.g. def-smith)")
    export = f"ALL,SUB={subproject},VER={version}" + (",STAGE=1" if stage else "") + \
             (f",OUTPUT_ROOT={output_root}" if output_root else "")
    cmd = ["sbatch", f"--account={account}", f"--time={format_slurm_time(time_s)}",
           f"--mem={mem_gb}G", f"--cpus-per-task={cpus}"]
    if gpus:
        cmd.append(f"--gpus-per-node={gpus}")
    cmd += [f"--job-name={subproject}-{version}"[:60], f"--export={export}", "scripts/job_template.sbatch"]

    return {"subproject": subproject, "version": version, "where": where,
            "time": format_slurm_time(time_s), "mem_gb": mem_gb, "cpus": cpus, "gpus": gpus,
            "stage": stage, "output_root": output_root or "data/outputs (in the project)",
            "inputs": {"bytes": in_bytes, "files": in_files, "missing": missing},
            "cluster_max_walltime": format_slurm_time(max_wall) if max_wall else "unknown (not on Fir?)",
            "notes": notes, "warnings": warnings, "sbatch": " ".join(cmd)}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("subproject")
    p.add_argument("version")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    cfg = load_config(subproject=a.subproject, version=a.version)
    fir_file = ROOT / "configs" / "fir.yaml"
    fir = (load_config(fir_file).get("fir") or {}) if fir_file.exists() else {}
    inputs = measure_inputs(cfg)
    history = past_runs(a.subproject, a.version, run_roots(fir))
    stats = sacct_stats([h["job_id"] for h in history if h.get("job_id")])
    plan = make_plan(a.subproject, a.version, cfg, fir, inputs, history, stats, cluster_max_walltime(fir))

    if a.json:
        print(json.dumps(plan, indent=2))
        return
    print(f"Plan for {a.subproject} / {a.version}")
    print(f"  Inputs:   {human(plan['inputs']['bytes'])} in {plan['inputs']['files']} file(s)")
    print(f"  Run on:   {plan['where']}")
    print(f"  Request:  time {plan['time']}, memory {plan['mem_gb']} GB, {plan['cpus']} CPUs"
          + (f", {plan['gpus']} GPU(s)" if plan["gpus"] else ""))
    print(f"  Stage inputs to local disk: {'yes' if plan['stage'] else 'no'}")
    print(f"  Outputs:  {plan['output_root']}")
    print(f"  Cluster time limit: {plan['cluster_max_walltime']}")
    for n in plan["notes"]:
        print(f"  - {n}")
    for w in plan["warnings"]:
        print(f"  ! {w}")
    print("\nSubmit (commit your code first):\n  " + plan["sbatch"])


if __name__ == "__main__":
    main()
