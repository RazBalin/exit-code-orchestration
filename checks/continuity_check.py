#!/usr/bin/env python3
"""continuity_check.py: the continuity budgets, the findings register's structure and the clocks.

Reads, under the workspace root (config/workspace.json "workspace_root", or --root):

  CONTINUITY.md  at most budgets.continuity_chars characters; at most budgets.close_summaries_max close
                 summaries, each at most budgets.close_summary_chars. A close summary is a paragraph
                 opening with **CLOSE · YYYY-MM-DD.
  FINDINGS.md    blocks "### F-YYYY-MM-DD-SESSION-NN" followed by six keys in order (state, owner,
                 session, source, statement, closure), one per line; state is OPEN, QUEUED, CLOSED or
                 DROPPED; a CLOSED or DROPPED item carries a closure; ids are unique. Advisory: an OPEN
                 item older than budgets.open_finding_stale_days.
  CLOCKS.md      table rows "| YYYY-MM-DD | item | owner | source | status |"; rows whose status is
                 DONE or DROPPED are skipped; the rest are listed OVERDUE or SOON (within
                 clock_horizon_days). Clocks are information, never a failure.

Exit 0: budgets and structure hold. Exit 1: a budget or a structural rule is broken. Exit 2: the
continuity file is missing or empty. --today YYYY-MM-DD fixes the date; --selftest runs synthetic cases.
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import shutil
import sys
import tempfile
from collections.abc import Callable

from workspace import REPO, config

KEYS = ("state", "owner", "session", "source", "statement", "closure")
STATES = ("OPEN", "QUEUED", "CLOSED", "DROPPED")
CLOSE_RE = re.compile(r"^\*\*CLOSE · \d{4}-\d{2}-\d{2}")
ITEM_RE = re.compile(r"^### (F-(\d{4}-\d{2}-\d{2})-[A-Za-z0-9]+-\d{2,})\s*$")
ROW_RE = re.compile(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|")


def check_continuity(text: str, b: dict) -> tuple[list[str], list[str]]:
    errs = []
    info = ["continuity file: %d characters (budget %d)" % (len(text), b["continuity_chars"])]
    if len(text) > b["continuity_chars"]:
        errs.append("continuity file over budget: %d > %d" % (len(text), b["continuity_chars"]))
    summaries = [p for p in re.split(r"\n\s*\n", text) if CLOSE_RE.match(p.strip())]
    info.append("close summaries: %d (at most %d)" % (len(summaries), b["close_summaries_max"]))
    if len(summaries) > b["close_summaries_max"]:
        errs.append("%d close summaries; at most %d" % (len(summaries), b["close_summaries_max"]))
    for s in summaries:
        if len(s) > b["close_summary_chars"]:
            errs.append("close summary '%s' is %d characters, over %d"
                        % (s.strip()[:30], len(s), b["close_summary_chars"]))
    return errs, info


def check_findings(text: str, today: dt.date, stale_days: int) -> tuple[list[str], list[str]]:
    errs, info, stale, seen = [], [], [], set()
    counts = {s: 0 for s in STATES}
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        m = ITEM_RE.match(lines[i])
        if not m:
            i += 1
            continue
        fid, date = m.group(1), m.group(2)
        if fid in seen:
            errs.append("%s appears twice" % fid)
        seen.add(fid)
        values = {}
        for key, line in zip(KEYS, lines[i + 1:i + 1 + len(KEYS)]):
            if not line.startswith(key + ":"):
                errs.append("%s: expected '%s:', found '%s'" % (fid, key, line[:30]))
                break
            values[key] = line[len(key) + 1:].strip()
        else:
            state = values["state"]
            if state not in STATES:
                errs.append("%s: state '%s' not in %s" % (fid, state, "/".join(STATES)))
            else:
                counts[state] += 1
                if state in ("CLOSED", "DROPPED") and not values["closure"]:
                    errs.append("%s: %s without a closure" % (fid, state))
                if state == "OPEN" and (today - dt.date.fromisoformat(date)).days > stale_days:
                    stale.append(fid)
        i += 1 + len(KEYS)
    info.append("findings: %d (%s)" % (sum(counts.values()), ", ".join("%s %d" % kv for kv in counts.items())))
    if stale:
        info.append("advisory: OPEN for more than %d days: %s" % (stale_days, ", ".join(stale)))
    return errs, info


def clocks(text: str, today: dt.date, horizon: int) -> list[str]:
    rows = []
    for line in text.split("\n"):
        m = ROW_RE.match(line.strip())
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[-1].upper() in ("DONE", "DROPPED"):
            continue
        when = dt.date.fromisoformat(m.group(1))
        delta = (when - today).days
        item = cells[1] if len(cells) > 1 else ""
        owner = cells[2] if len(cells) > 2 else ""
        if delta < 0:
            rows.append("OVERDUE %s (%d days): %s [%s]" % (when, -delta, item, owner))
        elif delta <= horizon:
            rows.append("SOON    %s (in %d days): %s [%s]" % (when, delta, item, owner))
    return sorted(rows, key=lambda r: r[8:18])


def run(root: pathlib.Path, today: dt.date, cfg: dict, quiet: bool = False) -> int:
    cont = root / cfg["continuity_file"]
    if not cont.exists() or not cont.read_text(encoding="utf-8").strip():
        print("[continuity_check] %s missing or empty: NOT CLEAN" % cont)
        return 2
    b = cfg["budgets"]
    errs, info = check_continuity(cont.read_text(encoding="utf-8"), b)
    reg = root / cfg["findings_register"]
    if reg.exists():
        e2, i2 = check_findings(reg.read_text(encoding="utf-8"), today, b["open_finding_stale_days"])
        errs, info = errs + e2, info + i2
    else:
        errs.append("%s missing" % cfg["findings_register"])
    clk = root / cfg["clocks_file"]
    rows = clocks(clk.read_text(encoding="utf-8"), today, cfg["clock_horizon_days"]) if clk.exists() else []
    if not quiet:
        for line in info:
            print("  " + line)
        print("  clocks (today %s, overdue or within %d days): %d" % (today, cfg["clock_horizon_days"], len(rows)))
        for r in rows:
            print("    " + r)
        for e in errs:
            print("FAIL: " + e)
    print("[continuity_check] %s" % ("PASS" if not errs else "FAIL (%d)" % len(errs)))
    return 1 if errs else 0


def selftest_cases() -> list[tuple[str, Callable[[], str | None]]]:
    """The synthetic cases, each a (name, function) pair; the function returns None on a pass, else what failed.

    Each case builds its own temporary workspace. --selftest runs them all; tests/test_selftests.py exposes
    each one as a unittest test.
    """
    today = dt.date(2025, 3, 14)
    good_cont = "# State\n\n**CLOSE · 2025-03-14 (S07).** Goal reached.\n"
    good_reg = ("### F-2025-03-14-S07-01\nstate: OPEN\nowner: investigator\nsession: S07\n"
                "source: x\nstatement: y\nclosure:\n")
    good_clk = ("| date | item | owner | source | status |\n|---|---|---|---|---|\n"
                "| 2025-03-01 | past | a | s | OPEN |\n| 2025-03-20 | near | a | s | OPEN |\n"
                "| 2025-09-01 | far | a | s | OPEN |\n| 2025-03-02 | done | a | s | DONE |\n")

    def exits(want: int, why: str, cont=None, reg=None) -> Callable[[], str | None]:
        def case() -> str | None:
            cfg = config()
            body = cont(cfg) if callable(cont) else (good_cont if cont is None else cont)
            tmp = pathlib.Path(tempfile.mkdtemp(prefix="continuity_"))
            try:
                (tmp / cfg["continuity_file"]).write_text(body, encoding="utf-8")
                (tmp / cfg["findings_register"]).write_text(good_reg if reg is None else reg, encoding="utf-8")
                (tmp / cfg["clocks_file"]).write_text(good_clk, encoding="utf-8")
                got = run(tmp, today, cfg, quiet=True)
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
            return None if got == want else "%s: exit %d, expected %d" % (why, got, want)
        return case

    def clock_rows() -> str | None:
        rows = clocks(good_clk, today, config()["clock_horizon_days"])
        ok = len(rows) == 2 and rows[0].startswith("OVERDUE") and rows[1].startswith("SOON")
        return None if ok else "clocks: %r" % rows

    closed_bare = ("### F-2025-03-14-S07-01\nstate: CLOSED\nowner: a\nsession: S07\nsource: x\n"
                   "statement: y\nclosure:\n")

    def too_many(cfg: dict) -> str:
        return "".join("**CLOSE · 2025-03-1%d.** x\n\n" % k for k in range(cfg["budgets"]["close_summaries_max"] + 1))

    def over(cfg: dict) -> str:
        return "x" * (cfg["budgets"]["continuity_chars"] + 1)

    return [
        ("a clean workspace passes", exits(0, "a clean workspace")),
        ("clocks list the overdue and the near, not the far or the done", clock_rows),
        ("a CLOSED finding without a closure is caught", exits(1, "CLOSED without a closure", reg=closed_bare)),
        ("too many close summaries are caught", exits(1, "too many close summaries", cont=too_many, reg="")),
        ("an over-budget continuity file is caught", exits(1, "an over-budget continuity file", cont=over, reg="")),
        ("an empty continuity file exits 2", exits(2, "an empty continuity file", cont="  \n", reg="")),
    ]


def selftest() -> int:
    fails = [msg for msg in (case() for _, case in selftest_cases()) if msg]
    for f in fails:
        print("FAIL:", f)
    print("[continuity_check] selftest: %s (%d failure(s))" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root")
    ap.add_argument("--today")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    cfg = config()
    root = pathlib.Path(a.root) if a.root else REPO / cfg["workspace_root"]
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    return run(root, today, cfg)


if __name__ == "__main__":
    sys.exit(main())
