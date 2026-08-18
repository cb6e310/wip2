# ZuCo 2.0 NR Targeted Admission (schema v3)

## Decision

Admission remains **FAIL**. The six conditions are `PASS, PASS, FAIL, PASS, PASS, PASS`; no data card was generated and `S0_DATA_CARD` remains BLOCKED. Runs 005-006 and schema v1/v2 artifacts are immutable. Schema v3 supersedes only their active admission conclusion.

## Six admission conditions

| Condition | Result | Evidence |
|---|---|---|
| 1. Authorized local path | PASS | Retained run-005 authorized-path evidence |
| 2. License evidence | PASS | Retained physical OSF CC-BY-4.0 artifact |
| 3. Complete physical schema, identity, missing/event/segment policy | FAIL | Schema-v3 subpredicate ledger |
| 4. Unsafe pickle is not the only entry point | PASS | HDF5 summaries, preprocessed MAT/HDF5, official readers |
| 5. Manifest/hash matches OSF | PASS | Retained 27/27 run-005 hashes plus current sizes; no large-file re-hash |
| 6. No held-out/test outcome read | PASS | Bounded outcome-blind audit declaration |

## Condition-3 subpredicates

| Subpredicate | Result | Detail |
|---|---|---|
| identity_and_slot_complete | PASS | 18 x 349 = 6,282 |
| material_sequence_exact | PASS | 6,282/6,282 ordered hashes |
| block_line_occurrence_complete | PASS | Block, material line and canonical occurrence IDs are complete |
| summary_expected_fields_complete | PASS | No expected field missing |
| all_eeg_cells_classified | PASS | 5,911 valid multisample, 367 nonfinite placeholders, 4 finite single-sample |
| missing_exclusion_ledger_consistent | PASS | 5,905 final candidates + 377 excluded = 6,282 |
| channel_contract_consistent | PASS | One 105-channel contract across 126 blocks |
| coordinate_contract_complete | PASS | Complete stable coordinate contract |
| sampling_contract_consistent | PASS | 500 Hz across 126 blocks |
| acquisition_reference_bound | PASS | Cz local metadata |
| processed_reference_bound | PASS | Common-average local metadata |
| event_structure_valid | PASS | Finite integer monotone bounded latency, nonnegative duration, valid urevent |
| event_semantics_bound | **FAIL** | Source mapping is valid, but six YTL occurrences violate the physical state machine |
| summary_layer_bound | PASS | 5,905/5,905 exact segment identity |
| summary_reference_bound | PASS | Exact identity transfers the bound preprocessed reference |
| preprocessed_unit_bound | **FAIL** | UNRESOLVED |
| summary_unit_bound | **FAIL** | UNRESOLVED |
| admissible_cell_policy_frozen | PASS | Content + cell + event + exact segment conjunction |
| ordinary_control_event_partition_complete | PASS | 303 ordinary + 46 control per subject |
| control_response_contract_valid | **FAIL** | Sanitized YTL state-machine anomalies include response placement failure |
| event_occurrence_count_exact | PASS | 6,282 total occurrences |
| event_to_material_slot_alignment_exact | **FAIL** | Six YTL occurrences are invalid and cannot be admitted by ordinal alignment |
| segment_convention_global_unique | PASS | One global finish-inclusive convention |
| segment_correspondence_complete | PASS | Every event-valid comparable row is exact |
| source_evidence_cache_valid | PASS | Allowlist, raw hash, normalized claim and applicability checks pass |

Condition 3 is the logical AND of all recorded subpredicates.

## Event occurrence contract

Every subject has 303 ordinary `10→11` and 46 control `12→13` occurrences; every control family also has 46 code-15 events. Aggregate counts are `10=11=5,454` and `12=13=15=828`; code 15 does not create an occurrence. Per-block occurrence counts are `50,50,51,50,50,49,49` for every subject.

The complete parser retains physical anomalies in:

- `task1 - NR/Preprocessed/YTL/gip_YTL_NR3_EEG.mat` — `PHYSICAL_ANOMALY_RETAINED` (one sanitized anomaly)
- `task1 - NR/Preprocessed/YTL/oip_YTL_NR6_EEG.mat` — `PHYSICAL_ANOMALY_RETAINED` (five sanitized anomalies)

The committed event ledger contains only subject/block/ordinal/code/state evidence. It contains no latency values.

## Exact segment correspondence

The endpoint grid was frozen before comparison: EEGLAB one-based finish-exclusive and finish-inclusive. A deterministic 380-row pilot passed only finish-inclusive. Full comparison then covered all 5,905 event-valid finite multisample rows.

| State | Count |
|---|---:|
| EXACT_MATCH | 5,905 |
| EVENT_UNRESOLVED | 6 |
| SHAPE_MISMATCH | 0 |
| VALUE_MISMATCH | 0 |

All 5,905 exact rows are both dtype-exact-and-equal and canonical-numeric-equal. The pilot read 2,859,996,720 bytes. The complete audit, including the pilot, read 46,511,614,800 bytes of corresponding summary cells and preprocessed windows. It emitted no EEG values, differences or waveform hashes. Exact identity binds summary `rawData` to the preprocessed layer and common-average reference; it does not establish physical unit.

## Unit, layer and reference verdicts

- Preprocessed reference: `BOUND`
- Preprocessed unit: `UNRESOLVED`
- Summary layer: `BOUND_BY_EXACT_CORRESPONDENCE`
- Summary reference: `BOUND_BY_EXACT_CORRESPONDENCE`
- Summary unit: `UNRESOLVED`

The bounded evidence cache was rebuilt from the allowed release sources and validated as input. The OSF Data format bytes match the frozen SHA256. Paper thresholds/processing context and issue #5's ZuCo 1.0 SR example do not bind the current ZuCo 2.0 NR arrays.

## Data-card and safety decision

No data card exists because condition 3 fails. The final ledger admits 5,905 candidates and excludes 377 rows: 367 nonfinite placeholders, 4 finite single-sample cells, and 6 otherwise-valid cells with unresolved event windows.

No historical prediction, metric, report outcome, held-out/test outcome, checkpoint, pickle or joblib object was read. No EEG/archive/weight/new data was downloaded. No backbone/A was selected, no split or scientific algorithm was implemented, no training occurred, and no Gate ran.
