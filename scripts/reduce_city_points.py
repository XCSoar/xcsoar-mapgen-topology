#!/usr/bin/python3

from dbutil import connect

conn = connect()
cur = conn.cursor()

# Keep osm2pgsql mercator (EPSG:3857). Export transforms to WGS84.
# Split by OSM place so topology.tpl can show city (15 nm), town (10 nm),
# suburb/village (3 nm). Named places only; skip hamlet (too dense).
# Do not cast population: OSM values are often non-numeric and abort the query.
cur.execute(
    """
    DROP TABLE IF EXISTS reduced_place_points;
    CREATE TABLE reduced_place_points AS
    SELECT way AS geom, name, place
    FROM planet_osm_point
    WHERE place IN ('city', 'town', 'suburb', 'village')
      AND name IS NOT NULL
      AND name <> '';
"""
)
conn.commit()

cur.close()
conn.close()
