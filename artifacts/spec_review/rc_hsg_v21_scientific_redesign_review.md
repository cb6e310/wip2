# RC-HSG v2.1 scientific redesign review

Date: 2026-08-24  
Reviewed remote: `https://github.com/cb6e310/wip2`  
Reviewed commit: `3b97fdc966b9b56d72287df619a80f6145d71189`

## Verdict

Run 011 is accepted. The deterministic joint split and population freeze are present on clean
`main`, with 164/41/68/69 primary group capacities, 34/34 calibration reserves, 18 LOSO folds,
locked test identities and the frozen equal-weight subject-macro/bootstrap contract. No model,
semantic statistic, calibration result, test value or Gate has been computed.

The author redesign record is accepted as a version-level scientific amendment. Because v2.0 is
already active and immutable run-011 provenance, the redesign activates as v2.1 rather than silently
replacing v2.0. Existing data, grouping, split, no-leakage and test-lock evidence are inherited.

The paper route changes from NC-HSG evidence attribution to RC-HSG reliability alignment. Reference
relative quantities are routing features; old Gate A becomes non-blocking Mechanism A. Core claim
survival is decided by Gate R (reference utility), Gate C (risk certification wording) and Gate H
(hierarchy utility).

## Frozen author decisions

1. Method name: `RC-HSG`.
2. Reference priority: admissible full-coverage N2 common-phase reference primary; N1 strict
   permutation mechanism/robustness and pre-registered fallback only.
3. Primary features: `s, delta, robust_z, empirical_upper_rank, MAD, structural_parent_features`.
4. Primary spread: MAD only.
5. Reliability model: per-level L2-regularized binomial-logistic GLM with fixed lambda grid and
   deterministic inner-val selection.
6. Candidate content: shared absolute-score, parent-consistent selection; reference affects routing
   only.
7. Anti-abstention: paired 95% upper bound for `Delta M_sem <= 0.05`.
8. Confirmatory family: RC-HSG vs Absolute-HSG, Flat-RC and PMI; one-sided subject-paired bootstrap
   with Holm family-wise 0.05.
9. Calibration data route: two-stage 34-group cal-select then independent 34-group cal-cert; theorem
   remains blocked by a required finite-sample feasibility review.
10. Primary A: project-native clean-room `RC_HSG_NATIVE_SPECTRAL_A1_V1`; no external source code,
    checkpoint, weight download, guessed unit or channel interpolation.

## Independent checks

- Fresh clone: `HEAD=origin/main=3b97fdc966b9b56d72287df619a80f6145d71189`; clean.
- Joint split 13/13, identity 12/12, similarity 12/12, analysis view 11/11, project memory 39/39,
  input audit 8/8: 95/95 PASS.
- Validator: PASS, 54 tasks, 26 DONE, sole READY `S0_A_POLICY_REVIEW`.
- Output hashes match run 011; `git diff --check` PASS.
- Server run 011 records targeted data audit 21/21 PASS; no local re-claim is made where an
  environment lacks the full data-audit dependency chain.

## Required transition

```text
SPEC_V21_REVIEW
-> S0_SCIENTIFIC_REDESIGN_FREEZE
-> S0_A_POLICY_REVIEW
-> S0_A_INTERFACE (READY; Codex; stop)
```

This activation run changes governance/specification only. It must not implement the frontend,
read EEG values or outcomes, download/import external models, unlock test, train, run the leakage
audit, or execute Gate R0/R/C/H/Mechanism A.
