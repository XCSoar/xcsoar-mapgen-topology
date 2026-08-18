#!/usr/bin/python3

import geopandas as gpd

from dbutil import connect, write_shapefile

conn = connect()
gdf = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM reduced_railway", conn, geom_col="way_reduced"
)
write_shapefile(gdf.to_crs("EPSG:4326"), "railway_line.shp")
conn.close()
