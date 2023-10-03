#!/bin/bash
osm2pgsql --flat-nodes ./flatnodes --slim -U osmuser -W -d osm -S ../conf/default.style -H localhost -c "$1"
