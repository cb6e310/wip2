# RC-HSG v2.1 active project handoff

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_1_2026-08-24.md` (version `v2.1`).

Baseline reviewed: `wip2@3b97fdc966b9b56d72287df619a80f6145d71189`  
Activated: 2026-08-24

## Purpose

Run 012 activates the author-frozen RC-HSG scientific redesign, migrates the
task/state machine, and materializes `RC_HSG_NATIVE_SPECTRAL_A1_V1`. It does
not implement the frontend or any later scientific component.

Run-011 data, stimulus identity/grouping, deterministic split, subject-macro
population, bootstrap, and test-lock artifacts remain immutable. RC-HSG v2.1
section 20 supersedes only the older NC-HSG scientific interpretation and
downstream Gate/task architecture.

## Active files

- `guide/RC_HSG_Paper_Spec_v2_1_2026-08-24.md`: active scientific and governance contract.
- `artifacts/spec_review/rc_hsg_v21_scientific_redesign_review.md`: accepted baseline/redesign review.
- `artifacts/backbone_a_policy.yaml`: author-frozen native spectral A policy.
- `runs/2026-08-24_012_rc_hsg_scientific_redesign_freeze.md`: immutable activation record.
- `CODEX_NEXT_TASK.md`: sole next-task boundary.

## Stop state

`S0_A_INTERFACE` is the sole READY recommendation and is owned by `CODEX`.
The A policy is selected but the frontend is not implemented. Test remains
locked. Do not read EEG/outcomes, copy or download external model code/weights,
train, run the full leakage audit, execute any Gate, or continue beyond this
stop without a new exact instruction.
