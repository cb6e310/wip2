# RC-HSG v2.6 active project handoff

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_6_2026-08-24.md` (version `v2.6`).

Baseline reviewed: `wip2@1c432a02f50cacda99359f630f14cfbfdfb439a1`  
Completed: 2026-08-24

## Purpose

Run 017 completed the frozen outcome-blind outer-train N1 block-feasibility
audit. It used the audited loader and exact A1 spectral tokenizer on 3,497
eligible arrays once, while reading zero short, calibration, or test arrays.

The decision is `DEGRADED_COVERAGE`: structural status PASS, minimum
subject-role population coverage 0.777777777778, and 199/199 unique joint
mapping hashes. This does not admit N1 as the primary fallback.

## Stop state

The sole READY task is `S0_N1_SAMPLER`, owner `CHATGPT_OR_AUTHOR`, for
mechanism/robustness only under a new exact contract. Test remains
`LOCKED_UNTIL_ROUTE_LOCK` and the route remains unlocked. Do not rerun the
production scan, implement a sampler, train, execute a Gate, or unlock test
under run-017 authorization.
