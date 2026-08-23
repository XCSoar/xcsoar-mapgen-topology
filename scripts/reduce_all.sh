#!/bin/bash
cd "$(dirname "$0")" || exit

./reduce_railway.py
./reduce_power.py
./reduce_water.py
./reduce_airstrips_lines.py
./reduce_airfield.py
./reduce_buildings.py
./reduce_city.py
./reduce_city_points.py
./reduce_peaks.py
./reduce_passes.py
./reduce_forest.py
./reduce_roads_big.py
./reduce_roads_medium.py
./reduce_roads_small.py
