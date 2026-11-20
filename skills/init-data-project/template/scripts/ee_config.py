"""OPT-IN per-project Earth Engine identity isolation.

Import this module BEFORE ``import ee`` to redirect Earth Engine's credential
lookup into ``./.ee_auth/`` so this project holds its own EE login (useful for
parallel downloads under separate identities). Consequences to understand:
  - ``.ee_auth/`` will contain a LIVE OAuth token — gitignored and read-blocked;
    never read, print, copy, or back it up
  - other libraries that consult HOME will also write state there
If the project uses the normal ambient login, do not import this module.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

EE_AUTH_DIR = PROJECT_ROOT / ".ee_auth"
EE_AUTH_DIR.mkdir(parents=True, exist_ok=True)

# Earth Engine's credential lookup follows the platform home directory.
os.environ["HOME"] = str(EE_AUTH_DIR)
os.environ["USERPROFILE"] = str(EE_AUTH_DIR)

EE_PROJECT = os.environ.get("EE_PROJECT", "").strip()
if not EE_PROJECT:
    raise RuntimeError("EE_PROJECT is not set — copy .env.example to .env and fill it in.")
