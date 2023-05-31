#!/usr/bin/python3

import psycopg2
import geopandas as gpd
from configparser import ConfigParser

# Read the connection information from the configuration file
config = ConfigParser()
config.read("../conf/../conf/config.ini")
database = config.get("postgresql", "database")
user = config.get("postgresql", "user")
password = config.get("postgresql", "password")
host = config.get("postgresql", "host")
port = config.get("postgresql", "port")

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    database=database, user=user, password=password, host=host, port=port
)

# Set the SQL queries to retrieve the desired geometries
sql_small = "SELECT * FROM water_polygons_small"
sql_large = "SELECT * FROM water_polygons_large"
sql_lines = "SELECT * FROM water_lines"

# Fetch the geometries from the database and create GeoDataFrames
gdf_small = gpd.GeoDataFrame.from_postgis(sql_small, conn, geom_col="way")
gdf_large = gpd.GeoDataFrame.from_postgis(sql_large, conn, geom_col="way")
gdf_lines = gpd.GeoDataFrame.from_postgis(sql_lines, conn, geom_col="way")

# Set the output shapefile paths
output_dir = "out/"
output_shapefile_small = output_dir + "water_area_small.shp"
output_shapefile_large = output_dir + "water_area_large.shp"
output_shapefile_lines = output_dir + "water_lines.shp"

# Set the CRS (WGS84)
crs = "EPSG:4326"

# Export the GeoDataFrames to shapefiles with ISO encoding and WGS84 SRS
gdf_small.to_file(
    output_shapefile_small, driver="ESRI Shapefile", encoding="ISO-8859-1", crs=crs
)
gdf_large.to_file(
    output_shapefile_large, driver="ESRI Shapefile", encoding="ISO-8859-1", crs=crs
)
gdf_lines.to_file(
    output_shapefile_lines, driver="ESRI Shapefile", encoding="ISO-8859-1", crs=crs
)

# Close the database connection
conn.close()
