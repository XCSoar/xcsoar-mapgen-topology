#!/usr/bin/python3

from dbutil import connect

conn = connect()
cur = conn.cursor()

# Visible out to 10 nm. Transmission lines are long and straight;
# 15 m is enough even when zoomed in.
cur.execute(
    """
    DROP TABLE IF EXISTS reduced_powerlines;
    CREATE TABLE reduced_powerlines AS
    SELECT osm_id, way_reduced
    FROM (
      SELECT osm_id, ST_Simplify(way, 15) AS way_reduced
      FROM planet_osm_line
      WHERE "power" = 'line'
    ) s
    WHERE way_reduced IS NOT NULL AND NOT ST_IsEmpty(way_reduced);
"""
)
conn.commit()

cur.close()
conn.close()
