# Current Handoff

Active SPEC: `guide/NC_HSG_Paper_Spec_v1_5_2026-08-16.md` (version `v1.5`).

## Current state

Run 005 is retained as immutable first-audit history. Run 006 completed the bounded schema-v2 repair and supersedes only the active admission conclusion. Data admission remains blocked by the exact failed condition-3 subpredicates below.

## Verified evidence

- Official OSF node `2urht` resolves to CC-BY-4.0 through license relationship `563c1cf88c5e4a3877f9e96a`.
- All 27 admitted files retain the run-005 OSF SHA256 matches; no large summary file was re-hashed.
- 18 subjects x 349 slots; all 6,282 material occurrences match exactly, with 21 practice rows excluded before the 349-row ordered contract.
- Cell ledger: 5,911 `VALID_FINITE_MULTISAMPLE`, 367 `NONFINITE_PLACEHOLDER`, and 4 `FINITE_SINGLE_SAMPLE_REVIEW_REQUIRED`; all 371 non-valid cells are exclusion candidates.
- 126 preprocessed blocks retain stable 105-channel, coordinate, 500 Hz, `Cz` acquisition-reference, and `common-average` processed-reference contracts.
- Event structure is valid in 126/126 blocks. Event semantics remains FAIL because two YTL blocks contain non-pairable sentence onset/finish ordering despite the official trigger mapping.
- Summary `rawData` layer/reference/unit and preprocessed `EEG/data` unit remain unresolved after the bounded source audit.
- Six admission conditions: `PASS, PASS, FAIL, PASS, PASS, PASS`.
- No data card was generated. `S0_DATA_CARD` remains BLOCKED.

## Required next action

`NO_READY_TASK`. The failed condition-3 subpredicates are `event_semantics_bound`, `summary_layer_bound`, `summary_reference_bound`, `preprocessed_unit_bound`, and `summary_unit_bound`. New authoritative release-applicable evidence or a documented correction of the physical event anomalies is required before another bounded audit. Do not repeat broad discovery. Keep `S0_A_INTERFACE` BLOCKED until a later outcome-blind author/ChatGPT decision selects exactly one primary A.

## Safety boundary

Do not read historical results, metrics, predictions, or held-out outcomes; deserialize checkpoints/pickles; download data/weights; infer unit/layer/reference semantics; select a backbone; implement scientific algorithms; train; or run a Gate.
