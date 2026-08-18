#!/usr/bin/python3

from dbutil import connect, in_map_bbox

conn = connect()
cur = conn.cursor()

# Visible out to 10 nm, still drawn when zoomed in.
cur.execute(
    f"""
    DROP TABLE IF EXISTS reduced_railway;
    CREATE TABLE reduced_railway AS
    SELECT osm_id, way_reduced
    FROM (
      SELECT osm_id,
        ST_SimplifyPreserveTopology(way, 10) AS way_reduced
      FROM planet_osm_line
      WHERE "railway" IN ('rail', 'narrow_gauge')
        AND {in_map_bbox()}
    ) s
    WHERE way_reduced IS NOT NULL AND NOT ST_IsEmpty(way_reduced);
"""
)
conn.commit()

cur.close()
conn.close()
