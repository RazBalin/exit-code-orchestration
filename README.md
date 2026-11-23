# Exit-Code Orchestration

A generic, runnable skeleton of an architecture for AI-orchestrated research operations: one
orchestrator with sole write access, read-only subagents of fixed roles, decision lists,
continuity files with checked budgets, a findings register, a context gauge, an outbound audit and a
data boundary enforced by a pre-tool hook. Every control is a script with an exit code.

It is written on a fictional domain, the Boulder Moss Survey, so that it runs out of the box. The example ships the files its checks read; files its records cite that
no check reads are not shipped. The method
note that describes the architecture is in `docs/`.

Raz Balin, doctoral researcher in neuroscience · ORCID
[0000-0001-8895-1537](https://orcid.org/0000-0001-8895-1537)

## Run it

Python 3.11 or later, standard library only; nothing to install. From a fresh clone:

```bash
python3 -B checks/run_all.py
```

Seven legs print PASS and the script exits 0: the checks' own synthetic cases, the agent definitions
and their hooks, the example's continuity file, its launch file, its outward text, the context gauge and
a hygiene sweep of the repository.

The test suite exposes every synthetic case of the checks as a test, and tests the data boundary and the
spawn rule through the pre-tool hook on synthetic tool calls:

```bash
python3 -B -m unittest discover -s tests -v
```

Both run in continuous integration on Python 3.11 to 3.14 (`.github/workflows/checks.yml`), and in a
container pinned to Python 3.11.15:

```bash
docker build -t exit-code-orchestration . && docker run --rm exit-code-orchestration
```

## Layout

| Path | What it is |
|---|---|
| `SKILL.md` | The instruction set the orchestrator reads first |
| `agents/` | Five agent definitions: `fact-checker`, `web-searcher`, `reconciler`, `evaluator`, `helper` |
| `checks/` | `continuity_check.py`, `launch_gate.py`, `outbound_audit.py`, `agent_defs_check.py`, `context_gauge.py`, `boundary_hook.py`, `run_all.py` |
| `config/` | `workspace.json` (paths, protected trees, budgets, gauge bands, outbound rules) and `models.json` (tier to model) |
| `templates/` | Decision list, launch file, continuity file, findings register, three briefs |
| `example/` | The fictional program's workspace, with its analysis inputs and the agreement check |
| `example/transcript/` | One full worker session on the example, run in a real agent harness: the transcript, and the harness wiring it ran under (`harness/`) |
| `docs/` | The method note and its architecture figure |
| `tests/` | The test suite: the checks' synthetic cases, the data boundary and the spawn rule |
| `.github/workflows/checks.yml` | Continuous integration: the checks and the tests on Python 3.11 to 3.14, and the container |
| `Dockerfile`, `pyproject.toml` | The pinned container; the project's metadata and its supported Python versions |
| `CONTRIBUTING.md`, `CHANGELOG.md` | How to contribute; what changed in each version |

## Adapt it

1. Rewrite `SKILL.md` for your program; keep its sections and replace the domain.
2. Set `config/workspace.json`: your workspace root, your protected trees (give them distinctive folder
   names), your budgets and your outbound word list.
3. Map each tier in `config/models.json` to a model your harness runs, local or hosted. The agent
   definitions in `agents/` name a tier, never a model; the harness files of the recorded example
   session (`example/transcript/harness/`) name a model for each agent.
4. Wire `checks/boundary_hook.py --agent TYPE` as the pre-tool hook of each agent in your harness, and
   map the spawn tool's name and keys in `config/workspace.json` ("agents", "spawn"). The hook reads the
   proposed call as JSON on stdin and refuses it with exit 2.
5. Run `python3 -B checks/run_all.py` until it exits 0, then point the legs at your own workspace.

Templates mark their slots as double-bracketed names; the outbound audit blocks any slot left in a text
that leaves the workspace.

## License

Code (`checks/`, `config/`, `tests/`, the scripts in `example/analysis/`, the workflow, `Dockerfile`,
`pyproject.toml`) under the MIT License, `LICENSE`. Documentation (`SKILL.md`, this README, `CHANGELOG.md`,
`CONTRIBUTING.md`, `agents/`, `templates/`, `example/` apart from its scripts, `docs/`) under Creative Commons
Attribution 4.0 International, `LICENSE-docs.md`.

## Cite

See `CITATION.cff`.
