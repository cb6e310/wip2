# Current Handoff

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_1_2026-08-24.md` (version `v2.1`).

## Current state

Run 012 completed `SPEC_V21_REVIEW -> S0_SCIENTIFIC_REDESIGN_FREEZE -> S0_A_POLICY_REVIEW`. `S0_A_INTERFACE` is READY, is the sole recommended next task, and is owned by `CODEX`. Run 012 stops before frontend implementation.

The active method is RC-HSG. Old Gate A1/A/B tasks and the superseded NC-HSG/direct-C implementation path remain as historical `SKIPPED` records. Active Gates are Gate R0, Gate R, Gate C, Gate H, and non-blocking Mechanism A; all remain BLOCKED with null outcomes.

## Frozen A policy

- Policy: `RC_HSG_NATIVE_SPECTRAL_A1_V1`.
- Project-native clean-room implementation; no external source-code copy.
- No pretrained checkpoint, no weight download, and all methods share a train-from-scratch frontend.
- Input remains 105-channel, 500 Hz, common-average, release-native amplitude with no physical-unit conversion or channel interpolation.
- Per-trial robust normalization, 500/250 Hann windows, eight frozen spectral bands, 840-dimensional log-relative-bandpower tokens, 256-dimensional projection, and a two-layer Transformer encoder are frozen in `artifacts/backbone_a_policy.yaml`.
- Segments shorter than 500 valid samples must fail future admission. A, F, schema, reference generation, reliability models, and calibration are not implemented by this run.

## Preserved run-011 evidence

- Regime I group capacities remain 164/41/68/69; calibration reserves remain 34/34.
- Regime II remains 18-fold LOSO without held-out-subject adaptation.
- The equal-weight 18-subject population and 10,000 x 18 paired bootstrap contract remain unchanged.
- All committed split/population artifact hashes remain byte-identical to run 011.
- Test identities remain `LOCKED_UNTIL_ROUTE_LOCK`.

## Required next action

Implement and freeze only the `RC_HSG_NATIVE_SPECTRAL_A1_V1` tensor/admission interface under a new exact instruction. Do not begin the semantic decoder, schema, reference families, reliability models, calibration, training, full leakage audit, any Gate, or test-value read.
