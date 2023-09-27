#!/bin/bash

sudo -u postgres psql -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'osm' AND pid <> pg_backend_pid();"
sudo -u postgres dropdb osm
sudo -u postgres dropuser osmuser
