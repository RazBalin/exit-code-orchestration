# CONTINUITY: Boulder Moss Survey (fictional)

Read in full at every session open. Budgets: config/workspace.json; checked by
`python3 -B checks/continuity_check.py`.

## 1. State (what is true now)

- Goal of the season: cover estimates for all 48 quadrats on the twelve survey boulders, recounted
  where the two observers disagree by more than the agreed margin (DECISIONS_S07 item 1).
- Analysis: `analysis/cover_model.py` fits the season's cover model from the derived table
  `analysis/derived/cover_by_quadrat.csv`; the raw plot sheets stay in `data/field_raw/`, read by the
  investigator alone.
- Manuscript: `manuscript/draft.md`, methods section drafted; no result section yet.
- Outbound: the season summary for the program's funder, `outbound/season_summary.md`, audit exit 0.

## 2. Open decisions

- None open. DECISIONS_S07 answered 2025-03-14 (all three items executed).

## 3. Clocks

See `CLOCKS.md`.

## 4. Close summaries

**CLOSE · 2025-03-07 (S06).** Goal: the photo index rebuilt from the field log; reached. Verified:
`python3 -B checks/continuity_check.py` exit 0. Next action: the recount decision.

**CLOSE · 2025-03-14 (S07).** Goal: the recount decided and launched; reached. Decided, in the
investigator's words: "recount the six disputed quadrats in April, same two observers". Paths
written: `records/2025-03-14_S07/`. Verified: the launch gate and the outbound audit, both exit 0.
Open: the recount, due 2025-04-18. Next action: the worker session from `LAUNCH_RECOUNT_2025-03-14.md`.
