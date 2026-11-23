#!/usr/bin/env python3
"""agreement_check.py: the two observers' cover estimates per quadrat, against the agreed margin.

  python3 -B example/analysis/agreement_check.py                       the season's table
  python3 -B example/analysis/agreement_check.py --recount FILE        with a recount table applied

Reads analysis/derived/cover_by_quadrat.csv (boulder, quadrat, observer_a, observer_b; percent cover, whole
points). With --recount, a table with the columns quadrat, observer_a and observer_b replaces the two estimates
of each quadrat it lists. A quadrat is disputed when its two estimates differ by more than MARGIN points, the
margin the program agreed for the season. Prints one summary line and each disputed quadrat.

Exit 0: no quadrat disputed. Exit 1: one or more disputed. Exit 2: a table is missing, empty or malformed.
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
TABLE = HERE / "derived" / "cover_by_quadrat.csv"
MARGIN = 10


def read(path: pathlib.Path, keys: tuple[str, ...]) -> dict[str, tuple[int, int]] | None:
    try:
        with path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
    except OSError:
        return None
    if not rows or any(k not in rows[0] for k in keys):
        return None
    try:
        return {r["quadrat"]: (int(r["observer_a"]), int(r["observer_b"])) for r in rows}
    except (TypeError, ValueError):
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--recount")
    a = ap.parse_args()
    table = read(TABLE, ("quadrat", "observer_a", "observer_b"))
    if table is None:
        print("[agreement_check] %s missing, empty or malformed: NOT CHECKED" % TABLE.name)
        return 2
    if a.recount:
        recount = read(pathlib.Path(a.recount), ("quadrat", "observer_a", "observer_b"))
        if recount is None:
            print("[agreement_check] %s missing, empty or malformed: NOT CHECKED" % a.recount)
            return 2
        unknown = sorted(set(recount) - set(table))
        if unknown:
            print("[agreement_check] recount names quadrats not in the season's table: %s" % ", ".join(unknown))
            return 2
        table.update(recount)
    disputed = {q: v for q, v in sorted(table.items()) if abs(v[0] - v[1]) > MARGIN}
    print("[agreement_check] %d quadrats, margin %d points%s: %d disputed"
          % (len(table), MARGIN, " (recount applied)" if a.recount else "", len(disputed)))
    for q, (x, y) in disputed.items():
        print("  %s  observer_a %d  observer_b %d  difference %d" % (q, x, y, abs(x - y)))
    return 1 if disputed else 0


if __name__ == "__main__":
    sys.exit(main())
