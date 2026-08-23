#!/usr/bin/python3

from dbutil import connect, in_map_bbox

conn = connect()
cur = conn.cursor()

cur.execute(
    """
    SELECT EXISTS (
      SELECT 1 FROM information_schema.tables
      WHERE table_schema = 'public' AND table_name = 'mp_point'
    )
    """
)
if not cur.fetchone()[0]:
    raise SystemExit("mp_point missing — run scripts/import_passes.sh first")

# Same idea as peaks: keep every high alpine col, and only the local high
# point among the rest. Name filter is Col/Colle/Passo/Pass/Joch (including
# German *pass), not every Sattel/Scharte. Snap-dedupe copies of the same
# col within ~400 m before the local-max test.
LOCAL_MAX_M = 12000
HIGH_ELE_M = 2000
MIN_ELE_M = 1000

cur.execute(
    f"""
DROP TABLE IF EXISTS tmp_named_passes;
CREATE TEMP TABLE tmp_named_passes AS
SELECT DISTINCT ON (
    floor(ST_X(way) / 500), floor(ST_Y(way) / 500), lower(name)
  )
  osm_id, way, name, m
FROM (
  SELECT osm_id, way, name,
    NULLIF(regexp_replace(ele, '[^0-9.\\-].*$', ''), '')::double precision AS m
  FROM mp_point
  WHERE {in_map_bbox()}
    AND mountain_pass = 'yes'
    AND name IS NOT NULL AND name <> ''
    AND name ~ '[A-Za-zÀ-ÿ]'
    AND name ~* '(col |colle |collado |passo |pass |joch|fuorcla|pass$)'
    AND name !~* '(sattel|scharte|forcella |bocchetta )'
    AND NULLIF(regexp_replace(ele, '[^0-9.\\-].*$', ''), '') IS NOT NULL
) s
WHERE m >= {MIN_ELE_M}
ORDER BY floor(ST_X(way) / 500), floor(ST_Y(way) / 500), lower(name), m DESC;
CREATE INDEX tmp_named_passes_gix ON tmp_named_passes USING GIST (way);

DROP TABLE IF EXISTS reduced_passes_high;
CREATE TABLE reduced_passes_high AS
SELECT way AS geom,
  name || ' ' || round(m)::int AS name
FROM tmp_named_passes
WHERE m >= {HIGH_ELE_M};

DROP TABLE IF EXISTS reduced_passes;
CREATE TABLE reduced_passes AS
SELECT p.way AS geom,
  p.name || ' ' || round(p.m)::int AS name
FROM tmp_named_passes p
WHERE p.m >= {MIN_ELE_M} AND p.m < {HIGH_ELE_M}
  AND NOT EXISTS (
    SELECT 1 FROM tmp_named_passes o
    WHERE o.osm_id <> p.osm_id
      AND o.m > p.m
      AND ST_DWithin(p.way, o.way, {LOCAL_MAX_M})
  );

CREATE INDEX reduced_passes_high_gix ON reduced_passes_high USING GIST (geom);
CREATE INDEX reduced_passes_gix ON reduced_passes USING GIST (geom);
"""
)
conn.commit()
cur.close()
conn.close()
