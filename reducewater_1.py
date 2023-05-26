#!/usr/bin/python3

import psycopg2

# Connect to the PostGIS database with OpenStreetMap data imported using osm2pgsql
conn = psycopg2.connect(
    "dbname=osm user=osmuser password=newgis23 host=worldbox port=5432"
)
cur = conn.cursor()

# Create a table for the filtered and simplified polygons
cur.execute("""
DROP TABLE IF EXISTS water_polygons_small;
DROP TABLE IF EXISTS water_polygons_large;

CREATE TABLE water_polygons_small AS
SELECT osm_id, ST_SimplifyPreserveTopology(way, 15) AS way
FROM planet_osm_polygon
WHERE ("natural" = 'water' OR "landuse" = 'reservoir' OR "landuse" = 'basin')
  AND ST_Area(way) >= 1500 AND ST_Area(way) < 300000;

CREATE TABLE water_polygons_large AS
SELECT osm_id, ST_SimplifyPreserveTopology(way, 15) AS way
FROM planet_osm_polygon
WHERE ("natural" = 'water' OR "landuse" = 'reservoir' OR "landuse" = 'basin')
  AND ST_Area(way) >= 300000;
""")
conn.commit()

cur.execute("""
DROP TABLE IF EXISTS water_lines;
CREATE TABLE water_lines AS
SELECT osm_id, ST_Simplify(way, 15) AS way
FROM planet_osm_line
WHERE waterway = 'river';
""")
conn.commit()


# Close the database connection
cur.close()
conn.close()


