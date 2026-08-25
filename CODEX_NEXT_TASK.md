# Codex stop state after RC-HSG v2.9.3 Gate R0

## Completed run

- Run 020 completed cumulative v2.9.3 Gate R0.
- Scientific decision: `FAIL_NO_PRIMARY_REFERENCE`.
- N2 primary: `NOT_ADMITTED`.
- N1: structural PASS, mechanism/robustness-only, primary-ineligible.
- All 3,497 eligible outer-train arrays were read exactly once.
- Short, calibration, test EEG, text, outcome, and test-identity reads were zero.

## Current stop state

- Active SPEC: `guide/RC_HSG_Paper_Spec_v2_9_3_2026-08-24.md` (version `v2.9.3`).
- Tasks: 79 total / 48 DONE / 8 SKIPPED / 22 BLOCKED / 1 READY.
- Sole READY: `S0_SEMANTIC_ITEM`, owner=`CHATGPT_OR_AUTHOR`.
- Route: unlocked; provisional primary=`ORDINARY_HIERARCHICAL_SELECTIVE_GENERATION`.
- Test: `LOCKED_UNTIL_ROUTE_LOCK`.
- Gate R/C/H and Mechanism A outcomes remain null.

`S0_SEMANTIC_ITEM` has not been authorized for execution. A new exact ChatGPT/author-frozen contract must adjudicate the ordinary hierarchical semantic schema and any downstream task-graph migration after the failed reference Gate.

Do not rerun Gate R0 or alter its panel, model, target, thresholds, metrics, replicates, artifacts, or decision. Do not implement semantic/schema/candidates/reference features/reliability/calibration; do not train, read calibration/test/outcomes, execute Gate R/C/H or Mechanism A, lock route, or unlock test.
