# NC-HSG v1.2 Implementation-Review Decision Log

Date: 2026-08-16  
Evidence scope: specification and primary-source review only; no `wip2` repository files, EEG values, model output, held-out metric, or Gate result were available.

## Decisions frozen before repository execution

1. **Semantic depth is L0-L3.** L4 remains a constrained renderer and cannot increase Specificity@Risk.
2. **Candidate selection is part of the statistic.** The fixed candidate library is evaluated for real and every pseudo-real; a winner chosen on real EEG cannot be treated as prespecified for a naive permutation p-value.
3. **N1 uses joint block permutations.** Each replicate is one within-block bijection over the evaluation split. Per-trial independent donor draws are forbidden.
4. **N1 no-text AUC is a checksum.** N1 validity comes from block, scope, bijection, coverage, fixed-point, determinism, and symmetric-statistic audits.
5. **N2 primary candidate uses common multichannel phase increments.** Independent channel phases are not primary because they destroy cross-channel structure; AAFT/IAAFT remain sensitivity candidates.
6. **Calibration selection must be accounted for.** Use either independent cal-select/cal-cert or a simultaneous LTT/multiplicity-valid bound over the finite policy set.
7. **Subject is the inferential cluster.** Seeds are aggregated within subject and are never treated as independent observations.
8. **Signed effects matter.** Gate A uses Cliff delta at least +0.20, not absolute delta.
9. **The first repository action is governance and evidence recovery.** The other-project v3.11 ZIP is not repository evidence.

## Research basis

- ZuCo 2.0 primary data paper: https://aclanthology.org/2020.lrec-1.18/
- COFETT original preprint: https://arxiv.org/abs/2607.18749
- NeuroLM official paper: https://openreview.net/forum?id=Io9yFt7XH7
- Risk-controlling prediction sets: https://arxiv.org/abs/2101.02703
- Learn then Test: https://arxiv.org/abs/2110.01052
- Multivariate Fourier surrogates: https://link.aps.org/doi/10.1103/PhysRevLett.73.951
- Generalized permutation tests: https://arxiv.org/abs/2204.13581

## Still open

V0 repository state, V1 data, V2 backbone, V3 semantic schema, V4 real-data null feasibility/tolerances, V5 exact calibration route, and V6 concrete candidate sources remain blockers. Codex must not resolve them by preference or inference during the governance bootstrap.
