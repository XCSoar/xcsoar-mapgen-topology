#!/usr/bin/python3

import psycopg2
from configparser import ConfigParser

# Read the connection information from the configuration file
config = ConfigParser()
config.read('config.ini')
database = config.get('postgresql', 'database')
user = config.get('postgresql', 'user')
password = config.get('postgresql', 'password')
host = config.get('postgresql', 'host')
port = config.get('postgresql', 'port')

# Connect to the PostGIS database with OpenStreetMap data imported using osm2pgsql
conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

cur = conn.cursor()

# Create a table for the filtered and simplified polygons
cur.execute("""
DROP TABLE IF EXISTS forest_polygons_small;
DROP TABLE IF EXISTS forest_polygons_large;

CREATE TABLE forest_polygons_small AS
SELECT osm_id, name, ST_SimplifyPreserveTopology(way, 15) AS way
FROM planet_osm_polygon
WHERE ("landuse" = 'forest')
  AND ST_Area(way) >= 1000 AND ST_Area(way) < 300000;

CREATE TABLE forest_polygons_large AS
SELECT osm_id, name, ST_SimplifyPreserveTopology(way, 15) AS way
FROM planet_osm_polygon
WHERE ("landuse" = 'forest')
  AND ST_Area(way) >= 300000;
""")
conn.commit()

# Close the database connection
cur.close()
conn.close()
