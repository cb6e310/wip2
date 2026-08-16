# Current Handoff

Active SPEC: `guide/NC_HSG_Paper_Spec_v1_4_2026-08-16.md` (version `v1.4`).

## Current state

Run 005 repaired the active-SPEC conflict and completed the outcome-blind targeted ZuCo 2.0 NR audit. Data admission remains blocked by one exact physical fact: no EEG unit is recoverable from the selectively readable metadata for summary `sentenceData/rawData` or preprocessed `EEG/data`.

## Verified evidence

- Official OSF node `2urht` resolves to CC-BY-4.0 through license relationship `563c1cf88c5e4a3877f9e96a`.
- All 27 admitted files match OSF SHA256 exactly.
- 18 subjects × 349 slots; 126 preprocessed NR EEG blocks; 105 stable channels with complete coordinates; 500 Hz; `Cz` acquisition reference; `common-average` processed reference; event and trial metadata present.
- 344 unique normalized stimuli, 5 exact cross-block duplicate groups, 0 missing assignments.
- Six admission conditions: `PASS, PASS, FAIL, PASS, PASS, PASS`.
- No data card was generated. `S0_DATA_CARD` remains BLOCKED.

## Required next action

`NO_READY_TASK`. Recover authoritative release-applicable EEG unit metadata for the two admitted data layers, then rerun only `scripts/audit_zuco2_nr.py`. Do not repeat broad discovery. Keep `S0_A_INTERFACE` BLOCKED until a later outcome-blind author/ChatGPT decision selects exactly one primary A.

## Safety boundary

Do not read historical results, metrics, predictions, or held-out outcomes; deserialize checkpoints/pickles; download data/weights; infer the unit; select a backbone; implement scientific algorithms; train; or run a Gate.
