#!/bin/bash

sudo -u postgres createuser osmuser
sudo -u postgres psql --command="ALTER USER osmuser WITH ENCRYPTED PASSWORD 'newgis23';"
sudo -u postgres createdb --encoding=UTF8 --owner=osmuser osm
sudo -u postgres psql osm --command='CREATE EXTENSION postgis;'
sudo -u postgres psql osm --command='CREATE EXTENSION hstore;'
