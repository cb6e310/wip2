# RC-HSG v2.3 active project handoff

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_3_2026-08-24.md` (version `v2.3`).

Baseline reviewed: `wip2@237788090dcb20e533f304f63ae8feb2f545fe0b`  
Activated: 2026-08-24

## Purpose

Run 014 activates v2.3 and validates the exact
`RC_HSG_NATIVE_SPECTRAL_A1_V1` interface on the frozen bounded real-data panel.
It does not perform full admission, leakage audit, or any later component.

Run-011 data, stimulus identity/grouping, deterministic split, subject-macro
population, bootstrap, and test-lock artifacts remain immutable. RC-HSG v2.1
section 20 supersedes only the older NC-HSG scientific interpretation and
downstream Gate/task architecture.

## Active files

- `guide/RC_HSG_Paper_Spec_v2_3_2026-08-24.md`: active scientific and governance contract.
- `artifacts/spec_review/rc_hsg_v23_real_frontend_review.md`: accepted bounded-frontend review.
- `artifacts/backbone_a_policy.yaml`: author-frozen native spectral A policy.
- `artifacts/backbone_a_contract.yaml`: implemented synthetic interface contract.
- `artifacts/a1_frontend_freeze.yaml`: bounded real-frontend validation contract.
- `runs/2026-08-24_014_a1_real_frontend_validation.md`: immutable validation record.
- `CODEX_NEXT_TASK.md`: sole next-task boundary.

## Stop state

The early `S0_LEAKAGE_AUDIT` is the sole READY recommendation and is owned by
`CODEX`. The 107-row panel passed, but 3,390 eligible rows remain unread and
full admission is pending. Test remains locked. Do not read further EEG or
outcomes, train, run either leakage audit, execute any Gate, or continue beyond
this stop without a new exact instruction.
