#!/usr/bin/python3

from dbutil import connect, in_map_bbox

conn = connect()
cur = conn.cursor()

# Runways stay on airstrip_area (range 10). Other aeroway polygons are
# split at export into OSM Carto colours (aerodrome, apron, taxiway,
# hangar, terminal). Range 5 so taxiways do not blob at cruise.
# Closed aeroway ways are stored as lines by osm2pgsql; polygonize them.
AREA_TAGS = (
    "aerodrome",
    "apron",
    "hangar",
    "terminal",
    "helipad",
    "heliport",
    "airstrip",
)
BUFFER_TAGS = ("taxiway", "taxilane", "stopway")
area_list = ", ".join(f"'{t}'" for t in AREA_TAGS)
buffer_list = ", ".join(f"'{t}'" for t in BUFFER_TAGS)

cur.execute(
    rf"""
DROP TABLE IF EXISTS airfield_polygons;

CREATE TABLE airfield_polygons (
    osm_id bigint,
    aeroway varchar(255),
    name varchar(255),
    geom geometry(MultiPolygon, 3857)
);

INSERT INTO airfield_polygons (osm_id, aeroway, name, geom)
SELECT
    osm_id,
    aeroway,
    name,
    ST_Multi(ST_CollectionExtract(
        ST_MakeValid(ST_SimplifyPreserveTopology(way, 3)),
        3
    ))
FROM planet_osm_polygon
WHERE aeroway IN ({area_list})
  AND way IS NOT NULL
  AND NOT ST_IsEmpty(ST_CollectionExtract(ST_MakeValid(way), 3))
  AND {in_map_bbox()};

INSERT INTO airfield_polygons (osm_id, aeroway, name, geom)
SELECT
    osm_id,
    aeroway,
    name,
    ST_Multi(ST_CollectionExtract(
        ST_MakeValid(ST_SimplifyPreserveTopology(ST_MakePolygon(way), 3)),
        3
    ))
FROM planet_osm_line
WHERE aeroway IN ({area_list})
  AND way IS NOT NULL
  AND ST_IsClosed(way)
  AND ST_NPoints(way) >= 4
  AND {in_map_bbox()};

INSERT INTO airfield_polygons (osm_id, aeroway, name, geom)
SELECT
    osm_id,
    aeroway,
    name,
    ST_Multi(ST_CollectionExtract(
        ST_MakeValid(ST_SimplifyPreserveTopology(buffered, 3)),
        3
    ))
FROM (
    SELECT
        osm_id,
        aeroway,
        name,
        ST_Transform(
            ST_SetSRID(
                ST_Buffer(
                    ST_Transform(ST_MakeValid(way), 4326)::geography,
                    CASE
                        WHEN width ~ '^[0-9]+([.][0-9]+)?$'
                        THEN width::numeric / 2
                        ELSE 5.5
                    END
                )::geometry,
                4326
            ),
            3857
        ) AS buffered
    FROM planet_osm_line
    WHERE aeroway IN ({buffer_list})
      AND way IS NOT NULL
      AND NOT ST_IsEmpty(way)
      AND NOT (ST_IsClosed(way) AND ST_NPoints(way) >= 4)
      AND {in_map_bbox()}
) s
WHERE buffered IS NOT NULL AND NOT ST_IsEmpty(buffered);

INSERT INTO airfield_polygons (osm_id, aeroway, name, geom)
SELECT
    osm_id,
    aeroway,
    name,
    ST_Multi(ST_CollectionExtract(
        ST_MakeValid(ST_SimplifyPreserveTopology(way, 3)),
        3
    ))
FROM planet_osm_polygon
WHERE aeroway IN ({buffer_list})
  AND way IS NOT NULL
  AND NOT ST_IsEmpty(ST_CollectionExtract(ST_MakeValid(way), 3))
  AND {in_map_bbox()};

DELETE FROM airfield_polygons
WHERE geom IS NULL OR ST_IsEmpty(geom) OR ST_Dimension(geom) < 2;

CREATE INDEX idx_airfield_polygons ON airfield_polygons USING GIST (geom);
"""
)
conn.commit()

cur.close()
conn.close()
