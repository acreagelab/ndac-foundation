"""Smoke test: layout, config, and .gitignore protections are intact."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_layout():
    for d in ("data/raw", "data/interim", "data/processed", "data/outputs",
              "configs", "src", "scripts", "logs", "docs", "docs/research/diagrams",
              "tests", "subprojects", "notebooks"):
        assert (ROOT / d).is_dir(), f"missing directory: {d}"
    for f in ("CLAUDE.md", ".gitignore", ".env.example", "requirements.txt",
              "environment.yml", "CITATION.cff", "docs/ACKNOWLEDGEMENT.md",
              "docs/data_sources.md", "docs/experiments.md",
              "docs/research/objectives.md", "docs/research/plan.md",
              "docs/research/diagrams/pipeline.mmd", ".githooks/pre-push",
              "init_project.sh", "scripts/setup_fir_env.sh", "scripts/job_template.sbatch",
              "configs/fir.yaml", "scripts/fir_plan.py", "scripts/fir_stage.py"):
        assert (ROOT / f).is_file(), f"missing file: {f}"


def test_config_loads_and_crs_is_metric():
    cfg = yaml.safe_load((ROOT / "configs" / "default.yaml").read_text(encoding="utf-8"))
    assert isinstance(cfg["project"]["seed"], int)
    assert cfg["project"]["crs_analysis"].upper() != "EPSG:3857", \
        "Web Mercator is display-only: use a metric CRS for analysis"


def test_gitignore_covers_credentials_data_and_reports():
    gi = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    for pattern in (".env", ".ee_auth/", ".ee_accounts/", "**/credentials",
                    "*service-account*.json", "data/**", "report/**", "*.csv",
                    "*.xlsx", "*.shp", "*.dbf", "*.geojson", "*.gpkg", "*.tif",
                    "*.pkl", "*.pt", "*.npy"):
        assert pattern in gi, f".gitignore missing protection: {pattern}"


def test_ndac_acknowledgement_present():
    ack = (ROOT / "docs" / "ACKNOWLEDGEMENT.md").read_text(encoding="utf-8")
    assert "Nutrien Digital Agriculture Centre" in ack
    assert "Nutrien Digital Agriculture Centre" in (ROOT / "README.md").read_text(encoding="utf-8")
