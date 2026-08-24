# RC-HSG Project Instructions

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_8_2026-08-24.md` (version `v2.8`).

Before doing any work in this repository, read `AI_START_HERE.md` and follow
its recovery sequence. Project state must be recovered from
`PROJECT_STATE.yaml`, `HANDOFF.md`, `TASKS.yaml`, physical evidence, and run
records rather than chat history.

RC-HSG v2.8 sections 20-27 supersede the older NC-HSG scientific interpretation
and downstream Gate graph. Sections 14-19 and committed run-011 artifacts
remain authoritative for data, identity, split, population, and test-lock
facts. If state, evidence, and the active SPEC disagree, report
`STATE_SPEC_CONFLICT` and stop instead of guessing.

Run 019 implemented the synthetic-only N2 multivariate common-phase sampler with the
frozen SHA256/PCG64 law, 199-replicate replay, preservation diagnostics, and zero real
EEG/text/outcome/test reads. N1 remains mechanism/robustness only and N2 is not admitted
as primary until a real outcome-blind Gate R0 passes. The sole READY task is `GATE_R0`,
owner `CHATGPT_OR_AUTHOR`; it requires a new exact real-audit contract and is not
authorized by run 019.
Before ending any state-changing
session, update the state files, add one immutable run record, and run the
validator, status command, relevant tests, and `git diff --check`.
