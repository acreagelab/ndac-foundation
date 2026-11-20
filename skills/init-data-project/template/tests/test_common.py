"""Tests for src/common.py: config layering, paths, run folders, manifests, seeding."""
import json

import numpy as np
import pytest
import yaml

from src import common


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A throwaway project root with default + sub-project configs."""
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "default.yaml").write_text(
        "project: {name: t, seed: 7, crs_analysis: 'EPSG:32613'}\nparams: {a: 1, b: {x: 1, y: 2}}\n",
        encoding="utf-8")
    cdir = tmp_path / "subprojects" / "sp" / "configs"
    cdir.mkdir(parents=True)
    (cdir / "base.yaml").write_text("params: {b: {y: 20}}\n", encoding="utf-8")
    (cdir / "v1.yaml").write_text("version: {name: v1}\nparams: {a: 100}\n", encoding="utf-8")
    monkeypatch.setattr(common, "ROOT", tmp_path)
    monkeypatch.delenv("RUNS_ROOT", raising=False)   # set inside Fir jobs
    return tmp_path


def test_deep_merge_nested_and_does_not_mutate():
    base = {"a": 1, "b": {"x": 1, "y": 2}}
    out = common.deep_merge(base, {"b": {"y": 3}, "c": 4})
    assert out == {"a": 1, "b": {"x": 1, "y": 3}, "c": 4}
    assert base == {"a": 1, "b": {"x": 1, "y": 2}}


def test_load_config_layers_in_order(project):
    cfg = common.load_config(subproject="sp", version="v1")
    assert cfg["params"] == {"a": 100, "b": {"x": 1, "y": 20}}
    assert cfg["project"]["seed"] == 7
    assert [p.split("\\")[-1].split("/")[-1] for p in cfg["_sources"]] == \
        ["default.yaml", "base.yaml", "v1.yaml"]


def test_load_config_unknown_version_lists_known(project):
    with pytest.raises(FileNotFoundError, match="v1"):
        common.load_config(subproject="sp", version="nope")


def test_invalid_names_rejected(project):
    with pytest.raises(ValueError):
        common.new_run_dir("../escape", "v1")
    with pytest.raises(ValueError):
        common.load_config(subproject="sp", version="v1/../../x")


def test_resolve_path(project, monkeypatch):
    monkeypatch.setenv("DATA_ROOT", str(project / "shared"))
    assert common.resolve_path("${DATA_ROOT}/a/b.gpkg") == project / "shared" / "a" / "b.gpkg"
    assert common.resolve_path("data/raw/x.csv") == project / "data" / "raw" / "x.csv"


def test_new_run_dir_never_reuses_a_folder(project):
    first = common.new_run_dir("sp", "v1")
    second = common.new_run_dir("sp", "v1")
    assert first != second
    assert first.is_dir() and second.is_dir()
    assert first.parent == project / "data" / "outputs" / "sp" / "v1"


def test_manifest_records_config_inputs_and_git(project):
    cfg = common.load_config(subproject="sp", version="v1")
    data = project / "input.txt"
    data.write_text("hello", encoding="utf-8")
    run = common.new_run_dir("sp", "v1")
    common.write_metrics(run, {"rmse": 0.5})
    path = common.write_run_manifest(run, cfg, inputs=[data])

    m = json.loads(path.read_text(encoding="utf-8"))
    assert m["seed"] == 7
    assert {"sha", "dirty", "branch"} <= set(m["git"])
    assert len(m["config_layers"]) == 3
    assert m["inputs"][0]["sha256"] == common.sha256_file(data)
    resolved = yaml.safe_load((run / "config_resolved.yaml").read_text(encoding="utf-8"))
    assert "_sources" not in resolved and resolved["params"]["a"] == 100
    assert json.loads((run / "metrics.json").read_text(encoding="utf-8")) == {"rmse": 0.5}


def test_runs_root_env_redirects_run_folders(project, tmp_path, monkeypatch):
    monkeypatch.setenv("RUNS_ROOT", str(tmp_path / "fast"))
    run = common.new_run_dir("sp", "v1")
    assert run.parent == tmp_path / "fast" / "sp" / "v1"


def test_manifest_records_slurm_job(project, monkeypatch):
    monkeypatch.setenv("SLURM_JOB_ID", "4242")
    monkeypatch.setenv("SLURM_CPUS_PER_TASK", "8")
    monkeypatch.setenv("STAGE", "1")
    run = common.new_run_dir("sp", "v1")
    m = json.loads(common.write_run_manifest(run, common.load_config(subproject="sp", version="v1"))
                   .read_text(encoding="utf-8"))
    assert m["slurm"]["job_id"] == "4242" and m["slurm"]["staged_to_local_disk"] is True


def test_seed_everything_is_reproducible():
    common.seed_everything(123)
    a = np.random.rand(3)
    common.seed_everything(123)
    assert np.array_equal(a, np.random.rand(3))
