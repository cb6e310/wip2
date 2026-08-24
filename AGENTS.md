# RC-HSG Project Instructions

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_7_2026-08-24.md` (version `v2.7`).

Before doing any work in this repository, read `AI_START_HERE.md` and follow
its recovery sequence. Project state must be recovered from
`PROJECT_STATE.yaml`, `HANDOFF.md`, `TASKS.yaml`, physical evidence, and run
records rather than chat history.

RC-HSG v2.7 sections 20-26 supersede the older NC-HSG scientific interpretation
and downstream Gate graph. Sections 14-19 and committed run-011 artifacts
remain authoritative for data, identity, split, population, and test-lock
facts. If state, evidence, and the active SPEC disagree, report
`STATE_SPEC_CONFLICT` and stop instead of guessing.

Run 018 implemented the metadata-only N1 mechanism sampler with exact parity for all
199 run-017 mappings, 35,529 fixed points, and zero EEG/text/outcome/test reads. N1
remains ineligible as the primary fallback due to frozen `DEGRADED_COVERAGE`. The sole
READY task is `S0_N2_SAMPLER`, owner `CHATGPT_OR_AUTHOR`; it requires a new exact
common-phase contract and is not authorized by run 018.
Before ending any state-changing
session, update the state files, add one immutable run record, and run the
validator, status command, relevant tests, and `git diff --check`.
