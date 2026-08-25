# RC-HSG v2.9.3 Gate R0 Reference Integrity Audit

## Outcome

Decision: `FAIL_NO_PRIMARY_REFERENCE`.
This outcome-blind audit decides reference admissibility only. It is not semantic performance, calibration, or mechanism evidence.

## Scope

Eligible outer-train arrays read once: 3497.
Short, calibration, test, text, outcome, and test-identity reads: 0.
N1 used frozen metadata only and remains mechanism/robustness-only.

## Frozen checks

The 216 theoretical role-cells are structural coverage only: 192 are non-empty and 24 are missing.
Matched nuisance support is 88/16/0/4 across MATCHED/TRAIN_ONLY/INNER_ONLY/ABSENT_BOTH; the panel has 176 rows (88/88 by role).
Support ledger SHA256: `3f2eb411e54c730453d1dd8a39c5bfeff0aa34ee278c545ac66d2f24b2af2246`; panel SHA256: `2cffa7699e7a29eee4996172a20707678ba1ec3529d35e32b2ca453ad79aa806`.
N2 eligible coverage: `0x1.0000000000000p+0`; system population coverage: `0x1.f9a3510b34b43p-1`.
Classifier threshold and bootstrap upper threshold: `0x1.4cccccccccccdp-1`.
Numerical relative-norm threshold: `0x1.0c6f7a0b5ed8dp-20`.
Scientific failures: ['classifier-point:1', 'classifier-point:2', 'classifier-point:199', 'nuisance:subject:1', 'nuisance:subject:2', 'nuisance:subject:199', 'nuisance:length:1', 'nuisance:length:2', 'amplitude-endpoint:YAC:1', 'amplitude-endpoint:YAC:2', 'amplitude-endpoint:YAC:199', 'amplitude-endpoint:YAG:1', 'amplitude-endpoint:YAG:2', 'amplitude-endpoint:YAG:199', 'amplitude-endpoint:YAK:1', 'amplitude-endpoint:YAK:2', 'amplitude-endpoint:YAK:199', 'amplitude-endpoint:YDG:1', 'amplitude-endpoint:YDG:2', 'amplitude-endpoint:YDG:199', 'amplitude-endpoint:YDR:1', 'amplitude-endpoint:YDR:2', 'amplitude-endpoint:YDR:199', 'amplitude-endpoint:YFR:1', 'amplitude-endpoint:YFR:2', 'amplitude-endpoint:YFR:199', 'amplitude-endpoint:YFS:1', 'amplitude-endpoint:YFS:2', 'amplitude-endpoint:YFS:199', 'amplitude-endpoint:YHS:1', 'amplitude-endpoint:YHS:2', 'amplitude-endpoint:YHS:199', 'amplitude-endpoint:YIS:1', 'amplitude-endpoint:YIS:2', 'amplitude-endpoint:YIS:199', 'amplitude-endpoint:YLS:1', 'amplitude-endpoint:YLS:2', 'amplitude-endpoint:YLS:199', 'amplitude-endpoint:YMD:1', 'amplitude-endpoint:YMD:2', 'amplitude-endpoint:YMD:199', 'amplitude-endpoint:YMS:1', 'amplitude-endpoint:YMS:2', 'amplitude-endpoint:YMS:199', 'amplitude-endpoint:YRH:1', 'amplitude-endpoint:YRH:2', 'amplitude-endpoint:YRH:199', 'amplitude-endpoint:YRK:1', 'amplitude-endpoint:YRK:2', 'amplitude-endpoint:YRK:199', 'amplitude-endpoint:YRP:1', 'amplitude-endpoint:YRP:2', 'amplitude-endpoint:YRP:199', 'amplitude-endpoint:YSD:1', 'amplitude-endpoint:YSD:2', 'amplitude-endpoint:YSD:199', 'amplitude-endpoint:YSL:1', 'amplitude-endpoint:YSL:2', 'amplitude-endpoint:YSL:199', 'amplitude-endpoint:YTL:1', 'amplitude-endpoint:YTL:2', 'amplitude-endpoint:YTL:199']; inconclusive checks: [].

## Boundary

Route remains unlocked and test remains `LOCKED_UNTIL_ROUTE_LOCK`.
Run 020 stops before semantic schema, candidates, reference scores, reliability, calibration, later Gates, route lock, or test unlock.
