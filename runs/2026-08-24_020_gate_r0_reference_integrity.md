# Run 020: RC-HSG v2.9.3 Gate R0 reference integrity

## Scope and baseline

- Baseline: `main@4fa6fadc8bdee0d163acc8bf9ee48aeac4d3095d`, equal to `origin/main`, clean before execution.
- Authorized chain: `SPEC_V29_REVIEW -> SPEC_V291_REVIEW -> SPEC_V292_REVIEW -> SPEC_V293_REVIEW -> GATE_R0 -> S0_SEMANTIC_ITEM READY -> STOP`.
- Cumulative active SPEC: `guide/RC_HSG_Paper_Spec_v2_9_3_2026-08-24.md`.
- Cumulative SPEC SHA256: `8650a71144af074ecf6b0ca1e3c92dcc76a9283891c991de0672edfd124f3745`.
- v2.9.1 cumulative SHA256: `d37692f7ed64c33d53534b5ccdfefa600775c4e66874523a00254242d3205f40`.
- v2.9.2 cumulative SHA256: `4a5138bcfe8199d7ab5c9cd90d6a2669c987b624953c63a419df41730858225c`.

All four ZIP SHA256 values and every `PACKAGE_MANIFEST.sha256` entry passed before import. Only the nine paths named by the four `PROJECT_IMPORT_MANIFEST.txt` files were imported. Cumulative v2.9.1, v2.9.2, and v2.9.3 specs were generated mechanically from the authorized base and addendum bytes.

## Pre-read certificates

Two independent metadata-only implementations agreed on 3,541 assignment rows, 3,497 eligible rows, 3,493 power-PASS rows, four insufficient-power rows, 216/192/24 theoretical/non-empty/missing role cells, and 108 support strata with status counts 88/16/0/4. The matched panel contains 176 rows, split 88 train-fit and 88 inner-val across 18 subjects.

- Support SHA256: `3f2eb411e54c730453d1dd8a39c5bfeff0aa34ee278c545ac66d2f24b2af2246`.
- Panel SHA256: `2cffa7699e7a29eee4996172a20707678ba1ec3529d35e32b2ca453ad79aa806`.
- sklearn: `1.9.0`.
- Legacy/modern binary API: one isolated legacy `FutureWarning`, zero modern warnings, identical classes and iteration arrays, and zero maximum absolute difference for coefficient, intercept, decision, and probability comparisons at `rtol=0, atol=1e-14`.
- Legacy/modern iterations: 11/11.
- K=2/3/18 deterministic capability fits: zero warnings, exact classes and binary/multiclass shapes, finite parameters/decisions/probabilities, valid probability sums, iterations 11/16/25.
- Certificate SHA256: `0f9d4232922588a8a9859ad64b6e122362e79f1ae6c0123cf1ce8b0d40b5af34`.

## Production execution

The production CLI was executed exactly once. It read every eligible array once through the frozen reader and retained one row at a time. N2 replicates were exactly 1, 2, and 199. Only the 176 matched panel rows produced in-memory audit features. No waveform, surrogate, token, feature, FFT, phase, model, coefficient, probability, or value cache was persisted.

Read counters:

```text
eligible outer-train arrays    3497
train-fit / inner-val          2797 / 700
matched panel                  176 = 88 / 88
eligible outside panel         3321
short arrays                   0 / 44
calibration arrays             0
test arrays                    0
text reads                     0
outcome reads                  0
test-identity reads            0
N1 real EEG reads              0
```

All production model constructor/fit warning counts were zero. Fit diagnostics were:

```text
reference detector rep 1       classes=[0,1], K=2, p=2302, coef=(1,2302), n_iter=120
reference detector rep 2       classes=[0,1], K=2, p=2302, coef=(1,2302), n_iter=120
reference detector rep 199     classes=[0,1], K=2, p=2302, coef=(1,2302), n_iter=117
subject nuisance               exact 18 subjects, K=18, p=2302, coef=(18,2302), n_iter=274
length nuisance                W01_04/W05_16/W17_PLUS, K=3, p=2302, coef=(3,2302), n_iter=187
power nuisance                 P_HIGH/P_LOW, K=2, p=2302, coef=(1,2302), n_iter=87
```

Four sklearn `UserWarning` messages were emitted by per-subject `balanced_accuracy_score` calls because predictions included globally fitted classes absent from a local subject's `y_true`. They occurred after all model fits, did not alter the defined mean-recall metric, and are not constructor/fit warnings; all frozen fit warning counters remained zero.

## Mechanical Gate result

Decision: `FAIL_NO_PRIMARY_REFERENCE`.

Classifier threshold was 0.65 for both point AUC and the 97.5% subject-bootstrap upper bound:

```text
replicate   subject-macro AUC   bootstrap upper
1           0.9823302469135802  0.9946913580246913
2           0.9712345679012346  0.9888888888888889
199         0.9386882716049383  0.9686111111111111
```

All three point and upper checks failed. With nuisance absolute-difference threshold 0.05, subject differences were 0.10648148/0.125/0.13240741 for replicates 1/2/199; length differences were 0.07407407/0.07407407/0.01851852; power differences were 0.03703704/0.00462963/0.00462963. Subject failed all replicates, length failed 1 and 2, and power passed all three.

All PSD, covariance, mean, and cross-spectrum relative norms passed the 1e-6 threshold. Across full replicate 1 and panel replicates 2/199, observed maxima were at most `1.3714732217062608e-08`. Amplitude/endpoint passed 0/18 subjects for every replicate: maximum subject-median KS was 0.15647 against 0.15, maximum quantile shift was 2.41359 against 0.25, jump-ratio ranges were entirely below the frozen 0.5 lower bound, and replicate-1 slip ratios reached 2.03476 above the 2.0 upper bound.

N1 replay remained structural PASS with 199 unique mappings, 35,529 fixed points, range 145-214, zero EEG reads, mechanism/robustness admitted, and primary/fallback ineligible due to degraded coverage. N2 is `NOT_ADMITTED`.

Production elapsed time was 662.7446818873286 seconds; peak RSS was 692,486,144 bytes.

## Artifacts

```text
6b4bae7b74ba7110d0d933c828c87f3581a46efca44d509d83699c540417d72e  artifacts/governance/run019_postcommit_correction.yaml
0f9d4232922588a8a9859ad64b6e122362e79f1ae6c0123cf1ce8b0d40b5af34  artifacts/gates/gate_r0_logistic_api_equivalence_v1.yaml
3f2eb411e54c730453d1dd8a39c5bfeff0aa34ee278c545ac66d2f24b2af2246  artifacts/gates/gate_r0_matched_support_v1.jsonl
2cffa7699e7a29eee4996172a20707678ba1ec3529d35e32b2ca453ad79aa806  artifacts/gates/gate_r0_panel_v1.jsonl
820cb97c3db810c927c74ad4792693154746f9d33ae1266bba712a5059b413be  artifacts/gates/gate_r0_n2_coverage_v1.jsonl
b1cdf2e4932ea40e833f7835944f604024c5cf28b94ddc1bc97fc005d6dc04a3  artifacts/gates/gate_r0.yaml
b23d07e059ac92630714abdd9a75faedcbf50eac6c34ff6b72250419d1ba4293  reports/gate_r0.md
```

## Validation and stop state

Pre-production validation passed: Gate focused 25/25, N2 17/17, N2 builder 10/10, N1 9/9, N1 builder 9/9, native A1 12/12, and full discovery 293/293 with zero skip. After governance synchronization, Gate focused passed 25/25, the combined N1/N2/native-A1 regression group passed 74/74, project-memory tests passed 63/63, and final full discovery passed 293/293 with zero skip. The state validator, status command, and `git diff --check` also passed.

The mechanical FAIL branch closes B_V4, sets the unlocked provisional route primary to `ORDINARY_HIERARCHICAL_SELECTIVE_GENERATION`, retains N1 as mechanism/robustness-only, and keeps test `LOCKED_UNTIL_ROUTE_LOCK`. The sole READY task is `S0_SEMANTIC_ITEM`, owner `CHATGPT_OR_AUTHOR`. Run 020 does not authorize that task or any later schema, candidate/reference, reliability, calibration, Gate, route-lock, test-unlock, training, or main-experiment work.
