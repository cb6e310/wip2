# RC-HSG v2.9.2 Gate R0 LogisticRegression API addendum（2026-08-24）

> **Authority and scope.** This author-frozen addendum resolves the second
> pre-read `TECHNICAL_ABORT_NO_OUTCOME` in run-020. It supersedes only the v2.9
> §28.5 `LogisticRegression` constructor and the directly dependent model-warning
> preflight. v2.9.1 §29 remains authoritative for the 176-row matched-support
> panel. Every other v2.9 §28 input, read, transform, classifier, bootstrap,
> threshold, nuisance/numerical audit, outcome, safety, test, state, commit/push,
> and hard-stop contract remains unchanged.

> At adjudication time, the v2.9.1 support/panel preflight had passed, but there
> had been zero production HDF5 dereferences, zero eligible/short/cal/test EEG
> reads, zero text/outcome/test-identity reads, no production Gate CLI, no Gate
> outcome, and no repository modification. The remote baseline remains
> `4fa6fadc8bdee0d163acc8bf9ee48aeac4d3095d`.

## 30.1 Conflict adjudication

The frozen v2.9 constructor explicitly set `penalty="l2"`. In scikit-learn
1.9.0 that legacy spelling is mathematically valid and converges, but emits a
deterministic `FutureWarning` because `penalty` was deprecated in version 1.8
and is scheduled for removal in 1.10. The same v2.9 contract required technical
abort on any warning and prohibited an implementation-agent parameter change.
Codex therefore stopped at the correct boundary.

The official scikit-learn equivalence is:

```text
legacy penalty="l2"  <=>  l1_ratio=0
```

The author-level repair is to use the supported API spelling, not to weaken the
warning rule. Production Gate code must omit the deprecated `penalty` argument
and explicitly set `l1_ratio=0.0`. This preserves the same L2-regularized
binomial-logistic objective, `C`, solver, tolerance, iteration cap, intercept,
class weighting, and warm-start behavior.

Authoritative sources:

```text
https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
https://scikit-learn.org/stable/whats_new/v1.8.html
```

## 30.2 Frozen production constructor

The v2.9 §28.5 constructor is replaced exactly by:

```python
LogisticRegression(
    l1_ratio=0.0,
    C=1.0,
    solver="lbfgs",
    tol=1e-8,
    max_iter=2000,
    fit_intercept=True,
    class_weight=None,
    warm_start=False,
)
```

Production code must not pass `penalty` at all. It must not set or tune any
additional constructor argument. In artifacts and reports, the scientific
model identity is recorded as:

```text
model_family                  binomial_logistic_regression
regularization                L2
regularization_api            l1_ratio=0.0
C                             1.0
solver                        lbfgs
tol                           1e-8
max_iter                      2000
fit_intercept                 true
class_weight                  null
warm_start                    false
sklearn_version               1.9.0
```

No model family, penalty strength, feature, standardization, label, sample,
bootstrap, score, or Gate threshold changes.

## 30.3 Warning law remains fail-closed

Every production constructor call and `.fit(...)` must execute inside a local
`warnings.catch_warnings(record=True)` context with
`warnings.simplefilter("always")`. The captured warning list must be empty.

```text
production warning count == 0                    continue
production warning count > 0                     TECHNICAL_ABORT_NO_OUTCOME
constructor/fit exception                        TECHNICAL_ABORT_NO_OUTCOME
```

No production warning category is globally ignored, filtered, demoted, or
allowlisted. In particular, `ConvergenceWarning`, `RuntimeWarning`,
`FutureWarning`, `DeprecationWarning`, and `UserWarning` all remain fatal if
emitted by the revised production path. The only expected legacy warning is
captured inside the isolated equivalence test in §30.4; that test never reads
real data and its local capture must not change the process warning filters.

## 30.4 Mandatory isolated API-equivalence certificate

Before any real array read, use scikit-learn exactly `1.9.0` and the following
fixed float64 fixture:

```python
X = np.asarray([
    [-2.0, -1.0,  0.00],
    [-1.5, -0.5,  0.25],
    [-1.0, -1.5, -0.25],
    [-0.5, -2.0,  0.50],
    [ 0.5,  2.0, -0.50],
    [ 1.0,  1.5,  0.25],
    [ 1.5,  0.5, -0.25],
    [ 2.0,  1.0,  0.00],
], dtype=np.float64)
y = np.asarray([0, 0, 0, 0, 1, 1, 1, 1], dtype=np.int64)
```

Fit two estimators in separate local warning-capture contexts:

```text
legacy: v2.9 constructor with penalty="l2" and no l1_ratio argument
modern: §30.2 constructor with l1_ratio=0.0 and no penalty argument
```

The certificate must prove:

1. `sklearn.__version__ == "1.9.0"`.
2. Legacy fit emits exactly one warning.
3. Its category is exactly `FutureWarning`.
4. Its normalized message contains both
   `penalty was deprecated in version 1.8` and `removed in 1.10`.
5. Modern construction and fit emit zero warnings.
6. Both estimators have identical `classes_` and `n_iter_`.
7. `coef_`, `intercept_`, `decision_function(X)`, and `predict_proba(X)` agree
   with `rtol=0` and `atol=1e-14`.
8. Both satisfy `1 <= int(n_iter_[0]) < 2000` and all compared arrays are
   finite.

Write only a compact metadata certificate—versions, warning category/message
SHA256, iteration counts, comparison maxima, tolerances, verdict, and safety
flags—to:

```text
artifacts/gates/gate_r0_logistic_api_equivalence_v1.yaml
```

Do not persist fixture arrays, coefficients, intercepts, decision values, or
probabilities. The certificate must be byte-stable and contain no absolute
temporary path or timestamp. Any mismatch is
`GATE_R0_MODEL_API_EQUIVALENCE_MISMATCH / TECHNICAL_ABORT_NO_OUTCOME` before
the first real dataset dereference.

## 30.5 Production post-fit assertions

For every production fit required by v2.9, in addition to the zero-warning law,
assert before using predictions:

```text
classes_ == [0, 1]
n_iter_.shape == (1,)
1 <= int(n_iter_[0]) < 2000
coef_, intercept_, decision values and probabilities are finite
probability rows are finite, within [0,1], and sum to 1 within v2.9 tolerance
n_features_in_ equals the frozen feature width
```

Any failure is `GATE_R0_MODEL_FIT_INVALID / TECHNICAL_ABORT_NO_OUTCOME`.
Iteration count is diagnostic, not a tunable target. The observed isolated
legacy count `32` is not frozen as a production or fixture expectation.

## 30.6 Tests and negative mutations

Add focused tests proving:

- the production constructor has no `penalty` keyword and has
  `l1_ratio=0.0`;
- the exact remaining constructor values are frozen;
- official legacy/modern equivalence passes on §30.4;
- modern construction and fit are warning-free under `simplefilter("always")`;
- explicit `penalty="l2"` in production is rejected before real read;
- changing `l1_ratio`, `C`, solver, tolerance, iteration cap, intercept,
  class-weight, or warm-start fails closed;
- injected `FutureWarning`, `ConvergenceWarning`, `RuntimeWarning`, and
  `UserWarning` each cause technical abort;
- equivalence coefficient/probability drift above `1e-14`, altered warning
  category/message, version drift, nonfinite output, wrong classes, or
  `n_iter_ >= 2000` fails closed;
- warning filters outside the local legacy-equivalence context are unchanged;
- the certificate contains no fixture/model values or forbidden paths and is
  byte-identical across two builds;
- an abort leaves all read counters at zero and Gate outcome null.

All v2.9 and v2.9.1 targeted, regression, full-suite, validator, status, and
diff checks remain mandatory and must pass with zero skip.

## 30.7 Run/state law

The two pre-read aborts remain external provenance, not scientific outcomes or
completed repository runs:

```text
v2.9 abort reason       impossible 216-row panel assertion
v2.9.1 abort reason     deprecated legacy model API + any-warning law
scientific outcome      null
production data reads   zero
repository mutation     none
authorized retry        run-020 under cumulative v2.9.2
```

After all v2.9.1 panel and v2.9.2 model preflights pass, execute the unchanged
Gate R0 chain. Scientific PASS/FAIL and technical-abort semantics remain v2.9
§28.7. Neither preflight repair constitutes a scientific PASS.

Importing v2.9, v2.9.1, and v2.9.2 adds three review tasks. On completed
scientific PASS or FAIL, the final counts are:

```text
78 total / 47 DONE / 8 SKIPPED / 22 BLOCKED / 1 READY
```

The sole READY is still `S0_SEMANTIC_ITEM`, owner=`CHATGPT_OR_AUTHOR`; route
remains unlocked, test remains locked, all later Gate outcomes remain null, and
the hard stop remains mandatory. `SPEC_V292_REVIEW` has prerequisite
`SPEC_V291_REVIEW` and is completed by run-020. A technical abort produces no
scientific outcome and no final state transition.

## 30.8 Cumulative active-spec assembly

Supply the original v2.9, v2.9.1, and v2.9.2 packages. Validate:

```text
v2.9 ZIP SHA256    6d5e0327a1d8fc0477a787d014b01218a9427b1794a3830e81b020468c8ec2fc
v2.9.1 ZIP SHA256  e84a13d958ea509574c0479b8082df2feddbb3750d76c94742eee5f8a131061b
```

First rebuild cumulative v2.9.1 exactly as §29.7 and require SHA256:

```text
d37692f7ed64c33d53534b5ccdfefa600775c4e66874523a00254242d3205f40
```

Then construct the cumulative active v2.9.2 file mechanically:

```text
base = bytes(cumulative v2.9.1).rstrip(CR/LF)
addendum = bytes(this file).lstrip(CR/LF)
active = base || LF || LF || addendum
output = guide/RC_HSG_Paper_Spec_v2_9_2_2026-08-24.md
```

Record its SHA256 in run-020 and all active entrypoints. Historical specs,
reviews, abort reports, runs, and artifacts remain append-only.
