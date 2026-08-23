#!/bin/bash
# Extract building/stadium polygons from the Alps PBF into bldg_* tables.
# Does not replace planet_osm_* (osm2pgsql --prefix bldg).
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
PBF="$REPO_ROOT/osm/ALPS_HighRes.osm.pbf"
OUT="$REPO_ROOT/osm/buildings.osm.pbf"
STYLE="$REPO_ROOT/conf/buildings.style"
CONFIG="$REPO_ROOT/conf/config.ini"

if [[ ! -f "$PBF" ]]; then
  echo "Missing $PBF — run download_alps_osm.sh first." >&2
  exit 1
fi

if [[ -z "${PGPASSWORD:-}" && -f "$CONFIG" ]]; then
  PGPASSWORD=$(awk -F= '/^password=/{print $2; exit}' "$CONFIG")
  export PGPASSWORD
fi

echo "Filtering buildings and stadiums from $(basename "$PBF")..."
osmium tags-filter "$PBF" \
  wr/building \
  wr/leisure=stadium \
  wr/leisure=sports_centre \
  wr/leisure=grandstand \
  -o "$OUT" --overwrite

echo "Importing into bldg_polygon..."
osm2pgsql \
  --prefix bldg \
  --slim --drop \
  -c \
  -C 4000 \
  --number-processes "$(nproc)" \
  -U osmuser -d osm -H 127.0.0.1 \
  -S "$STYLE" \
  "$OUT"

echo "Wrote bldg_polygon from $OUT"
