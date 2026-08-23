#!/usr/bin/python3

import geopandas as gpd

from dbutil import connect, write_shapefile

# One shapefile per fill colour (XCSoar cannot vary colour inside a layer).
# Colours follow OSM Carto. Draw order is topology.tpl (grounds first).
AIRFIELD_LAYERS = (
    ("aerodrome_area.shp", ("aerodrome", "heliport", "airstrip")),
    ("apron_area.shp", ("apron",)),
    ("taxiway_area.shp", ("taxiway", "taxilane", "stopway", "helipad")),
    ("hangar_area.shp", ("hangar",)),
    ("terminal_area.shp", ("terminal",)),
)

conn = connect()
gdf = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM runway_polygons", conn, geom_col="multipolygon"
)
gdf = gdf.set_crs("EPSG:3857")
write_shapefile(gdf.to_crs("EPSG:4326"), "airstrip_area.shp")

gdf_field = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM airfield_polygons", conn, geom_col="geom"
)
gdf_field = gdf_field.set_crs("EPSG:3857")
gdf_field = gdf_field.to_crs("EPSG:4326")

for filename, tags in AIRFIELD_LAYERS:
    part = gdf_field[gdf_field["aeroway"].isin(tags)]
    if part.empty:
        print(f"skip empty {filename}")
        continue
    write_shapefile(part.copy(), filename)

conn.close()
