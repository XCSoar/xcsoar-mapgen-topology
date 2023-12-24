#!/usr/bin/python3

import psycopg2
import geopandas as gpd
from configparser import ConfigParser


def connect_to_postgresql():
    config = ConfigParser()
    config.read("../conf/config.ini")
    database = config.get("postgresql", "database")
    user = config.get("postgresql", "user")
    password = config.get("postgresql", "password")
    host = config.get("postgresql", "host")
    port = config.get("postgresql", "port")

    conn = psycopg2.connect(
        database=database, user=user, password=password, host=host, port=port
    )
    return conn


def fetch_and_export_gdf(conn, sql_query, output_shapefile, crs="EPSG:4326"):
    gdf = gpd.GeoDataFrame.from_postgis(sql_query, conn, geom_col="way")
    gdf = gdf.to_crs(crs)
    gdf.to_file(
        output_shapefile, driver="ESRI Shapefile", encoding="ISO-8859-1", crs=crs
    )
    extent = gdf.total_bounds
    formatted_extent = (
        f"Extent: ({extent[0]}, {extent[1]}) - ({extent[2]}, {extent[3]})"
    )
    print(sql_query)


def main():
    conn = connect_to_postgresql()

    #    fetch_and_export_gdf(
    #        conn, "SELECT * FROM runway_polygons", "out/airstrip_area.shp", crs="EPSG:4326"
    #    )

    fetch_and_export_gdf(
        conn,
        "SELECT * FROM city_polygons_small",
        "out/city_area_small.shp",
        crs="EPSG:4326",
    )

    fetch_and_export_gdf(
        conn,
        "SELECT * FROM city_polygons_large",
        "out/city_area_large.shp",
        crs="EPSG:4326",
    )

    fetch_and_export_gdf(
        conn,
        "SELECT * FROM forest_polygons_small",
        "out/forest_area_small.shp",
        crs="EPSG:4326",
    )

    fetch_and_export_gdf(
        conn,
        "SELECT * FROM forest_polygons_large",
        "out/forest_area_large.shp",
        crs="EPSG:4326",
    )

    #    fetch_and_export_gdf(
    ##        conn, "SELECT * FROM reduced_railway", "out/railway_line.shp", crs="EPSG:4326"
    #    )

    fetch_and_export_gdf(
        conn, "SELECT * FROM reduced_roads_big", "out/roadbig_line.shp", crs="EPSG:4326"
    )

    #    fetch_and_export_gdf(
    #        conn, "SELECT * FROM reduced_roads_medium", "out/roadmedium_line.shp", crs="EPSG:4326"
    #    )

    #    fetch_and_export_gdf(
    #        conn, "SELECT * FROM reduced_roads_small", "out/roadsmall_line.shp", crs="EPSG:4326"
    #    )

    fetch_and_export_gdf(
        conn,
        "SELECT * FROM water_polygons_small",
        "out/water_area_small.shp",
        crs="EPSG:4326",
    )

    fetch_and_export_gdf(
        conn,
        "SELECT * FROM water_polygons_large",
        "out/water_area_large.shp",
        crs="EPSG:4326",
    )

    fetch_and_export_gdf(
        conn, "SELECT * FROM water_lines", "out/water_lines.shp", crs="EPSG:4326"
    )

    conn.close()


if __name__ == "__main__":
    main()
