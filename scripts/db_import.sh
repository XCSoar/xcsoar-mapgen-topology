#!/bin/bash
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

osm2pgsql --flat-nodes "$REPO_ROOT/flatnodes" --slim -U osmuser -W -d osm \
	-S "$REPO_ROOT/conf/default.style" -H localhost -c "$1"
