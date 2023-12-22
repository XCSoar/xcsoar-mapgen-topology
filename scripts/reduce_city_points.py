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
    DROP TABLE IF EXISTS reduced_cities;
    CREATE TABLE reduced_cities AS (
    SELECT ST_SetSRID(ST_MakePoint(ST_X(way), ST_Y(way)), 4326) as geom, name as city_name, population
    FROM planet_osm_point
    WHERE (place = 'city' or place = 'town') AND population::integer > 10000);
"""
)
conn.commit()

# Close the database connection
cur.close()
conn.close()
