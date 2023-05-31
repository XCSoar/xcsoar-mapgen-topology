#!/usr/bin/python3

import psycopg2
from configparser import ConfigParser

# Read the connection information from the configuration file
config = ConfigParser()
config.read("../conf/config.ini")
database = config.get("postgresql", "database")
user = config.get("postgresql", "user")
password = config.get("postgresql", "password")
host = config.get("postgresql", "host")
port = config.get("postgresql", "port")

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    database=database, user=user, password=password, host=host, port=port
)
cur = conn.cursor()

# Create a table for the filtered and simplified polygons
cur.execute(
    """
DROP TABLE IF EXISTS water_polygons_small;
DROP TABLE IF EXISTS water_polygons_large;

CREATE TABLE water_polygons_small AS
SELECT osm_id, name, ST_SimplifyPreserveTopology(way, 15) AS way
FROM planet_osm_polygon
WHERE ("natural" = 'water' OR "landuse" = 'reservoir' OR "landuse" = 'basin')
  AND ST_Area(way) >= 1000 AND ST_Area(way) < 300000;

CREATE TABLE water_polygons_large AS
SELECT osm_id, name, ST_SimplifyPreserveTopology(way, 15) AS way
FROM planet_osm_polygon
WHERE ("natural" = 'water' OR "landuse" = 'reservoir' OR "landuse" = 'basin')
  AND ST_Area(way) >= 300000;
"""
)
conn.commit()

cur.execute(
    """
DROP TABLE IF EXISTS water_lines;
CREATE TABLE water_lines AS
SELECT osm_id, name, ST_Simplify(way, 15) AS way
FROM planet_osm_line
WHERE waterway = 'river';
"""
)
conn.commit()


# Close the database connection
cur.close()
conn.close()
