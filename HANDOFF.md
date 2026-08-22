# Current Handoff

Active SPEC: `guide/NC_HSG_Paper_Spec_v1_7_2026-08-21.md` (version `v1.7`).

## Current state

Run 008 completed `SPEC_V17_REVIEW -> S0_DATA_ADMISSION_POLICY_REPAIR -> S0_DATA_CARD`. Runs 005-007 and schema-v1/v2/v3 artifacts remain immutable history. The repository-only builder froze a deterministic analysis view and data card from the four committed schema-v3 inputs. `S0_STIMULUS_ID` is READY and is the only recommendation; it was not executed in run 008.

## Verified evidence

- Source release: 6,282 physical assignments; strict full-release diagnostic remains `FAIL` with the schema-v3 failed subpredicates preserved.
- Analysis view: `PASS`; 5,905 admitted and 377 excluded, recomputed row by row.
- EEG classes: 5,911 valid finite multisample, 367 nonfinite placeholders, and 4 finite single-sample rows.
- Event overlap: 10 event-invalid rows, including all 4 single-sample rows; the additional 6 finite-multisample rows are distributed across YTL NR3/NR5/NR6 blocks as 1/1/4.
- Identity: 18 subjects, one session, NR task, 7 blocks, 349 slots per subject, and reused run-005 27/27 OSF SHA256 evidence without re-hashing large files.
- Signal contract: 105 channels at 500 Hz, Cz acquisition reference, common-average processed reference, and exact finish-inclusive summary correspondence.
- Unit: `UNRESOLVED_RELEASE_NATIVE_AMPLITUDE`; inference was not performed and unit-sensitive use is prohibited until `S0_A_INTERFACE`.
- Safety: no real EEG or outcome was read; no download, A selection, split, training, or Gate occurred.

## Required next action

Execute only `S0_STIMULUS_ID`: normalize stimulus identity and freeze exact/near-duplicate groups using committed, outcome-blind assignment evidence. Do not build a split in the same run unless a later explicit task authorizes it. Unknown physical unit does not block identity-only work.

## Safety boundary

Do not read historical results, metrics, predictions, held-out/test outcomes, raw EEG values, checkpoints, pickle/joblib objects, or the `trust_align` result trees. Do not infer microvolts, repair YTL events by guess, select a backbone, build a split early, train, or run a Gate.

