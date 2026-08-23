#!/usr/bin/python3

from dbutil import connect, in_map_bbox, split_area_sql

conn = connect()
cur = conn.cursor()

# Footprints >= 1 ha only. Smaller buildings were a range-2 layer;
# XCSoar thinning made them specks, so they are omitted.
SMALL_TYPES = """
          '', 'no', 'house', 'detached', 'terrace', 'semidetached_house',
          'garage', 'garages', 'shed', 'hut', 'cabin', 'carport',
          'bungalow', 'static_caravan', 'ruins', 'construction',
          'kiosk', 'roof', 'entrance'
"""

cur.execute(
    f"""
DROP TABLE IF EXISTS building_polygons;
DROP TABLE IF EXISTS building_polygons_small;
DROP TABLE IF EXISTS building_polygons_large;

CREATE TABLE building_polygons_large AS
SELECT osm_id, name, building, leisure, (d).geom AS way
FROM (
  SELECT osm_id, name, building, leisure,
    ST_MakeValid(ST_SimplifyPreserveTopology(ST_MakeValid(way), 15)) AS way
  FROM bldg_polygon
  WHERE way IS NOT NULL
    AND {in_map_bbox()}
    AND ST_Area(way) >= 10000
    AND (
      COALESCE(leisure, '') IN ('stadium', 'sports_centre', 'grandstand')
      OR COALESCE(building, '') NOT IN ({SMALL_TYPES})
    )
) s,
LATERAL {split_area_sql()} AS piece,
LATERAL ST_Dump(ST_CollectionExtract(ST_MakeValid(piece), 3)) AS d
WHERE s.way IS NOT NULL
  AND NOT ST_IsEmpty(s.way)
  AND GeometryType((d).geom) IN ('POLYGON', 'POLYGONZ');

CREATE INDEX building_polygons_large_gix ON building_polygons_large USING GIST (way);
"""
)
conn.commit()

cur.close()
conn.close()
