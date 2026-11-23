"""The data boundary and the spawn rule, on synthetic tool calls, through the pre-tool hook as a harness runs it.

The hook reads the proposed call as JSON on stdin and answers by exit code: 0 the call may run, 2 it is
refused. Run from the repository root:

    python3 -B -m unittest discover -s tests -v
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "checks"))

import agent_defs_check  # noqa: E402
from workspace import config, models  # noqa: E402

CFG = config()
SPAWN = CFG["agents"]["spawn"]["tool_names"][0]
TYPE_KEY = CFG["agents"]["spawn"]["type_keys"][0]
MODEL_KEY = CFG["agents"]["spawn"]["model_keys"][0]
HELPER = CFG["agents"]["helper_type"]


def hook(agent: str, tool: str, tool_input: dict) -> int:
    call = json.dumps({"tool_name": tool, "tool_input": tool_input})
    r = subprocess.run([sys.executable, "-B", "checks/boundary_hook.py", "--agent", agent], input=call,
                       capture_output=True, text=True, cwd=REPO, timeout=60)
    return r.returncode


class TestDataBoundary(unittest.TestCase):
    """Every protected tree is refused to every agent, by path or inside a command."""

    def test_a_path_into_each_protected_tree_is_refused(self) -> None:
        for tree in CFG["protected_trees"]:
            for agent in CFG["agents"]["types"]:
                with self.subTest(tree=tree, agent=agent):
                    self.assertEqual(hook(agent, "read", {"path": tree.strip("/") + "/item.csv"}), 2)

    def test_a_command_that_names_the_tree_is_refused(self) -> None:
        tree = CFG["protected_trees"][0].strip("/")
        last = tree.split("/")[-1]
        for command in ("cat ./%s/x" % tree, "cd %s && ls %s" % (tree.rsplit("/", 1)[0], last)):
            with self.subTest(command=command):
                self.assertEqual(hook("fact-checker", "shell-read", {"command": command}), 2)

    def test_a_search_that_only_excludes_the_tree_is_allowed(self) -> None:
        last = CFG["protected_trees"][0].strip("/").split("/")[-1]
        command = "grep -r moss . --exclude-dir=%s" % last
        self.assertEqual(hook("fact-checker", "shell-read", {"command": command}), 0)

    def test_an_ordinary_path_is_allowed(self) -> None:
        self.assertEqual(hook("fact-checker", "read", {"path": "records/notes.md"}), 0)


class TestSpawnRule(unittest.TestCase):
    """A subagent may spawn only the helper, with no model named; the helper spawns nothing."""

    def test_a_subagent_may_spawn_the_helper(self) -> None:
        self.assertEqual(hook("fact-checker", SPAWN, {TYPE_KEY: HELPER}), 0)

    def test_a_subagent_may_not_name_a_model(self) -> None:
        self.assertEqual(hook("fact-checker", SPAWN, {TYPE_KEY: HELPER, MODEL_KEY: "any"}), 2)

    def test_a_subagent_may_not_spawn_another_subagent(self) -> None:
        self.assertEqual(hook("fact-checker", SPAWN, {TYPE_KEY: "evaluator"}), 2)

    def test_the_helper_may_not_spawn(self) -> None:
        self.assertEqual(hook(HELPER, SPAWN, {TYPE_KEY: HELPER}), 2)

    def test_the_orchestrator_may_spawn_any_type_but_not_name_a_model(self) -> None:
        self.assertEqual(hook("orchestrator", SPAWN, {TYPE_KEY: "evaluator"}), 0)
        self.assertEqual(hook("orchestrator", SPAWN, {TYPE_KEY: "evaluator", MODEL_KEY: "any"}), 2)


class TestAgentDefinitions(unittest.TestCase):
    """Every definition parses, pins its tier, declares the hook and carries the identical standing rules."""

    def test_every_definition_passes_every_leg(self) -> None:
        fails, read = agent_defs_check.legs(CFG, models()["tiers"])
        self.assertEqual(read, len(CFG["agents"]["types"]))
        self.assertEqual(fails, [])


if __name__ == "__main__":
    unittest.main()
