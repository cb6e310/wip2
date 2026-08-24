# Current Handoff

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_4_2026-08-24.md` (version `v2.4`).

## Current state

Run 015 completed `SPEC_V24_REVIEW -> S0_LEAKAGE_AUDIT`. `S0_A1_ADMISSION` is READY, is the sole recommended next task, and is owned by `CODEX`. Run 015 stops before full admission.

The active method is RC-HSG. Old Gate A1/A/B tasks and the superseded NC-HSG/direct-C implementation path remain as historical `SKIPPED` records. Active Gates are Gate R0, Gate R, Gate C, Gate H, and non-blocking Mechanism A; all remain BLOCKED with null outcomes.

## Frozen A policy

- Policy: `RC_HSG_NATIVE_SPECTRAL_A1_V1`.
- Project-native clean-room implementation; no external source-code copy.
- No pretrained checkpoint, no weight download, and all methods share a train-from-scratch frontend.
- Input remains 105-channel, 500 Hz, common-average, release-native amplitude with no physical-unit conversion or channel interpolation.
- Per-trial robust normalization, 500/250 Hann windows, eight frozen spectral bands, 840-dimensional log-relative-bandpower tokens, 256-dimensional projection, and a two-layer Transformer encoder are frozen in `artifacts/backbone_a_policy.yaml`.
- The exact interface passed a bounded 107-row real-value panel on CPU and CUDA; 44 outer-train short rows were ledgered without dereference.
- The early split/data/A-path firewall passed without opening production HDF5 or reading new real values.
- The remaining 3,390 eligible outer-train rows, calibration/test EEG, full admission, method leakage audit, F, schema, reference generation, reliability models, and calibration were not executed by this run.

## Preserved run-011 evidence

- Regime I group capacities remain 164/41/68/69; calibration reserves remain 34/34.
- Regime II remains 18-fold LOSO without held-out-subject adaptation.
- The equal-weight 18-subject population and 10,000 x 18 paired bootstrap contract remain unchanged.
- All committed split/population artifact hashes remain byte-identical to run 011.
- Test identities remain `LOCKED_UNTIL_ROUTE_LOCK`.

## Required next action

Under a new author-frozen exact instruction, execute only `S0_A1_ADMISSION`. The run-015 package is not admission authorization. Do not begin the later method leakage audit, training, semantic decoder, schema, reference families, reliability models, calibration, any Gate, or test-value read.
