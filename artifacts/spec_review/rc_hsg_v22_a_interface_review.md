# RC-HSG v2.2 A-interface pre-implementation review

Date: 2026-08-24  
Reviewed remote baseline: `main@91997faa1de1616d1eb662cd36edc1547613206d`  
Decision scope: outcome-blind `S0_A_INTERFACE` only

## Verdict

Run 012 is accepted. The repository is internally consistent with active RC-HSG v2.1: 67 tasks,
29 DONE, sole READY `S0_A_INTERFACE`, frozen Regime I/II split and population, and locked test.
The next scientifically valid action is not training or real-data admission. It is to freeze and
implement the project-native spectral A interface using synthetic tensors, while producing a
metadata-only eligibility overlay.

The supplied NC-HSG to RC-HSG redesign record remains correctly reflected in active v2.1:
reference information is a sample-level reliability input; Gate R/C/H are the core claims;
real-vs-reference population separation is Mechanism A and cannot kill the method by itself.
Nothing in the A-interface decision reactivates the old Gate-A attribution chain.

## Repository evidence checked

- Fresh clone is clean and `HEAD=origin/main=91997faa1de1616d1eb662cd36edc1547613206d`.
- Active SPEC is `guide/RC_HSG_Paper_Spec_v2_1_2026-08-24.md` and the A policy is
  `RC_HSG_NATIVE_SPECTRAL_A1_V1`.
- A-policy SHA256 is
  `034a523119f12f648266d94e0499179882fbe181584d10c1af17a3502a797425`.
- Analysis-view, split, data-card, targeted-manifest and dependency-lock hashes match v2.2 §21.1.
- Current local environment passed 104 available repository tests: project memory 48, joint split
  13, identity 12, similarity 12, analysis view 11 and input audit 8. Validator/status and
  `git diff --check` passed. The server run-012 record separately reports targeted audit 21/21;
  the review runtime lacks `h5py`, so that real-file audit was not falsely rerun or claimed locally.
- No real EEG value, semantic outcome, prediction, calibration result, test result or historical
  model metric was read during this review.

## Research result: short segments must remain in the population

Committed metadata contains 5,905 rows with `raw_samples` from 24 to 27,010. With the already
selected 500-sample window, 73 rows cannot produce a full window: 35 train-fit, 9 inner-val,
15 calibration and 14 locked-test rows. Deleting these rows would change the frozen subject-macro
population and selectively remove short trials. Padding would manufacture A input. Both would bias
the fixed-risk comparison.

v2.2 therefore resolves the previous phrase “fail admission” as an interface failure, not a
population exclusion. The pipeline must not call A on those rows and must force all A-dependent
methods to L0 on them. They remain in every denominator and paired common-row set. Their length,
window count and eligibility are forbidden model/reliability features. This is outcome-blind and
prevents a later performance-driven missing-row rule.

## Frozen interface decision

The code contract is fully specified in v2.2 §21 and is not delegated to Codex:

- exact public input `[B,105,T]`, valid lengths and frozen metadata assertions;
- explicit median/MAD-or-RMS normalization and clipping;
- full 500/250 symmetric-Hann windows only;
- exact 1-Hz rFFT bins, denominator, eight half-open bands, epsilon and feature order;
- exact 840-to-256 projection, two-layer pre-norm Transformer and masked outputs;
- exact trainable parameter count 1,270,528 and deterministic initialization;
- synthetic-only numerical/error/determinism/gradient tests;
- metadata-only 5,905-row eligibility build with 5,832 eligible, 73 forced-L0 rows and 60,522
  full windows; and
- no source-code copy, checkpoint, download, unit inference, interpolation or backbone switch.

The interface may be implemented now because all algorithm choices are fixed. Real EEG traversal
remains a separate `S0_A1_FRONTEND` task and must not be smuggled into run 013.

## Task-graph correction

The v2.1 graph would make `S0_LEAKAGE_AUDIT` and `S0_A1_FRONTEND` READY together after interface
completion. v2.2 changes leakage-audit prerequisites to `S0_A1_FRONTEND` plus `S0_JOINT_SPLIT`,
giving the single ordered chain:

```text
S0_A_INTERFACE -> S0_A1_FRONTEND -> S0_LEAKAGE_AUDIT -> S0_A1_ADMISSION
```

Run 013 must add/complete `SPEC_V22_REVIEW`, complete `S0_A_INTERFACE`, close/supersede B_V7,
open B_V8 for unvalidated real frontend, and stop with exactly 68 tasks, 31 DONE and sole READY
`S0_A1_FRONTEND`.

## Hard boundary for Codex

Codex is authorized to implement only the fixed interface, synthetic tests, metadata-only builder,
contracts/reports and project-memory migration. It is not authorized to inspect real EEG arrays,
train, choose seeds/optimizer, implement F/schema/candidates/N1/N2/reference/reliability/calibration,
run the full leakage audit or any Gate, change split/population/window policy, drop short rows or
unlock test. A fixed-fact conflict is `STATE_SPEC_CONFLICT`; an implementation/environment failure
is `A_INTERFACE_IMPLEMENTATION_BLOCKED`.
