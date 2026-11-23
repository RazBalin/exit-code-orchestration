#!/usr/bin/env python3
"""agent_defs_check.py: the agent definitions parse, pin, refuse what they must, and share their rules.

For every type in config/workspace.json agents.types, agents/TYPE.md must exist and pass four legs:

  PARSE  the front matter parses (flat 'key: value'); name equals the file stem.
  PINS   tier exists in config/models.json; a subagent's tier is "subagent", the helper's "helper";
         writes is "none"; every tool is in agents.read_only_tools; a subagent may spawn only the helper,
         the helper nothing.
  HOOK   the definition's pre_tool_hook, run on synthetic tool calls: a path into a protected tree is
         refused (exit 2), a search that only excludes the tree is allowed, an ordinary path is
         allowed; a subagent's spawn of the helper is allowed, with a model named or of another type is
         refused; any spawn by the helper is refused.
  RULES  the block from "STANDING RULES, VERBATIM." to the end of the file is byte-identical across all
         definitions, so a rule changed in one place is changed everywhere or the check fails.

Exit 0 all legs pass; 1 a leg fails; 2 no definition was read.
"""
from __future__ import annotations

import json
import shlex
import subprocess
import sys

from workspace import REPO, config, front_matter, models

RULES_MARK = "STANDING RULES, VERBATIM."


def run_hook(cmd: str, call: dict) -> int:
    argv = shlex.split(cmd)
    if argv and argv[0] == "python3":
        argv[0] = sys.executable
    r = subprocess.run(argv, input=json.dumps(call), capture_output=True, text=True, cwd=REPO, timeout=60)
    return r.returncode


def legs(cfg: dict, tiers: dict) -> tuple[list[str], int]:
    fails, read, rules = [], 0, {}
    ag = cfg["agents"]
    helper = ag["helper_type"]
    tree = cfg["protected_trees"][0].strip("/")
    spawn_tool, type_key, model_key = ag["spawn"]["tool_names"][0], ag["spawn"]["type_keys"][0], ag["spawn"]["model_keys"][0]
    for name in ag["types"]:
        path = REPO / "agents" / ("%s.md" % name)
        if not path.exists():
            fails.append("%s: missing" % name)
            continue
        text = path.read_text(encoding="utf-8")
        read += 1
        try:
            fm, _ = front_matter(text)
        except ValueError as e:
            fails.append("%s: PARSE %s" % (name, e))
            continue
        if fm.get("name") != name:
            fails.append("%s: PARSE name is %r" % (name, fm.get("name")))
        want_tier = "helper" if name == helper else "subagent"
        if fm.get("tier") != want_tier or want_tier not in tiers:
            fails.append("%s: PINS tier %r, expected %r (and present in models.json)" % (name, fm.get("tier"), want_tier))
        if fm.get("writes") != "none":
            fails.append("%s: PINS writes %r, expected 'none'" % (name, fm.get("writes")))
        tools = fm.get("tools") or []
        extra = [t for t in tools if t not in ag["read_only_tools"]]
        if not tools or extra:
            fails.append("%s: PINS tools %r (not read-only: %r)" % (name, tools, extra))
        want_spawn = [] if name == helper else [helper]
        if (fm.get("may_spawn") or []) != want_spawn:
            fails.append("%s: PINS may_spawn %r, expected %r" % (name, fm.get("may_spawn"), want_spawn))
        hook = fm.get("pre_tool_hook") or ""
        if not hook:
            fails.append("%s: HOOK none declared" % name)
        else:
            cases = [({"tool_name": "read", "tool_input": {"path": "%s/plot_07.csv" % tree}}, 2),
                     ({"tool_name": "shell-read", "tool_input": {"command": "cat ./%s/x" % tree}}, 2),
                     ({"tool_name": "shell-read", "tool_input": {"command": "grep -r moss . --exclude-dir=%s"
                                                                 % tree.split("/")[-1]}}, 0),
                     ({"tool_name": "read", "tool_input": {"path": "records/notes.md"}}, 0)]
            if name == helper:
                cases.append(({"tool_name": spawn_tool, "tool_input": {type_key: helper}}, 2))
            else:
                cases += [({"tool_name": spawn_tool, "tool_input": {type_key: helper}}, 0),
                          ({"tool_name": spawn_tool, "tool_input": {type_key: helper, model_key: "x"}}, 2),
                          ({"tool_name": spawn_tool, "tool_input": {type_key: "evaluator"}}, 2)]
            for call, want in cases:
                got = run_hook(hook, call)
                if got != want:
                    fails.append("%s: HOOK %s exit %d, expected %d" % (name, call["tool_input"], got, want))
        for c in cfg["outbound"]["blocked_characters"]:
            if c in text:
                fails.append("%s: a blocked character" % name)
        i = text.find(RULES_MARK)
        rules[name] = text[i:] if i != -1 else None
    if any(v is None for v in rules.values()):
        fails.append("RULES: a definition lacks the standing-rules block")
    elif len(set(rules.values())) > 1:
        fails.append("RULES: the standing-rules block differs across definitions")
    return fails, read


def main() -> int:
    cfg = config()
    fails, read = legs(cfg, models()["tiers"])
    if read == 0:
        print("[agent_defs_check] read 0 definitions: NOT CLEAN")
        return 2
    for f in fails:
        print("FAIL: " + f)
    print("[agent_defs_check] %d definitions read: %s" % (read, "PASS" if not fails else "FAIL (%d)" % len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
