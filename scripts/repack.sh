#!/bin/sh

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

tmp_dir=$(mktemp -d)
xcm_dir=$(mktemp -d)
unzip -d "$xcm_dir" "$REPO_ROOT/xcm/ALPS_HighRes.xcm"

# delete topology files
cp "$xcm_dir"/terrain.* "$tmp_dir"/

cp "$SCRIPT_DIR"/out/* "$REPO_ROOT/topology/topology.tpl" "$tmp_dir"

rm -f ~/.xcsoar/ALPS_Test.xcm waypoints.cup

(
	cd "$tmp_dir" || exit
	zip -0 ~/.xcsoar/ALPS_Test.xcm ./*
)

rm -rf "$tmp_dir" "$xcm_dir"
