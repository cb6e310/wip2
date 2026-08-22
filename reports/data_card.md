# ZuCo 2.0 NR Data Card

## Scope and verdicts

The source release contains 6,282 physical subject-slot assignments. Its strict full-release diagnostic remains **FAIL**; failed subpredicates are `event_semantics_bound, preprocessed_unit_bound, summary_unit_bound, control_response_contract_valid, event_to_material_slot_alignment_exact`.

The frozen analysis view is **PASS** with 5,905 admitted rows and 377 excluded rows (6,282 total). This subset verdict does not imply a gap-free source release or model/Gate readiness.

## Composition

- Dataset/revision: ZuCo 2.0 / OSF node revision modified 2023-08-25
- License: CC-By Attribution 4.0 International (OSF node `2urht`)
- Subjects/sessions/task: 18 / 1 / NR
- Blocks and slots: 7 blocks, 349 slots per subject
- Signal contract: 105 channels at 500 Hz; acquisition reference `Cz`, processed reference `common-average`
- Segment convention: `EEGLAB_ONE_BASED_FINISH_INCLUSIVE`; summary layer/reference `BOUND_BY_EXACT_CORRESPONDENCE`

## Exclusions and limitations

The exclusion union is recomputed row by row. It contains 367 nonfinite placeholders, 4 finite single-sample rows, and 6 additional finite-multisample event-unresolved rows. The event-invalid total is 10; 4 single-sample rows overlap that set.

YTL anomaly files:

- `task1 - NR/Preprocessed/YTL/gip_YTL_NR3_EEG.mat`
- `task1 - NR/Preprocessed/YTL/gip_YTL_NR5_EEG.mat`
- `task1 - NR/Preprocessed/YTL/oip_YTL_NR6_EEG.mat`

Physical unit status is `UNRESOLVED_RELEASE_NATIVE_AMPLITUDE`. Unit inference was not performed, and unit-sensitive use is `PROHIBITED_UNTIL_S0_A_INTERFACE`.

## Intended and prohibited use

Use only as the frozen outcome-blind input inventory for future NC-HSG work after the required stimulus-disjoint split and downstream admissions.

Do not infer physical units, admit a unit-sensitive frontend, treat excluded rows as usable, read outcomes, or claim model or Gate validity from this data-card PASS.

TSR may be used only as a later robustness task, not as a substitute for the primary NR analysis view.

## Safety declaration

No outcome was read; no data or weights were downloaded; no backbone was selected; no split, training, or Gate was run. The artifacts contain no stimulus text, event latency, EEG value, finite-value count, or waveform hash.
