# Contributing

Issues and pull requests are welcome on the repository's GitHub page.

## Before a pull request

From the repository root, both commands must exit 0:

```bash
python3 -B checks/run_all.py
python3 -B -m unittest discover -s tests -v
```

The continuous-integration workflow (`.github/workflows/checks.yml`) runs the same two commands on Python
3.11, 3.12, 3.13 and 3.14, and builds and runs the container defined in `Dockerfile`.

## What the checks hold you to

- Standard library only, so that a fresh clone runs with no install.
- A new check carries its synthetic cases in a `selftest_cases()` function: `--selftest` runs them, and
  `tests/test_selftests.py` exposes each one as a test without further edits.
- An agent definition in `agents/` names a tier, never a model, and its standing-rules block stays byte-identical
  across the definitions (`checks/agent_defs_check.py`).
- The example stays fictional: no real person, project, dataset or result.
- No text file carries an invisible or bidirectional code point (the hygiene leg of `run_all.py`).

## Reporting a problem

Open an issue with the command you ran, its output and its exit code.

## License of contributions

Contributions are accepted under the repository's licenses: code (`checks/`, `config/`, `tests/`, the
scripts in `example/analysis/`, the workflow, `Dockerfile`, `pyproject.toml`) under the MIT License (`LICENSE`), documentation under Creative
Commons Attribution 4.0 International (`LICENSE-docs.md`).
