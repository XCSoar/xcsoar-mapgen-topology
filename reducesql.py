#!/usr/bin/python3

import psycopg2

# Connect to the PostGIS database with OpenStreetMap data imported using osm2pgsql
conn = psycopg2.connect(
    "dbname=osm user=osmuser password=foobar23 host=localhost port=5432"
)
cur = conn.cursor()

# Create a table for the filtered and simplified polygons
cur.execute("""
    DROP TABLE IF EXISTS water_polygons;
    CREATE TABLE water_polygons AS
    SELECT osm_id, ST_SimplifyPreserveTopology(way, 15) AS way
    FROM planet_osm_polygon
    WHERE ("natural" = 'water' OR "waterway" = '*' OR "landuse" = 'reservoir') AND ST_Area(way) >= 10000;
""")
conn.commit()

# Close the database connection
cur.close()
conn.close()


