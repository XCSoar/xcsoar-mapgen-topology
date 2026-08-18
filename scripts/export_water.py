#!/usr/bin/python3

import geopandas as gpd

from dbutil import connect, write_shapefile

conn = connect()
crs = "EPSG:4326"

gdf_small = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM water_polygons_small", conn, geom_col="way"
)
gdf_large = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM water_polygons_large", conn, geom_col="way"
)
gdf_lines = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM water_lines", conn, geom_col="way"
)

write_shapefile(gdf_small.to_crs(crs), "water_area_small.shp")
write_shapefile(gdf_large.to_crs(crs), "water_area_large.shp")
write_shapefile(gdf_lines.to_crs(crs), "water_lines.shp")
conn.close()
