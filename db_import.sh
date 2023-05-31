#!/bin/bash
osm2pgsql -C 14000 --drop --slim -U osmuser -W -d osm -S osmstyle/default.style -H localhost -c $1
