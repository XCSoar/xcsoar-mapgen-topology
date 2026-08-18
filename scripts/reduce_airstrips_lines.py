#!/usr/bin/python3

from dbutil import connect, in_map_bbox

conn = connect()
cur = conn.cursor()

# Buffer line runways in metres (geography), not Web Mercator units.
# Taxiways are omitted: at 10 nm they turn airfields into blobs.
# Also keep polygon runways from OSM. 3 m simplify drops buffer arcs.
cur.execute(
    rf"""
DROP TABLE IF EXISTS runway_polygons;

CREATE TABLE runway_polygons (
    osm_id bigint,
    aeroway varchar(255),
    ref varchar(255),
    width numeric,
    multipolygon geometry(MultiPolygon, 3857)
);

INSERT INTO runway_polygons (osm_id, aeroway, ref, width, multipolygon)
SELECT
    osm_id,
    aeroway,
    ref,
    CASE
        WHEN width ~ '^[0-9]+([.][0-9]+)?$' THEN width::numeric
        ELSE 30
    END AS width,
    ST_Multi(ST_CollectionExtract(
        ST_MakeValid(ST_SimplifyPreserveTopology(buffered, 3)),
        3
    )) AS multipolygon
FROM (
    SELECT
        osm_id,
        aeroway,
        ref,
        width,
        ST_Transform(
            ST_SetSRID(
                ST_Buffer(
                    ST_Transform(ST_MakeValid(way), 4326)::geography,
                    CASE
                        WHEN width ~ '^[0-9]+([.][0-9]+)?$'
                        THEN width::numeric / 2
                        ELSE 15
                    END
                )::geometry,
                4326
            ),
            3857
        ) AS buffered
    FROM planet_osm_line
    WHERE aeroway = 'runway'
      AND way IS NOT NULL
      AND NOT ST_IsEmpty(way)
      AND {in_map_bbox()}
) s
WHERE buffered IS NOT NULL AND NOT ST_IsEmpty(buffered);

INSERT INTO runway_polygons (osm_id, aeroway, ref, width, multipolygon)
SELECT
    osm_id,
    aeroway,
    ref,
    CASE
        WHEN width ~ '^[0-9]+([.][0-9]+)?$' THEN width::numeric
        ELSE NULL
    END AS width,
    ST_Multi(ST_CollectionExtract(
        ST_MakeValid(ST_SimplifyPreserveTopology(way, 3)),
        3
    )) AS multipolygon
FROM planet_osm_polygon
WHERE aeroway = 'runway'
  AND way IS NOT NULL
  AND NOT ST_IsEmpty(ST_CollectionExtract(ST_MakeValid(way), 3))
  AND {in_map_bbox()};

CREATE INDEX idx_runway_polygons ON runway_polygons USING GIST (multipolygon);
"""
)
conn.commit()

cur.close()
conn.close()
