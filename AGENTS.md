# RC-HSG Project Instructions

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_9_3_2026-08-24.md` (version `v2.9.3`).

Before doing any work in this repository, read `AI_START_HERE.md` and follow
its recovery sequence. Project state must be recovered from
`PROJECT_STATE.yaml`, `HANDOFF.md`, `TASKS.yaml`, physical evidence, and run
records rather than chat history.

RC-HSG v2.9.3 sections 20-31 supersede the older NC-HSG scientific interpretation
and downstream Gate graph. Sections 14-19 and committed run-011 artifacts
remain authoritative for data, identity, split, population, and test-lock
facts. If state, evidence, and the active SPEC disagree, report
`STATE_SPEC_CONFLICT` and stop instead of guessing.

Run 020 completed the frozen outcome-blind Gate R0 audit. All 3,497 eligible outer-train
arrays were read exactly once; short, calibration, test, text, outcome, and test-identity
reads were zero. The mechanical result is `FAIL_NO_PRIMARY_REFERENCE`: N2 is not admitted,
and N1 remains mechanism/robustness-only and primary-ineligible. The route is still
unlocked with ordinary hierarchical selective generation as the provisional primary.
The sole READY task is `S0_SEMANTIC_ITEM`, owner `CHATGPT_OR_AUTHOR`; run 020 does not
authorize its implementation.
Before ending any state-changing
session, update the state files, add one immutable run record, and run the
validator, status command, relevant tests, and `git diff --check`.
