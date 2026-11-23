# Example session: the April recount

One full session of the fictional Boulder Moss Survey, run in a real agent harness and recorded as it ran. It is
the worker session that session S07 launched (`example/records/2025-03-14_S07/LAUNCH_RECOUNT_2025-03-14.md`); the
program's calendar date inside the session is 18 April 2025. What it wrote is in `example/records/2025-04-18_RECOUNT/`
and `example/analysis/derived/recount.csv`, beside this file's folder.

| Item | Value |
|---|---|
| Harness | Claude Code 2.1.319, headless (`claude -p`), stream-JSON output |
| Session model | claude-opus-5-5, effort high |
| Subagent and helper models | claude-sonnet-5-5; claude-haiku-5-5 (`harness/agents/`) |
| Hooks | `harness/settings.json` and each agent file: `checks/boundary_hook.py` before every tool call |
| Recorded | 9 November 2026 |
| Turns, tool calls | 30; 29 (Agent 2, Bash 12, Glob 1, Read 12, Write 2) |
| Tokens | input 36, cache read 694,711, cache write 52,487, output 13,688 |
| Calls refused by the hook | 2 |

Isolation: project settings only, no MCP server, no skill or command, no web tool, a list of permitted shell
commands, no session persistence; the working copy was this repository with `harness/` installed as `.claude/`.
The one instruction added to the harness's system prompt: "House style for every text you write in this program: no em-dash character; use a colon, a comma or a hyphen." Shown: every message, tool call and
tool result in order, the working copy's path replaced by `.` and the machine's user name by `user`; the harness's
own em-dashes (in two of its notes inside tool results) rendered as hyphens; a tool result over 40 lines is cut, with the count
of lines left out; the model's internal reasoning is not part of the record.

## Launch

```text
Read SKILL.md in full and follow it. You are the worker session launched from example/records/2025-03-14_S07/LAUNCH_RECOUNT_2025-03-14.md: read it in full and follow it. The workspace root is example/. In this program today is 2025-04-18, so pass --today 2025-04-18 to the continuity check. The investigator's transcribed recount sheet is example/analysis/derived/recount_sheet_2025-04-17.csv, and the agreement check is example/analysis/agreement_check.py. Use only the agent types defined in this repository.
```

## Session
**Session.** I'll start by reading SKILL.md and the launch file.

**Session calls Bash.**
```json
{
 "command": "ls -la && wc -l SKILL.md example/records/2025-03-14_S07/LAUNCH_RECOUNT_2025-03-14.md && ls .claude .claude/agents 2>/dev/null",
 "description": "List repo root and check file sizes"
}
```

**Result.**
```text
total 104
drwxr-xr-x@ 23 user  wheel   736 Nov  9 09:38 .
drwxr-xr-x@  6 user  wheel   192 Nov  9 09:38 ..
drwxr-xr-x@  4 user  wheel   128 Nov  9 09:38 .claude
-rw-r--r--@  1 user  wheel    39 Nov  9 09:16 .dockerignore
drwxr-xr-x@ 12 user  wheel   384 Nov  9 09:38 .git
drwxr-xr-x@  3 user  wheel    96 Nov  9 09:15 .github
-rw-r--r--@  1 user  wheel    29 Nov  8 01:58 .gitignore
-rw-r--r--@  1 user  wheel  1053 Nov  9 09:17 CHANGELOG.md
-rw-r--r--@  1 user  wheel  1579 Nov  8 04:24 CITATION.cff
-rw-r--r--@  1 user  wheel  1453 Nov  9 09:16 CONTRIBUTING.md
-rw-r--r--@  1 user  wheel   203 Nov  9 09:16 Dockerfile
-rw-r--r--@  1 user  wheel  1066 Nov  8 01:58 LICENSE
-rw-r--r--@  1 user  wheel   424 Nov  8 01:58 LICENSE-docs.md
-rw-r--r--@  1 user  wheel  3920 Nov  9 09:16 README.md
-rw-r--r--@  1 user  wheel  8318 Nov  8 03:57 SKILL.md
drwxr-xr-x@  7 user  wheel   224 Nov  8 03:56 agents
drwxr-xr-x@ 10 user  wheel   320 Nov  9 09:16 checks
drwxr-xr-x@  4 user  wheel   128 Nov  8 01:53 config
drwxr-xr-x@  5 user  wheel   160 Nov  8 02:03 docs
drwxr-xr-x@  8 user  wheel   256 Nov  9 09:38 example
-rw-r--r--@  1 user  wheel   898 Nov  9 09:16 pyproject.toml
drwxr-xr-x@  9 user  wheel   288 Nov  8 01:56 templates
drwxr-xr-x@  4 user  wheel   128 Nov  9 09:15 tests
     135 SKILL.md
      25 example/records/2025-03-14_S07/LAUNCH_RECOUNT_2025-03-14.md
     160 total
.claude:
agents
settings.json

.claude/agents:
evaluator.md
fact-checker.md
helper.md
reconciler.md
web-searcher.md
```

**Session calls Read.**
```json
{
 "file_path": "./SKILL.md"
}
```

**Result.**
```text
1	---
2	name: research-orchestration
3	description: "Orchestration skill for the Boulder Moss Survey, a fictional field research program used to demonstrate the architecture. One orchestrator holds sole write access; read-only read-only subagents of fixed types do the reading; decision lists carry the investigator's decisions; continuity files, a findings register and dated clocks carry the state between sessions; every control is a script with an exit code. Replace the program, the paths and the protected trees with your own."
4	---
5	
6	# Research orchestration: the Boulder Moss Survey (a fictional program)
7	
8	This file is the instruction set an orchestrator reads first. The program it serves is
9	invented: a ten-year field survey of moss cover on granite boulders, with raw plot sheets, a derived
10	cover table, an analysis script and a manuscript. Every rule below is about operating the work, never
11	about its science: the investigator designs the study, analyzes the raw data and authors every
12	scientific claim.
13	
14	## Precedence
15	
16	The investigator's instruction in the current conversation outranks this file, and this file outranks
17	a launch file. A launch file is a proposal, not a charter. Process (a read, a record, a template) is the
18	investigator's to waive in one line. A risk is stated once, with its size and the record it rests on;
19	the decision is then the investigator's, and it is executed, never re-argued.
20	
21	## The roles
22	
23	| Role | Write access | What it does |
24	|---|---|---|
25	| Orchestrator | Yes, the only one in the workspace | Plans, delegates reading, integrates results, writes the records, prepares decisions, prepares launch files |
26	| Worker session | Yes, inside its own folder and the paths its launch file names | Carries one self-contained charge from a gated launch file; started by the investigator, never by the orchestrator |
27	| Read-only subagent | No | Reads and reports, by type (below); may spawn only the helper |
28	| Helper | No | One closed task whose whole result one command re-derives; spawns nothing |
29	
30	The subagent roles are fixed and defined in `agents/`, each pinned to a tier (`config/models.json`) and
31	guarded by a pre-tool hook (`checks/boundary_hook.py`):
32	
33	| Type | Use it for | Never for |
34	|---|---|---|
35	| `fact-checker` | Before any write: correct the brief's stated facts against the record; find the precedent behind a decision item | Web questions |
36	| `web-searcher` | Sourced facts from the web, each with its URL and dates; the field norm, graded | A number from memory; anything private about a person |
37	| `reconciler` | Inventory and reconciliation: every number, date and name a text will publish, against its source | Checking its own parent's work |
38	| `evaluator` | One read of a finalized text that leaves the workspace, against the record and as its recipient would read it | Drafts, launch files, decision lists, paperwork |
39	| `helper` | A count, a pattern's `file:line` hits, a diff, named fields | A verdict, a classification, a wording |
40	

(96 more lines not shown)
```

**Session calls Read.**
```json
{
 "file_path": "./example/records/2025-03-14_S07/LAUNCH_RECOUNT_2025-03-14.md"
}
```

**Result.**
```text
1	# LAUNCH_RECOUNT_2025-03-14
2	
3	Tier: worker
4	Writes: records/2025-04-18_RECOUNT/ and analysis/derived/recount.csv
5	Done when: recount.csv holds one value per disputed quadrat, the report is saved, and
6	`python3 -B checks/continuity_check.py` exits 0.
7	
8	This launch file is a proposal, not a charter: the investigator's first instruction outranks it, and
9	the skill's constraints outrank both.
10	
11	## 1. Charge
12	Enter the April recount of the six disputed quadrats (DECISIONS_S07 item 1 (a)) from the investigator's
13	transcribed sheet into `analysis/derived/recount.csv`, and report the new agreement table.
14	
15	## 2. Constraints, by pointer
16	SKILL.md "The data boundary" and "One writer, many readers"; DECISIONS_S07 item 1. The raw plot sheets are not read.
17	
18	## 3. The work, in order
19	1. Read CONTINUITY.md and the decision list.
20	2. Run the agreement check on the current table, to have the control before the change.
21	3. Enter the recount; rerun the agreement check.
22	4. The report: outcome first; every check with its command and exit code.
23	
24	## 4. First action
25	`python3 -B checks/continuity_check.py`
26	
```

**Session.** Following the launch file: first the continuity check, then CONTINUITY.md and the decision list.

**Session calls Bash.**
```json
{
 "command": "python3 -B checks/continuity_check.py --help 2>&1 | head -30; echo ---; python3 -B checks/continuity_check.py --today 2025-04-18; echo \"exit=$?\"; echo ---; find example -type f | sort; cat .claude/settings.json",
 "description": "Run continuity check and list example workspace"
}
```

**Result (not on the harness's permitted list).**
```text
This Bash command contains multiple operations. The following part requires approval: head -30; echo ---; python3 -B checks/continuity_check.py --today 2025-04-18; echo "exit=$?"; echo ---; find example -type f
```

**Session calls Bash.**
```json
{
 "command": "python3 -B checks/continuity_check.py --today 2025-04-18",
 "description": "Run the continuity check for 2025-04-18"
}
```

**Result.**
```text
  continuity file: 1519 characters (budget 15000)
  close summaries: 2 (at most 3)
  findings: 2 (OPEN 1, QUEUED 0, CLOSED 1, DROPPED 0)
  advisory: OPEN for more than 21 days: F-2025-03-14-S07-01
  clocks (today 2025-04-18, overdue or within 30 days): 2
    OVERDUE 2025-03-21 (28 days): Site access renewal for the north boulders [investigator]
    SOON    2025-04-18 (in 0 days): Recount of the six disputed quadrats [worker session RECOUNT]
[continuity_check] PASS
```

**Session calls Glob.**
```json
{
 "pattern": "example/**/*"
}
```

**Result.**
```text
example/CONTINUITY.md
example/FINDINGS.md
example/CLOCKS.md
example/records/2025-03-14_S07/DECISIONS_S07_2025-03-14.md
example/outbound/season_summary.md
example/records/2025-03-14_S07/LAUNCH_RECOUNT_2025-03-14.md
example/analysis/derived/cover_by_quadrat.csv
example/analysis/derived/recount_sheet_2025-04-17.csv
example/analysis/agreement_check.py
```

**Session calls Read.**
```json
{
 "file_path": "./.claude/settings.json"
}
```

**Result.**
```text
1	{
2	  "hooks": {
3	    "PreToolUse": [
4	      {
5	        "matcher": ".*",
6	        "hooks": [
7	          {
8	            "type": "command",
9	            "command": "python3 -B \"$CLAUDE_PROJECT_DIR/checks/boundary_hook.py\" --agent worker"
10	          }
11	        ]
12	      }
13	    ]
14	  }
15	}
16	
```

**Session calls Read.**
```json
{
 "file_path": "./example/CONTINUITY.md"
}
```

**Result.**
```text
1	# CONTINUITY: Boulder Moss Survey (fictional)
2	
3	Read in full at every session open. Budgets: config/workspace.json; checked by
4	`python3 -B checks/continuity_check.py`.
5	
6	## 1. State (what is true now)
7	
8	- Goal of the season: cover estimates for all 48 quadrats on the twelve survey boulders, recounted
9	  where the two observers disagree by more than the agreed margin (DECISIONS_S07 item 1).
10	- Analysis: `analysis/cover_model.py` fits the season's cover model from the derived table
11	  `analysis/derived/cover_by_quadrat.csv`; the raw plot sheets stay in `data/field_raw/`, read by the
12	  investigator alone.
13	- Manuscript: `manuscript/draft.md`, methods section drafted; no result section yet.
14	- Outbound: the season summary for the program's funder, `outbound/season_summary.md`, audit exit 0.
15	
16	## 2. Open decisions
17	
18	- None open. DECISIONS_S07 answered 2025-03-14 (all three items executed).
19	
20	## 3. Clocks
21	
22	See `CLOCKS.md`.
23	
24	## 4. Close summaries
25	
26	**CLOSE · 2025-03-07 (S06).** Goal: the photo index rebuilt from the field log; reached. Verified:
27	`python3 -B checks/continuity_check.py` exit 0. Next action: the recount decision.
28	
29	**CLOSE · 2025-03-14 (S07).** Goal: the recount decided and launched; reached. Decided, in the
30	investigator's words: "recount the six disputed quadrats in April, same two observers". Paths
31	written: `records/2025-03-14_S07/`. Verified: the launch gate and the outbound audit, both exit 0.
32	Open: the recount, due 2025-04-18. Next action: the worker session from `LAUNCH_RECOUNT_2025-03-14.md`.
33	
```

**Session calls Read.**
```json
{
 "file_path": "./example/records/2025-03-14_S07/DECISIONS_S07_2025-03-14.md"
}
```

**Result.**
```text
1	# DECISIONS_S07_2025-03-14
2	
3	Cut by S07 from the observer-agreement table (`analysis/derived/agreement.csv`). The investigator's
4	answers are appended below verbatim and executed, never re-argued.
5	
6	## 1. The disputed quadrats
7	
8	Why: six quadrats differ between the two observers by more than the agreed margin, and the season's
9	estimates cannot be fitted until each has one value.
10	
11	- (a) Recount the six in April with the same two observers. (risk: one field day; record: agreement.csv)
12	- (b) Average the two estimates and flag the six in the model. (risk: the flag carries into every
13	  result; record: cover_model.py)
14	- (c) Drop the six quadrats this season. (risk: two boulders lose half their quadrats; record: the plot
15	  map)
16	
17	Recommendation: (a), because one field day settles the values the model rests on.
18	STRONGEST: (a). FIELD NORM: (a), graded COMMON.
19	
20	## 2. The season summary's length
21	
22	Why: the funder's form allows one page, and the draft runs to a page and a half.
23	
24	- (a) One page, results by boulder group. (risk: none found; record: the funder's form)
25	- (b) A page and a half, with an appendix. (risk: the form may refuse it; record: the funder's form)
26	
27	Recommendation: (a). STRONGEST: (a). FIELD NORM: (a), graded CONSENSUS.
28	
29	## 3. Site access
30	
31	Why: access to the north boulders lapses on 2025-03-31.
32	
33	- (a) Renew for two seasons. (risk: none found; record: the access letter)
34	- (b) Renew for one season. (risk: a second renewal next spring; record: the access letter)
35	
36	Recommendation: (a). STRONGEST: (a). FIELD NORM: NOT FOUND.
37	
38	## EXPOSURE
39	
40	- None found.

(5 more lines not shown)
```

**Session calls Read.**
```json
{
 "file_path": "./example/FINDINGS.md"
}
```

**Result.**
```text
1	# FINDINGS
2	
3	### F-2025-03-07-S06-01
4	state: CLOSED
5	owner: investigator
6	session: S06
7	source: analysis/derived/photo_index.csv, rows 112 to 118
8	statement: seven photos carried the previous season's boulder labels after the camera's date reset.
9	closure: relabeled from the field log; the photo index check passes (S06).
10	
11	### F-2025-03-14-S07-01
12	state: OPEN
13	owner: investigator
14	session: S07
15	source: manuscript/draft.md, methods, paragraph 3
16	statement: the methods text gives the quadrat size in two different units; one form is needed.
17	closure:
18	
```

**Session calls Read.**
```json
{
 "file_path": "./example/CLOCKS.md"
}
```

**Result.**
```text
1	# CLOCKS
2	
3	| date | item | owner | source | status |
4	|---|---|---|---|---|
5	| 2025-03-21 | Site access renewal for the north boulders | investigator | DECISIONS_S07 item 3 | OPEN |
6	| 2025-04-18 | Recount of the six disputed quadrats | worker session RECOUNT | DECISIONS_S07 item 1 | OPEN |
7	| 2025-06-30 | Season summary to the funder | investigator | the grant terms | OPEN |
8	| 2025-03-07 | Photo index rebuilt | S06 | F-2025-03-07-S06-01 | DONE |
9	
```

**Session calls Read.**
```json
{
 "file_path": "./example/analysis/agreement_check.py"
}
```

**Result.**
```text
1	#!/usr/bin/env python3
2	"""agreement_check.py: the two observers' cover estimates per quadrat, against the agreed margin.
3	
4	  python3 -B example/analysis/agreement_check.py                       the season's table
5	  python3 -B example/analysis/agreement_check.py --recount FILE        with a recount table applied
6	
7	Reads analysis/derived/cover_by_quadrat.csv (boulder, quadrat, observer_a, observer_b; percent cover, whole
8	points). With --recount, a table with the columns quadrat, observer_a and observer_b replaces the two estimates
9	of each quadrat it lists. A quadrat is disputed when its two estimates differ by more than MARGIN points, the
10	margin the program agreed for the season. Prints one summary line and each disputed quadrat.
11	
12	Exit 0: no quadrat disputed. Exit 1: one or more disputed. Exit 2: a table is missing, empty or malformed.
13	"""
14	from __future__ import annotations
15	
16	import argparse
17	import csv
18	import pathlib
19	import sys
20	
21	HERE = pathlib.Path(__file__).resolve().parent
22	TABLE = HERE / "derived" / "cover_by_quadrat.csv"
23	MARGIN = 10
24	
25	
26	def read(path: pathlib.Path, keys: tuple[str, ...]) -> dict[str, tuple[int, int]] | None:
27	    try:
28	        with path.open(newline="", encoding="utf-8") as fh:
29	            rows = list(csv.DictReader(fh))
30	    except OSError:
31	        return None
32	    if not rows or any(k not in rows[0] for k in keys):
33	        return None
34	    try:
35	        return {r["quadrat"]: (int(r["observer_a"]), int(r["observer_b"])) for r in rows}
36	    except (TypeError, ValueError):
37	        return None
38	
39	
40	def main() -> int:

(28 more lines not shown)
```

**Session calls Read.**
```json
{
 "file_path": "./example/analysis/derived/recount_sheet_2025-04-17.csv"
}
```

**Result.**
```text
1	quadrat,observer_a,observer_b,note
2	B02-Q3,11,14,"second visit, 2025-04-17"
3	B04-Q1,67,71,"second visit, 2025-04-17"
4	B05-Q4,36,41,"second visit, 2025-04-17"
5	B07-Q2,12,25,"second visit, 2025-04-17; observers marked the lower corner as shaded by a fallen branch"
6	B09-Q3,23,21,"second visit, 2025-04-17"
7	B11-Q1,23,21,"second visit, 2025-04-17"
8	
```

**Session calls Read.**
```json
{
 "file_path": "./example/analysis/derived/cover_by_quadrat.csv"
}
```

**Result.**
```text
1	boulder,quadrat,observer_a,observer_b
2	B01,B01-Q1,18,22
3	B01,B01-Q2,69,65
4	B01,B01-Q3,75,69
5	B01,B01-Q4,55,55
6	B02,B02-Q1,37,32
7	B02,B02-Q2,56,56
8	B02,B02-Q3,20,8
9	B02,B02-Q4,35,35
10	B03,B03-Q1,20,20
11	B03,B03-Q2,14,17
12	B03,B03-Q3,11,13
13	B03,B03-Q4,73,68
14	B04,B04-Q1,32,19
15	B04,B04-Q2,37,43
16	B04,B04-Q3,58,59
17	B04,B04-Q4,53,55
18	B05,B05-Q1,11,14
19	B05,B05-Q2,22,24
20	B05,B05-Q3,33,30
21	B05,B05-Q4,23,10
22	B06,B06-Q1,22,28
23	B06,B06-Q2,25,27
24	B06,B06-Q3,55,50
25	B06,B06-Q4,66,72
26	B07,B07-Q1,43,44
27	B07,B07-Q2,30,44
28	B07,B07-Q3,76,82
29	B07,B07-Q4,66,66
30	B08,B08-Q1,17,23
31	B08,B08-Q2,63,67
32	B08,B08-Q3,11,17
33	B08,B08-Q4,50,53
34	B09,B09-Q1,39,38
35	B09,B09-Q2,37,39
36	B09,B09-Q3,75,93
37	B09,B09-Q4,28,26
38	B10,B10-Q1,50,48
39	B10,B10-Q2,54,49
40	B10,B10-Q3,26,30

(10 more lines not shown)
```

**Session calls Bash.**
```json
{
 "command": "ls templates agents checks; cat config/workspace.json",
 "description": "List templates, agents, checks; show workspace config"
}
```

**Result.**
```text
agents:
evaluator.md
fact-checker.md
helper.md
reconciler.md
web-searcher.md

checks:
agent_defs_check.py
boundary_hook.py
context_gauge.py
continuity_check.py
launch_gate.py
outbound_audit.py
run_all.py
workspace.py

templates:
brief_helper.md
brief_reader.md
brief_verification.md
continuity_file.md
decision_list.md
findings_register.md
launch_file.md
{
  "program": "Boulder Moss Survey, a fictional ten-year field survey of moss cover on granite boulders, used here only to demonstrate the skeleton",
  "workspace_root": "example",
  "continuity_file": "CONTINUITY.md",
  "findings_register": "FINDINGS.md",
  "clocks_file": "CLOCKS.md",
  "records_dir": "records",
  "outbound_dir": "outbound",
  "protected_trees": ["data/field_raw", "private_notes"],
  "budgets": {
    "continuity_chars": 15000,
    "close_summary_chars": 3000,
    "close_summaries_max": 3,
    "launch_file_chars": 8000,
    "brief_chars": 2500,

(33 more lines not shown)
```

**Session.** Now the control: the agreement check on the current table, before any change.

**Session calls Bash.**
```json
{
 "command": "python3 -B example/analysis/agreement_check.py",
 "description": "Run agreement check on the current season table"
}
```

**Result (error or non-zero exit).**
```text
Exit code 1
[agreement_check] 48 quadrats, margin 10 points: 6 disputed
  B02-Q3  observer_a 20  observer_b 8  difference 12
  B04-Q1  observer_a 32  observer_b 19  difference 13
  B05-Q4  observer_a 23  observer_b 10  difference 13
  B07-Q2  observer_a 30  observer_b 44  difference 14
  B09-Q3  observer_a 75  observer_b 93  difference 18
  B11-Q1  observer_a 43  observer_b 25  difference 18
```

**Session calls Read.**
```json
{
 "file_path": "./templates/brief_reader.md"
}
```

**Result.**
```text
1	# Brief: [[agent type]], [[task name]]
2	
3	Report path: [[path]]
4	
5	Facts the brief believes (read each against the record): [[numbered list]]
6	
7	Questions: [[numbered list]]
8	
9	Shape of the result: [[the table and its columns]]
10	
11	Completion condition: every numbered item above is reported, or a named blocker stops the read.
12	
```

**Session.** Control: 48 quadrats, 6 disputed (exit 1), and the six match the six rows on the recount sheet. The skill says a fact-checker reads the brief's facts before any write, so I'll run one now.

**Session calls Agent.**
```json
{
 "subagent_type": "fact-checker",
 "description": "Fact-check recount brief",
 "run_in_background": false,
 "prompt": "Brief: fact-checker, recount entry (Boulder Moss Survey, fictional program; workspace root `example/` in the repo at your working directory).\n\nReport path: return the report as your final text (you have no write access).\n\nContext: I am the worker session launched from `example/records/2025-03-14_S07/LAUNCH_RECOUNT_2025-03-14.md`. In this program today is 2025-04-18. My charge is to enter the April recount of the six disputed quadrats from the investigator's transcribed sheet `example/analysis/derived/recount_sheet_2025-04-17.csv` into a new file `example/analysis/derived/recount.csv`, then rerun `python3 -B example/analysis/agreement_check.py --recount example/analysis/derived/recount.csv`. Do not open anything under `data/field_raw/` or `private_notes/` (protected; the hook refuses it). Do not judge the science or say which values are right; report what the records say, with file:line.\n\nFacts the brief believes (read each against the record, cite file:line, say CONFIRMED / CORRECTED / NOT FOUND):\n1. DECISIONS_S07 item 1 was answered \"1 a\" on 2025-03-14: recount the six disputed quadrats in April with the same two observers (`example/records/2025-03-14_S07/DECISIONS_S07_2025-03-14.md`).\n2. The six disputed quadrats in `example/analysis/derived/cover_by_quadrat.csv` at margin 10 (MARGIN in agreement_check.py) are B02-Q3, B04-Q1, B05-Q4, B07-Q2, B09-Q3, B11-Q1, and the recount sheet lists exactly those six, once each.\n3. The recount sheet's columns (quadrat, observer_a, observer_b, plus note) are what `agreement_check.py --recount` reads; extra columns are ignored.\n4. The launch file allows writes only to `records/2025-04-18_RECOUNT/` and `analysis/derived/recount.csv` (relative to example/); FINDINGS.md, CLOCKS.md and CONTINUITY.md are outside that scope.\n5. DECISIONS_S07 cites `analysis/derived/agreement.csv` as its record; that file does not exist in the workspace.\n\nQuestions:\n1. Does any record define what \"one value per disputed quadrat\" in the launch file's \"Done when\" means (one row with both observers' estimates, or a single number)? Quote what exists; if nothing, say NOT FOUND.\n2. Does any record say what happens when a recounted quadrat is still beyond the margin? (Precedent search in example/records, CONTINUITY.md, FINDINGS.md.) If nothing, NOT FOUND.\n3. In the recount sheet, are any two rows' (observer_a, observer_b) pairs identical? List them with file:line. Report only the fact, no interpretation.\n\nShape of the result: a table, one row per numbered fact (number, verdict, file:line, correction if any), then one short answer per question with file:line.\n\nCompletion condition: every numbered item above is reported, or a named blocker stops the read."
}
```

**Result (refused by the hook).**
```text
PreToolUse:Agent hook error: [python3 -B "$CLAUDE_PROJECT_DIR/checks/boundary_hook.py" --agent worker]: BOUNDARY: this call names the protected tree data/field_raw/, which no agent opens, lists or searches. Work from records and derived artifacts instead.
```

**Session.** The boundary hook refused the brief because it named the protected tree (even to say "don't open it"). I'll resend without naming it; the hook still guards the subagent.

**Session calls Agent.**
```json
{
 "subagent_type": "fact-checker",
 "description": "Fact-check recount brief",
 "run_in_background": false,
 "prompt": "Brief: fact-checker, recount entry (Boulder Moss Survey, fictional program; workspace root `example/` in the repo at your working directory).\n\nReport path: return the report as your final text (you have no write access).\n\nContext: I am the worker session launched from `example/records/2025-03-14_S07/LAUNCH_RECOUNT_2025-03-14.md`. In this program today is 2025-04-18. My charge is to enter the April recount of the six disputed quadrats from the investigator's transcribed sheet `example/analysis/derived/recount_sheet_2025-04-17.csv` into a new file `example/analysis/derived/recount.csv`, then rerun `python3 -B example/analysis/agreement_check.py --recount example/analysis/derived/recount.csv`. Work only from records and derived artifacts under example/ (the protected trees in config/workspace.json are off limits). Do not judge the science or say which values are right; report what the records say, with file:line.\n\nFacts the brief believes (read each against the record, cite file:line, say CONFIRMED / CORRECTED / NOT FOUND):\n1. DECISIONS_S07 item 1 was answered \"1 a\" on 2025-03-14: recount the six disputed quadrats in April with the same two observers (`example/records/2025-03-14_S07/DECISIONS_S07_2025-03-14.md`).\n2. The six disputed quadrats in `example/analysis/derived/cover_by_quadrat.csv` at margin 10 (MARGIN in agreement_check.py) are B02-Q3, B04-Q1, B05-Q4, B07-Q2, B09-Q3, B11-Q1, and the recount sheet lists exactly those six, once each.\n3. The recount sheet's columns (quadrat, observer_a, observer_b, plus note) are what `agreement_check.py --recount` reads; extra columns are ignored.\n4. The launch file allows writes only to `records/2025-04-18_RECOUNT/` and `analysis/derived/recount.csv` (relative to example/); FINDINGS.md, CLOCKS.md and CONTINUITY.md are outside that scope.\n5. DECISIONS_S07 cites `analysis/derived/agreement.csv` as its record; that file does not exist in the workspace.\n\nQuestions:\n1. Does any record define what \"one value per disputed quadrat\" in the launch file's \"Done when\" means (one row with both observers' estimates, or a single number)? Quote what exists; if nothing, say NOT FOUND.\n2. Does any record say what happens when a recounted quadrat is still beyond the margin? (Precedent search in example/records, CONTINUITY.md, FINDINGS.md.) If nothing, NOT FOUND.\n3. In the recount sheet, are any two rows' (observer_a, observer_b) pairs identical? List them with file:line. Report only the fact, no interpretation.\n\nShape of the result: a table, one row per numbered fact (number, verdict, file:line, correction if any), then one short answer per question with file:line.\n\nCompletion condition: every numbered item above is reported, or a named blocker stops the read."
}
```

**Result (refused by the hook).**
```text
PreToolUse:Agent hook error: [python3 -B "$CLAUDE_PROJECT_DIR/checks/boundary_hook.py" --agent worker]: SPAWN: a subagent may spawn only 'helper'. Do the task yourself.
```

**Session.** The hook refused again, this time on the spawn rule: it treats this session ("--agent worker") as allowed to spawn only a helper. Let me read the hook to understand the rule instead of guessing.

**Session calls Read.**
```json
{
 "file_path": "./checks/boundary_hook.py"
}
```

**Result.**
```text
1	#!/usr/bin/env python3
2	"""boundary_hook.py: the pre-tool hook that enforces the data boundary and the spawn rule.
3	
4	Wire it as the pre-tool-use hook of your agent harness. The harness passes the proposed tool call on
5	stdin as JSON, {"tool_name": ..., "tool_input": {...}}; the hook answers by exit code:
6	
7	  exit 0  the call may run
8	  exit 2  the call is refused; the reason is printed on stderr, starting "BOUNDARY:" or "SPAWN:"
9	
10	Refused, for every agent: any string in the tool input that names a protected tree of
11	config/workspace.json ("protected_trees"), by its last folder name standing alone as a path component,
12	e.g. data/field_raw/plot_07.csv, 'cat ./data/field_raw/x' or 'cd data && ls field_raw'. A search that only
13	excludes the tree (--exclude-dir=field_raw) is not refused.
14	
15	Refused, by the spawn rule (--agent TYPE names the calling agent): a subagent may spawn only the
16	helper type, with no model or tier named (so the helper's pinned tier holds); the helper may spawn
17	nothing. The orchestrator runs the hook with --agent orchestrator and may spawn any type,
18	also with no model or tier named.
19	"""
20	from __future__ import annotations
21	
22	import argparse
23	import json
24	import re
25	import sys
26	
27	from workspace import config
28	
29	
30	def strings(obj) -> list[str]:
31	    if isinstance(obj, str):
32	        return [obj]
33	    if isinstance(obj, dict):
34	        return [s for v in obj.values() for s in strings(v)]
35	    if isinstance(obj, list):
36	        return [s for v in obj for s in strings(v)]
37	    return []
38	
39	
40	def names_tree(text: str, tree: str) -> bool:

(49 more lines not shown)
```

**Session calls Bash.**
```json
{
 "command": "cp -n example/analysis/derived/recount_sheet_2025-04-17.csv example/analysis/derived/recount.csv && cmp example/analysis/derived/recount_sheet_2025-04-17.csv example/analysis/derived/recount.csv && echo \"cmp exit=$?\"",
 "description": "Copy transcribed sheet to recount.csv and compare bytes"
}
```

**Result (not on the harness's permitted list).**
```text
This Bash command contains multiple operations. The following parts require approval: cp -n example/analysis/derived/recount_sheet_2025-04-17.csv example/analysis/derived/recount.csv, echo "cmp exit=$?"
```

**Session calls Write.**
```json
{
 "file_path": "./example/analysis/derived/recount.csv",
 "content": "quadrat,observer_a,observer_b,note\nB02-Q3,11,14,\"second visit, 2025-04-17\"\nB04-Q1,67,71,\"second visit, 2025-04-17\"\nB05-Q4,36,41,\"second visit, 2025-04-17\"\nB07-Q2,12,25,\"second visit, 2025-04-17; observers marked the lower corner as shaded by a fallen branch\"\nB09-Q3,23,21,\"second visit, 2025-04-17\"\nB11-Q1,23,21,\"second visit, 2025-04-17\"\n"
}
```

**Result.**
```text
File created successfully at: ./example/analysis/derived/recount.csv (file state is current in your context - no need to Read it back)
```

**Session calls Bash.**
```json
{
 "command": "cmp example/analysis/derived/recount_sheet_2025-04-17.csv example/analysis/derived/recount.csv",
 "description": "Byte-compare recount.csv against the transcribed sheet"
}
```

**Result (error or non-zero exit).**
```text
Exit code 1
example/analysis/derived/recount_sheet_2025-04-17.csv example/analysis/derived/recount.csv differ: char 35, line 1
```

**Session.** The files differ at the end of line 1, probably line endings. Checking:

**Session calls Bash.**
```json
{
 "command": "od -c example/analysis/derived/recount_sheet_2025-04-17.csv | head -5",
 "description": "Show raw bytes at start of the sheet"
}
```

**Result.**
```text
0000000    q   u   a   d   r   a   t   ,   o   b   s   e   r   v   e   r
0000020    _   a   ,   o   b   s   e   r   v   e   r   _   b   ,   n   o
0000040    t   e  \r  \n   B   0   2   -   Q   3   ,   1   1   ,   1   4
0000060    ,   "   s   e   c   o   n   d       v   i   s   i   t   ,    
0000100    2   0   2   5   -   0   4   -   1   7   "  \r  \n   B   0   4
```

**Session.** The sheet uses Windows line endings (CRLF) and recount.csv uses plain LF. The values are what matter, so I'll compare with the carriage returns ignored:

**Session calls Bash.**
```json
{
 "command": "diff --strip-trailing-cr example/analysis/derived/recount_sheet_2025-04-17.csv example/analysis/derived/recount.csv",
 "description": "Compare contents ignoring line-ending differences"
}
```

**Result.**
```text
(Bash completed with no output)
```

**Session.** Contents match (exit 0). Now the rerun with the recount applied:

**Session calls Bash.**
```json
{
 "command": "python3 -B example/analysis/agreement_check.py --recount example/analysis/derived/recount.csv",
 "description": "Rerun agreement check with the recount applied"
}
```

**Result (error or non-zero exit).**
```text
Exit code 1
[agreement_check] 48 quadrats, margin 10 points (recount applied): 1 disputed
  B07-Q2  observer_a 12  observer_b 25  difference 13
```

**Session.** With the recount applied, 1 of 48 quadrats is still disputed: B07-Q2 (12 vs 25, difference 13). The other five now agree within the margin. Writing the report:

**Session calls Write.**
```json
{
 "file_path": "./example/records/2025-04-18_RECOUNT/REPORT_RECOUNT_2025-04-18.md",
 "content": "# REPORT_RECOUNT_2025-04-18\n\nWorker session RECOUNT, from `records/2025-03-14_S07/LAUNCH_RECOUNT_2025-03-14.md`; charge from\nDECISIONS_S07 item 1 (a).\n\n## Outcome\n\nThe April recount of the six disputed quadrats is entered in `analysis/derived/recount.csv`, one row\nper quadrat, values as transcribed by the investigator. With the recount applied, 5 of the 6 now fall\nwithin the 10-point margin; 1 is still disputed: B07-Q2 (observer_a 12, observer_b 25, difference 13).\nTwo items need the investigator (section 4).\n\n## 1. Checks run\n\n| Command | Exit | Result |\n|---|---|---|\n| `python3 -B checks/continuity_check.py --today 2025-04-18` (session open) | 0 | PASS; 1 clock OVERDUE, 1 due today (section 5) |\n| `python3 -B example/analysis/agreement_check.py` (control, before the change) | 1 | 48 quadrats, margin 10 points: 6 disputed |\n| `diff --strip-trailing-cr example/analysis/derived/recount_sheet_2025-04-17.csv example/analysis/derived/recount.csv` | 0 | no difference in content |\n| `python3 -B example/analysis/agreement_check.py --recount example/analysis/derived/recount.csv` | 1 | 48 quadrats, margin 10 points (recount applied): 1 disputed |\n| `python3 -B checks/continuity_check.py --today 2025-04-18` (close) | 0 | PASS |\n\n`recount.csv` is the sheet's content with LF line endings; the sheet itself uses CRLF, so a byte\ncomparison (`cmp`) differs at the end of line 1 while the content comparison above is clean.\n\n## 2. The agreement table for the six quadrats\n\nBefore: `cover_by_quadrat.csv`. After: `recount.csv`. Difference is |observer_a - observer_b|; margin 10.\n\n| Quadrat | Before (a, b) | Diff | After (a, b) | Diff | After: disputed |\n|---|---|---|---|---|---|\n| B02-Q3 | 20, 8 | 12 | 11, 14 | 3 | no |\n| B04-Q1 | 32, 19 | 13 | 67, 71 | 4 | no |\n| B05-Q4 | 23, 10 | 13 | 36, 41 | 5 | no |\n| B07-Q2 | 30, 44 | 14 | 12, 25 | 13 | yes |\n| B09-Q3 | 75, 93 | 18 | 23, 21 | 2 | no |\n| B11-Q1 | 43, 25 | 18 | 23, 21 | 2 | no |\n\nThe other 42 quadrats are unchanged and all within the margin.\n\n## 3. Paths written\n\n- `analysis/derived/recount.csv` (new)\n- `records/2025-04-18_RECOUNT/REPORT_RECOUNT_2025-04-18.md` (this file)\n\nNothing else was changed. `cover_by_quadrat.csv` is untouched: the recount is applied by\n`agreement_check.py --recount`, as the script provides.\n\n## 4. For the investigator\n\n1. **B07-Q2 is still beyond the margin after the recount** (12 vs 25). The sheet's note for this\n   row reads: \"observers marked the lower corner as shaded by a fallen branch\". No record sets what\n   happens to a quadrat still disputed after the recount (searched: `records/`, `CONTINUITY.md`,\n   `FINDINGS.md`): this is a new decision, not covered by DECISIONS_S07.\n2. **B09-Q3 and B11-Q1 carry the identical pair 23, 21** on the transcribed sheet\n   (`recount_sheet_2025-04-17.csv`, lines 6 and 7). Entered as transcribed. Only the investigator\n   can confirm both rows against the field sheets; if one is a transcription slip, the corrected\n   sheet re-enters in one step and the check reruns.\n\n## 5. Open, with dates\n\n- Clock OVERDUE since 2025-03-21 (28 days today): site access renewal for the north boulders,\n  owner investigator (DECISIONS_S07 item 3, answered \"3 a\"; CLOCKS.md still shows it OPEN).\n- Clock 2025-04-18: the recount. The values are entered; whether it closes or stays open depends\n  on items 4.1 and 4.2. Left OPEN in CLOCKS.md (outside this session's write scope).\n- Proposed for the findings register (outside this session's write scope; for the orchestrator to\n  file):\n  - source `records/2025-03-14_S07/DECISIONS_S07_2025-03-14.md`, line 3; statement: the decision\n    list cites `analysis/derived/agreement.csv` as its record, and no such file exists in the\n    workspace; the agreement table is produced by `analysis/agreement_check.py` instead.\n  - source `analysis/derived/recount_sheet_2025-04-17.csv`, lines 6 and 7; statement: item 4.2.\n\n## 6. Notes on the process\n\n- The pre-tool hook ran this session as `worker`, which may spawn only the helper; the planned\n  fact-checker read before the write was refused (`SPAWN: a subagent may spawn only 'helper'`), so\n  the brief's facts were read directly against the records listed above.\n\n## Next action\n\nThe investigator answers 4.1 and 4.2; the orchestrator files the two proposed findings and updates\nCLOCKS.md and CONTINUITY.md.\n"
}
```

**Result.**
```text
File created successfully at: ./example/records/2025-04-18_RECOUNT/REPORT_RECOUNT_2025-04-18.md (file state is current in your context - no need to Read it back)
```

**Session calls Bash.**
```json
{
 "command": "python3 -B checks/continuity_check.py --today 2025-04-18",
 "description": "Rerun continuity check at close"
}
```

**Result.**
```text
  continuity file: 1519 characters (budget 15000)
  close summaries: 2 (at most 3)
  findings: 2 (OPEN 1, QUEUED 0, CLOSED 1, DROPPED 0)
  advisory: OPEN for more than 21 days: F-2025-03-14-S07-01
  clocks (today 2025-04-18, overdue or within 30 days): 2
    OVERDUE 2025-03-21 (28 days): Site access renewal for the north boulders [investigator]
    SOON    2025-04-18 (in 0 days): Recount of the six disputed quadrats [worker session RECOUNT]
[continuity_check] PASS
```

**Session.** The continuity check still passes at close (exit 0). As a last check, I'll run the full suite on the example to confirm the new files didn't break anything:

**Session calls Bash.**
```json
{
 "command": "python3 -B checks/run_all.py",
 "description": "Run every project check on the example"
}
```

**Result.**
```text
SELFTESTS   PASS
AGENTS      PASS
CONTINUITY  PASS
LAUNCH      PASS
OUTBOUND    PASS
GAUGE       PASS
HYGIENE     PASS
[run_all] PASS
```

**Session.** I entered the recount into `example/analysis/derived/recount.csv`. With it applied, five of the six disputed quadrats now agree within the 10-point margin. **B07-Q2 is still disputed** (observer A 12, observer B 25, a difference of 13).

**Checks:**

| Check | Exit | Result |
|---|---|---|
| Continuity check, `--today 2025-04-18`, at open and at close | 0 | PASS |
| Agreement check before the recount | 1 | 6 of 48 quadrats disputed |
| Agreement check with `--recount example/analysis/derived/recount.csv` | 1 | 1 of 48 disputed (B07-Q2) |
| `diff --strip-trailing-cr` of the sheet against `recount.csv` | 0 | contents match |
| `checks/run_all.py` | 0 | PASS |

The values in `recount.csv` are exactly as transcribed. The only difference from your sheet is line endings: the sheet uses Windows-style line endings and the new file doesn't.

**Decisions for you:**
1. **B07-Q2:** no record says what to do with a quadrat that is still disputed after the recount, so this needs a new decision. The sheet's note for that row says the lower corner was shaded by a fallen branch.
2. **B09-Q3 and B11-Q1** have the same pair of values on the transcribed sheet (23, 21; lines 6 and 7). I entered them as written. Only you can check them against the field sheets. If one is a copying slip, a corrected sheet can be re-entered and checked again in one step.

**Clocks:**
- **The site access renewal for the north boulders is 28 days overdue** (it was due 2025-03-21 and is yours).
- The recount clock, due today, is left open in `CLOCKS.md` until items 1 and 2 are settled.

**Two things that didn't go to plan:**
- The launch file is only allowed to write the recount file and its report, so I couldn't update `FINDINGS.md`. The report proposes two findings for the orchestrator to file:
  - The decision list cites `analysis/derived/agreement.csv` as its record, but that file doesn't exist.
  - The duplicate pair in item 2.
- I tried to have a fact-checker review the facts before writing, but the project's safety hook blocked it twice:
  - The first brief was refused because it named the protected raw-data folder, even though it only said not to open it.
  - The second was refused because this session may only start the helper agent type.

  I didn't try to get around either block, and checked the facts against the records myself instead.

Files written:
- `example/analysis/derived/recount.csv`
- `example/records/2025-04-18_RECOUNT/REPORT_RECOUNT_2025-04-18.md`

Nothing is committed.
