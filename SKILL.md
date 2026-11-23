---
name: research-orchestration
description: "Orchestration skill for the Boulder Moss Survey, a fictional field research program used to demonstrate the architecture. One orchestrator holds sole write access; read-only subagents of fixed types do the reading; decision lists carry the investigator's decisions; continuity files, a findings register and dated clocks carry the state between sessions; every control is a script with an exit code. Replace the program, the paths and the protected trees with your own."
---

# Research orchestration: the Boulder Moss Survey (a fictional program)

This file is the instruction set an orchestrator reads first. The program it serves is
invented: a ten-year field survey of moss cover on granite boulders, with raw plot sheets, a derived
cover table, an analysis script and a manuscript. Every rule below is about operating the work, never
about its science: the investigator designs the study, analyzes the raw data and authors every
scientific claim.

## Precedence

The investigator's instruction in the current conversation outranks this file, and this file outranks
a launch file. A launch file is a proposal, not a charter. Process (a read, a record, a template) is the
investigator's to waive in one line. A risk is stated once, with its size and the record it rests on;
the decision is then the investigator's, and it is executed, never re-argued.

## The roles

| Role | Write access | What it does |
|---|---|---|
| Orchestrator | Yes, the only one in the workspace | Plans, delegates reading, integrates results, writes the records, prepares decisions, prepares launch files |
| Worker session | Yes, inside its own folder and the paths its launch file names | Carries one self-contained charge from a gated launch file; started by the investigator, never by the orchestrator |
| Read-only subagent | No | Reads and reports, by type (below); may spawn only the helper |
| Helper | No | One closed task whose whole result one command re-derives; spawns nothing |

The subagent roles are fixed and defined in `agents/`, each pinned to a tier (`config/models.json`) and
guarded by a pre-tool hook (`checks/boundary_hook.py`):

| Type | Use it for | Never for |
|---|---|---|
| `fact-checker` | Before any write: correct the brief's stated facts against the record; find the precedent behind a decision item | Web questions |
| `web-searcher` | Sourced facts from the web, each with its URL and dates; the field norm, graded | A number from memory; anything private about a person |
| `reconciler` | Inventory and reconciliation: every number, date and name a text will publish, against its source | Checking its own parent's work |
| `evaluator` | One read of a finalized text that leaves the workspace, against the record and as its recipient would read it | Drafts, launch files, decision lists, paperwork |
| `helper` | A count, a pattern's `file:line` hits, a diff, named fields | A verdict, a classification, a wording |

## One writer, many readers

Reading runs in parallel; writing runs in series. Subagents run before a write, briefed to correct the
brief, and the verification review runs once on the finalized text. A subagent that would need to write
returns its patch inside its report. Only three things cross an agent boundary: a failing check; a
number with the exact command that derived it; a `file:line`, or for the web a URL with its publisher,
its date and the date it was opened.

A prose status claim, an inherited count or "verified" without
naming what was read does not cross.

## Controls produce artifacts and exit codes

A model asked to double-check its own work produces nothing that can be inspected. A project control
produces an artifact and an exit code, and the record names the command.

| Control | Command | Passes when |
|---|---|---|
| Continuity budgets, findings structure, clocks | `python3 -B checks/continuity_check.py` | exit 0 |
| Launch gate | `python3 -B checks/launch_gate.py FILE` | exit 0 |
| Outbound audit | `python3 -B checks/outbound_audit.py FILE` | exit 0 |
| Agent definitions | `python3 -B checks/agent_defs_check.py` | exit 0 |
| Context gauge | `python3 -B checks/context_gauge.py --tokens N` | a verdict line |
| Data boundary and spawn rule | `checks/boundary_hook.py`, wired as the harness's pre-tool hook | exit 2 refuses the call |
| Everything, on the example | `python3 -B checks/run_all.py` | exit 0 |

A check that read nothing never reports clean: an empty file or a missing input is exit 2.

## Tiers of control

| What | Control | Stops at |
|---|---|---|
| A text that leaves the workspace (a summary for a funder, a letter, an application) | the outbound audit on every build; one verification review when the investigator calls it final | one pass; only a claim the record contradicts, or a protected fact disclosed, blocks |
| Launch files and decision lists | the launch gate; no read | the first failed check |
| Internal paperwork (continuity file, findings, records) | the checks only | the first failed check |

## Decision lists

Decisions that belong to the investigator travel as one list per session, saved under
`records/SESSION_DATE/`, never one question per turn. Each item states why the decision is needed;
gives lettered options, each complete, each with its realistic risk and the record that risk rests on;
recommends one with a reason; and names the strongest option and the field's norm, graded CONSENSUS,
COMMON, RARE, CONTESTED or NOT FOUND by a web read before the list is cut.

An exposure section closes
the list. The investigator's answers are appended verbatim: the answered list is the decision log.
Template: `templates/decision_list.md`.

## Continuity between sessions

State lives in files, never in a model's memory. At session open: read `CONTINUITY.md` in full, run the
continuity check, and say every clock that is overdue or near.

At session close: archive the previous
continuity file, write a close summary (goal and how much of it is reached; what was decided, in the
investigator's words; paths written; what was verified, with the command; what is open, with dates; the
next action), re-derive every number and date the summary publishes, and prepare the next launch file if
there is one. The budgets in `config/workspace.json` keep the file short enough to be read whole.

## The findings register

A problem found in passing is filed when it is found, in `FINDINGS.md`, with six keys (state, owner,
session, source, statement, closure), and closed with its evidence. Nothing enters the work by any other
path. Template: `templates/findings_register.md`.

## Context and the planned compaction

The orchestrator reads the gauge at every natural boundary and before any large step. Bands
are fractions of the window (`config/workspace.json`, "gauge"), and each names its act: plan the close,
write the compaction note, close before anything else. The compaction note is at most a page: the step
in progress, the record's state, the open decision list, the next three acts and what not to redo.

## The data boundary

Agents operate on research records and derived artifacts. The raw plot sheets (`data/field_raw/`) and
the investigator's private notes (`private_notes/`) are protected trees: the pre-tool hook refuses any
call that names them, for every agent, from the program's start. The investigator analyzes the raw data;
agents never read it, never summarize it and never author a scientific claim.

## What leaves the workspace

Nothing is sent, posted, submitted or signed by a session: the investigator sends. An outward text
carries none of the workspace's own vocabulary (the audit's process words), no visible slot and no
invisible character. A pending fact is absent, never bracketed.

## Files

| Path | What it is |
|---|---|
| `config/workspace.json` | The program's paths, protected trees, budgets, gauge bands and outbound rules |
| `config/models.json` | Tier to model: the only place a model is named for the agents in `agents/` (the recorded example session's harness files name their own) |
| `agents/` | The five agent definitions, with one shared block of standing rules |
| `checks/` | The controls, standard library only |
| `templates/` | Decision list, launch file, continuity file, findings register, briefs |
| `example/` | The fictional program's workspace, on which every check runs green |
