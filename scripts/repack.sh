#!/bin/sh

tmp_dir=$(mktemp -d)
unzip -d "$tmp_dir" ../xcm/ALPS_HighRes.xcm

# delete topology files
find "$tmp_dir" \( -name '*.dbf' -o -name '*.prj' -o -name '*.qix' -o -name '*.shp' -o -name '*.shx' \) -delete

cp out/* topology.tpl "$tmp_dir"

rm -f ~/.xcsoar/ALPS_Test.xcm waypoints.cup

(
	cd "$tmp_dir" || exit
	zip -0 ~/.xcsoar/ALPS_Test.xcm ./*
)

rm -rf "$tmp_dir"
