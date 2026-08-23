#!/usr/bin/python3

import ctypes
from configparser import ConfigParser
from pathlib import Path

import psycopg2

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
CONFIG_PATH = REPO_ROOT / "conf" / "config.ini"
OUTPUT_DIR = SCRIPTS_DIR / "out"

# ALPS_HighRes.xcm info.txt rectangle (WGS84). osm2pgsql stores
# geometries in EPSG:3857, so reduce queries filter with this envelope
# instead of clipping the PBF first.
MAP_BBOX_WEST = 4.5
MAP_BBOX_SOUTH = 43.4
MAP_BBOX_EAST = 16.5
MAP_BBOX_NORTH = 49.0


def in_map_bbox(column="way"):
    """GIST-indexable overlap with the XCSoar map rectangle."""
    return (
        f"{column} && ST_Transform(ST_MakeEnvelope("
        f"{MAP_BBOX_WEST}, {MAP_BBOX_SOUTH}, "
        f"{MAP_BBOX_EAST}, {MAP_BBOX_NORTH}, 4326), 3857)"
    )


# XCSoar XShape.cpp keeps 16384 vertices per ring and 64 rings per
# shape. Subdivide well below that so OpenGL ear-clip stays cheap.
# Interior rings above the cap are dropped first: XCSoar fills every
# ring and cannot punch holes.
POLYGON_MAX_RINGS = 64
POLYGON_SUBDIVIDE_VERTS = 256


def split_area_sql(column="way"):
    """SQL expression: tile a polygon for the XCSoar renderer."""
    return (
        "ST_Subdivide("
        f"CASE WHEN ST_NRings({column}) > {POLYGON_MAX_RINGS} "
        f"THEN ST_MakePolygon(ST_ExteriorRing({column})) "
        f"ELSE {column} END, {POLYGON_SUBDIVIDE_VERTS})"
    )


def connect():
    config = ConfigParser()
    if not config.read(CONFIG_PATH):
        raise FileNotFoundError(f"Could not read {CONFIG_PATH}")
    return psycopg2.connect(
        database=config.get("postgresql", "database"),
        user=config.get("postgresql", "user"),
        password=config.get("postgresql", "password"),
        host=config.get("postgresql", "host"),
        port=config.get("postgresql", "port"),
    )


def output_file(name):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return str(OUTPUT_DIR / name)


_GDAL = None

# GDALOpenEx flags (gdal.h)
_GDAL_OF_UPDATE = 0x01
_GDAL_OF_VECTOR = 0x04


def _libgdal():
    """Load the GDAL library bundled with pyogrio."""
    global _GDAL
    if _GDAL is not None:
        return _GDAL

    import pyogrio

    libs_dir = Path(pyogrio.__file__).resolve().parent.parent / "pyogrio.libs"
    matches = sorted(libs_dir.glob("libgdal*"))
    if not matches:
        raise FileNotFoundError(f"Could not find bundled libgdal in {libs_dir}")

    lib = ctypes.CDLL(str(matches[0]))
    lib.GDALAllRegister.argtypes = []
    lib.GDALOpenEx.argtypes = [
        ctypes.c_char_p,
        ctypes.c_uint,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    lib.GDALOpenEx.restype = ctypes.c_void_p
    lib.GDALDatasetExecuteSQL.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.c_void_p,
        ctypes.c_char_p,
    ]
    lib.GDALDatasetExecuteSQL.restype = ctypes.c_void_p
    lib.GDALDatasetReleaseResultSet.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    lib.GDALClose.argtypes = [ctypes.c_void_p]
    lib.CPLGetLastErrorMsg.restype = ctypes.c_char_p
    lib.GDALAllRegister()
    _GDAL = lib
    return lib


def create_qix_index(shp_path):
    """Build a MapServer-style .qix quadtree next to an existing shapefile."""
    shp_path = Path(shp_path)
    lib = _libgdal()
    ds = lib.GDALOpenEx(
        str(shp_path).encode(),
        _GDAL_OF_VECTOR | _GDAL_OF_UPDATE,
        None,
        None,
        None,
    )
    if not ds:
        msg = lib.CPLGetLastErrorMsg() or b"GDALOpenEx failed"
        raise RuntimeError(f"Cannot open {shp_path} for QIX: {msg.decode()}")
    try:
        sql = f"CREATE SPATIAL INDEX ON {shp_path.stem}".encode()
        result = lib.GDALDatasetExecuteSQL(ds, sql, None, None)
        if result:
            lib.GDALDatasetReleaseResultSet(ds, result)
    finally:
        lib.GDALClose(ds)

    qix = shp_path.with_suffix(".qix")
    if not qix.is_file():
        raise RuntimeError(f"Failed to create {qix}")
    return qix


def ensure_qix_indexes(directory=None):
    """Create or refresh .qix indexes for every shapefile in directory."""
    directory = Path(directory or OUTPUT_DIR)
    shps = sorted(directory.glob("*.shp"))
    if not shps:
        raise FileNotFoundError(f"No shapefiles in {directory}")
    for shp in shps:
        qix = shp.with_suffix(".qix")
        if qix.is_file() and qix.stat().st_mtime >= shp.stat().st_mtime:
            print(f"qix up to date: {qix.name}")
            continue
        create_qix_index(shp)
        print(f"wrote {qix.name} ({qix.stat().st_size} bytes)")


def write_shapefile(gdf, name):
    # GeoPandas 1.x / pyogrio rejects a crs= argument; to_crs() already
    # set the CRS on the frame. Reprojection to WGS84 can introduce
    # self-intersections; make_valid + explode so XCSoar never sees a
    # MultiPolygon or an invalid ring. SPATIAL_INDEX writes a .qix
    # quadtree; CREATE SPATIAL INDEX is the fallback if the writer skips it.
    gdf = gdf.copy()
    gdf = gdf.set_geometry(gdf.geometry.make_valid())
    gdf = gdf.explode(index_parts=False, ignore_index=True)
    gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty]
    path = output_file(name)
    gdf.to_file(
        path,
        driver="ESRI Shapefile",
        encoding="ISO-8859-1",
        spatial_index=True,
    )
    qix = Path(path).with_suffix(".qix")
    if not qix.is_file():
        create_qix_index(path)
