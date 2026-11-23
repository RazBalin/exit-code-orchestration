"""Each check's synthetic cases as unittest tests: one test per case, the same cases --selftest runs.

The cases live in each check's selftest_cases(); this module only exposes them, so a case added to a
check is a test here without further edits. Run from the repository root:

    python3 -B -m unittest discover -s tests -v
"""
from __future__ import annotations

import contextlib
import io
import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "checks"))

import context_gauge  # noqa: E402
import continuity_check  # noqa: E402
import launch_gate  # noqa: E402
import outbound_audit  # noqa: E402

MODULES = (outbound_audit, continuity_check, launch_gate, context_gauge)


def _test(case):
    def test(self: unittest.TestCase) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            failure = case()
        self.assertIsNone(failure, failure)
    return test


def _test_class(module) -> type:
    attrs: dict = {}
    for name, case in module.selftest_cases():
        slug = "test_" + re.sub(r"\W+", "_", name.lower()).strip("_")
        while slug in attrs:
            slug += "_"
        method = _test(case)
        method.__doc__ = name
        attrs[slug] = method
    return type("Test_" + module.__name__, (unittest.TestCase,), attrs)


for _module in MODULES:
    globals()["Test_" + _module.__name__] = _test_class(_module)


class TestSelftestEntryPoints(unittest.TestCase):
    """Each check's --selftest still runs its cases and returns 0."""

    def test_every_selftest_returns_0(self) -> None:
        for module in MODULES:
            with self.subTest(check=module.__name__):
                self.assertGreater(len(module.selftest_cases()), 0)
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(module.selftest(), 0)


if __name__ == "__main__":
    unittest.main()
