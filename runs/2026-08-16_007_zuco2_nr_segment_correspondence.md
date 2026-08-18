# Run 007: ZuCo 2.0 NR Segment Correspondence

Date: 2026-08-18  
Task: `SPEC_V16_REVIEW` -> `S0_ZUCO2_NR_SEGMENT_CORRESPONDENCE`  
Baseline: `c807a2e83fad02763193a6c1db81fd26db19fd97` on clean `main`  
Origin: `https://github.com/cb6e310/wip2`

## Package and governance

The v1.6 handoff ZIP was extracted outside the repository. `sha256sum -c PACKAGE_MANIFEST.sha256` returned OK for all four manifest entries. Only manifest-listed project files were imported. SPEC v1.6 and its review were activated with `reviewed_commit` equal to the exact baseline. Earlier SPECs, reviews, runs 005-006, and all schema-v1/v2 artifacts were retained unchanged.

## Read and unread boundary

Read: repository governance/state; SPEC v1.6 section 15 and review; run 006/report/v2 manifests; targeted code/tests; retained run-005 hash/license evidence; admitted 18 NR summaries, 126 NR preprocessed blocks, seven material CSVs and official readers; only the allowlisted OSF, ACL, Frontiers/PMC and GitHub issue sources. Numeric reads were limited to referenced summary cells and corresponding event windows for exact in-memory comparison.

Not read: `trust_align/03_runs`, `trust_align/04_results`, historical predictions/metrics/reports, held-out/test outcomes, checkpoints, pickle/joblib objects or unrelated datasets. No broad discovery, large-MAT re-hash or data/weight download ran.

## Event parser and YTL decision

The parser combines ordinary `10→11` and control `12→13` occurrences and requires code 15 after each control finish before the next onset. Every subject has 303 ordinary and 46 control occurrences, 349 total; aggregate counts are `10=11=5,454` and `12=13=15=828`. Per-block counts are `50,50,51,50,50,49,49`.

The complete state machine retains one sanitized anomaly in YTL NR3 and five in YTL NR6. Both files are `PHYSICAL_ANOMALY_RETAINED`, not `OLD_PROJECTION_FALSE_ANOMALY`. Six otherwise-valid cells are event-unresolved. Artifacts contain code/ordinal/state only, never latency.

## Pilot and full exact comparison

The preregistered grid was finish-exclusive versus finish-inclusive under EEGLAB one-based latency semantics. The 380-row pilot selected only finish-inclusive and read 2,859,996,720 bytes. Full comparison then covered all 5,905 comparable rows. Total bytes read including the pilot were 46,511,614,800.

Results: 5,905 `EXACT_MATCH`, 0 `SHAPE_MISMATCH`, 0 `VALUE_MISMATCH`, and 6 `EVENT_UNRESOLVED` among the 5,911 finite multisample cells. All 5,905 exact rows are dtype-exact-and-equal and canonical-numeric-equal. Summary layer/reference are bound by exact identity to the preprocessed common-average array. No tolerance, correlation, scale, filtering, interpolation, re-reference or per-row convention selection was used.

## Source, unit and admission verdicts

The versioned release evidence cache validates its URL allowlist, raw hashes, normalized claim hashes and applicability. The OSF Data format raw SHA256 is `3cc1b85c021042d93db4f077145b84e6c3beebad3a474f6781746a6a40dbdbb4`. Event roles are derived from that cache, not a Python verdict constant.

Preprocessed reference is BOUND; summary layer/reference are `BOUND_BY_EXACT_CORRESPONDENCE`; preprocessed and summary units remain `UNRESOLVED`.

Six conditions are `PASS, PASS, FAIL, PASS, PASS, PASS`. Failed condition-3 subpredicates are `event_semantics_bound`, `preprocessed_unit_bound`, `summary_unit_bound`, `control_response_contract_valid`, and `event_to_material_slot_alignment_exact`. Final counts are 5,905 admitted candidates and 377 exclusions. No data card was generated; `S0_DATA_CARD` remains BLOCKED.

## Validation

- `.venv/bin/python -m unittest discover -s tests -p 'test_audit_zuco2_nr.py'`: exit 0, 20 tests passed.
- `.venv/bin/python -m unittest discover -s tests -p 'test_project_memory.py'`: exit 0, 38 tests passed.
- `.venv/bin/python -m unittest discover -s tests -p 'test_audit_input_sources.py'`: exit 0, 8 tests passed.
- `.venv/bin/python scripts/check_project_state.py`: exit 0, `PROJECT STATE VALID | tasks=45 | done=14`.
- `.venv/bin/python scripts/project_status.py`: exit 0, v1.6 / BLOCKED / no READY task.
- Generated-artifact assertions: exit 0; 303 ordinary + 46 control per subject, 6,282 event/material rows, 5,911 segment states, condition-3 AND equivalence, source-cache validation, data-card absence, and no stimulus/event-latency/EEG-value output.
- `git diff --check`: exit 0.

## Scope declaration

No outcome was read; no data or weights were downloaded; no backbone/A was selected; no split, adapter, null, semantic schema or NC-HSG implementation was started; no training occurred; and no Gate was run.
