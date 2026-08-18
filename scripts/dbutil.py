#!/usr/bin/python3

from configparser import ConfigParser
from pathlib import Path

import psycopg2

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
CONFIG_PATH = REPO_ROOT / "conf" / "config.ini"
OUTPUT_DIR = SCRIPTS_DIR / "out"


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
