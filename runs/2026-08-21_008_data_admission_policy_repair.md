# Run 008: ZuCo 2.0 NR Data Admission Policy Repair

Date: 2026-08-22  
Task: `SPEC_V17_REVIEW` -> `S0_DATA_ADMISSION_POLICY_REPAIR` -> `S0_DATA_CARD`  
Baseline: `bf958fe2fc543e6b5c465a9eed3c743d4b0d0aa7` on clean `main`  
Origin: `https://github.com/cb6e310/wip2`

## Package and governance

The v1.7 handoff ZIP SHA256 was `17cb68086b8b569975ff36a08dfba0d6dd28d7413e7cf4dc7a70fd8bd276b3a7`. It was extracted outside the repository and `sha256sum -c PACKAGE_MANIFEST.sha256` returned `OK` for all four entries. Only manifest-listed project files were imported. SPEC v1.7 and its review were activated with `reviewed_commit=bf958fe2fc543e6b5c465a9eed3c743d4b0d0aa7`. Older SPECs, reviews, runs 001-007, and schema-v1/v2/v3 admission artifacts were retained unchanged.

## Read and unread boundary

The builder read only these committed inputs:

| Input | SHA256 |
|---|---|
| `artifacts/admission/zuco2_nr_targeted_manifest_v3.yaml` | `50806a60937b28ae36207509c44d606af6f6b6b1be2a69c06081672f0931bfaf` |
| `artifacts/admission/zuco2_nr_stimulus_manifest_v3.jsonl` | `2512c55bb7471896aad7bfa7ba96843fbce8a46067abffda6c16ad87ce3e44be` |
| `artifacts/admission/zuco2_nr_event_occurrence_manifest_v1.jsonl` | `44fa6ce6f797a6ca26c889c5e754419f3091ba937718af52ae07355617cab68d` |
| `artifacts/admission/zuco2_nr_segment_correspondence_v1.yaml` | `28612065ecba93b0e63f8e8c1b604076c63a398b799d5a45d4f437205a07b84e` |

Retained license and OSF metadata artifacts and run-005 27/27 identity evidence were used only as committed provenance. No MAT, HDF5, CSV, real EEG, event latency, EEG value, historical prediction, metric, result report, held-out/test outcome, checkpoint, pickle/joblib object, or `trust_align` data/result tree was read. No network request, data/weight download, large-file re-hash, targeted audit, or broad audit ran.

## Policy repair and NR5 correction

SPEC v1.7 separates the immutable strict source-release diagnostic from the reproducibility verdict for a fully ledgered subset. The strict diagnostic remains `FAIL` with the schema-v3 failed subpredicates unchanged. The analysis view is separately `PASS` because every physical row is classified, every exclusion has a reason, and every admitted row satisfies the frozen content/cell/event/segment conjunction.

The old compact `ytl_anomaly_verdicts` logic hard-coded NR3 and NR6 even though schema-v3 `files_with_semantic_anomaly` included NR5. Future auditor output now derives compact verdicts from every `subject=YTL` file with `event_semantics_bound=false`. A synthetic regression test requires NR3, NR5, and NR6. Run 007 and all schema-v3 artifacts were not rewritten.

## Recomputed counts and overlap

- All physical subject-slot rows: 6,282.
- `VALID_FINITE_MULTISAMPLE`: 5,911.
- Final analysis-view admitted rows: 5,905.
- Final excluded union: 377; admitted plus excluded equals 6,282.
- `NONFINITE_PLACEHOLDER`: 367.
- `FINITE_SINGLE_SAMPLE_REVIEW_REQUIRED`: 4.
- Event-invalid total: 10; all four single-sample rows overlap this set.
- Additional finite-multisample `EVENT_UNRESOLVED`: 6.
- YTL finite-multisample event-unresolved by block: NR3=1, NR5=1, NR6=4.

The unit remains `UNRESOLVED_RELEASE_NATIVE_AMPLITUDE`; `unit_inference_performed=false`; unit-sensitive use is `PROHIBITED_UNTIL_S0_A_INTERFACE`. This blocker is scoped only to `S0_A_INTERFACE`, `S0_A1_FRONTEND`, `S0_A1_ADMISSION`, and unit-sensitive candidate admission.

## Deterministic outputs

| Output | Rows | SHA256 |
|---|---:|---|
| `artifacts/admission/zuco2_nr_analysis_view_v1.jsonl` | 5,905 | `0751259f9f9455cba72bd7d027ffa1423e790e631ac0f5174c38da65d7cd12ff` |
| `artifacts/admission/zuco2_nr_analysis_view_v1.yaml` | n/a | `5e387ef3dc9e930e3ca3e4b6ccb6a009a3cc719281f1ac183cfbf56ac7b66181` |
| `artifacts/data_card.yaml` | n/a | `d9331bfe34937c264b7b8c667a2b831569c4440120e1d445011aeaf419c30f84` |
| `reports/data_card.md` | n/a | `b64b0e743823eeaba20703fd1a125174b0f00b38fef7318ad7b59147fbc158b0` |

The analysis view is sorted by `(subject, slot)` and contains only the frozen locator/identity/shape allowlist. Core artifacts contain no timestamp, stimulus text, event latency, EEG value, finite-value count, waveform hash, credential, or outcome metric. Two complete builds are byte-identical.

## State transition

- `SPEC_V17_REVIEW`: `DONE`.
- `S0_DATA_ADMISSION_POLICY_REPAIR`: `DONE`.
- `S0_DATA_CARD`: `DONE`.
- `B_V1_DATA_NOT_PRESENT`: removed.
- `B_V1_UNIT_UNBOUND_FOR_UNIT_SENSITIVE_A`: active and narrowly scoped.
- `S0_STIMULUS_ID`: `READY`, sole recommendation, not executed.
- Execution: stage 0 `READY`; last completed task is `S0_DATA_CARD`.

## Validation

- `.venv/bin/python -m unittest discover -s tests -p 'test_build_zuco2_nr_analysis_view.py'`: exit 0, 11 tests passed.
- `.venv/bin/python -m unittest discover -s tests -p 'test_audit_zuco2_nr.py'`: exit 0, 21 tests passed.
- `.venv/bin/python -m unittest discover -s tests -p 'test_project_memory.py'`: exit 0, 38 tests passed.
- `.venv/bin/python -m unittest discover -s tests -p 'test_audit_input_sources.py'`: exit 0, 8 tests passed.
- `.venv/bin/python scripts/check_project_state.py`: exit 0, 47 tasks and 17 DONE.
- `.venv/bin/python scripts/project_status.py`: exit 0, v1.7 / stage 0 READY / sole recommendation `S0_STIMULUS_ID`.
- Machine assertions: exit 0 for counts, predicates, reasons, NR3/NR5/NR6, unit policy, sensitive-field absence, cross-artifact hashes, and sole first candidate.
- `git diff --check`: exit 0.

## Scope declaration

No real EEG or outcome was read; no data or weights were downloaded; no backbone/A was selected; no stimulus grouping or split was built; no training occurred; and no Gate ran.
