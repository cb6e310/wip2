# RC-HSG Project Instructions

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_4_2026-08-24.md` (version `v2.4`).

Before doing any work in this repository, read `AI_START_HERE.md` and follow
its recovery sequence. Project state must be recovered from
`PROJECT_STATE.yaml`, `HANDOFF.md`, `TASKS.yaml`, physical evidence, and run
records rather than chat history.

RC-HSG v2.4 sections 20-23 supersede the older NC-HSG scientific interpretation
and downstream Gate graph. Sections 14-19 and committed run-011 artifacts
remain authoritative for data, identity, split, population, and test-lock
facts. If state, evidence, and the active SPEC disagree, report
`STATE_SPEC_CONFLICT` and stop instead of guessing.

The frozen 107-row bounded real-frontend panel and the static-code/committed-metadata
A-path leakage firewall passed without new real-value reads; this is not full
outer-train admission. The sole READY task is `S0_A1_ADMISSION`; do not execute it
without a new author-frozen exact contract. Before ending any state-changing
session, update the state files, add one immutable run record, and run the
validator, status command, relevant tests, and `git diff --check`.
