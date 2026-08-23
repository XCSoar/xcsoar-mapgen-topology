#!/usr/bin/python3
"""Check topology shapefiles for geometries that make XCSoar choke.

XCSoar throws on empty shapefiles, NULL shapes, and malformed bounds
(non-finite or north < south; lon/lat outside ±180/±90).

The OpenGL path ear-clips each ring (O(n²) unless thinned). Self-
intersections, NaNs, and rings with fewer than 3 unique vertices make
that fail. Rings longer than 16384 points are truncated (XShape.cpp),
which can leave an unclosed cut. At most 64 rings per shape are kept.

Usage:
  check_topology.py              # scripts/out
  check_topology.py DIR_OR.xcm
"""

import sys
import tempfile
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np
import pyogrio
import shapely

from dbutil import OUTPUT_DIR, REPO_ROOT

TPL_PATH = REPO_ROOT / "topology" / "topology.tpl"

# src/Topography/XShape.cpp
MAX_LINES = 64
MAX_LINE_POINTS = 16384

T_POINT, T_LINE, T_POLYGON = 0, 1, 3
T_MULTIPOINT, T_MULTILINE, T_MULTIPOLYGON = 4, 5, 6

FAMILY = {
    T_POINT: "point",
    T_LINE: "line",
    T_POLYGON: "area",
    T_MULTIPOINT: "point",
    T_MULTILINE: "line",
    T_MULTIPOLYGON: "area",
}


def parse_tpl(path):
    layers = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("*"):
            continue
        layers.append(line.split(",")[0].strip())
    return layers


def extract_xcm(xcm_path):
    tmp = tempfile.TemporaryDirectory(prefix="topology-check-")
    with zipfile.ZipFile(xcm_path) as zf:
        zf.extractall(tmp.name)
    return tmp, Path(tmp.name)


def sample_reasons(geoms, mask, limit=8):
    reasons = []
    for i in np.flatnonzero(mask)[:limit]:
        reasons.append(shapely.is_valid_reason(geoms[i]))
    return reasons


def iter_rings(geom):
    if geom is None or geom.is_empty:
        return
    gt = geom.geom_type
    if gt == "Polygon":
        yield geom.exterior
        yield from geom.interiors
    elif gt == "MultiPolygon":
        for p in geom.geoms:
            yield p.exterior
            yield from p.interiors
    elif gt in ("LineString", "LinearRing"):
        yield geom
    elif gt == "MultiLineString":
        yield from geom.geoms


def ring_stats(geoms, family):
    """Per-shape ring/vertex limits that XCSoar actually applies."""
    max_ring = 0
    n_huge = 0
    n_many = 0
    n_short = 0
    min_pts = 1 if family == "point" else 2 if family == "line" else 4
    for geom in geoms:
        if geom is None or geom.is_empty:
            continue
        if family == "point":
            continue
        rings = list(iter_rings(geom))
        if not rings:
            n = shapely.get_num_coordinates(geom)
            max_ring = max(max_ring, int(n))
            if n < min_pts:
                n_short += 1
            if n > MAX_LINE_POINTS:
                n_huge += 1
            continue
        if len(rings) > MAX_LINES:
            n_many += 1
        for ring in rings:
            k = len(ring.coords)
            max_ring = max(max_ring, k)
            if k < min_pts:
                n_short += 1
            if k > MAX_LINE_POINTS:
                n_huge += 1
    return max_ring, n_huge, n_many, n_short


def check_layer(out_dir, name):
    errors = []
    warnings = []
    shp = out_dir / f"{name}.shp"
    if not shp.is_file():
        return [f"{name}: missing {shp.name}"], []

    try:
        info = pyogrio.read_info(shp)
        gdf = pyogrio.read_dataframe(shp, columns=[])
    except Exception as exc:  # noqa: BLE001
        return [f"{name}: cannot read shapefile ({exc})"], []

    n = int(info.get("features") or 0)
    geoms = gdf.geometry.values
    if n == 0 or len(geoms) == 0:
        return [f"{name}: empty shapefile (XCSoar throws)"], []

    type_ids = shapely.get_type_id(geoms)
    families = {FAMILY.get(int(t), f"type{int(t)}") for t in np.unique(type_ids)}
    if len(families) != 1:
        errors.append(f"{name}: mixed geometry types {sorted(families)}")
        family = None
    else:
        family = families.pop()

    empty = shapely.is_empty(geoms) | shapely.is_missing(geoms)
    n_empty = int(empty.sum())
    if n_empty:
        errors.append(f"{name}: {n_empty} empty/null shapes (XCSoar throws)")

    coords = shapely.get_coordinates(geoms)
    n_nan = n_range = 0
    if coords.size:
        n_nan = int((~np.isfinite(coords)).any(axis=1).sum())
        if n_nan:
            errors.append(f"{name}: {n_nan} non-finite coordinates")
        lon, lat = coords[:, 0], coords[:, 1]
        n_range = int(
            ((lon < -180) | (lon > 180) | (lat < -90) | (lat > 90)).sum()
        )
        if n_range:
            errors.append(
                f"{name}: {n_range} coords outside lon[-180,180]/lat[-90,90] "
                "(GeoBounds::Check fails)"
            )

    bounds = shapely.total_bounds(geoms)
    if not np.all(np.isfinite(bounds)):
        errors.append(f"{name}: shapefile bounds are not finite")
    elif bounds[3] < bounds[1]:
        errors.append(f"{name}: malformed bounds (north < south)")

    n_invalid = 0
    n_huge = n_many = n_short = 0
    max_ring = 0
    if family:
        invalid = ~shapely.is_valid(geoms)
        n_invalid = int(invalid.sum())
        if n_invalid:
            reasons = Counter(sample_reasons(geoms, invalid))
            detail = "; ".join(f"{r} (x{c})" for r, c in reasons.most_common(5))
            if family == "area":
                errors.append(
                    f"{name}: {n_invalid} invalid polygons "
                    f"(ear-clip will fail): {detail}"
                )
            else:
                errors.append(f"{name}: {n_invalid} invalid geometries: {detail}")

        max_ring, n_huge, n_many, n_short = ring_stats(geoms, family)
        if n_short:
            errors.append(
                f"{name}: {n_short} rings/lines below XCSoar's minimum vertex count"
            )
        if n_huge:
            errors.append(
                f"{name}: {n_huge} rings with more than {MAX_LINE_POINTS} "
                "vertices; XCSoar truncates them and may triangulate a cut ring"
            )
        if n_many:
            warnings.append(
                f"{name}: {n_many} shapes have more than {MAX_LINES} rings; "
                "extra rings are dropped"
            )

    print(
        f"  {name:<22} {n:>8}  {family or '?':<6}  "
        f"invalid={n_invalid:<5} empty={n_empty:<4} "
        f"max_ring={max_ring:<6} huge={n_huge:<3} parts>64={n_many}",
        flush=True,
    )
    return errors, warnings


def check_dir(out_dir):
    errors = []
    warnings = []
    if not out_dir.is_dir():
        return [f"Not a directory: {out_dir}"], []

    tpl = out_dir / "topology.tpl"
    if not tpl.is_file():
        tpl = TPL_PATH
    if not tpl.is_file():
        return [f"Missing {TPL_PATH}"], []

    layers = parse_tpl(tpl)
    if not layers:
        return [f"No layers in {tpl}"], []

    print(f"Checking renderer geometry of {len(layers)} layers in {out_dir}")
    print(
        f"  {'layer':<22} {'n':>8}  {'type':<6}  "
        "invalid empty  max_ring huge parts>64",
        flush=True,
    )
    for name in layers:
        e, w = check_layer(out_dir, name)
        errors.extend(e)
        warnings.extend(w)
    return errors, warnings


def main(argv):
    tmp = None
    target = OUTPUT_DIR
    if len(argv) > 1:
        target = Path(argv[1]).expanduser().resolve()
        if target.suffix.lower() == ".xcm":
            tmp, target = extract_xcm(target)

    try:
        errors, warnings = check_dir(target)
    finally:
        if tmp is not None:
            tmp.cleanup()

    for msg in warnings:
        print(f"warning: {msg}")
    if errors:
        for msg in errors:
            print(f"error: {msg}", file=sys.stderr)
        print(f"topology check failed ({len(errors)} error(s))", file=sys.stderr)
        return 1
    print("topology check ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
