# ZuCo 2.0 NR Targeted Admission Repair (schema v2)

## Decision

Admission remains **FAIL**. Conditions are `PASS, PASS, FAIL, PASS, PASS, PASS`; therefore no data card was generated and `S0_DATA_CARD` remains BLOCKED. Run 005 and its schema-v1 artifacts remain immutable history. This report and the schema-v2 artifacts supersede only run 005's active admission conclusion.

## Six admission conditions

| Condition | Result | Evidence |
|---|---|---|
| 1. Authorized local path | PASS | Run-005 authorized-path evidence retained |
| 2. License evidence | PASS | Physical OSF CC-BY-4.0 license artifact retained |
| 3. Complete physical schema, identity, and missing policy | FAIL | Schema-v2 subpredicate ledger below |
| 4. Unsafe pickle is not the only entry point | PASS | HDF5 summaries, preprocessed MAT/HDF5, and official readers |
| 5. Admitted manifest/hash matches OSF | PASS | Run-005 27/27 hash evidence reused with current size checks; large MAT files were not re-hashed |
| 6. No held-out/test outcome read | PASS | Bounded outcome-blind audit declaration |

## Condition-3 subpredicates

| Subpredicate | Result | Detail |
|---|---|---|
| identity_and_slot_complete | PASS | 18 x 349 = 6,282 |
| material_sequence_exact | PASS | 6,282/6,282 ordered hashes |
| block_line_occurrence_complete | PASS | Every row has block, material line, and canonical occurrence ID |
| summary_expected_fields_complete | PASS | No expected field missing |
| all_eeg_cells_classified | PASS | Seven-state classifier is exhaustive and mutually exclusive |
| missing_exclusion_ledger_consistent | PASS | 5,911 valid + 371 excluded = 6,282 |
| channel_contract_consistent | PASS | One 105-channel order contract across 126 blocks |
| coordinate_contract_complete | PASS | Complete stable coordinate contract across 126 blocks |
| sampling_contract_consistent | PASS | 500 Hz across 126 blocks |
| acquisition_reference_bound | PASS | Local metadata binds acquisition reference to Cz |
| processed_reference_bound | PASS | Local metadata binds preprocessed reference to common-average |
| event_structure_valid | PASS | 126/126 blocks: finite, ordered, bounded latency; nonnegative duration; valid urevent |
| event_semantics_bound | **FAIL** | Official 10/11 mapping exists, but two YTL blocks have non-pairable onset/finish ordering |
| summary_layer_bound | **FAIL** | UNRESOLVED |
| summary_reference_bound | **FAIL** | UNRESOLVED |
| preprocessed_unit_bound | **FAIL** | UNRESOLVED |
| summary_unit_bound | **FAIL** | UNRESOLVED |
| admissible_cell_policy_frozen | PASS | Only finite `[T,105]`, `T>=2`, is admissible |

Condition 3 is the logical AND of the recorded subpredicates, so its result is FAIL. Supplying only a unit cannot make it pass.

## EEG cell ledger

Overall:

| Class | Count | Admission |
|---|---:|---|
| VALID_FINITE_MULTISAMPLE | 5,911 | admissible candidate |
| NONFINITE_PLACEHOLDER | 367 | excluded |
| FINITE_SINGLE_SAMPLE_REVIEW_REQUIRED | 4 | excluded |
| All other schema-v2 classes | 0 | excluded if present |

Valid sample-length quantiles are min 24, q25 1,669, median 2,521, q75 3,658, max 27,010. No backbone-specific minimum-length rule was applied.

By subject (`placeholder / single-sample / valid`):

| Subject | Counts | Subject | Counts |
|---|---:|---|---:|
| YAC | 102 / 0 / 247 | YAG | 0 / 0 / 349 |
| YAK | 51 / 0 / 298 | YDG | 0 / 0 / 349 |
| YDR | 3 / 0 / 346 | YFR | 106 / 0 / 243 |
| YFS | 13 / 0 / 336 | YHS | 0 / 0 / 349 |
| YIS | 0 / 0 / 349 | YLS | 6 / 0 / 343 |
| YMD | 7 / 0 / 342 | YMS | 3 / 0 / 346 |
| YRH | 52 / 0 / 297 | YRK | 10 / 0 / 339 |
| YRP | 6 / 0 / 343 | YSD | 1 / 0 / 348 |
| YSL | 6 / 0 / 343 | YTL | 1 / 4 / 344 |

By recovered block (`placeholder / single-sample / valid`):

| Block | Counts |
|---:|---:|
| 1 | 9 / 0 / 891 |
| 2 | 121 / 0 / 779 |
| 3 | 52 / 1 / 865 |
| 4 | 39 / 0 / 861 |
| 5 | 67 / 0 / 833 |
| 6 | 60 / 3 / 819 |
| 7 | 19 / 0 / 863 |

## Deterministic occurrence recovery

The seven material files contain 370 non-empty rows. The first three rows of each block are practice, giving 21 excluded practice rows and 349 post-practice rows with block counts `50,50,51,50,50,49,49`. Every subject's 349 summary slots matches this sequence position by position: 6,282/6,282. Block and material line are assigned only after this proof. Five cross-block duplicate-text groups retain shared stimulus hashes but distinct canonical occurrence IDs. The former 180 schema-v1 null-block rows are repaired to zero without altering the old ledger.

## Event structure and semantics

All 126 blocks pass the structural checks. The official OSF Data format wiki binds triggers 10 and 11 to sentence onset and sentence finish, respectively. Physical ordering fails the sentence-pair contract in:

- `task1 - NR/Preprocessed/YTL/gip_YTL_NR3_EEG.mat`
- `task1 - NR/Preprocessed/YTL/oip_YTL_NR6_EEG.mat`

Accordingly, source semantics are known but the complete physical event-semantic contract is FAIL.

## Unit, reference, and layer provenance

- `preprocessed_EEG_data_reference_status`: BOUND
- `preprocessed_EEG_data_unit_status`: UNRESOLVED
- `summary_rawData_layer_status`: UNRESOLVED
- `summary_rawData_reference_status`: UNRESOLVED
- `summary_rawData_unit_status`: UNRESOLVED

The local preprocessed files bind common-average processed reference and Cz acquisition reference but expose no applicable unit field. Papers containing microvolt thresholds or processing descriptions are context, not stored-array bindings. GitHub issue #5 is open and has a collaborator response stating microvolts, but its question explicitly names a ZuCo 1.0 SR result file, so it is non-binding context for ZuCo 2.0 NR. The bounded source set is exhausted without guessing.

## Safety and scope declaration

This run read no historical prediction, metric, report outcome, held-out/test outcome, checkpoint, pickle, or joblib object. It downloaded no EEG, archive, weight, or new data; selected no backbone or A-interface; created no split; performed no training; and ran no Gate. It did not emit stimulus text, EEG values, waveforms, or participant results.
