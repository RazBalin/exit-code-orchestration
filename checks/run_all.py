#!/usr/bin/env python3
"""run_all.py: every check, on the example workspace, from the repository root. One line per leg.

  SELFTESTS   each check's synthetic cases: outbound_audit, continuity_check, launch_gate, context_gauge
  AGENTS      agent_defs_check over agents/
  CONTINUITY  continuity_check on example/ (dated 2025-03-14, the example's last session)
  LAUNCH      launch_gate on every LAUNCH_*.md under example/records/
  OUTBOUND    outbound_audit on every file under example/outbound/
  GAUGE       context_gauge on a sample reading
  HYGIENE     no invisible code point and no blocked character in any text file of the repository;
              every agent type in the configuration has its definition, and no definition is unlisted

Exit 0 when every leg passes; 1 otherwise. Usage: python3 -B checks/run_all.py
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

from workspace import REPO, config

CHECKS = REPO / "checks"
EXAMPLE_DAY = "2025-03-14"
TEXT = {".md", ".py", ".json", ".txt", ".cff", ".svg", ".yml", ".yaml", ".toml", ".gitignore", ""}
INVISIBLE = re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u2069\ufeff]")


def run(*argv: str) -> tuple[int, str]:
    p = subprocess.run([sys.executable, "-B", *argv], capture_output=True, text=True, cwd=REPO, timeout=300)
    out = (p.stdout + p.stderr).strip().splitlines()
    return p.returncode, out[-1] if out else ""


def leg_selftests(cfg) -> list[str]:
    errs = []
    for name in ("outbound_audit.py", "continuity_check.py", "launch_gate.py", "context_gauge.py"):
        rc, last = run(str(CHECKS / name), "--selftest")
        if rc != 0:
            errs.append("%s --selftest exit %d: %s" % (name, rc, last))
    return errs


def leg_agents(cfg) -> list[str]:
    rc, last = run(str(CHECKS / "agent_defs_check.py"))
    return [] if rc == 0 else ["agent_defs_check exit %d: %s" % (rc, last)]


def leg_continuity(cfg) -> list[str]:
    rc, last = run(str(CHECKS / "continuity_check.py"), "--today", EXAMPLE_DAY)
    return [] if rc == 0 else ["continuity_check exit %d: %s" % (rc, last)]


def leg_launch(cfg) -> list[str]:
    files = sorted((REPO / cfg["workspace_root"] / cfg["records_dir"]).rglob("LAUNCH_*.md"))
    if not files:
        return ["no launch file found under the example's records"]
    errs = []
    for f in files:
        rc, last = run(str(CHECKS / "launch_gate.py"), str(f))
        if rc != 0:
            errs.append("%s exit %d: %s" % (f.name, rc, last))
    return errs


def leg_outbound(cfg) -> list[str]:
    files = sorted(p for p in (REPO / cfg["workspace_root"] / cfg["outbound_dir"]).rglob("*") if p.is_file())
    if not files:
        return ["no outbound file found in the example"]
    errs = []
    for f in files:
        rc, last = run(str(CHECKS / "outbound_audit.py"), str(f))
        if rc != 0:
            errs.append("%s exit %d: %s" % (f.name, rc, last))
    return errs


def leg_gauge(cfg) -> list[str]:
    rc, last = run(str(CHECKS / "context_gauge.py"), "--tokens", "60000", "--role", "orchestrator")
    return [] if rc == 0 and "WORK" in last else ["context_gauge exit %d: %s" % (rc, last)]


def leg_hygiene(cfg) -> list[str]:
    errs = []
    blocked = cfg["outbound"]["blocked_characters"]
    for p in sorted(REPO.rglob("*")):
        parts = p.relative_to(REPO).parts
        if not p.is_file() or ".git" in parts or "__pycache__" in parts or p.suffix not in TEXT:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        rel = "/".join(parts)
        if INVISIBLE.search(text):
            errs.append("%s: an invisible code point" % rel)
        if any(c in text for c in blocked):
            errs.append("%s: a blocked character" % rel)
    listed = set(cfg["agents"]["types"])
    present = {p.stem for p in (REPO / "agents").glob("*.md")}
    for t in sorted(listed - present):
        errs.append("agent type %s has no definition" % t)
    for t in sorted(present - listed):
        errs.append("definition %s is not listed in the configuration" % t)
    return errs


def main() -> int:
    cfg = config()
    total = 0
    for name, fn in (("SELFTESTS", leg_selftests), ("AGENTS", leg_agents), ("CONTINUITY", leg_continuity),
                     ("LAUNCH", leg_launch), ("OUTBOUND", leg_outbound), ("GAUGE", leg_gauge),
                     ("HYGIENE", leg_hygiene)):
        try:
            errs = fn(cfg)
        except Exception as e:  # noqa: BLE001
            errs = ["crashed: %s" % e]
        print("%-11s %s" % (name, "PASS" if not errs else "FAIL"))
        for e in errs:
            print("            " + e)
        total += len(errs)
    print("[run_all] %s" % ("PASS" if not total else "FAIL (%d)" % total))
    return 0 if not total else 1


if __name__ == "__main__":
    sys.exit(main())
