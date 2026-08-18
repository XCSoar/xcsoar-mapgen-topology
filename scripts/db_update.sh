#!/bin/bash
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

osm2pgsql -C 14000 --slim -v -U osmuser -W -d osm \
	-S "$REPO_ROOT/conf/default.style" -H localhost -a "$1"
osm2pgsql-replicate init -H aria2c --seed-time=0 \
	https://planet.openstreetmap.org/pbf/planet-latest.osm.pbf.torrent
