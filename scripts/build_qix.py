#!/usr/bin/python3
"""Build MapServer-style .qix spatial indexes for exported shapefiles."""

from dbutil import ensure_qix_indexes

if __name__ == "__main__":
    ensure_qix_indexes()
