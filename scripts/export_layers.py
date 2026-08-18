#!/usr/bin/python3

import geopandas as gpd

from dbutil import connect, write_shapefile


def fetch_and_export_gdf(
    conn, sql_query, filename, crs="EPSG:4326", geom_col="way"
):
    gdf = gpd.GeoDataFrame.from_postgis(sql_query, conn, geom_col=geom_col)
    write_shapefile(gdf.to_crs(crs), filename)
    print(sql_query)


def main():
    conn = connect()

    fetch_and_export_gdf(
        conn, "SELECT * FROM city_polygons_small", "city_area_small.shp"
    )
    fetch_and_export_gdf(
        conn, "SELECT * FROM city_polygons_large", "city_area_large.shp"
    )
    fetch_and_export_gdf(
        conn, "SELECT * FROM forest_polygons_small", "forest_area_small.shp"
    )
    fetch_and_export_gdf(
        conn, "SELECT * FROM forest_polygons_large", "forest_area_large.shp"
    )
    fetch_and_export_gdf(
        conn,
        "SELECT * FROM reduced_roads_big",
        "roadbig_line.shp",
        geom_col="way_reduced",
    )
    fetch_and_export_gdf(
        conn, "SELECT * FROM water_polygons_small", "water_area_small.shp"
    )
    fetch_and_export_gdf(
        conn, "SELECT * FROM water_polygons_large", "water_area_large.shp"
    )
    fetch_and_export_gdf(conn, "SELECT * FROM water_lines", "water_lines.shp")

    conn.close()


if __name__ == "__main__":
    main()
