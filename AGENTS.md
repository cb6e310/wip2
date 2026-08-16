# NC-HSG Project Instructions

Active SPEC: `guide/NC_HSG_Paper_Spec_v1_5_2026-08-16.md` (version `v1.5`).

Before doing any work in this repository, read `AI_START_HERE.md` and follow
its recovery sequence. Project state must be recovered
from `PROJECT_STATE.yaml`, `HANDOFF.md`, `TASKS.yaml`, physical evidence, and
run records rather than chat history.

If state, evidence, and the active SPEC disagree, report
`STATE_SPEC_CONFLICT` and stop instead of guessing. Before ending any
state-changing session, update the state files, add one immutable run record,
and run the validator, status command, relevant tests, and `git diff --check`.
