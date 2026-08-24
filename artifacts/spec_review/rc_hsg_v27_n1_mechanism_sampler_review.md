# RC-HSG v2.7 N1 mechanism-sampler scientific review

Date: 2026-08-24  
Reviewed remote baseline: `082ed4f72f1b8bbc18096a5f0caea2075b2783c4`

## Outcome

Run 017 is accepted as an outcome-blind structural audit of the frozen N1 assignment law. N1 is
structurally reproducible but has the frozen result `DEGRADED_COVERAGE`; it is permanently
ineligible as primary fallback. The justified repository action is one minimal index-only N1
mechanism sampler, followed immediately by a stop at `S0_N2_SAMPLER` for a new author-frozen N2
contract.

## Remote repository findings

- Clean `main`, `HEAD=origin/main=082ed4f7...`, commit `feat: audit N1 block feasibility`.
- Validator reports `PROJECT STATE VALID`; status is 73 tasks / 39 DONE / 8 SKIPPED /
  25 BLOCKED / 1 READY.
- Sole READY is `S0_N1_SAMPLER`, owner `CHATGPT_OR_AUTHOR`; route remains unlocked and test remains
  `LOCKED_UNTIL_ROUTE_LOCK`.
- Run 017 records full discovery 219/219, project-memory 59/59 and the new feasibility suite 17/17,
  all no skip. `git diff --check` passes.
- Fixed hashes for the v2.6 SPEC/review, assignment, feasibility YAML/report/code, run 017, split
  and A1 admission ledger were recomputed from the clean checkout.

## Evidence review

The assignment has 3,541 outer-train rows: 3,481 evaluable and 60 non-evaluable (44 short
forced-L0, four unavailable power edges and 12 singleton rows). It yields 192 populated
role-scoped blocks, 180 evaluable blocks, and 199/199 unique joint mapping hashes with zero
bijection or cross-block violations.

An independent local reimplementation rebuilt all 199 mappings from the committed assignment.
Every joint hash and fixed-point count matched the committed feasibility YAML; the total was
35,529 fixed points, range 145–214. This is independent evidence that the production sampler can
be implemented from metadata without rereading EEG or importing the feasibility script.

## Why N1 was degraded

The minimum population coverage is `YAK × inner_val = 28/36 = 0.777777777778`: seven rows are
short and one lacks a train-fit power edge. `YAK × train_fit = 118/143 = 0.825174825175`, with 24
short rows and one unavailable edge. Overall eligible-conditional coverage is 0.995424649700, so
the main limitation is the pre-frozen complete-population denominator rather than permutation
integrity.

Changing bins, borrowing an edge, deleting short/singleton rows, forcing derangements or changing
the denominator would be post-result redesign. v2.7 forbids those changes.

## Scientific direction

N2 common-phase remains the primary reference family. N1 is retained only as a strict blockwise
mechanism/robustness reference. The implementation budget is therefore deliberately small: a
metadata-only mapper, a 199-row parity manifest, and synthetic tests that prove real and
pseudo-real observations traverse the same select-then-score callback.

No semantic schema or candidate library is frozen, so run 018 cannot compute a randomization
p-value or claim exchangeability/semantic validity. Those claims remain blocked until Gate R0 and
the candidate/path pipeline exist.

## Authorized next action

Implement only §26 of the v2.7 SPEC, update project memory and run 018, commit/push, then stop with
sole READY `S0_N2_SAMPLER`, owner `CHATGPT_OR_AUTHOR`. Do not begin N2, reread real arrays, create
donor values, train, execute a Gate, lock the route or unlock test.
