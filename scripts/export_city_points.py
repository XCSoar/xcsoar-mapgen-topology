#!/usr/bin/python3

import geopandas as gpd

from dbutil import connect, write_shapefile

PLACE_LAYERS = (
    ("city", "city_point.shp"),
    ("town", "town_point.shp"),
    ("suburb", "suburb_point.shp"),
    ("village", "village_point.shp"),
)

conn = connect()

for place, filename in PLACE_LAYERS:
    sql = (
        "SELECT name, geom FROM reduced_place_points "
        f"WHERE place = '{place}'"
    )
    gdf = gpd.GeoDataFrame.from_postgis(sql, conn, geom_col="geom")
    if gdf.empty:
        continue
    write_shapefile(gdf.to_crs("EPSG:4326"), filename)

conn.close()
