#!/usr/bin/env python3
"""context_gauge.py: how full a session's context is, its headroom, and the act its band asks for.

Recall degrades as a context fills, so a session reads this gauge at every natural boundary and
before any step expected to be large, and it plans its compaction instead of meeting it. The session
decides and prepares; the gauge never asks anyone whether to compact.

Input, model-agnostic (the harness supplies the count):
  --tokens N            the session's current context size in tokens, or
  --usage-file PATH     a JSON object: "context_tokens" if present, else the sum of every integer
                        field whose name ends in "_tokens".
  --role                orchestrator or worker (bands differ: an orchestrator closes earlier, because
                        its close integrates more).
  --window N            the context window; default config gauge.window_tokens.

Bands are fractions of the window (config gauge.bands): WORK, PLAN, NOTE, CLOSE, IMMINENT.
Output: one line, the band, the headroom and the act. Exit 0 with a verdict; 2 when nothing was read.
--selftest runs synthetic readings.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections.abc import Callable

from workspace import config

ORDER = ("plan", "note", "close", "imminent")
ACTS = {
    "WORK": "work freely; context is no reason to stop",
    "PLAN": "at the next natural boundary, close if what remains is a new task; otherwise sum the rest of "
            "the plan and the close, and write the compaction note if the sum exceeds the headroom",
    "NOTE": "write the compaction note now (where you stand, the record's state, the next three acts, what "
            "not to redo), then continue",
    "CLOSE": "the close artifacts come before anything else",
    "IMMINENT": "rewrite the compaction note now; open no new decision list or integration",
}


def reading(args) -> int | None:
    if args.tokens is not None:
        return args.tokens
    if args.usage_file:
        try:
            data = json.loads(pathlib.Path(args.usage_file).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if isinstance(data.get("context_tokens"), int):
            return data["context_tokens"]
        values = [v for k, v in data.items() if k.endswith("_tokens") and isinstance(v, int)]
        return sum(values) if values else None
    return None


def verdict(tokens: int, role: str, window: int, bands: dict) -> tuple[str, int, str]:
    band = "WORK"
    for name in ORDER:
        if tokens >= bands[role][name] * window:
            band = name.upper()
    return band, window - tokens, ACTS[band]


def selftest_cases() -> list[tuple[str, Callable[[], str | None]]]:
    """The synthetic cases, each a (name, function) pair; the function returns None on a pass, else what failed.

    --selftest runs them all; tests/test_selftests.py exposes each one as a unittest test.
    """
    window = 100_000

    def bands() -> dict:
        return config()["gauge"]["bands"]

    def at_zero(role: str) -> Callable[[], str | None]:
        def case() -> str | None:
            return None if verdict(0, role, window, bands())[0] == "WORK" else "%s: 0 tokens not WORK" % role
        return case

    def at_threshold(role: str, name: str) -> Callable[[], str | None]:
        def case() -> str | None:
            b = bands()
            at = int(b[role][name] * window)
            if verdict(at, role, window, b)[0] != name.upper():
                return "%s: %d tokens not %s" % (role, at, name.upper())
            if at > 0 and verdict(at - 1, role, window, b)[0] == name.upper():
                return "%s: %d tokens already %s" % (role, at - 1, name.upper())
            return None
        return case

    def closes_first() -> str | None:
        b = bands()
        return "the orchestrator closes later than a worker" if b["orchestrator"]["close"] > b["worker"]["close"] else None

    cases = []
    for role in ("orchestrator", "worker"):
        cases.append(("gauge %s at 0 tokens is WORK" % role, at_zero(role)))
        cases += [("gauge %s enters %s at its threshold, not before" % (role, name.upper()), at_threshold(role, name))
                  for name in ORDER]
    cases.append(("gauge: the orchestrator closes no later than a worker", closes_first))
    return cases


def selftest() -> int:
    fails = [msg for msg in (case() for _, case in selftest_cases()) if msg]
    for f in fails:
        print("FAIL:", f)
    print("[context_gauge] selftest: %s (%d failure(s))" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main() -> int:
    cfg = config()
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tokens", type=int)
    ap.add_argument("--usage-file")
    ap.add_argument("--role", choices=("orchestrator", "worker"), default="orchestrator")
    ap.add_argument("--window", type=int, default=cfg["gauge"]["window_tokens"])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    tokens = reading(a)
    if tokens is None:
        print("[context_gauge] no reading (give --tokens or a readable --usage-file): NOT MEASURED")
        return 2
    band, headroom, act = verdict(tokens, a.role, a.window, cfg["gauge"]["bands"])
    print("[context_gauge] %s %s: %d of %d tokens, headroom %d: %s" % (a.role, band, tokens, a.window, headroom, act))
    return 0


if __name__ == "__main__":
    sys.exit(main())
