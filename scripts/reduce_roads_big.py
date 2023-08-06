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
    DROP TABLE IF EXISTS reduced_roads_big;
    CREATE TABLE reduced_roads_big AS
    SELECT osm_id, ST_Simplify(way, 8) AS way_reduced
    FROM planet_osm_roads
    WHERE ("highway" = 'motorway' OR "highway" = 'primary' OR "highway" = 'primary_link')
"""
)
conn.commit()

# Close the database connection
cur.close()
conn.close()
