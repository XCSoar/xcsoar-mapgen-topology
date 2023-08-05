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
-- Drop the table if it already exists
DROP TABLE IF EXISTS runway_polygons;

-- Create a new table to store the rectangular polygons
CREATE TABLE runway_polygons (
    osm_id bigint,
    aeroway varchar(255),
    ref varchar(255),
    width numeric,
    polygon geometry(Polygon, 3857) -- Set SRID to 4326 (WGS84)
);

-- Insert data into the new table with explicit SRID setting
INSERT INTO runway_polygons (osm_id, aeroway, ref, width, polygon)
SELECT
    osm_id,
    aeroway,
    ref,
    CASE
        WHEN width ~ '^[-+]?[0-9]+(\.[0-9]+)?$' THEN width::numeric
        ELSE 30
    END AS width,
    ST_SetSRID(ST_Buffer(ST_MakeValid(way), CASE WHEN width ~ '^[-+]?[0-9]+(\.[0-9]+)?$' THEN width::numeric / 2 ELSE 15 END, 'endcap=flat join=mitre'), 3857) AS polygon
FROM
    planet_osm_line
WHERE
    aeroway = 'runway' AND ST_IsValid(way);

-- Add an index for better query performance
CREATE INDEX idx_runway_polygons ON runway_polygons USING GIST (polygon);

"""
)
conn.commit()

# Close the database connection
cur.close()
conn.close()
