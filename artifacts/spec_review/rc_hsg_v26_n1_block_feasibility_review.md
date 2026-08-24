# RC-HSG v2.6 N1 block-feasibility scientific review

Date: 2026-08-24  
Reviewed remote baseline: `1c432a02f50cacda99359f630f14cfbfdfb439a1`

## Outcome

Run 016 is accepted as full Regime-I outer-train A1 input/frontend admission. The next justified
step is exactly one outcome-blind N1 block-feasibility run. It is not yet justified to implement a
production N1 donor sampler, N2, semantic targets, reference scores, reliability models,
calibration, any Gate, or test evaluation.

## Repository findings

- `HEAD=origin/main=1c432a02...`, branch `main`, clean worktree.
- State validator reports 72 tasks / 37 DONE; status reports 8 SKIPPED, 26 BLOCKED and sole READY
  `S0_N1_BLOCK_FEASIBILITY`, owner `CHATGPT_OR_AUTHOR`.
- Route is unlocked and test remains `LOCKED_UNTIL_ROUTE_LOCK`.
- Run-016 hashes, 3,541-row ledger, 3,497 eligible cumulative reads, 3,390 run-016 reads, 44 short
  no-read rows, both outer roles and all PASS statuses were independently cross-checked.
- Server evidence records 198/198 tests with no skip. The review environment lacks h5py, so only
  project-memory 55/55 was locally reproducible; no unavailable suite is claimed as rerun.
- B_V9 is correctly closed. `GATE_R0.blocked_reason` is stale because it still says B_V9 is active
  and full frontend/early leakage are incomplete. v2.6 makes this wording repair mandatory without
  changing the blocked Gate outcome.

## Scientific design decision

The N1 scientific nuisance key remains `subject × session × length-bin × power-bin`; split role is
added only as a donor-scope firewall. Source experimental block is deliberately not added because
it was not in the pre-registered N1 key and would fragment cells after the fact.

Length bins reuse the already frozen EEG window-count strata `W01_04`, `W05_16`, `W17_PLUS`.
Committed metadata shows that train-fit is generally well populated, while inner-val contains
several extreme-length cells of size one to three. This makes binary power binning the highest
information/coverage choice; tertiles or per-band Cartesian bins would predictably over-fragment
inner-val before any outcome is observed.

The power proxy uses the exact A1 per-trial robust normalization and spectral tokenizer, then takes
the exact median of all finite log-relative-bandpower tokens. It is dimensionless and invariant to
positive global amplitude scaling, so it does not require resolving the release physical unit. It
is only a nuisance-matching scalar, not EEG evidence or a quality metric.

Power edges are fitted from train-fit only within each `subject × session × length-bin` cell. A
cell needs at least four train-fit rows; sparse cells become explicitly not evaluable. Edges are
binary medians, ties go to low, and no adjacent-length, cross-subject, inner-val, calibration or
test borrowing is allowed. Actual row proxies are never persisted.

Singleton blocks remain in the population but receive no donor. Coverage is reported both
conditional on A eligibility and against the complete outer-train population; the latter includes
short, edge-unavailable and singleton rows and is the frozen 0.90 decision denominator.

The K=199 feasibility probe is index-only. Each replicate is one joint, deterministic hash-sort
bijection inside every evaluable block. Fixed points are allowed and reported; forcing a
derangement would change the randomization law. All 199 joint mapping hashes must be unique, while
the actual donor map is not persisted.

## Decision consequences frozen before values

- PASS: every subject×role population coverage is at least 0.90 and structural checks pass. N1
  sampler research may continue, but primary fallback remains pending calibration coverage and
  Gate R0.
- DEGRADED_COVERAGE: structural checks pass but at least one subject×role is below 0.90. N1 may be
  implemented only for mechanism/robustness and can never become the primary fallback.
- FAIL: structural feasibility fails. N1 is removed and the next research task becomes N2.
- Execution/hash/read/test failure is a blocker, not a scientific FAIL, and causes no state
  migration.

## Paper direction

The paper remains RC-HSG: reference-relative information is used to estimate sample-level
reliability under stimulus-disjoint generalization. N2 retains primary reference priority; N1 is a
strict-randomization mechanism/robustness family and a pre-registered fallback only if its full
pre-test coverage and Gate R0 later pass. Therefore a degraded or failed N1 does not kill the paper,
and no run-017 result may revive the old evidence-increment/Gate-A-first story.

## Authorized next run

Run 017 may reread each of the 3,497 eligible outer-train arrays once for the new power-proxy
purpose through the exact audited loader and A1 spectral tokenizer. It must read zero short,
calibration or test arrays; save no proxy/token/embedding/donor map; produce only the frozen
assignment ledger, feasibility YAML and report; migrate state by the mechanical branch; then stop
at the next owner=`CHATGPT_OR_AUTHOR` task.
