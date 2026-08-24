# RC-HSG v2.7 active project handoff

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_7_2026-08-24.md` (version `v2.7`).

Baseline reviewed: `wip2@082ed4f72f1b8bbc18096a5f0caea2075b2783c4`  
Completed: 2026-08-24

## Purpose

Run 018 completed the frozen metadata-only N1 mechanism sampler. All 199 mappings
match run 017 exactly, with 35,529 fixed points, 3,481 evaluable rows, 180 blocks,
and 60 exclusions. Synthetic tests prove complete selection/path recomputation.

## Stop state

The sole READY task is `S0_N2_SAMPLER`, owner `CHATGPT_OR_AUTHOR`, under a new
exact common-phase contract. Test remains `LOCKED_UNTIL_ROUTE_LOCK` and the route
remains unlocked. Do not begin N2, train, execute Gate R0, or unlock test under
run-018 authorization.
