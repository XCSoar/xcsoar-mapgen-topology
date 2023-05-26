#!/usr/bin/python3

import psycopg2

# Connect to the PostGIS database with OpenStreetMap data imported using osm2pgsql
conn = psycopg2.connect(
    "dbname=osm user=osmuser password=newgis23 host=worldbox port=5432"
)
cur = conn.cursor()

# Create a table for the filtered and simplified polygons
cur.execute("""
DROP TABLE IF EXISTS city_polygons_small;
DROP TABLE IF EXISTS city_polygons_large;

CREATE TABLE city_polygons_small AS
SELECT osm_id, name, ST_SimplifyPreserveTopology(way, 15) AS way
FROM planet_osm_polygon
WHERE ("landuse" = 'residential' OR "landuse" = 'industrial' OR "landuse" = 'commercial')
  AND ST_Area(way) >= 1000 AND ST_Area(way) < 300000;

CREATE TABLE city_polygons_large AS
SELECT osm_id, name, ST_SimplifyPreserveTopology(way, 15) AS way
FROM planet_osm_polygon
WHERE ("landuse" = 'residential' OR "landuse" = 'industrial' OR "landuse" = 'commercial')
  AND ST_Area(way) >= 300000;
""")
conn.commit()

# Close the database connection
cur.close()
conn.close()


