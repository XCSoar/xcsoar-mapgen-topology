#!/usr/bin/python3

import geopandas as gpd

from dbutil import connect, write_shapefile

conn = connect()

gdf_high = gpd.GeoDataFrame.from_postgis(
    "SELECT name, geom FROM reduced_peaks_high", conn, geom_col="geom"
)
write_shapefile(gdf_high.to_crs("EPSG:4326"), "peak_point_high.shp")

gdf = gpd.GeoDataFrame.from_postgis(
    "SELECT name, geom FROM reduced_peaks", conn, geom_col="geom"
)
write_shapefile(gdf.to_crs("EPSG:4326"), "peak_point.shp")

gdf_pass_high = gpd.GeoDataFrame.from_postgis(
    "SELECT name, geom FROM reduced_passes_high", conn, geom_col="geom"
)
write_shapefile(gdf_pass_high.to_crs("EPSG:4326"), "pass_point_high.shp")

gdf_pass = gpd.GeoDataFrame.from_postgis(
    "SELECT name, geom FROM reduced_passes", conn, geom_col="geom"
)
write_shapefile(gdf_pass.to_crs("EPSG:4326"), "pass_point.shp")

conn.close()
