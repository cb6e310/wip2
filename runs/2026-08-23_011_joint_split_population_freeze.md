# Run 011: Deterministic Joint Split and Subject-Macro Population Freeze

Date: 2026-08-23  
Task: `SPEC_V20_REVIEW` -> `S0_JOINT_SPLIT` -> `S0_GATE_A_POPULATION_E5` -> stop with `S0_A_POLICY_REVIEW` READY  
Baseline: `e852e7de24c31410387ad46d75fb44a5cac9e850` on clean `main`  
Origin: `https://github.com/cb6e310/wip2`

## Package and governance

The v2.0 handoff ZIP SHA256 was `482a49d6139cdd3ae7425442fc4e1d49bdc7571c4feb6fd59a56e232794935a7`. It was extracted outside the repository after rejecting absolute paths, traversal, symlinks, duplicate entries, and case conflicts. All six package-manifest hashes verified. Only active SPEC v2.0, its post-push review, and the root next-task file from `PROJECT_IMPORT_MANIFEST.txt` entered the repository. Older SPECs, reviews, runs 001-010, and committed artifacts remained unchanged.

A real `git fetch origin main` preceded changes. The server repository and fresh exact-byte clone both confirmed `main`, `HEAD=origin/main=e852e7de24c31410387ad46d75fb44a5cac9e850`, and a clean worktree. Recovery produced `tasks=52`, `done=23`, stage 0 READY, and sole READY/recommended task `S0_JOINT_SPLIT`; no `STATE_SPEC_CONFLICT` existed.

## Fixed read boundary

The production builder reads only these five committed inputs after exact SHA256 validation:

| Input | SHA256 |
|---|---|
| `artifacts/stimulus_identity.yaml` | `f6b94449d58c0e26d7da972968943f0eca0fa2bfc16cf2495ce8c41da80a69ea` |
| `artifacts/stimulus_groups.json` | `4408e57defbdc7ac5bd503c35489d68941d231d56009550a2bb17d0973b1fded` |
| `artifacts/admission/zuco2_nr_analysis_view_v1.jsonl` | `0751259f9f9455cba72bd7d027ffa1423e790e631ac0f5174c38da65d7cd12ff` |
| `artifacts/admission/zuco2_nr_analysis_view_v1.yaml` | `5e387ef3dc9e930e3ca3e4b6ccb6a009a3cc719281f1ac183cfbf56ac7b66181` |
| `artifacts/data_card.yaml` | `d9331bfe34937c264b7b8c667a2b831569c4440120e1d445011aeaf419c30f84` |

The 5,905-row analysis ledger was projected immediately to `occurrence_id,subject,session,task,block,slot,stimulus_sha256`. Raw sample, shape, channel, and source-locator fields did not enter features, ordering, objectives, or outputs. No source text, similarity value, signal value, event, result, prediction, or test value was read.

## Frozen assignment algorithm

Policy ID is `NC_HSG_JOINT_SPLIT_POLICY_V1`. Each of the 342 group feature vectors contains only 18 frozen-order subject row counts, seven block occurrence counts, and one total occurrence count. The production CLI exposes only optional `--output-root`; role capacities, domains, objective, and all assertions are constants.

The primary roles/capacities are `train_fit/inner_val/cal/test = 164/41/68/69`, with domain `NC_HSG_JOINT_SPLIT_V1\0PRIMARY\0`. Fixed hash initialization and deterministic ASCII pair-swap search terminated after exactly 25 swaps at integer objective `(201, 804726, 344, 651510, 201, 76266)`. The canonical group-role ledger SHA256 is `531539ff3592cc28d89c5e3ef568d019eaab733ccdb1053c1fcf1c471e9dac1c`.

The final 68 calibration groups were assigned to two 34-group reserves with domain `NC_HSG_JOINT_SPLIT_V1\0CAL_RESERVE\0`. Search terminated after exactly six swaps at `(34, 30056, 34, 2312, 34, 2312)`. The reserve ledger SHA256 is `5f464d97e695ab6bc58d10ac2342351195fa936144487bd9e78f96e5e7a8442c`. Reserve labels do not select a calibration theorem.

## Fixed summaries

| Role | Groups | Occurrences | Rows | Block occurrences | Subject-row range |
|---|---:|---:|---:|---|---:|
| train_fit | 164 | 167 | 2,832 | 24,23,25,24,24,24,23 | 117-167 |
| inner_val | 41 | 42 | 709 | 7,6,6,6,6,5,6 | 29-42 |
| cal | 68 | 69 | 1,171 | 9,10,10,10,10,10,10 | 48-69 |
| test | 69 | 71 | 1,193 | 10,11,10,10,10,10,10 | 49-71 |
| cal_select_reserve | 34 | 35 | 591 | 5,5,5,5,5,5,5 | 24-35 |
| cal_cert_reserve | 34 | 34 | 580 | 4,5,5,5,5,5,5 | 24-34 |

Regime I covers all 342 groups, 344 exact IDs, 349 stimulus occurrences, and 5,905 admitted rows exactly once. Role group sets are pairwise disjoint, every subject occurs in every role, and test is `LOCKED_UNTIL_ROUTE_LOCK`.

Regime II contains 18 frozen-order LOSO folds that reuse Regime I group roles. Each fold partitions all 5,905 rows into exactly one of six statuses. Train-fit ranges 2,665-2,715 rows, inner-val 667-680, calibration 1,102-1,123, and held-out test 49-71. Training/calibration contain neither the held-out subject nor test groups; test contains only the held-out subject and frozen test groups. Held-out-subject non-test rows cannot be used for adaptation. Interpretation is `EMPIRICAL_EXTERNAL_VALIDITY_ONLY`.

## Population and bootstrap

Policy `NC_HSG_GATE_A_POPULATION_V1` freezes the 18-subject equal-weight Regime I macro and the 18-fold equal-weight descriptive Regime II macro. Regime I test rows in frozen subject order are `50,71,60,71,70,49,68,71,71,69,69,70,60,68,69,70,69,68`.

Aggregation is trial-to-subject on fixed common rows, then five-seed mean within subject, then equal-weight mean across subjects. Comparisons are paired on row, subject, and seed. There is no zero-fill or silent subject deletion; a wholly missing frozen subject makes the confirmatory Gate `NOT_EVALUABLE`.

The fixed SHA256 counter-rejection generator produced 180,000 uint8 index bytes for the 10,000 x 18 paired subject bootstrap. Their SHA256 is `e77ca92b29c414a17c1e66edf4075edd470c007dfe2019487c36758f5f99c86d`. Only the contract/hash is committed; no binary indices, statistic, confidence interval value, or Gate result is committed.

## Deterministic outputs

| Output | SHA256 |
|---|---|
| `artifacts/split_regimeI.json` | `e2c065e5b395053cd655670fede8a2b117f6eb9821af884ca31c6fed3842fbab` |
| `artifacts/split_regimeII.json` | `9643dd5abe953e863e7535989f2f65d0f013a1c775c167e49f7d107545016393` |
| `artifacts/split_manifest.yaml` | `56ccf23881c4e5dee2f3f00704a8af4847636d116783a9da8c2526fdb5c2549f` |
| `artifacts/gate_a_population.yaml` | `279e3edf1c41971b6967f74657ec531533977d90ea4dc3d48a5efd63dd295d60` |
| `reports/joint_split_population.md` | `13755eac6198352b9c4dd6605f95a31b6e859db395bb5e6539a715427f742d09` |

Two production CLI builds used distinct repository-external roots `/tmp/nc_hsg_v20_a.qTp4Dv` and `/tmp/nc_hsg_v20_b.SBCBPG`. All five corresponding files were byte-identical and had the hashes above. The formal repository build reproduced the same hashes.

## Validation

- `test_build_joint_split.py`: 13/13 PASS.
- `test_build_stimulus_identity.py`: 12/12 PASS.
- `test_build_stimulus_similarity_diagnostic.py`: 12/12 PASS.
- `test_build_zuco2_nr_analysis_view.py`: 11/11 PASS.
- `test_audit_zuco2_nr.py`: 21/21 PASS.
- `test_project_memory.py`: 39/39 PASS.
- `test_audit_input_sources.py`: 8/8 PASS.
- Fixed input, assignment, ledger, summary, LOSO, population, bootstrap, lock, and safety assertions: PASS.
- Two-build byte stability, state validator, status command, and `git diff --check`: PASS.
- `HEAD=origin/main`, final clean worktree, and push checks: PASS after commit and synchronization.

No test was skipped to claim success.

## State transition and hard stop

`SPEC_V20_REVIEW`, `S0_JOINT_SPLIT`, and `S0_GATE_A_POPULATION_E5` are DONE. `S0_A_POLICY_REVIEW` is READY, owned by `CHATGPT_OR_AUTHOR`, and is the sole recommendation. `S0_A_INTERFACE` and `S0_LEAKAGE_AUDIT` remain BLOCKED.

No alternative split or seed was searched. No grouping rule, capacity, domain, objective, or calibration reserve was changed. No test value was read or unlocked, no full leakage audit ran, no physical unit was inferred, no backbone was selected/downloaded/implemented, no later-stage method was implemented, no training occurred, and no Gate executed.
