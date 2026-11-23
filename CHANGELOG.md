# Changelog

Notable changes to this repository, newest first. Versions follow semantic versioning.

## 1.0.0 (November 2026)

First public release.

- The method note (`docs/method_note.md`, `docs/method_note.pdf`), its architecture figure and the figure of its pilot comparison.
- Six checks with an exit code each (`checks/`): the continuity check, the launch gate, the context gauge,
  the outbound audit, the agent-definitions check and the pre-tool boundary hook; `run_all.py` runs every
  leg on the example workspace.
- Five agent definitions (`agents/`) with a shared standing-rules block and the pre-tool hook declared.
- Templates for the decision list, the launch file, the continuity file, the findings register and three
  briefs (`templates/`).
- A worked example on a fictional field program (`example/`), and one full worker session on it, run in a real agent
  harness, with its transcript, the records it wrote and the harness wiring (`example/transcript/`).
- A test suite (`tests/`): every synthetic case of the checks as a test, and the data boundary and the
  spawn rule tested through the hook on synthetic tool calls.
- Continuous integration on Python 3.11 to 3.14, a container on Python 3.11.15, and `pyproject.toml`.
