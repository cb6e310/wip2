# Codex Next Task - RC-HSG v2.3 / S0_LEAKAGE_AUDIT

## Stop state

Run 014 completed `SPEC_V23_REVIEW -> S0_A1_FRONTEND`. The bounded 107-row
real-frontend panel and all 44 no-read outer-train short ledger rows passed the
frozen CPU/CUDA self-check. This is not full admission.

Current state is exactly 70 tasks, 33 DONE, 8 SKIPPED, 28 BLOCKED, and one
READY task. The sole recommended task is `S0_LEAKAGE_AUDIT`, owner `CODEX`.
Test remains `LOCKED_UNTIL_ROUTE_LOCK`.

## Next boundary

Under a new exact instruction, `S0_LEAKAGE_AUDIT` may audit only the Regime-I
data split and A-frontend firewall: source/role allowlists, train-fit and
inner-val scope, short bypass, zero calibration/test dereference, no cross-row
normalization or fitting, no output cache, and fail-closed loading.

Do not execute that task from run 014. Do not start `S0_A1_ADMISSION`, read the
remaining 3,390 eligible rows, read short/calibration/test arrays or outcomes,
run `S0_METHOD_LEAKAGE_AUDIT`, train, implement later methods, execute a Gate,
or unlock test without a new exact instruction.
