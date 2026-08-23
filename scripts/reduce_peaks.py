#!/usr/bin/python3

from dbutil import connect, in_map_bbox

conn = connect()
cur = conn.cursor()

# Mercator 12 km ≈ 8 km true distance at 46°N. Local maxima among named
# 2000 m+ peaks, plus every named 3500 m+ summit (Eiger-class peaks that
# sit next to a higher neighbour).
LOCAL_MAX_M = 12000
HIGH_ELE_M = 3500
MIN_ELE_M = 2000

cur.execute(
    f"""
DROP TABLE IF EXISTS tmp_named_peaks;
CREATE TEMP TABLE tmp_named_peaks AS
SELECT osm_id, way, name,
  NULLIF(regexp_replace(ele, '[^0-9.\\-].*$', ''), '')::double precision AS m
FROM planet_osm_point
WHERE {in_map_bbox()}
  AND "natural" IN ('peak', 'volcano')
  AND name IS NOT NULL AND name <> ''
  AND NULLIF(regexp_replace(ele, '[^0-9.\\-].*$', ''), '') IS NOT NULL;
CREATE INDEX tmp_named_peaks_gix ON tmp_named_peaks USING GIST (way);

DROP TABLE IF EXISTS reduced_peaks_high;
CREATE TABLE reduced_peaks_high AS
SELECT way AS geom,
  name || ' ' || round(m)::int AS name
FROM tmp_named_peaks
WHERE m >= {HIGH_ELE_M};

DROP TABLE IF EXISTS reduced_peaks;
CREATE TABLE reduced_peaks AS
SELECT p.way AS geom,
  p.name || ' ' || round(p.m)::int AS name
FROM tmp_named_peaks p
WHERE p.m >= {MIN_ELE_M} AND p.m < {HIGH_ELE_M}
  AND NOT EXISTS (
    SELECT 1 FROM tmp_named_peaks o
    WHERE o.osm_id <> p.osm_id
      AND o.m > p.m
      AND ST_DWithin(p.way, o.way, {LOCAL_MAX_M})
  );

CREATE INDEX reduced_peaks_high_gix ON reduced_peaks_high USING GIST (geom);
CREATE INDEX reduced_peaks_gix ON reduced_peaks USING GIST (geom);
"""
)
conn.commit()
cur.close()
conn.close()
