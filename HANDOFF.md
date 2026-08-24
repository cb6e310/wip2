# Current Handoff

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_2_2026-08-24.md` (version `v2.2`).

## Current state

Run 013 completed `SPEC_V22_REVIEW -> S0_A_INTERFACE`. `S0_A1_FRONTEND` is READY, is the sole recommended next task, and is owned by `CODEX`. Run 013 stops before any real EEG tensor traversal.

The active method is RC-HSG. Old Gate A1/A/B tasks and the superseded NC-HSG/direct-C implementation path remain as historical `SKIPPED` records. Active Gates are Gate R0, Gate R, Gate C, Gate H, and non-blocking Mechanism A; all remain BLOCKED with null outcomes.

## Frozen A policy

- Policy: `RC_HSG_NATIVE_SPECTRAL_A1_V1`.
- Project-native clean-room implementation; no external source-code copy.
- No pretrained checkpoint, no weight download, and all methods share a train-from-scratch frontend.
- Input remains 105-channel, 500 Hz, common-average, release-native amplitude with no physical-unit conversion or channel interpolation.
- Per-trial robust normalization, 500/250 Hann windows, eight frozen spectral bands, 840-dimensional log-relative-bandpower tokens, 256-dimensional projection, and a two-layer Transformer encoder are frozen in `artifacts/backbone_a_policy.yaml`.
- The exact 1,270,528-parameter interface is implemented and synthetic-tested. A metadata-only overlay marks 5,832 eligible rows and 73 short rows as `FORCED_L0_NO_FRONTEND` without removing them from the 5,905-row population.
- Real-data frontend validation, A admission, F, schema, reference generation, reliability models, and calibration are not implemented by this run.

## Preserved run-011 evidence

- Regime I group capacities remain 164/41/68/69; calibration reserves remain 34/34.
- Regime II remains 18-fold LOSO without held-out-subject adaptation.
- The equal-weight 18-subject population and 10,000 x 18 paired bootstrap contract remain unchanged.
- All committed split/population artifact hashes remain byte-identical to run 011.
- Test identities remain `LOCKED_UNTIL_ROUTE_LOCK`.

## Required next action

Under a new exact instruction, validate only the frozen frontend on authorized outer-train real data. Do not alter the interface, infer units, begin admission/training, semantic decoder, schema, reference families, reliability models, calibration, full leakage audit, any Gate, or test-value read.
