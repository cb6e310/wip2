# Current Handoff

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_6_2026-08-24.md` (version `v2.6`).

## Current state

Run 017 completed `SPEC_V26_REVIEW -> S0_N1_BLOCK_FEASIBILITY`. The exact audit returned `DEGRADED_COVERAGE`: structural status PASS, minimum subject-role population coverage 0.777777777778, and 199/199 unique joint mapping hashes. N1 cannot be the primary fallback; a mechanism/robustness-only sampler remains unauthorized pending a new exact contract.

The active method is RC-HSG. Old Gate A1/A/B tasks and the superseded NC-HSG/direct-C implementation path remain as historical `SKIPPED` records. Active Gates are Gate R0, Gate R, Gate C, Gate H, and non-blocking Mechanism A; all remain BLOCKED with null outcomes.

## Frozen A policy

- Policy: `RC_HSG_NATIVE_SPECTRAL_A1_V1`.
- Project-native clean-room implementation; no external source-code copy.
- No pretrained checkpoint, no weight download, and all methods share a train-from-scratch frontend.
- Input remains 105-channel, 500 Hz, common-average, release-native amplitude with no physical-unit conversion or channel interpolation.
- Per-trial robust normalization, 500/250 Hann windows, eight frozen spectral bands, 840-dimensional log-relative-bandpower tokens, 256-dimensional projection, and a two-layer Transformer encoder are frozen in `artifacts/backbone_a_policy.yaml`.
- The exact interface passed a bounded 107-row real-value panel on CPU and CUDA; run 016 reused this evidence without rereading the panel.
- The remaining 3,390 eligible outer-train rows passed one audited-loader streaming scan on CUDA; cumulative admission covers 3,497 eligible rows and 35,745 windows.
- All 44 short rows remain forced L0 without dereference; calibration/test EEG, N1/N2, method leakage audit, F, schema, reference generation, reliability models, and calibration were not executed by this run.

## Preserved run-011 evidence

- Regime I group capacities remain 164/41/68/69; calibration reserves remain 34/34.
- Regime II remains 18-fold LOSO without held-out-subject adaptation.
- The equal-weight 18-subject population and 10,000 x 18 paired bootstrap contract remain unchanged.
- All committed split/population artifact hashes remain byte-identical to run 011.
- Test identities remain `LOCKED_UNTIL_ROUTE_LOCK`.

## Required next action

The sole READY task is `S0_N1_SAMPLER`, owner `CHATGPT_OR_AUTHOR`. Do not execute it without a new exact contract. Do not begin N2 sampling, the later method leakage audit, training, semantic decoder, schema, reference families, reliability models, calibration, any Gate, route lock, or test-value read.
