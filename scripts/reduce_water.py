#!/usr/bin/python3

from dbutil import connect, in_map_bbox, split_area_sql

conn = connect()
cur = conn.cursor()

# Layers stay visible when zoomed in, so simplify for close range.
# Small (range 3): 5 m, keep holes; include river/stream areas.
# Large (range 30): 5 m, same as small — these stay on when zoomed in.
# Holes ≥ 0.5 ha (lakes) / 0.2 ha (rivers). 40 m left Geneva/Garda as
# ~200 m shoreline segments. XCSoar already thins vertices near the
# layer threshold, so the shapefile can stay dense.
# Lines (range 15): river + canal centreline at 10 m, clipped away where
# a water polygon is already drawn (XCSoar cannot hide a layer on zoom).
cur.execute(
    f"""
DROP TABLE IF EXISTS water_polygons_small;
DROP TABLE IF EXISTS water_polygons_large;

CREATE TABLE water_polygons_small AS
SELECT osm_id, name, way
FROM (
  SELECT osm_id, name,
    ST_MakeValid(ST_SimplifyPreserveTopology(ST_MakeValid(way), 5)) AS way
  FROM planet_osm_polygon
  WHERE ("natural" = 'water' OR "landuse" IN ('reservoir', 'basin'))
    AND (water IS NULL OR water NOT IN (
      'canal', 'ditch', 'drain'))
    AND ST_Area(way) >= 1000 AND ST_Area(way) < 300000
    AND {in_map_bbox()}
) s
WHERE way IS NOT NULL
  AND NOT ST_IsEmpty(way)
  AND ST_Dimension(way) = 2;

CREATE TABLE water_polygons_large AS
SELECT osm_id, name, way
FROM (
  SELECT osm_id, name,
    ST_MakeValid(ST_SimplifyPreserveTopology(
      CASE
        WHEN holes IS NULL THEN ST_MakePolygon(ST_ExteriorRing(geom))
        ELSE ST_MakePolygon(ST_ExteriorRing(geom), holes)
      END,
      simplify_m
    )) AS way
  FROM (
    SELECT d.osm_id, d.name, d.geom, d.simplify_m,
      (
        SELECT array_agg(ST_InteriorRingN(d.geom, n))
        FROM generate_series(
          1, ST_NumInteriorRings(d.geom)
        ) AS n
        WHERE ST_NumInteriorRings(d.geom) > 0
          AND ST_Area(ST_MakePolygon(
            ST_InteriorRingN(d.geom, n)
          )) >= d.hole_min_m2
      ) AS holes
    FROM (
      SELECT osm_id, name,
        (ST_Dump(ST_MakeValid(way))).geom AS geom,
        5 AS simplify_m,
        CASE WHEN water = 'river' THEN 2000 ELSE 5000 END AS hole_min_m2
      FROM planet_osm_polygon
      WHERE ("natural" = 'water' OR "landuse" IN ('reservoir', 'basin'))
        AND (water IS NULL OR water NOT IN (
          'stream', 'canal', 'ditch', 'drain'))
        AND ST_Area(way) >= 300000
        AND {in_map_bbox()}
    ) d
    WHERE GeometryType(d.geom) IN ('POLYGON', 'POLYGONZ')
  ) r
) s
WHERE way IS NOT NULL
  AND NOT ST_IsEmpty(way)
  AND ST_Dimension(way) = 2;

DROP TABLE IF EXISTS water_polygons_small_split;
CREATE TABLE water_polygons_small_split AS
SELECT osm_id, name, (d).geom AS way
FROM water_polygons_small,
LATERAL {split_area_sql()} AS piece,
LATERAL ST_Dump(ST_CollectionExtract(ST_MakeValid(piece), 3)) AS d
WHERE GeometryType((d).geom) IN ('POLYGON', 'POLYGONZ')
  AND ST_Dimension((d).geom) = 2;
DROP TABLE water_polygons_small;
ALTER TABLE water_polygons_small_split RENAME TO water_polygons_small;

DROP TABLE IF EXISTS water_polygons_large_split;
CREATE TABLE water_polygons_large_split AS
SELECT osm_id, name, (d).geom AS way
FROM water_polygons_large,
LATERAL {split_area_sql()} AS piece,
LATERAL ST_Dump(ST_CollectionExtract(ST_MakeValid(piece), 3)) AS d
WHERE GeometryType((d).geom) IN ('POLYGON', 'POLYGONZ')
  AND ST_Dimension((d).geom) = 2;
DROP TABLE water_polygons_large;
ALTER TABLE water_polygons_large_split RENAME TO water_polygons_large;
"""
)
conn.commit()

cur.execute(
    f"""
CREATE INDEX IF NOT EXISTS water_polygons_small_way_idx
  ON water_polygons_small USING GIST (way);
CREATE INDEX IF NOT EXISTS water_polygons_large_way_idx
  ON water_polygons_large USING GIST (way);

DROP TABLE IF EXISTS water_lines;
CREATE TABLE water_lines AS
SELECT osm_id, name, geom AS way
FROM (
  SELECT l.osm_id, l.name,
    (ST_Dump(
      ST_CollectionExtract(
        ST_MakeValid(ST_SimplifyPreserveTopology(clipped, 10)),
        2
      )
    )).geom AS geom
  FROM (
    SELECT l.osm_id, l.name,
      CASE
        WHEN mask.geom IS NULL THEN l.way
        ELSE ST_Difference(l.way, mask.geom)
      END AS clipped
    FROM planet_osm_line l
    LEFT JOIN LATERAL (
      SELECT ST_Union(ST_Buffer(p.way, 25)) AS geom
      FROM (
        SELECT way FROM water_polygons_small
        WHERE ST_DWithin(l.way, way, 50)
        UNION ALL
        SELECT way FROM water_polygons_large
        WHERE ST_DWithin(l.way, way, 50)
      ) p
    ) mask ON true
    WHERE l.waterway IN ('river', 'canal')
      AND {in_map_bbox("l.way")}
  ) l
) s
WHERE geom IS NOT NULL
  AND NOT ST_IsEmpty(geom)
  AND ST_Length(geom) >= 50;
"""
)
conn.commit()

cur.close()
conn.close()
