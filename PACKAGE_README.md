# RC-HSG v2.9.3 active project handoff

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_9_3_2026-08-24.md` (version `v2.9.3`).

Baseline reviewed: `wip2@4fa6fadc8bdee0d163acc8bf9ee48aeac4d3095d`  
Completed: 2026-08-24

## Purpose

Run 020 completed cumulative v2.9.3 Gate R0. The exact 3,497-row one-read audit and
176-row matched panel produced `FAIL_NO_PRIMARY_REFERENCE`; N2 is not admitted and N1
remains mechanism/robustness-only.

## Stop state

The sole READY task is `S0_SEMANTIC_ITEM`, owner `CHATGPT_OR_AUTHOR`. Test remains
`LOCKED_UNTIL_ROUTE_LOCK` and the route remains unlocked. Do not start semantic/schema,
candidate/reference, reliability/calibration, later Gates, training, route lock, or test
unlock under run-020 authorization.
