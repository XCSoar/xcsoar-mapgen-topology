#!/bin/sh
cd "$(dirname "$0")" || exit

PYTHON=python3
if [ -x "$(dirname "$0")/../bin/python3" ]; then
  PYTHON="$(dirname "$0")/../bin/python3"
fi

"$PYTHON" ./export_airstrips.py
"$PYTHON" ./export_buildings.py
"$PYTHON" ./export_city.py
"$PYTHON" ./export_forest.py
"$PYTHON" ./export_railway.py
"$PYTHON" ./export_roads_big.py
"$PYTHON" ./export_roads_medium.py
"$PYTHON" ./export_roads_small.py
"$PYTHON" ./export_water.py
"$PYTHON" ./export_power.py
"$PYTHON" ./export_city_points.py
"$PYTHON" ./export_peaks.py
"$PYTHON" ./build_qix.py
"$PYTHON" ./check_topology.py
