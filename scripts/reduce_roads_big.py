#!/usr/bin/python3

from dbutil import connect, in_map_bbox

conn = connect()
cur = conn.cursor()

# Visible out to 15 nm, and still drawn when zoomed in. 10 m is about
# one pixel at 2 nm and keeps motorway curves. Drop OSM tunnels
# (tunnel=yes and similar); they are not useful on a flying map.
cur.execute(
    f"""
    DROP TABLE IF EXISTS reduced_roads_big;
    CREATE TABLE reduced_roads_big AS
    SELECT osm_id, way_reduced
    FROM (
      SELECT osm_id,
        ST_SimplifyPreserveTopology(way, 10) AS way_reduced
      FROM planet_osm_roads
      WHERE "highway" IN (
        'motorway', 'motorway_link',
        'trunk', 'trunk_link',
        'primary', 'primary_link'
      )
        AND (tunnel IS NULL OR tunnel = 'no')
        AND {in_map_bbox()}
    ) s
    WHERE way_reduced IS NOT NULL AND NOT ST_IsEmpty(way_reduced);
"""
)
conn.commit()

cur.close()
conn.close()
