# RC-HSG Project Instructions

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_5_2026-08-24.md` (version `v2.5`).

Before doing any work in this repository, read `AI_START_HERE.md` and follow
its recovery sequence. Project state must be recovered from
`PROJECT_STATE.yaml`, `HANDOFF.md`, `TASKS.yaml`, physical evidence, and run
records rather than chat history.

RC-HSG v2.5 sections 20-24 supersede the older NC-HSG scientific interpretation
and downstream Gate graph. Sections 14-19 and committed run-011 artifacts
remain authoritative for data, identity, split, population, and test-lock
facts. If state, evidence, and the active SPEC disagree, report
`STATE_SPEC_CONFLICT` and stop instead of guessing.

The frozen A1 frontend is admitted on all 3,497 eligible outer-train rows: run 014
evidence covers 107 rows and run 016 scanned the remaining 3,390 once; all 44
short rows remain forced L0 without dereference. The sole READY task is
`S0_N1_BLOCK_FEASIBILITY`; do not execute it without a new ChatGPT/author-frozen
exact contract. Before ending any state-changing
session, update the state files, add one immutable run record, and run the
validator, status command, relevant tests, and `git diff --check`.
