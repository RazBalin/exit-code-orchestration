# LAUNCH_RECOUNT_2025-03-14

Tier: worker
Writes: records/2025-04-18_RECOUNT/ and analysis/derived/recount.csv
Done when: recount.csv holds one value per disputed quadrat, the report is saved, and
`python3 -B checks/continuity_check.py` exits 0.

This launch file is a proposal, not a charter: the investigator's first instruction outranks it, and
the skill's constraints outrank both.

## 1. Charge
Enter the April recount of the six disputed quadrats (DECISIONS_S07 item 1 (a)) from the investigator's
transcribed sheet into `analysis/derived/recount.csv`, and report the new agreement table.

## 2. Constraints, by pointer
SKILL.md "The data boundary" and "One writer, many readers"; DECISIONS_S07 item 1. The raw plot sheets are not read.

## 3. The work, in order
1. Read CONTINUITY.md and the decision list.
2. Run the agreement check on the current table, to have the control before the change.
3. Enter the recount; rerun the agreement check.
4. The report: outcome first; every check with its command and exit code.

## 4. First action
`python3 -B checks/continuity_check.py`
