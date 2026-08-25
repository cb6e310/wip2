# Current Handoff

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_9_3_2026-08-24.md` (version `v2.9.3`).

## Current state

Run 020 completed `SPEC_V29_REVIEW -> SPEC_V291_REVIEW -> SPEC_V292_REVIEW -> SPEC_V293_REVIEW -> GATE_R0`. The cumulative corrections freeze the 176-row matched panel, warning-free supported logistic API, and fit-type-aware 2/18/3/2 class domains. The audit read all 3,497 eligible outer-train arrays exactly once and read zero short, calibration, test, text, outcome, or test-identity content.

Gate R0 mechanically returned `FAIL_NO_PRIMARY_REFERENCE`: N2 is not admitted, N1 remains mechanism/robustness-only and primary-ineligible, and the provisional unlocked route primary is ordinary hierarchical selective generation. Gate R/C/H and Mechanism A remain BLOCKED with null outcomes. Test remains `LOCKED_UNTIL_ROUTE_LOCK`.

## Frozen A policy

- Policy: `RC_HSG_NATIVE_SPECTRAL_A1_V1`.
- Project-native clean-room implementation; no external source-code copy.
- No pretrained checkpoint, no weight download, and all methods share a train-from-scratch frontend.
- Input remains 105-channel, 500 Hz, common-average, release-native amplitude with no physical-unit conversion or channel interpolation.
- Per-trial robust normalization, 500/250 Hann windows, eight frozen spectral bands, 840-dimensional log-relative-bandpower tokens, 256-dimensional projection, and a two-layer Transformer encoder are frozen in `artifacts/backbone_a_policy.yaml`.
- The exact interface passed a bounded 107-row real-value panel on CPU and CUDA; run 016 reused this evidence without rereading the panel.
- The remaining 3,390 eligible outer-train rows passed one audited-loader streaming scan on CUDA; cumulative admission covers 3,497 eligible rows and 35,745 windows.
- All 44 short rows remain forced L0 without dereference. Run 020 did not read short, calibration, or test EEG, text, outcomes, or test identities and did not execute the method leakage audit, F, schema, reference generation, reliability models, or calibration.

## Preserved run-011 evidence

- Regime I group capacities remain 164/41/68/69; calibration reserves remain 34/34.
- Regime II remains 18-fold LOSO without held-out-subject adaptation.
- The equal-weight 18-subject population and 10,000 x 18 paired bootstrap contract remain unchanged.
- All committed split/population artifact hashes remain byte-identical to run 011.
- Test identities remain `LOCKED_UNTIL_ROUTE_LOCK`.

## Required next action

The sole READY task is `S0_SEMANTIC_ITEM`, owner `CHATGPT_OR_AUTHOR`. Run 020 does not authorize its implementation. Do not rerun Gate R0, alter its outcome, or begin semantic/schema, candidate/reference features, reliability models, calibration, method leakage, training, later Gates, route lock, or any test-value read.
