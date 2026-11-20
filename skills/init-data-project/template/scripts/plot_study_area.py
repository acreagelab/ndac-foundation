"""Study-area map: plot an AGGREGATED outline of the study area to graph/<today>/.

    python scripts/plot_study_area.py --input "${DATA_ROOT}/<project>/boundaries.gpkg"
    python scripts/plot_study_area.py --input data/raw/rm.gpkg --by RMNO --label RMNAME

Governance (NDAC): field boundaries are identifying (C_Limited minimum). By default all
features are DISSOLVED into one outline, so individual fields are never drawn. Use --by
only with an aggregate unit (RM, ecodistrict, irrigation district), never a field/farm id.
The figure is written under graph/ (gitignored); run /export-check before sharing it.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src" / "common.py").exists())
sys.path.insert(0, str(ROOT))

from src.common import load_config, resolve_path  # noqa: E402

FIELD_LEVEL_HINTS = ("field", "farm", "operator", "owner", "ppid", "lld", "quarter", "parcel")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", required=True, help="vector file (config-style path, ${DATA_ROOT} allowed)")
    p.add_argument("--by", help="aggregate unit column to dissolve by (e.g. RM number)")
    p.add_argument("--label", help="column to label aggregated units with")
    p.add_argument("--title", default="Study area")
    p.add_argument("--out", default="study_area.png")
    a = p.parse_args()

    import geopandas as gpd
    import matplotlib.pyplot as plt

    if a.by and any(h in a.by.lower() for h in FIELD_LEVEL_HINTS):
        sys.exit(f"--by {a.by} looks field/operator-level; aggregate to RM/ecodistrict instead.")

    crs = load_config()["project"]["crs_analysis"]
    gdf = gpd.read_file(resolve_path(a.input)).to_crs(crs)
    if a.by:
        keep = [a.by] + ([a.label] if a.label and a.label != a.by else [])
        shapes = gdf[keep + ["geometry"]].dissolve(by=a.by, aggfunc="first").reset_index()
    else:
        shapes = gpd.GeoDataFrame(geometry=[gdf.geometry.union_all()], crs=crs)

    fig, ax = plt.subplots(figsize=(7, 7))
    shapes.plot(ax=ax, facecolor="#dfe9dc", edgecolor="#275D38", linewidth=0.8)
    if a.by and a.label:
        for _, row in shapes.iterrows():
            pt = row.geometry.representative_point()
            ax.annotate(str(row[a.label]), (pt.x, pt.y), ha="center", fontsize=7)
    ax.set_title(a.title)
    ax.set_xlabel(f"Easting (m), {crs}")
    ax.set_ylabel(f"Northing (m), {crs}")
    ax.ticklabel_format(style="plain")
    ax.set_aspect("equal")

    out = ROOT / "graph" / dt.date.today().isoformat() / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print(f"Saved: {out.relative_to(ROOT)}  (aggregated: {'by ' + a.by if a.by else 'single outline'})")


if __name__ == "__main__":
    main()
