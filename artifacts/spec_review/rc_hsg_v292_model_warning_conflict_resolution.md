# RC-HSG v2.9.2 model-warning conflict resolution

## Decision

The second `TECHNICAL_ABORT_NO_OUTCOME` is valid. The model converged, but the
author-frozen legacy constructor necessarily emitted a `FutureWarning`, while
the contract made every warning fatal and prohibited Codex from changing the
constructor.

The repair is to adopt scikit-learn's officially documented equivalent API:

```text
remove: penalty="l2"
add:    l1_ratio=0.0
```

Everything else remains fixed. This is the same L2-logistic objective with the
same `C=1.0`, `lbfgs`, `tol=1e-8`, `max_iter=2000`, intercept, class weighting,
and warm-start behavior.

The warning policy is not relaxed. The revised production constructor and fit
must emit zero warnings under `warnings.simplefilter("always")`; any production
warning remains a technical abort. The legacy warning is captured only in a
synthetic, pre-read API-equivalence test.

## Why this option is preferred

Broadly ignoring `FutureWarning` would hide unrelated compatibility drift.
Allowing only `ConvergenceWarning` to abort would also demote possible numerical
and API warnings without scientific justification. Using the supported
equivalent constructor removes the known warning at its source while keeping
the stricter fail-closed rule.

The official scikit-learn documentation states that `penalty` was deprecated
in 1.8 and that `l1_ratio=0` is the replacement for `penalty="l2"`:

- https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
- https://scikit-learn.org/stable/whats_new/v1.8.html

## Preserved scientific contract

- 176-row v2.9.1 matched-support panel unchanged.
- Full audit remains all 3,497 eligible arrays, each exactly once.
- Replicates `1, 2, 199`, features, labels, standardization, bootstrap, model
  capacity, and AUC/UCB `<=0.65` threshold unchanged.
- Short/cal/test/text/outcome/test-identity read laws unchanged.
- No Gate outcome existed when the repair was frozen.
- Remote baseline remains `4fa6fadc8bdee0d163acc8bf9ee48aeac4d3095d` and clean.

## Required proof before data

The fixed synthetic equivalence certificate must show one expected legacy
`FutureWarning`, zero modern warnings, and legacy/modern coefficient,
intercept, decision, and probability agreement at absolute tolerance `1e-14`.
It stores only aggregate comparison metadata, never model values.

If the environment or future scikit-learn behavior breaks this certificate,
Gate R0 stops before any real read rather than silently changing estimator
semantics.
