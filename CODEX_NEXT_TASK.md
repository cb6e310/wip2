# NO_READY_TASK

Active SPEC: `guide/NC_HSG_Paper_Spec_v1_4_2026-08-16.md` (version `v1.4`).

The six ZuCo 2.0 NR admission conditions are `PASS, PASS, FAIL, PASS, PASS, PASS`. The sole remaining V1 blocker is machine-specific:

```text
physical EEG unit is absent from selectively readable metadata for
task1 - NR/Matlab files/results*_NR.mat:sentenceData/rawData and
task1 - NR/Preprocessed/*/*_EEG.mat:EEG/data
```

Minimum next action: locate authoritative release-applicable unit metadata in an official source document or a selectively readable field/attribute for those exact layers, record its URL/path and identity hash, and rerun only `scripts/audit_zuco2_nr.py`. Do not infer the unit from `trust_align` code or historical outputs, and do not rerun `scripts/audit_input_sources.py`.

Until all six conditions PASS, do not generate `artifacts/data_card.yaml` or `reports/data_card.md`. Keep `S0_A_INTERFACE` BLOCKED pending a later explicit selection of exactly one primary A.
