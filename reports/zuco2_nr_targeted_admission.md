# ZuCo 2.0 NR Targeted Admission

## Decision

`FAIL`. The bounded physical-input audit completed successfully, but strict data admission did not: the EEG physical unit is not recoverable from the selectively readable local metadata. No data card was generated.

## Provenance and scope

- Authorized local root: `/home/song/projects/trust_align/01_data_protocol/datasets/zuco_2.0`
- Official node: OSF `2urht`, public, titled *ZuCo 2.0: A Dataset of Physiological Recordings During Natural Reading and Annotation*
- Official license relationship: `563c1cf88c5e4a3877f9e96a`, resolved as `CC-By Attribution 4.0 International`
- Physical admitted view: 18 NR summary MAT files, 7 NR material CSV files, and 2 official Python readers
- Metadata-only supporting view: 126 preprocessed NR EEG blocks
- Excluded: TSR, raw EEG/ET, the 117 GB archive, unsafe serialized objects, historical runs/results/reports, held-out metrics, predictions, and weights

## Local-to-OSF identity

All 27 admitted files have local SHA256 values. All 27 exactly match the SHA256 exposed by the OSF file-metadata API. The admitted summary files total 34,591,109,519 bytes. No official hash was missing and no file mismatched.

## Physical schema findings

- 18 subjects, one NR session, 7 blocks, 349 sentence slots per subject, and 6,282 subject-slot assignments.
- All 18 summary files are MATLAB v7.3 HDF5 with the same 22-field `sentenceData` schema.
- All 126 preprocessed EEG blocks expose 105 channels, one stable channel order, complete X/Y/Z/theta/radius coordinates, 500 Hz sampling, one trial, and event fields including `type` and `latency`.
- None of the 24 officially expected excluded peripheral labels remains in the processed channel locations.
- Acquisition reference is physically recoverable as `Cz`; processed reference is physically recoverable as `common-average`. Summary `rawData` is classified as the processed common-average layer.
- No local selectively readable unit field or unit-named metadata path was found across 126 blocks. The official LREC paper reports microvolt-scale artifact criteria and figures, but does not explicitly bind the stored `sentenceData/rawData` and `EEG/data` numeric arrays to that storage unit; the audit therefore does not infer or import a unit.
- Stimulus identity uses salt-free SHA256 after Unicode NFKC normalization and whitespace collapse. There are 344 unique normalized identities across 349 slots, including 5 exact duplicate groups that cross blocks. All 344 identities match the 7 official task-material files; no stimulus text is committed.
- Summary numeric leaves were streamed by reference/chunk for shape and finite aggregation; no EEG value is emitted. Missing subject-slot assignments: 0.

## Six admission conditions

1. **PASS** — An explicit authorized local path exists. Evidence: targeted manifest `authorized_dataset_root_recorded` and 27-file manifest.
2. **PASS** — Identifiable license/terms/author authorization has physical evidence. Evidence: `artifacts/admission/zuco2_osf_license.yaml`.
3. **FAIL** — Subject/session/task/block/trial, EEG, sampling, reference, channel/coordinate, event, stimulus ID, and text fields are recoverable, but EEG physical unit is not recoverable. Evidence: targeted manifest `physical_schema.unit_values: []`.
4. **PASS** — Unsafe pickle is not the only data entry. Evidence: HDF5 summary schema and two official static Python readers.
5. **PASS** — The complete admitted physical manifest has local SHA256 and all available OSF SHA256 values match: 27/27.
6. **PASS** — No held-out metric or test result was read. Evidence: the executable path boundary and manifest safety flags.

## Reproducibility

Two complete real-data audit executions produced byte-identical YAML and JSONL outputs. Final SHA256:

- `zuco2_nr_targeted_manifest.yaml`: `23f207862470b4f1170a9fc6f3cf44abf12277b8aae1b06859f7341f1a549fac`
- `zuco2_nr_stimulus_manifest.jsonl`: `6ef38478f2c12b5f59b23de83882b6540bba3f7ec0d1180a69677b63dc208066`

## Remaining V1 action

Recover an authoritative physical unit for the admitted summary `sentenceData/rawData` and preprocessed `EEG/data` layer from a release-applicable metadata field or source document, without loading historical results or guessing from another pipeline. Then rerun only this targeted audit. Broad discovery must not be repeated.
