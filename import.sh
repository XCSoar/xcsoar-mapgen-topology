#!/bin/bash

osm2pgsql -C 14000 --drop --slim -c -d osm -U osmuser -S osmstyle/xcsoar.style -W -H localhost $1
