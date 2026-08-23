#!/usr/bin/python3

from dbutil import connect, in_map_bbox

conn = connect()
cur = conn.cursor()

# power=line: high-voltage conductors, drawn to range 5.
# power=tower: lattice pylons (not wooden poles). Range 8 in topology.tpl.
cur.execute(
    f"""
    DROP TABLE IF EXISTS reduced_powerlines;
    CREATE TABLE reduced_powerlines AS
    SELECT osm_id, way_reduced
    FROM (
      SELECT osm_id, ST_Simplify(way, 15) AS way_reduced
      FROM planet_osm_line
      WHERE "power" = 'line'
        AND {in_map_bbox()}
    ) s
    WHERE way_reduced IS NOT NULL AND NOT ST_IsEmpty(way_reduced);

    DROP TABLE IF EXISTS reduced_power_minor;
    DROP TABLE IF EXISTS reduced_power_towers;
    CREATE TABLE reduced_power_towers AS
    SELECT osm_id, way AS geom
    FROM planet_osm_point
    WHERE "power" = 'tower'
      AND {in_map_bbox()};
"""
)
conn.commit()

cur.close()
conn.close()
