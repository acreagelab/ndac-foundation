"""Tests for scripts/fir_plan.py: parsing, sizing from history, staging and storage choices."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("fir_plan", ROOT / "scripts" / "fir_plan.py")
fp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fp)

GB = 1024 ** 3
FIR = {"account": "def-test", "storage": {"scratch": "/scratch/u/proj"},
       "defaults": {"time": "01:00:00", "mem_gb": 8, "cpus": 4, "gpus": 0},
       "margins": {"time": 1.5, "mem": 1.3},
       "thresholds": {"stage_input_gb": 1, "stage_many_files": 1000, "scratch_output_gb": 50,
                      "login_max_minutes": 10, "login_max_mem_gb": 4}}


@pytest.mark.parametrize("text,seconds", [("1-02:03:04", 93784), ("02:03:04", 7384),
                                          ("03:04", 184), ("45", 2700), ("UNLIMITED", None)])
def test_parse_slurm_time(text, seconds):
    assert fp.parse_slurm_time(text) == seconds


def test_format_roundtrip():
    assert fp.format_slurm_time(93784) == "1-02:03:04"
    assert fp.parse_slurm_time(fp.format_slurm_time(5400)) == 5400


@pytest.mark.parametrize("text,b", [("1024K", 1024 ** 2), ("2G", 2 * GB), ("1.5M", int(1.5 * 1024 ** 2)), ("", None)])
def test_parse_mem(text, b):
    assert fp.parse_mem(text) == b


def plan(inputs=None, history=None, stats=None, cfg=None, max_wall=None, fir=FIR):
    return fp.make_plan("sp", "v2", cfg or {}, fir, inputs or [], history or [], stats or {}, max_wall)


def test_first_run_uses_defaults_and_says_test_first():
    p = plan()
    assert p["time"] == "01:00:00" and p["mem_gb"] == 8 and p["cpus"] == 4
    assert "small test" in p["where"]
    assert "--account=def-test" in p["sbatch"] and "SUB=sp,VER=v2" in p["sbatch"]


def test_sizes_from_history_with_margin():
    hist = [{"version": "v2", "job_id": "11", "output_bytes": 0}]
    stats = {"11": {"state": "COMPLETED", "elapsed": 40 * 60, "maxrss": 10 * GB, "cpus": "4"}}
    p = plan(history=hist, stats=stats)
    assert p["time"] == "01:00:00"          # 40 min x 1.5 = 60 min, rounded to 15 min
    assert p["mem_gb"] == 13                # 10 GB x 1.3
    assert any("earlier run" in n for n in p["notes"])


def test_timeout_history_warns():
    hist = [{"version": "v2", "job_id": "12", "output_bytes": 0}]
    stats = {"12": {"state": "TIMEOUT", "elapsed": 3600, "maxrss": GB, "cpus": "4"}}
    assert any("time or memory limit" in w for w in plan(history=hist, stats=stats)["warnings"])


def test_big_inputs_are_staged():
    inputs = [{"name": "img", "exists": True, "bytes": 5 * GB, "files": 3, "on_data_root": True}]
    p = plan(inputs=inputs)
    assert p["stage"] and "STAGE=1" in p["sbatch"]


def test_many_small_files_staged_and_bundling_suggested():
    inputs = [{"name": "tiles", "exists": True, "bytes": 10 ** 6, "files": 5000, "on_data_root": True}]
    p = plan(inputs=inputs)
    assert p["stage"] and any("bundling" in n for n in p["notes"])


def test_big_outputs_go_to_scratch_with_warning():
    hist = [{"version": "v2", "job_id": None, "output_bytes": 80 * GB}]
    p = plan(history=hist)
    assert p["output_root"].startswith("/scratch/u/proj") and "OUTPUT_ROOT=" in p["sbatch"]
    assert any("NOT backed up" in w for w in p["warnings"])


def test_time_capped_at_cluster_limit_with_split_advice():
    hist = [{"version": "v2", "job_id": "13", "output_bytes": 0}]
    stats = {"13": {"state": "COMPLETED", "elapsed": 6 * 86400, "maxrss": GB, "cpus": "4"}}
    p = plan(history=hist, stats=stats, max_wall=7 * 86400)
    assert p["time"] == "7-00:00:00" and any("split" in w for w in p["warnings"])


def test_version_resources_override():
    p = plan(cfg={"resources": {"cpus": 16, "gpus": 1, "mem_gb": 64, "time": "12:00:00"}})
    assert (p["cpus"], p["gpus"], p["mem_gb"], p["time"]) == (16, 1, 64, "12:00:00")
    assert "--gpus-per-node=1" in p["sbatch"]


def test_tiny_measured_job_may_run_on_login_node():
    hist = [{"version": "v2", "job_id": "14", "output_bytes": 0}]
    stats = {"14": {"state": "COMPLETED", "elapsed": 60, "maxrss": GB // 2, "cpus": "1"}}
    p = plan(history=hist, stats=stats, fir={**FIR, "defaults": {**FIR["defaults"], "cpus": 1}})
    assert p["where"].startswith("login node")


def test_placeholder_account_warns():
    p = plan(fir={**FIR, "account": "def-TODO"})
    assert any("fir.account" in w for w in p["warnings"])


def test_parse_sacct_takes_state_from_job_and_memory_from_steps():
    out = ("777|COMPLETED|00:40:00||4|8G\n"
           "777.batch|COMPLETED|00:40:00|10485760K|4|\n"
           "777.extern|COMPLETED|00:40:01|1024K|4|\n"
           "778|TIMEOUT|01:00:00||4|8G\n"
           "778.batch|CANCELLED|01:00:03|2G|4|\n")
    s = fp.parse_sacct(out)
    assert s["777"]["state"] == "COMPLETED" and s["777"]["elapsed"] == 2401
    assert s["777"]["maxrss"] == 10 * GB
    assert s["778"]["state"] == "TIMEOUT" and s["778"]["maxrss"] == 2 * GB


def test_plan_from_parsed_sacct():
    stats = fp.parse_sacct("777|COMPLETED|00:40:00||4|8G\n777.batch|COMPLETED|00:40:00|10485760K|4|\n")
    p = plan(history=[{"version": "v2", "job_id": "777", "output_bytes": 0}], stats=stats)
    assert p["time"] == "01:00:00" and p["mem_gb"] == 13   # 40:00 x 1.5 = 60:00 exactly; 10 GB x 1.3


def test_measure_inputs(tmp_path, monkeypatch):
    (tmp_path / "a.bin").write_bytes(b"x" * 100)
    (tmp_path / "d").mkdir()
    (tmp_path / "d" / "b.bin").write_bytes(b"y" * 50)
    monkeypatch.setenv("DATA_ROOT", str(tmp_path))
    items = {i["name"]: i for i in fp.measure_inputs(
        {"inputs": {"a": "${DATA_ROOT}/a.bin", "d": "${DATA_ROOT}/d", "gone": "${DATA_ROOT}/nope"}})}
    assert items["a"]["bytes"] == 100 and items["d"]["files"] == 1 and not items["gone"]["exists"]
