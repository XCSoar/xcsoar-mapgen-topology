#!/usr/bin/python3

from dbutil import connect, in_map_bbox

conn = connect()
cur = conn.cursor()

# Dissolve adjacent OSM landuse patches into town blobs, then simplify
# by the zoom of each layer. Large city areas are drawn to 50 nm (still
# visible when zoomed in); small only to 2 nm.
cur.execute(
    f"""
DROP TABLE IF EXISTS city_polygons_small;
DROP TABLE IF EXISTS city_polygons_large;
DROP TABLE IF EXISTS city_dissolved;

CREATE TABLE city_dissolved AS
WITH simplified AS (
  SELECT ST_CollectionExtract(
           ST_MakeValid(ST_SimplifyPreserveTopology(ST_MakeValid(way), 15)),
           3
         ) AS way
  FROM planet_osm_polygon
  WHERE "landuse" IN ('residential', 'industrial', 'commercial')
    AND ST_Area(way) >= 2000
    AND {in_map_bbox()}
),
dissolved AS (
  SELECT (ST_Dump(
    ST_CollectionExtract(
      ST_MakeValid(ST_UnaryUnion(ST_Collect(way), 10)),
      3
    )
  )).geom AS way
  FROM (
    SELECT way,
      (ST_X(ST_Centroid(way)) / 10000)::int AS gx,
      (ST_Y(ST_Centroid(way)) / 10000)::int AS gy
    FROM simplified
    WHERE way IS NOT NULL AND NOT ST_IsEmpty(way)
  ) s
  GROUP BY gx, gy
)
SELECT way FROM dissolved
WHERE way IS NOT NULL AND NOT ST_IsEmpty(way)
  AND GeometryType(way) IN ('POLYGON', 'POLYGONZ');

CREATE TABLE city_polygons_small AS
SELECT geom AS way
FROM (
  SELECT (ST_Dump(ST_CollectionExtract(way, 3))).geom AS geom
  FROM (
    SELECT ST_MakeValid(ST_SimplifyPreserveTopology(
             ST_MakePolygon(ST_ExteriorRing(way)), 8
           )) AS way
    FROM city_dissolved
    WHERE ST_Area(way) >= 2000 AND ST_Area(way) < 300000
  ) s
  WHERE way IS NOT NULL AND NOT ST_IsEmpty(way)
) d
WHERE GeometryType(geom) IN ('POLYGON', 'POLYGONZ');

CREATE TABLE city_polygons_large AS
SELECT geom AS way
FROM (
  SELECT (ST_Dump(ST_CollectionExtract(way, 3))).geom AS geom
  FROM (
    SELECT ST_MakeValid(ST_Simplify(
             ST_MakePolygon(ST_ExteriorRing(way)), 40
           )) AS way
    FROM city_dissolved
    WHERE ST_Area(way) >= 300000
  ) s
  WHERE way IS NOT NULL AND NOT ST_IsEmpty(way)
) d
WHERE GeometryType(geom) IN ('POLYGON', 'POLYGONZ');

DROP TABLE city_dissolved;
"""
)
conn.commit()

cur.close()
conn.close()
