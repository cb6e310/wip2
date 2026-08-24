# Current Handoff

Active SPEC: `guide/NC_HSG_Paper_Spec_v2_0_2026-08-23.md` (version `v2.0`).

## Current state

Run 011 completed `SPEC_V20_REVIEW -> S0_JOINT_SPLIT -> S0_GATE_A_POPULATION_E5`. `S0_A_POLICY_REVIEW` is READY, is the sole recommended next task, and is owned by `CHATGPT_OR_AUTHOR`. Run 011 stops before backbone selection or implementation.

## Frozen split evidence

- Primary assignment: 164 train-fit, 41 inner-val, 68 calibration, and 69 test groups; 25 swaps; objective `(201, 804726, 344, 651510, 201, 76266)`; ledger `531539ff3592cc28d89c5e3ef568d019eaab733ccdb1053c1fcf1c471e9dac1c`.
- Calibration reserves: 34 select and 34 certification groups; six swaps; objective `(34, 30056, 34, 2312, 34, 2312)`; ledger `5f464d97e695ab6bc58d10ac2342351195fa936144487bd9e78f96e5e7a8442c`.
- Regime I covers 342 groups, 344 exact IDs, 349 stimulus occurrences, 5,905 admitted rows, and all 18 subjects. Test identities are `LOCKED_UNTIL_ROUTE_LOCK`.
- Regime II contains 18 LOSO folds, reuses Regime I group roles, and prohibits held-out-subject adaptation or non-heldout test-group leakage.
- Population policy uses equal-weight subject macro aggregation. The 180,000 bootstrap index bytes hash to `e77ca92b29c414a17c1e66edf4075edd470c007dfe2019487c36758f5f99c86d`; the bytes are not committed and no statistic or Gate was computed.
- Two repository-external production builds were byte-identical.

## Output hashes

| Output | SHA256 |
|---|---|
| `artifacts/split_regimeI.json` | `e2c065e5b395053cd655670fede8a2b117f6eb9821af884ca31c6fed3842fbab` |
| `artifacts/split_regimeII.json` | `9643dd5abe953e863e7535989f2f65d0f013a1c775c167e49f7d107545016393` |
| `artifacts/split_manifest.yaml` | `56ccf23881c4e5dee2f3f00704a8af4847636d116783a9da8c2526fdb5c2549f` |
| `artifacts/gate_a_population.yaml` | `279e3edf1c41971b6967f74657ec531533977d90ea4dc3d48a5efd63dd295d60` |
| `reports/joint_split_population.md` | `13755eac6198352b9c4dd6605f95a31b6e859db395bb5e6539a715427f742d09` |

## Safety boundary

Only opaque assignment metadata from the five fixed committed inputs was used. Outputs contain no source text, raw signal metadata, similarity scores, predictions, scientific statistics, or test values. No random split was searched, no physical unit was inferred, no backbone was selected or downloaded, no full leakage audit ran, no training occurred, and no Gate executed.

## Required next action

ChatGPT or the author must select or reject exactly one primary backbone A policy using the criteria in root `CODEX_NEXT_TASK.md`. Codex must not make that decision.
