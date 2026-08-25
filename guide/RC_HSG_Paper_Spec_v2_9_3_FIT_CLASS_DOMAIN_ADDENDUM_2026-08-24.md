# RC-HSG v2.9.3 Gate R0 fit-class-domain addendum（2026-08-24）

> **Authority and scope.** This author-frozen addendum resolves the third
> pre-read `TECHNICAL_ABORT_NO_OUTCOME` in run-020. It supersedes only v2.9.2
> §30.5's blanket `classes_ == [0,1]` assertion. v2.9.2's supported
> `l1_ratio=0.0` constructor and zero-production-warning law remain unchanged;
> v2.9.1's 176-row matched-support panel remains unchanged; every other v2.9
> §28 contract remains unchanged.

> At adjudication time all package, panel, and model-API equivalence preflights
> had passed, but there had been zero production HDF5 dereferences, zero EEG,
> text, outcome, or test-identity reads, no production Gate CLI, no Gate
> outcome, no certificate artifact, and no repository modification. The remote
> baseline remains `4fa6fadc8bdee0d163acc8bf9ee48aeac4d3095d`.

## 31.1 Conflict adjudication

v2.9 §28.5 freezes four distinct production fit types under the same estimator
hyperparameters:

```text
real-vs-N2 detector   binary target
subject nuisance      18-class target
length nuisance        3-class target
power nuisance         2-class target
```

v2.9.2 §30.5 incorrectly applied the detector-only assertion
`classes_ == [0,1]` to every production fit. That assertion is impossible for
the frozen subject and length nuisance fits. Codex correctly stopped rather
than changing targets or model use.

The repair changes no target, target encoding, sample, feature, estimator,
hyperparameter, or nuisance analysis. It only makes post-fit validation
fit-type-aware.

## 31.2 Frozen semantic target domains

Before any fit, derive the target vector exactly as already specified by v2.9
§28.5. Do not re-encode, relabel, merge, one-vs-rest expand, or otherwise change
it for this addendum. Independently validate its semantic source domain against
the frozen 176-row panel:

```text
fit_type=reference_detector
  semantic domain: {real, N2}
  frozen encoded labels: integer {0,1}
  expected cardinality: 2

fit_type=nuisance_subject
  semantic domain:
    {YAC,YAG,YAK,YDG,YDR,YFR,YFS,YHS,YIS,YLS,YMD,YMS,YRH,YRK,YRP,YSD,YSL,YTL}
  expected cardinality: 18

fit_type=nuisance_length
  semantic domain: {W01_04,W05_16,W17_PLUS}
  expected cardinality: 3

fit_type=nuisance_power
  semantic domain: {P_LOW,P_HIGH}
  expected cardinality: 2
```

The nuisance target's existing v2.9 representation is preserved. Its post-fit
expected class array is computed as `np.unique(y_fit)` only after the semantic
source-domain assertion passes. This avoids imposing a new string/integer
encoding while still fail-closing any missing, extra, or merged class.

For `reference_detector` only, require both the semantic domain and encoded
class array to be exactly `np.asarray([0, 1])`.

## 31.3 Fit-type-aware post-fit assertions

Replace v2.9.2 §30.5's first assertion with:

```python
expected_classes = np.unique(y_fit)
assert model.classes_.dtype == expected_classes.dtype
np.testing.assert_array_equal(model.classes_, expected_classes)
```

This comparison is necessary but not sufficient: §31.2's fit-type-specific
semantic-domain and cardinality assertions must already have passed.

For every production fit, assert:

```text
classes_.ndim == 1
len(classes_) == expected cardinality for fit_type
classes_ equals np.unique(y_fit), including dtype/value/order
n_iter_.shape == (1,)
1 <= int(n_iter_[0]) < 2000
coef_, intercept_, decision values and probabilities are finite
n_features_in_ equals the frozen feature width
probability shape == (n_samples, K)
probabilities are within [0,1] and each row sums to 1 within v2.9 tolerance
```

Shape contracts are:

```text
K == 2:
  coef_.shape       == (1, n_features)
  intercept_.shape  == (1,)
  decision shape    == (n_samples,)

K > 2:
  coef_.shape       == (K, n_features)
  intercept_.shape  == (K,)
  decision shape    == (n_samples, K)
```

The following exact class/cardinality expectations apply:

```text
reference_detector  K=2, classes_ exactly [0,1]
nuisance_subject    K=18, classes_ exactly np.unique(frozen subject target)
nuisance_length     K=3, classes_ exactly np.unique(frozen length target)
nuisance_power      K=2, classes_ exactly np.unique(frozen power target)
```

No other production fit type is authorized. An unknown fit type, wrong semantic
domain/cardinality, wrong class array/shape, warning, exception, iteration
failure, or nonfinite output is
`GATE_R0_MODEL_FIT_INVALID / TECHNICAL_ABORT_NO_OUTCOME`.

## 31.4 Mandatory multiclass capability preflight

Extend the pre-read synthetic certificate with modern-constructor fits for
`K in {2,3,18}`. Use four observations per class, six float64 features, and no
RNG. For class index `c=0..K-1` and replicate `j=0..3`, define:

```python
x = [
    (c - (K - 1) / 2) / max(K - 1, 1),
    (c % 3) - 1,
    ((c % 5) - 2) / 2,
    (j - 1.5) / 2,
    (((c + j) % 7) - 3) / 3,
    (((2 * c + j) % 11) - 5) / 5,
]
label = f"C{c:02d}"
```

Fit each with the exact v2.9.2 §30.2 modern constructor under local
`simplefilter("always")` warning capture. For each K require:

- zero warnings and no exception;
- class values exactly `C00..C(K-1)` in sorted order;
- all §31.3 class, iteration, coefficient/intercept, decision, probability,
  finiteness, and probability-sum assertions;
- no change to process-global warning filters.

Also retain v2.9.2 §30.4's legacy/modern binary API-equivalence test. These are
capability checks only; no fixture iteration count, coefficient, score, or
probability becomes a production expectation.

The compact certificate may add only:

```text
fit_type_contract_version
K values
class-count/shape summaries
warning counts/categories
iteration counts
finite/probability-sum verdicts
```

It must not persist fixture arrays, labels, coefficients, intercepts, decision
values, or probabilities.

## 31.5 Focused tests and mutations

Add tests proving:

- `[0,1]` is required only for `reference_detector`;
- exact 18/3/2 nuisance semantic domains pass without target changes;
- missing/extra subject, length, or power category fails before real read;
- `classes_ != np.unique(y_fit)` fails for every fit type;
- applying `[0,1]` to subject or length is a negative mutation;
- binary and multiclass coefficient/intercept/decision/probability shapes are
  validated as §31.3;
- K=2/3/18 synthetic modern fits are warning-free and finite;
- an unknown fit type, relabeling, class merge, one-vs-rest rewrite, or target
  re-encoding attempt fails closed;
- v2.9.2 warning, equivalence, iteration, finiteness, certificate, and zero-read
  negative tests remain PASS;
- technical abort leaves Gate outcome null and all real read counters zero.

All v2.9–v2.9.2 tests, regressions, full discovery, validator, status, and diff
checks remain mandatory with zero skip.

## 31.6 Run/state law

The three aborts remain pre-read technical provenance only:

```text
v2.9 abort      impossible 216-row panel
v2.9.1 abort    deprecated legacy model API versus any-warning law
v2.9.2 abort    detector-only class assertion applied to multiclass fits
Gate outcome    null
data reads      zero
repo mutation   none
authorized retry run-020 under cumulative v2.9.3
```

After all preflights pass, execute the unchanged Gate R0. The repair is not a
scientific PASS and changes no threshold or target.

Importing v2.9 through v2.9.3 adds four review tasks. On completed scientific
PASS or FAIL, final counts are:

```text
79 total / 48 DONE / 8 SKIPPED / 22 BLOCKED / 1 READY
```

The sole READY remains `S0_SEMANTIC_ITEM`, owner=`CHATGPT_OR_AUTHOR`; route
unlocked, test locked, later Gate outcomes null, and hard stop mandatory.
`SPEC_V293_REVIEW` depends on `SPEC_V292_REVIEW` and is completed by run-020.
A technical abort produces no scientific outcome or final state transition.

## 31.7 Cumulative active-spec assembly

Validate the earlier packages and first rebuild cumulative v2.9.2 exactly. Its
required SHA256 is:

```text
4a5138bcfe8199d7ab5c9cd90d6a2669c987b624953c63a419df41730858225c
```

Then construct cumulative v2.9.3:

```text
base = bytes(cumulative v2.9.2).rstrip(CR/LF)
addendum = bytes(this file).lstrip(CR/LF)
active = base || LF || LF || addendum
output = guide/RC_HSG_Paper_Spec_v2_9_3_2026-08-24.md
```

Record its SHA256 in run-020 and active entrypoints. Historical specs, reviews,
abort reports, runs, and artifacts remain append-only.
