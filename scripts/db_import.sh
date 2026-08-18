#!/bin/bash
# Import one OSM PBF into PostGIS (create mode).
# Do not use --flat-nodes on regional extracts: OSM node IDs are global
# and the file grows to tens of GB. Do not --append overlapping extracts;
# osmium merge them first.

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 file.osm.pbf" >&2
  exit 1
fi

CONFIG="$REPO_ROOT/conf/config.ini"
if [[ -z "${PGPASSWORD:-}" && -f "$CONFIG" ]]; then
  PGPASSWORD=$(awk -F= '/^password=/{print $2; exit}' "$CONFIG")
  export PGPASSWORD
fi

osm2pgsql \
  --slim --drop \
  -C 8000 \
  --number-processes "$(nproc)" \
  -U osmuser -d osm -H 127.0.0.1 \
  -S "$REPO_ROOT/conf/default.style" \
  -c "$1"
