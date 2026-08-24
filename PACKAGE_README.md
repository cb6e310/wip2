# RC-HSG v2.2 active project handoff

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_2_2026-08-24.md` (version `v2.2`).

Baseline reviewed: `wip2@91997faa1de1616d1eb662cd36edc1547613206d`  
Activated: 2026-08-24

## Purpose

Run 013 activates v2.2 and implements the exact synthetic
`RC_HSG_NATIVE_SPECTRAL_A1_V1` interface plus metadata-only eligibility overlay.
It does not validate real EEG traversal or implement any later component.

Run-011 data, stimulus identity/grouping, deterministic split, subject-macro
population, bootstrap, and test-lock artifacts remain immutable. RC-HSG v2.1
section 20 supersedes only the older NC-HSG scientific interpretation and
downstream Gate/task architecture.

## Active files

- `guide/RC_HSG_Paper_Spec_v2_2_2026-08-24.md`: active scientific and governance contract.
- `artifacts/spec_review/rc_hsg_v22_a_interface_review.md`: accepted baseline/interface review.
- `artifacts/backbone_a_policy.yaml`: author-frozen native spectral A policy.
- `artifacts/backbone_a_contract.yaml`: implemented synthetic interface contract.
- `runs/2026-08-24_013_native_spectral_a_interface.md`: immutable implementation record.
- `CODEX_NEXT_TASK.md`: sole next-task boundary.

## Stop state

`S0_A1_FRONTEND` is the sole READY recommendation and is owned by `CODEX`.
The interface is synthetic-tested but real EEG traversal is unvalidated. Test
remains locked. Do not read EEG/outcomes without an exact instruction, copy or download external model code/weights,
train, run the full leakage audit, execute any Gate, or continue beyond this
stop without a new exact instruction.
