#!/usr/bin/python3

import geopandas as gpd

from dbutil import connect, write_shapefile

conn = connect()
gdf = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM runway_polygons", conn, geom_col="multipolygon"
)
gdf = gdf.set_crs("EPSG:3857")
write_shapefile(gdf.to_crs("EPSG:4326"), "airstrip_area.shp")
conn.close()
