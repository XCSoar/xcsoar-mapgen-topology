#!/bin/bash
osm2pgsql -C 14000 --slim -v -U osmuser -W -d osm -S ../conf/default.style -H localhost -a "$1"
osm2pgsql-replicate init -H aria2c --seed-time=0 https://planet.openstreetmap.org/pbf/planet-latest.osm.pbf.torrent
