#!/usr/bin/python3

from dbutil import connect

conn = connect()
cur = conn.cursor()

# Visible only to 2 nm. 30 m simplify is several pixels at that range
# and turns residential streets into sticks.
cur.execute(
    """
    DROP TABLE IF EXISTS reduced_roads_small;
    CREATE TABLE reduced_roads_small AS
    SELECT osm_id, way_reduced
    FROM (
      SELECT osm_id,
        ST_SimplifyPreserveTopology(way, 5) AS way_reduced
      FROM planet_osm_line
      WHERE "highway" IN ('residential', 'unclassified')
        AND (tunnel IS NULL OR tunnel = 'no')
    ) s
    WHERE way_reduced IS NOT NULL AND NOT ST_IsEmpty(way_reduced);
"""
)
conn.commit()

cur.close()
conn.close()
