#!/usr/bin/python3

from dbutil import connect, in_map_bbox

conn = connect()
cur = conn.cursor()

# Visible only to 2 nm. 30 m simplify is several pixels at that range
# and turns residential streets into sticks. Streets fully inside a
# town surface are already covered by city_area_* at this zoom.
cur.execute(
    f"""
    DROP TABLE IF EXISTS reduced_roads_small;
    CREATE TABLE reduced_roads_small AS
    SELECT osm_id, way_reduced
    FROM (
      SELECT osm_id,
        ST_SimplifyPreserveTopology(way, 5) AS way_reduced
      FROM planet_osm_line
      WHERE "highway" IN ('residential', 'unclassified')
        AND (tunnel IS NULL OR tunnel = 'no')
        AND {in_map_bbox()}
    ) s
    WHERE way_reduced IS NOT NULL AND NOT ST_IsEmpty(way_reduced)
      AND NOT EXISTS (
        SELECT 1 FROM city_polygons_large c
        WHERE c.way && s.way_reduced AND ST_Within(s.way_reduced, c.way)
      )
      AND NOT EXISTS (
        SELECT 1 FROM city_polygons_small c
        WHERE c.way && s.way_reduced AND ST_Within(s.way_reduced, c.way)
      );
"""
)
conn.commit()

cur.close()
conn.close()
