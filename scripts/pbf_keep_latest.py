#!/usr/bin/python3
# Keep the highest version of each OSM object. Use after osmium merge of
# overlapping extracts (merge emits every version) and osmium sort.
# replace() is a shallow copy; copy tags/nodes/members into Python.

import sys

import osmium


def copy_node(n):
    loc = (n.lon, n.lat) if n.location.valid() else None
    return n.replace(tags=dict(n.tags), location=loc)


def copy_way(w):
    return w.replace(tags=dict(w.tags),
                     nodes=[nr.ref for nr in w.nodes])


def copy_relation(r):
    return r.replace(tags=dict(r.tags),
                     members=[(m.type, m.ref, m.role) for m in r.members])


class KeepHighestVersion(osmium.SimpleHandler):
    def __init__(self, writer):
        super().__init__()
        self.writer = writer
        self.pending_kind = None
        self.pending_id = None
        self.pending = None

    def _emit(self):
        if self.pending is None:
            return
        if self.pending_kind == "n":
            self.writer.add_node(self.pending)
        elif self.pending_kind == "w":
            self.writer.add_way(self.pending)
        else:
            self.writer.add_relation(self.pending)
        self.pending = None

    def _consider(self, kind, copy):
        if self.pending_kind == kind and self.pending_id == copy.id:
            self.pending = copy
            return
        self._emit()
        self.pending_kind = kind
        self.pending_id = copy.id
        self.pending = copy

    def node(self, n):
        self._consider("n", copy_node(n))

    def way(self, w):
        self._consider("w", copy_way(w))

    def relation(self, r):
        self._consider("r", copy_relation(r))

    def finish(self):
        self._emit()


def main():
    if len(sys.argv) != 3:
        print("Usage: pbf_keep_latest.py sorted.osm.pbf out.osm.pbf",
              file=sys.stderr)
        sys.exit(1)
    writer = osmium.SimpleWriter(sys.argv[2], overwrite=True)
    handler = KeepHighestVersion(writer)
    handler.apply_file(sys.argv[1])
    handler.finish()
    writer.close()


if __name__ == "__main__":
    main()
