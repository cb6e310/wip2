# Run 006: ZuCo 2.0 NR Admission Repair

Date: 2026-08-16  
Task: `SPEC_V15_REVIEW` -> `S0_ZUCO2_NR_ADMISSION_REPAIR`  
Baseline: `d6751eadd96b2f651e5dbd1bfd5366679688ce4d` on clean `main`  
Origin: `https://github.com/cb6e310/wip2`

## Package and governance

The v1.5 handoff ZIP was extracted outside the repository. `sha256sum -c PACKAGE_MANIFEST.sha256` returned OK for all four manifest entries. Only manifest-listed files were imported. SPEC v1.5 and its review were activated with `reviewed_commit` equal to the exact baseline. SPEC v1.2-v1.4, prior reviews, run 005, and all schema-v1 targeted artifacts were retained unchanged.

## Read and unread boundary

Read: repository governance/state entry points; v1.5 SPEC section 14 and review; targeted auditor/tests; run 005 and schema-v1 targeted artifacts; the 18 admitted NR summary files' selected fields and referenced cell datasets; seven NR material CSVs; 126 preprocessed blocks' keys, attributes, shapes, small scalar/string metadata and event metadata; the two official readers; bounded OSF/ACL/Frontiers/issue sources.

Not read: `trust_align/03_runs`, `trust_align/04_results`, historical predictions/metrics/reports, held-out/test outcomes, waveform dumps, checkpoints, pickle/joblib objects, or unrelated datasets. No broad discovery or large-MAT re-hash ran.

## D1-D6 repair

- D1: Replaced reference/nonempty admission with seven mutually exclusive EEG-cell states and chunked finite counts.
- D2: Excluded 7 x 3 practice rows, proved the 349-row ordered sequence for every subject, and assigned block/line/occurrence only after exact match.
- D3: Split event structure validation from release-source semantic binding and audited all 126 blocks.
- D4: Removed summary-layer inference from preprocessed reference and created a source-by-source unit/layer/reference audit.
- D5: Made condition 3 the explicit logical AND of its recorded subpredicates.
- D6: Added schema-v2 fixtures, deterministic output checks, and retained path, unsafe-format, channel, coordinate, and reference guards.

## Real targeted audit

- Rows: 6,282 = 18 x 349
- `NONFINITE_PLACEHOLDER`: 367
- `FINITE_SINGLE_SAMPLE_REVIEW_REQUIRED`: 4
- `VALID_FINITE_MULTISAMPLE`: 5,911
- Material rows: 370; practice excluded: 21; ordered post-practice: 349
- Ordered subject-slot matches: 6,282/6,282
- Prior schema-v1 null blocks: 180; schema-v2 null blocks: 0
- Cross-block duplicate groups: 5 with distinct occurrence IDs
- Event structure: PASS, 126/126
- Event semantics: FAIL, two YTL physical ordering anomalies
- Preprocessed reference: BOUND
- Preprocessed unit: UNRESOLVED
- Summary layer/reference/unit: UNRESOLVED / UNRESOLVED / UNRESOLVED

Frozen subject, block, material, and sequence expectations all passed without changing rules.

## Admission and data-card decision

Six conditions: `PASS, PASS, FAIL, PASS, PASS, PASS`.

Failed condition-3 subpredicates: `event_semantics_bound`, `summary_layer_bound`, `summary_reference_bound`, `preprocessed_unit_bound`, `summary_unit_bound`.

No data card was generated. `S0_DATA_CARD` remains BLOCKED. The 367 placeholders and 4 finite single-sample cells are explicit exclusion candidates. `S0_ZUCO2_NR_ADMISSION_REPAIR` is DONE because the bounded repair audit completed, while the admission outcome remains FAIL.

## Validation

- `.venv/bin/python -m unittest discover -s tests -p 'test_audit_zuco2_nr.py'`: exit 0, 12 tests passed.
- `.venv/bin/python -m unittest discover -s tests -p 'test_project_memory.py'`: exit 0, 38 tests passed.
- `.venv/bin/python -m unittest discover -s tests -p 'test_audit_input_sources.py'`: exit 0, 8 tests passed.
- `.venv/bin/python scripts/check_project_state.py`: exit 0, `PROJECT STATE VALID | tasks=43 | done=12`.
- `.venv/bin/python scripts/project_status.py`: exit 0, v1.5 / BLOCKED / no READY task.
- Generated-artifact assertions: exit 0; 6,282 rows, non-null occurrence fields, class/valid/excluded totals, condition-3 AND equivalence, data-card absence, no raw text/value keys, and v1.5 entry-point consistency.
- `git diff --check`: exit 0.

## Scope declaration

No outcomes were read; no data or weights were downloaded; no backbone/A was selected; no split, adapter, null, schema, or NC-HSG implementation was started; no training occurred; and no Gate was run.
