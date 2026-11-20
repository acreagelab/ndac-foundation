---
name: ndac-data-rules
description: NDAC data-governance and geospatial rules for prairie agricultural data. Use whenever working with field boundaries, yield, soil, sensor, survey or parcel data, choosing a CRS, buffering or computing areas/zonal statistics, aggregating results for release, handling credentials, or deciding whether something may be shared — in any NDAC project, including ones not created from the template.
---

# NDAC data rules

Projects created from the ndac-foundation template carry these rules in their CLAUDE.md.
This skill applies them everywhere else too. When a project's CLAUDE.md is stricter,
follow the project.

## Prairie identifiers are direct PII
Never export, publish, or paste into chats, issues or notebook outputs:
- ISC PPID (parcel identifier) and legal land descriptions (quarter/section/township/range/meridian), in tables AND shapefile DBF attributes
- Field-boundary polygons joined to quarter-section or parcel layers
- Coordinates finer than the upstream provider itself publishes
- Small cells: aggregates backed by < 5 farms/operators
- Field- or operator-level measurements (yield, soil EC/EM38 surveys, per-field sensor data) are C_Limited minimum; named-producer files, and figures whose extent outlines a producer's fields, never leave the secure environment

## Security zones
- Order: D_Restric > C_Limited > B_Internal > A_Public
- Writing output to a LOWER zone than its input is declassification: it needs a documented justification in the dataset's `.meta.yaml` sidecar and sign-off from the project's data steward (NDAC data manager by default) first

## Credentials
- Never read, print, or copy contents of: `.ee_auth/**`, `.ee_accounts/**`, `.ee_personal_account/**`, `**/credentials`, `application_default_credentials.json`, `*service-account*.json`, `*.pem`, `.env` values; report paths only
- `.gitignore` covering credential paths must exist BEFORE `git init` / first commit
- Earth Engine project via the `EE_PROJECT` env var, never hardcoded in configs, never a personal Gmail

## Publishing
- Before any public release: aggregate to RM/ecodistrict or coarser, suppress cells backed by < 5 farms, acknowledge NDAC, and run `/export-check`
- NDAC repos carry a pre-push guard blocking non-USask remotes; publish deliberately with `git config ndac.pushApproved true` only after `/export-check` passes

## OCAP® / CARE
- Stakeholder-interview or Indigenous-community data: de-identification is applied at ingest, before anything lands in `data/raw/`, not retroactively
- Flag such data for governance review regardless of de-identification state

## CRS policy
- Measurement (buffers, areas, distances, zonal stats): projected metric CRS only. Prairie-wide → EPSG:3347 (StatCan Lambert). Local → UTM zone: AB 32611/32612, SK 32613, MB 32614.
- NEVER EPSG:3857 (Web Mercator) for analysis (~1.66× area distortion at 53°N). Display/tiles only.
- Reproject to the metric CRS BEFORE buffering; buffer distance is in CRS units.

## Library gotchas
- Shapely 2.x: `union_all()`, not deprecated `unary_union`
- Shapefile DBF field names truncate at 10 chars (`RMNO_NUMBER` → `RMNO_NUMER`); verify join keys after any shapefile write. Prefer GeoPackage.
- Write CRS and nodata explicitly on every raster output

## Paths, layout, reproducibility
- No hardcoded drive-letter data paths or `C:\Users\...` paths in code or configs; use a `DATA_ROOT` env var loaded from `.env`
- `data/raw/` read-only; derived → `data/processed/` or `data/outputs/`; logs → `logs/`
- Seed `random`, `numpy`, and `torch` (+ cuda) together, never `torch` alone
- Pin dependencies exactly (floor pins `>=` do not reproduce; Shapely 2.0 changed geometry semantics)
- `test_*.py` is reserved for real pytest tests; name experiments `experiment_*.py`
- Write a run manifest (config used, package versions, seed, git SHA + dirty flag, input checksums) beside every metrics/model output
