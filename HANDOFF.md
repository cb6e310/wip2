# Current Handoff

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_8_2026-08-24.md` (version `v2.8`).

## Current state

Run 019 completed `SPEC_V28_REVIEW -> S0_N2_SAMPLER`. The synthetic-only sampler implements the frozen 105-channel common-phase Fourier law, passes the analytic preservation grid and 199-replicate replay, and leaves N2 real-data admissibility pending. The append-only run-018 provenance correction changes no scientific state. N1 remains mechanism/robustness only and N2 is not primary before Gate R0 PASS.

The active method is RC-HSG. Old Gate A1/A/B tasks and the superseded NC-HSG/direct-C implementation path remain as historical `SKIPPED` records. Active Gates are Gate R0, Gate R, Gate C, Gate H, and non-blocking Mechanism A; all outcomes remain null. Gate R0 is READY but unexecuted, and all later Gates remain BLOCKED.

## Frozen A policy

- Policy: `RC_HSG_NATIVE_SPECTRAL_A1_V1`.
- Project-native clean-room implementation; no external source-code copy.
- No pretrained checkpoint, no weight download, and all methods share a train-from-scratch frontend.
- Input remains 105-channel, 500 Hz, common-average, release-native amplitude with no physical-unit conversion or channel interpolation.
- Per-trial robust normalization, 500/250 Hann windows, eight frozen spectral bands, 840-dimensional log-relative-bandpower tokens, 256-dimensional projection, and a two-layer Transformer encoder are frozen in `artifacts/backbone_a_policy.yaml`.
- The exact interface passed a bounded 107-row real-value panel on CPU and CUDA; run 016 reused this evidence without rereading the panel.
- The remaining 3,390 eligible outer-train rows passed one audited-loader streaming scan on CUDA; cumulative admission covers 3,497 eligible rows and 35,745 windows.
- All 44 short rows remain forced L0 without dereference. Run 019 used only analytic synthetic fixtures; it did not read outer-train, short, calibration, or test EEG or execute the method leakage audit, F, schema, reference generation, reliability models, or calibration.

## Preserved run-011 evidence

- Regime I group capacities remain 164/41/68/69; calibration reserves remain 34/34.
- Regime II remains 18-fold LOSO without held-out-subject adaptation.
- The equal-weight 18-subject population and 10,000 x 18 paired bootstrap contract remain unchanged.
- All committed split/population artifact hashes remain byte-identical to run 011.
- Test identities remain `LOCKED_UNTIL_ROUTE_LOCK`.

## Required next action

The sole READY task is `GATE_R0`, owner `CHATGPT_OR_AUTHOR`. Do not execute it without a new exact real outcome-blind audit contract. Do not begin the later method leakage audit, training, semantic decoder, schema, candidate/reference features, reliability models, calibration, route lock, or test-value read.
