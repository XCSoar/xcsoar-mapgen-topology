#!/usr/bin/python3

from dbutil import connect

conn = connect()
cur = conn.cursor()

# Forests are drawn at 2–4 nm (still visible when zoomed in). Drop
# scraps under 2 ha, dissolve adjacent patches, strip small clearings,
# then simplify: 40 m on the 2 nm layer, 100 m on the 4 nm layer.
cur.execute(
    """
DROP TABLE IF EXISTS forest_polygons_small;
DROP TABLE IF EXISTS forest_polygons_large;
DROP TABLE IF EXISTS forest_dissolved;

CREATE TABLE forest_dissolved AS
WITH simplified AS (
  SELECT ST_CollectionExtract(
           ST_MakeValid(ST_Simplify(ST_MakeValid(way), 80)),
           3
         ) AS way
  FROM planet_osm_polygon
  WHERE ("landuse" = 'forest' OR "natural" = 'wood')
    AND ST_Area(way) >= 20000
),
dissolved AS (
  SELECT (ST_Dump(
    ST_CollectionExtract(
      ST_MakeValid(ST_UnaryUnion(ST_Collect(way), 20)),
      3
    )
  )).geom AS way
  FROM (
    SELECT way,
      (ST_X(ST_Centroid(way)) / 20000)::int AS gx,
      (ST_Y(ST_Centroid(way)) / 20000)::int AS gy
    FROM simplified
    WHERE way IS NOT NULL AND NOT ST_IsEmpty(way)
  ) s
  GROUP BY gx, gy
)
SELECT way FROM dissolved
WHERE way IS NOT NULL AND NOT ST_IsEmpty(way)
  AND GeometryType(way) IN ('POLYGON', 'POLYGONZ');

CREATE TABLE forest_polygons_small AS
SELECT (ST_Dump(way)).geom AS way
FROM (
  SELECT ST_CollectionExtract(
           ST_MakeValid(ST_Simplify(ST_MakePolygon(ST_ExteriorRing(way)), 40)),
           3
         ) AS way
  FROM forest_dissolved
  WHERE ST_Area(way) >= 20000 AND ST_Area(way) < 300000
) s
WHERE way IS NOT NULL AND NOT ST_IsEmpty(way);

CREATE TABLE forest_polygons_large AS
SELECT (ST_Dump(way)).geom AS way
FROM (
  SELECT ST_CollectionExtract(
    ST_MakeValid(ST_Simplify(
      CASE
        WHEN ST_NumInteriorRings(way) = 0 THEN way
        ELSE ST_MakePolygon(
          ST_ExteriorRing(way),
          ARRAY(
            SELECT ST_InteriorRingN(way, n)
            FROM generate_series(1, ST_NumInteriorRings(way)) AS n
            WHERE ST_Area(ST_MakePolygon(ST_InteriorRingN(way, n))) >= 40000
          )
        )
      END,
      100
    )),
    3
  ) AS way
  FROM forest_dissolved
  WHERE ST_Area(way) >= 300000
) s
WHERE way IS NOT NULL AND NOT ST_IsEmpty(way);

DROP TABLE forest_dissolved;
"""
)
conn.commit()

cur.close()
conn.close()
