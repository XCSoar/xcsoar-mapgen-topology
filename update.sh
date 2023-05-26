#!/bin/bash
osm2pgsql -C 14000 --slim -v -U osmuser -W -d osm -S osmstyle/default.style -H localhost -a $1
