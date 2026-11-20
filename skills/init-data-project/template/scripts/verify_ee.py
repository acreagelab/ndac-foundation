"""Verify the Earth Engine login without exposing tokens.

Default: ambient credentials (`earthengine authenticate`) + EE_PROJECT from .env.
Pass --isolated to use the project-local identity via scripts/ee_config.py (.ee_auth/).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

if "--isolated" in sys.argv:
    from ee_config import EE_PROJECT  # redirects HOME into ./.ee_auth BEFORE ee import
else:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    EE_PROJECT = os.environ.get("EE_PROJECT", "").strip()
    if not EE_PROJECT:
        raise SystemExit("EE_PROJECT is not set — copy .env.example to .env and fill it in.")

import ee
from google.auth.transport.requests import Request as GoogleAuthRequest

ee.Initialize(project=EE_PROJECT)
roots = ee.data.getAssetRoots()
identities = [root.get("id", "") for root in roots if root.get("id")]
credentials = ee.data.get_persistent_credentials()
credentials.refresh(GoogleAuthRequest())
identity_request = Request(
    "https://oauth2.googleapis.com/tokeninfo",
    data=urlencode({"access_token": credentials.token}).encode("ascii"),
    method="POST",
)
with urlopen(identity_request, timeout=30) as response:
    token_identity = json.load(response)
signed_in_email = token_identity.get("email", "(email not exposed by OAuth scopes)")

test_region = ee.Geometry.Rectangle([-106.01, 52.99, -106.0, 53.0])
test_url = ee.Image("USGS/SRTMGL1_003").select("elevation").getDownloadURL(
    {"region": test_region, "scale": 1000, "format": "GEO_TIFF"}
)
with urlopen(test_url, timeout=60) as response:
    payload = response.read()
if not payload:
    raise RuntimeError("Earth Engine returned an empty test image download.")

print(f"Project: {EE_PROJECT}")
print(f"Signed-in email: {signed_in_email}")
print("Signed-in asset root(s): " + (", ".join(identities) if identities else "(none returned)"))
print("Earth Engine initialization: OK")
print(f"Test image download: OK ({len(payload):,} bytes)")
