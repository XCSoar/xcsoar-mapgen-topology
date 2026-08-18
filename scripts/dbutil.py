#!/usr/bin/python3

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


def write_shapefile(gdf, name):
    # GeoPandas 1.x / pyogrio rejects a crs= argument; to_crs() already
    # set the CRS on the frame.
    gdf.to_file(
        output_file(name), driver="ESRI Shapefile", encoding="ISO-8859-1"
    )
