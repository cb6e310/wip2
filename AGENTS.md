# RC-HSG Project Instructions

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_6_2026-08-24.md` (version `v2.6`).

Before doing any work in this repository, read `AI_START_HERE.md` and follow
its recovery sequence. Project state must be recovered from
`PROJECT_STATE.yaml`, `HANDOFF.md`, `TASKS.yaml`, physical evidence, and run
records rather than chat history.

RC-HSG v2.6 sections 20-25 supersede the older NC-HSG scientific interpretation
and downstream Gate graph. Sections 14-19 and committed run-011 artifacts
remain authoritative for data, identity, split, population, and test-lock
facts. If state, evidence, and the active SPEC disagree, report
`STATE_SPEC_CONFLICT` and stop instead of guessing.

Run 017 read each of the 3,497 eligible outer-train arrays once through the audited
loader and exact A1 spectral tokenizer; all 44 short rows remained no-read. Structural
feasibility passed, but minimum subject-role coverage was 0.777777777778, so the frozen
decision is `DEGRADED_COVERAGE`. The sole READY task is `S0_N1_SAMPLER`, owner
`CHATGPT_OR_AUTHOR`; it requires a new exact contract and is not authorized by run 017.
Before ending any state-changing
session, update the state files, add one immutable run record, and run the
validator, status command, relevant tests, and `git diff --check`.
