#!/bin/bash
# Download OSM extracts that together cover ALPS_HighRes.xcm.
#
# ALPS_HighRes info.txt:
#   longitude range: 4.5 to 16.5
#   latitude range:  43.4 to 49.0
#
# Geofabrik's europe/alps extract is the mountain range, not the map
# rectangle: it cuts through the Swiss plateau (Zürich, Bern, Basel,
# Lausanne are outside) and the northern Austrian foreland. Country
# extracts fill those holes. Reduce scripts clip to the rectangle in
# PostGIS; do not osmium-extract first (that drops the same holes if
# the source poly never contained them).
#
# Overlapping PBFs must be merged with osmium before osm2pgsql.
# Do not osm2pgsql --append a second extract: shared OSM IDs duplicate.

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

OSM_DIR="$REPO_ROOT/osm"
SRC_DIR="$OSM_DIR/geofabrik"
OUT_PBF="$OSM_DIR/ALPS_HighRes.osm.pbf"
BASE="https://download.geofabrik.de"

EXTRACTS=(
  europe/alps-latest.osm.pbf
  europe/switzerland-latest.osm.pbf
  europe/austria-latest.osm.pbf
  europe/germany/bayern-latest.osm.pbf
  europe/germany/baden-wuerttemberg-latest.osm.pbf
  europe/france/rhone-alpes-latest.osm.pbf
  europe/france/bourgogne-latest.osm.pbf
  europe/france/franche-comte-latest.osm.pbf
  europe/france/alsace-latest.osm.pbf
  europe/france/provence-alpes-cote-d-azur-latest.osm.pbf
  europe/france/languedoc-roussillon-latest.osm.pbf
)

mkdir -p "$SRC_DIR"

for rel in "${EXTRACTS[@]}"; do
  dest="$SRC_DIR/$(basename "$rel")"
  echo "Downloading $rel"
  wget -c -O "$dest" "$BASE/$rel"
done

# osmium merge of overlapping extracts keeps every object version;
# osm2pgsql then fails with "node id N appears more than once".
echo "Merging extracts..."
MERGED="$OSM_DIR/ALPS_HighRes-merged.osm.pbf"
SORTED="$OSM_DIR/ALPS_HighRes-sorted.osm.pbf"
osmium merge "${SRC_DIR}"/*.osm.pbf -o "$MERGED" --overwrite

echo "Sorting and keeping the latest version of each object..."
TMPDIR="$OSM_DIR" osmium sort "$MERGED" -o "$SORTED" --overwrite
python3 "$SCRIPT_DIR/pbf_keep_latest.py" "$SORTED" "$OUT_PBF"
rm -f "$MERGED" "$SORTED"

osmium fileinfo -e "$OUT_PBF"
echo "Wrote $OUT_PBF"
