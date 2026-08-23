#!/bin/bash
# Replace topology in an existing .xcm, keeping its DEM (terrain.jp2).
#
# Usage: ./repack.sh [source.xcm] [dest.xcm]
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

SRC_XCM="${1:-}"
if [ -z "$SRC_XCM" ]; then
  for candidate in \
    "$REPO_ROOT/xcm/ALPS_HighRes.xcm" \
    "$HOME/.xcsoar/maps/ALPS_HighRes.xcm"
  do
    if [ -f "$candidate" ]; then
      SRC_XCM="$candidate"
      break
    fi
  done
fi

if [ -z "${SRC_XCM:-}" ] || [ ! -f "$SRC_XCM" ]; then
  echo "Need a source .xcm that contains terrain.jp2." >&2
  echo "Usage: $0 [source.xcm] [dest.xcm]" >&2
  exit 1
fi

OUT_DIR="$SCRIPT_DIR/out"
TPL="$REPO_ROOT/topology/topology.tpl"
DEST="${2:-$HOME/.xcsoar/maps/ALPS_Test.xcm}"

if [ ! -f "$TPL" ]; then
  echo "Missing $TPL" >&2
  exit 1
fi

if [ ! -d "$OUT_DIR" ] || [ -z "$(ls -A "$OUT_DIR" 2>/dev/null)" ]; then
  echo "No shapefiles in $OUT_DIR — run export first." >&2
  exit 1
fi

PYTHON=python3
if [ -x "$REPO_ROOT/bin/python3" ]; then
  PYTHON="$REPO_ROOT/bin/python3"
fi
"$PYTHON" "$SCRIPT_DIR/build_qix.py"
"$PYTHON" "$SCRIPT_DIR/check_topology.py"

tmp_dir=$(mktemp -d)
cleanup() { rm -rf "$tmp_dir"; }
trap cleanup EXIT

# Extract only the DEM and world file (and info.txt if present).
# -j: drop any directory prefix inside the zip.
if ! unzip -j -o "$SRC_XCM" terrain.jp2 terrain.j2w -d "$tmp_dir"; then
  echo "Failed to extract terrain.jp2 / terrain.j2w from $SRC_XCM" >&2
  exit 1
fi
unzip -j -o "$SRC_XCM" info.txt -d "$tmp_dir" 2>/dev/null || true

if [ ! -f "$tmp_dir/terrain.jp2" ] || [ ! -f "$tmp_dir/terrain.j2w" ]; then
  echo "Source $SRC_XCM is missing terrain.jp2 / terrain.j2w" >&2
  exit 1
fi

cp "$OUT_DIR"/* "$TPL" "$tmp_dir/"

mkdir -p "$(dirname "$DEST")"
rm -f "$DEST"

(
  cd "$tmp_dir"
  zip -0 -X "$DEST" *
)

# grep -q closes the pipe on the first hit; unzip then SIGPIPEs and
# pipefail treats that as a missing terrain.jp2.
if ! grep -F 'terrain.jp2' <<<"$(unzip -l "$DEST")" >/dev/null; then
  echo "Failed to pack terrain.jp2 into $DEST" >&2
  exit 1
fi

echo "Wrote $DEST (DEM from $SRC_XCM)"
"$PYTHON" "$SCRIPT_DIR/check_topology.py" "$DEST"
