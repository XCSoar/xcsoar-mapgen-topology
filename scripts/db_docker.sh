#!/bin/bash
# Start a PostGIS container with the same credentials as db_create.sh.
# Skip db_create.sh when using Docker.

docker run -d --name xcsoar-postgis \
	--shm-size=2g \
	-e POSTGRES_USER=osmuser \
	-e POSTGRES_PASSWORD=newgis23 \
	-e POSTGRES_DB=osm \
	-e POSTGRES_INITDB_ARGS="--encoding=UTF8" \
	-p 5432:5432 \
	-v xcsoar-postgis-data:/var/lib/postgresql/data \
	postgis/postgis:16-3.5

until docker exec xcsoar-postgis pg_isready -U osmuser -d osm >/dev/null 2>&1; do
	sleep 1
done

docker exec xcsoar-postgis psql -U osmuser -d osm \
	-c "CREATE EXTENSION IF NOT EXISTS hstore;"

echo "PostGIS is ready on localhost:5432 (user osmuser, database osm)."
