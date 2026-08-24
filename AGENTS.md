# RC-HSG Project Instructions

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_1_2026-08-24.md` (version `v2.1`).

Before doing any work in this repository, read `AI_START_HERE.md` and follow
its recovery sequence. Project state must be recovered from
`PROJECT_STATE.yaml`, `HANDOFF.md`, `TASKS.yaml`, physical evidence, and run
records rather than chat history.

RC-HSG v2.1 section 20 supersedes the older NC-HSG scientific interpretation
and downstream Gate graph. Sections 14-19 and committed run-011 artifacts
remain authoritative for data, identity, split, population, and test-lock
facts. If state, evidence, and the active SPEC disagree, report
`STATE_SPEC_CONFLICT` and stop instead of guessing.

The author has frozen `RC_HSG_NATIVE_SPECTRAL_A1_V1`, but the frontend is not
implemented. The sole READY task is `S0_A_INTERFACE`; do not proceed beyond
that task without a new exact instruction. Before ending any state-changing
session, update the state files, add one immutable run record, and run the
validator, status command, relevant tests, and `git diff --check`.
