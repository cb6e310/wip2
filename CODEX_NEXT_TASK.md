# Codex stop state after run 018

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_7_2026-08-24.md` (version `v2.7`).

Run 018 completed `SPEC_V27_REVIEW -> S0_N1_SAMPLER` and stopped. The
metadata-only mechanism sampler reconstructs 199 joint within-block permutations
over 3,481 evaluable rows in 180 blocks, preserving 60 exclusions. Every mapping
hash and fixed-point count matches run 017; hashes are 199/199 unique and fixed
points total 35,529 with range 145..214.

N1 remains permanently ineligible as the primary fallback because run 017 froze
`DEGRADED_COVERAGE`. It is available only for later mechanism/robustness work after
the remaining contracts and Gate R0 are complete.

The repository has 74 tasks, 41 DONE, 8 SKIPPED, 24 BLOCKED, and one READY task:
`S0_N2_SAMPLER`, owner `CHATGPT_OR_AUTHOR`. That task requires a new exact
multivariate common-phase contract and is not authorized by the run-018 package.

B_V4 remains active without blocking its N2 resolver. Every Gate remains BLOCKED
with null outcome, the route remains unlocked, and test remains
`LOCKED_UNTIL_ROUTE_LOCK`.

STOP. Do not begin N2, Gate R0, schema/candidates/reference features, training,
calibration, route lock, or test work. Run 018 read zero EEG, text, outcome, or
test content and did not calculate a paper p-value.
