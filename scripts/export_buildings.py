#!/usr/bin/python3

import geopandas as gpd

from dbutil import connect, write_shapefile

conn = connect()
gdf = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM building_polygons_large", conn, geom_col="way"
)
write_shapefile(gdf.to_crs("EPSG:4326"), "building_area_large.shp")
conn.close()
