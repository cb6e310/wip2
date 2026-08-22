# Codex Next Task: Freeze Stimulus Identity

Active task: `S0_STIMULUS_ID`.

Recover state from `AI_START_HERE.md`, `PROJECT_STATE.yaml`, `HANDOFF.md`, `TASKS.yaml`, active SPEC v1.7, run 008, and committed evidence. Confirm a clean expected baseline before changing files.

## Scope

Normalize stimulus identity and freeze exact and near-duplicate groups using only committed outcome-blind stimulus/assignment evidence. Record deterministic document, paragraph, and stimulus keys; version edit-distance and frozen-embedding thresholds; ledger exact duplicates, paraphrases, and unjoinable records.

## Boundaries

- Do not read real EEG values, event latency, historical predictions/metrics, held-out/test outcomes, or `trust_align` result trees.
- Do not infer the unresolved physical unit or repair YTL event semantics.
- Do not select A, build the joint split, train, or run any Gate in this task.
- Preserve runs 001-008, older SPECs, and all prior admission/analysis-view artifacts as immutable provenance.

The 5,905-row analysis view and 377-row exclusion union are frozen inputs. `analysis_view_admission=PASS` does not change `full_release_diagnostic=FAIL`.

