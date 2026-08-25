# RC-HSG v2.9.3 fit-class-domain conflict resolution

## Decision

The third `TECHNICAL_ABORT_NO_OUTCOME` is valid. v2.9.2 accidentally promoted
the real-vs-N2 detector's `[0,1]` class assertion into a universal requirement,
but v2.9 already freezes 18-class subject and 3-class length nuisance fits.

The correction is validation-only:

```text
reference detector  -> exactly [0,1]
subject nuisance    -> exact frozen 18-class target domain
length nuisance     -> exact frozen 3-class target domain
power nuisance      -> exact frozen 2-class target domain
```

For every fit, `classes_` must equal `np.unique(y_fit)` after the frozen
semantic target domain is independently verified. No nuisance target, target
encoding, sample, feature, model, or parameter changes.

## Shape and safety consequences

Binary fits retain `(1,p)` coefficients and one-dimensional decisions.
Multiclass K=3/18 fits require `(K,p)` coefficients and `(n,K)` decisions.
All fits retain zero-warning production execution, `1<=n_iter_<2000`, finite
outputs, valid probabilities, and the same v2.9.2 constructor.

Before data, deterministic K=2/3/18 synthetic fits must demonstrate these
contracts with zero warnings. The existing legacy/modern API-equivalence proof
also remains mandatory.

## Preserved Gate contract

- 176-row matched panel and its hashes unchanged.
- All 3,497 eligible arrays remain the full audit scope.
- Nuisance targets/model use and real-vs-N2 detector are unchanged.
- Replicates, thresholds, bootstrap, numerical/nuisance audits, outcomes, and
  failure routes are unchanged.
- All production warnings remain fatal.
- No Gate outcome or real read existed when this correction was frozen.
- Remote baseline remains `4fa6fadc8bdee0d163acc8bf9ee48aeac4d3095d`.
