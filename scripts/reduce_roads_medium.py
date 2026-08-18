#!/usr/bin/python3

from dbutil import connect

conn = connect()
cur = conn.cursor()

# Visible out to 8 nm. Tertiary belongs here (not on the 2 nm layer)
# so it remains useful for navigation at typical cross-country zoom.
cur.execute(
    """
    DROP TABLE IF EXISTS reduced_roads_medium;
    CREATE TABLE reduced_roads_medium AS
    SELECT osm_id, way_reduced
    FROM (
      SELECT osm_id,
        ST_SimplifyPreserveTopology(way, 10) AS way_reduced
      FROM planet_osm_line
      WHERE "highway" IN (
        'secondary', 'secondary_link',
        'tertiary', 'tertiary_link'
      )
        AND (tunnel IS NULL OR tunnel = 'no')
    ) s
    WHERE way_reduced IS NOT NULL AND NOT ST_IsEmpty(way_reduced);
"""
)
conn.commit()

cur.close()
conn.close()
