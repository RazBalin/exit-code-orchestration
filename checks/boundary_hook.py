#!/usr/bin/env python3
"""boundary_hook.py: the pre-tool hook that enforces the data boundary and the spawn rule.

Wire it as the pre-tool-use hook of your agent harness. The harness passes the proposed tool call on
stdin as JSON, {"tool_name": ..., "tool_input": {...}}; the hook answers by exit code:

  exit 0  the call may run
  exit 2  the call is refused; the reason is printed on stderr, starting "BOUNDARY:" or "SPAWN:"

Refused, for every agent: any string in the tool input that names a protected tree of
config/workspace.json ("protected_trees"), by its last folder name standing alone as a path component,
e.g. data/field_raw/plot_07.csv, 'cat ./data/field_raw/x' or 'cd data && ls field_raw'. A search that only
excludes the tree (--exclude-dir=field_raw) is not refused.

Refused, by the spawn rule (--agent TYPE names the calling agent): a subagent may spawn only the
helper type, with no model or tier named (so the helper's pinned tier holds); the helper may spawn
nothing. The orchestrator runs the hook with --agent orchestrator and may spawn any type,
also with no model or tier named.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

from workspace import config


def strings(obj) -> list[str]:
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, dict):
        return [s for v in obj.values() for s in strings(v)]
    if isinstance(obj, list):
        return [s for v in obj for s in strings(v)]
    return []


def names_tree(text: str, tree: str) -> bool:
    """True when the text names the tree's path, or its last folder name standing alone (so that
    'cd data && cat field_raw/x' is caught). Give protected trees distinctive folder names."""
    text = re.sub(r"--exclude(?:-dir)?[= ](?:'[^']*'|\"[^\"]*\"|\S+)", " ", text)
    last = re.escape(tree.strip("/").split("/")[-1])
    return re.search(r"(?<![\w.-])" + last + r"(?![\w.-])", text, re.I) is not None


def decide(call: dict, agent: str, cfg: dict) -> tuple[int, str]:
    tool = call.get("tool_name") or ""
    tin = call.get("tool_input") or {}
    for s in strings(tin):
        for tree in cfg["protected_trees"]:
            if names_tree(s, tree):
                return 2, ("BOUNDARY: this call names the protected tree %s/, which no agent opens, lists or "
                           "searches. Work from records and derived artifacts instead." % tree.strip("/"))
    spawn = cfg["agents"]["spawn"]
    if tool in spawn["tool_names"]:
        target = next((tin.get(k) for k in spawn["type_keys"] if tin.get(k)), "")
        named_model = any(tin.get(k) for k in spawn["model_keys"])
        helper = cfg["agents"]["helper_type"]
        if agent == helper:
            return 2, "SPAWN: the helper spawns nothing. Do the task yourself."
        if named_model:
            return 2, "SPAWN: a spawn names no model or tier; the definition's pinned tier holds."
        if agent != "orchestrator" and target != helper:
            return 2, "SPAWN: a subagent may spawn only '%s'. Do the task yourself." % helper
        if target not in cfg["agents"]["types"]:
            return 2, "SPAWN: '%s' is not a defined agent type." % target
    return 0, ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--agent", required=True)
    a = ap.parse_args()
    try:
        call = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.stderr.write("BOUNDARY: the hook could not read the tool call; refused.\n")
        return 2
    rc, why = decide(call, a.agent, config())
    if why:
        sys.stderr.write(why + "\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
