#!/usr/bin/env python3
"""launch_gate.py: the gate a launch file passes before a worker session starts from it.

A launch file is the self-contained instruction a worker session reads first. The gate checks:
  at most budgets.launch_file_chars characters;
  exactly one "Tier: orchestrator" or "Tier: worker" line;
  exactly one "Writes:" line (the only paths the session may write);
  exactly one "Done when:" line (the completion condition);
  no character from outbound.blocked_characters.

Exit 0 PASS, 1 FAIL, 2 unreadable or empty. --selftest runs synthetic cases.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
from collections.abc import Callable

from workspace import config

LINES = {"Tier": re.compile(r"^Tier:\s*(orchestrator|worker)\b", re.M),
         "Writes": re.compile(r"^Writes:\s*\S", re.M),
         "Done when": re.compile(r"^Done when:\s*\S", re.M)}


def check(text: str, cfg: dict) -> list[str]:
    errs = []
    cap = cfg["budgets"]["launch_file_chars"]
    if len(text) > cap:
        errs.append("%d characters, over %d" % (len(text), cap))
    for name, rx in LINES.items():
        n = len(rx.findall(text))
        if n != 1:
            errs.append("%d '%s:' lines; exactly one is required" % (n, name))
    for c in cfg["outbound"]["blocked_characters"]:
        if c in text:
            errs.append("a blocked character, U+%04X" % ord(c))
    return errs


def selftest_cases() -> list[tuple[str, Callable[[], str | None]]]:
    """The synthetic cases, each a (name, function) pair; the function returns None on a pass, else what failed.

    --selftest runs them all; tests/test_selftests.py exposes each one as a unittest test.
    """
    good = "# Launch\n\nTier: worker\nWrites: records/S08/\nDone when: the report is saved.\n\nWork.\n"
    cases = {"good": (lambda cfg: good, []),
             "two tiers": (lambda cfg: good + "Tier: orchestrator\n", ["Tier"]),
             "no writes": (lambda cfg: good.replace("Writes: records/S08/\n", ""), ["Writes"]),
             "no done": (lambda cfg: good.replace("Done when: the report is saved.\n", ""), ["Done when"]),
             "blocked": (lambda cfg: good + "a " + chr(0xA7) + " b\n", ["blocked character"]),
             "long": (lambda cfg: good + "x" * cfg["budgets"]["launch_file_chars"], ["over"])}

    def make(name: str, body, want: list[str]) -> Callable[[], str | None]:
        def case() -> str | None:
            cfg = config()
            cfg["outbound"] = dict(cfg["outbound"], blocked_characters=[chr(0xA7)])
            errs = check(body(cfg), cfg)
            if not want and errs:
                return "%s: %r" % (name, errs)
            missing = [w for w in want if not any(w in e for e in errs)]
            return "%s: expected an error naming %r, got %r" % (name, missing, errs) if missing else None
        return case

    return [("launch file %s: %s" % (name, "passes" if not want else "fails on " + ", ".join(want)),
             make(name, body, want)) for name, (body, want) in cases.items()]


def selftest() -> int:
    fails = [msg for msg in (case() for _, case in selftest_cases()) if msg]
    for f in fails:
        print("FAIL:", f)
    print("[launch_gate] selftest: %s (%d failure(s))" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("launch_file", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.launch_file:
        ap.error("name a launch file")
    p = pathlib.Path(a.launch_file)
    try:
        text = p.read_text(encoding="utf-8")
    except OSError as e:
        print("[launch_gate] %s: UNREADABLE (%s)" % (p, e))
        return 2
    if not text.strip():
        print("[launch_gate] %s: empty; NOT CLEAN" % p)
        return 2
    errs = check(text, config())
    for e in errs:
        print("FAIL: " + e)
    print("[launch_gate] %s (%d characters): %s" % (p.name, len(text), "PASS" if not errs else "FAIL"))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
