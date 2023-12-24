#!/bin/sh

tmp_dir=$(mktemp -d)
xcm_dir=$(mktemp -d)
unzip -d "$xcm_dir" ../xcm/ALPS_HighRes.xcm

# delete topology files
cp "$xcm_dir"/terrain.* "$tmp_dir"/

cp out/* ../topology/topology.tpl "$tmp_dir"

rm -f ~/.xcsoar/ALPS_Test.xcm waypoints.cup

(
	cd "$tmp_dir" || exit
	zip -0 ~/.xcsoar/ALPS_Test.xcm ./*
)

rm -rf "$tmp_dir" "$xcm_dir"
