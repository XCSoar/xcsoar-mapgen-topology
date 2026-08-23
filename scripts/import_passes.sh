#!/bin/bash
# Extract mountain_pass=yes nodes from the Alps PBF into mp_* tables.
# Does not replace planet_osm_* (osm2pgsql --prefix mp).
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
PBF="$REPO_ROOT/osm/ALPS_HighRes.osm.pbf"
OUT="$REPO_ROOT/osm/passes.osm.pbf"
STYLE="$REPO_ROOT/conf/passes.style"
CONFIG="$REPO_ROOT/conf/config.ini"

if [[ ! -f "$PBF" ]]; then
  echo "Missing $PBF — run download_alps_osm.sh first." >&2
  exit 1
fi

if [[ -z "${PGPASSWORD:-}" && -f "$CONFIG" ]]; then
  PGPASSWORD=$(awk -F= '/^password=/{print $2; exit}' "$CONFIG")
  export PGPASSWORD
fi

echo "Filtering mountain passes from $(basename "$PBF")..."
osmium tags-filter "$PBF" n/mountain_pass=yes -o "$OUT" --overwrite

echo "Importing into mp_point..."
osm2pgsql \
  --prefix mp \
  --slim --drop \
  -c \
  -C 1000 \
  --number-processes "$(nproc)" \
  -U osmuser -d osm -H 127.0.0.1 \
  -S "$STYLE" \
  "$OUT"

echo "Wrote mp_point from $OUT"
