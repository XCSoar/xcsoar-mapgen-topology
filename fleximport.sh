#!/bin/bash

osm2pgsql -O flex --slim -S flexscripts/water_reservoir.lua -U osmuser -W -d osm --drop -H localhost $1 
