# RC-HSG Project Instructions

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_3_2026-08-24.md` (version `v2.3`).

Before doing any work in this repository, read `AI_START_HERE.md` and follow
its recovery sequence. Project state must be recovered from
`PROJECT_STATE.yaml`, `HANDOFF.md`, `TASKS.yaml`, physical evidence, and run
records rather than chat history.

RC-HSG v2.3 sections 20-22 supersede the older NC-HSG scientific interpretation
and downstream Gate graph. Sections 14-19 and committed run-011 artifacts
remain authoritative for data, identity, split, population, and test-lock
facts. If state, evidence, and the active SPEC disagree, report
`STATE_SPEC_CONFLICT` and stop instead of guessing.

The frozen 107-row bounded real-frontend panel passed on CPU and CUDA without
training or outcome reads; this is not full outer-train admission. The sole
READY task is the early `S0_LEAKAGE_AUDIT`; do not execute it without a new
exact instruction. Before ending any state-changing
session, update the state files, add one immutable run record, and run the
validator, status command, relevant tests, and `git diff --check`.
