# Run 012: RC-HSG Scientific Redesign and A-Policy Freeze

Date: 2026-08-24  
Task: `SPEC_V21_REVIEW` -> `S0_SCIENTIFIC_REDESIGN_FREEZE` -> `S0_A_POLICY_REVIEW` -> stop with `S0_A_INTERFACE` READY  
Baseline: `3b97fdc966b9b56d72287df619a80f6145d71189` on clean `main`  
Origin: `https://github.com/cb6e310/wip2`

## Baseline, package, and import

A real `git fetch origin main` preceded all package and repository changes. The server repository confirmed branch `main`, `HEAD=origin/main=3b97fdc966b9b56d72287df619a80f6145d71189`, and an empty porcelain status. Recovery passed with 54 tasks, 26 DONE, stage 0 READY, and sole READY/recommended `S0_A_POLICY_REVIEW`; no `STATE_SPEC_CONFLICT` existed.

The handoff ZIP SHA256 was `ac94b1cce06fecae6a71ef9a25285fef687710b918ed63ebb9b7d2d3d5fb4ab2`. It was extracted outside the repository after rejecting absolute paths, traversal, symlinks, duplicate entries, and case conflicts. All entries in `PACKAGE_MANIFEST.sha256` passed. Handoff-only hashes were:

| File | SHA256 |
|---|---|
| `PACKAGE_MANIFEST.sha256` | `e4c4020641c368b0b9fb8197c7087d2e93ece625486c8af26de787c3b71da711` |
| `PROJECT_IMPORT_MANIFEST.txt` | `442eee3ea8a66b6eafef8a1a32bde0d0120daa02913c6bff4e0577f9212af54e` |
| `CODEX_EXECUTION_INSTRUCTION.md` | `95d98c66afcd0bb0d1e8fa5dc3bee5c8b8d409933dd9ccc98cd9d31cfb855bab` |
| `SOURCE_DECISION_RECORD.md` | `b3792597de611f8aaee10ca8e363704d831a8f5ab8b47c6cd3f68c35d412c1f8` |

Only the three import-manifest paths entered the repository. Their post-import hashes were:

| Imported path | SHA256 |
|---|---|
| `guide/RC_HSG_Paper_Spec_v2_1_2026-08-24.md` | `ea0dcf34d0b41d390ef06a92fe65fc696e5bc2bba1f944a194f3b8cd25cee54d` |
| `artifacts/spec_review/rc_hsg_v21_scientific_redesign_review.md` | `d8d58ad8148ab31128e56f72fa3b6702c8e316f9037f5c6a619c2b1243d1f2e2` |
| root `CODEX_NEXT_TASK.md` at import | `ab94d5c87e8b195f847668ce781a2354f0371dbb36d653753c43e51e0c6b7214` |

The root next-task file was then intentionally advanced to the post-run `S0_A_INTERFACE` stop state. No other package file entered the repository.

## Run-011 acceptance and supersession boundary

Run 011 is accepted without rewriting its files. The 342-group deterministic split remains 164 train-fit, 41 inner-val, 68 calibration, and 69 locked-test groups; calibration reserves remain 34/34; Regime II remains 18 LOSO folds; the population remains the equal-weight 18-subject macro; and the fixed 10,000 x 18 bootstrap stream remains unchanged. Test identities remain `LOCKED_UNTIL_ROUTE_LOCK`.

RC-HSG v2.1 section 20 supersedes only the older NC-HSG scientific interpretation, Gate architecture, claim routes, and downstream task graph. Sections 14-19 and all committed data, identity, grouping, split, population, and bootstrap artifacts remain immutable physical provenance.

## Frozen scientific question and owner decisions

The active question is whether, under stimulus-group-disjoint EEG-to-Text generalization, sample-level information from a structure-matched reference distribution improves identification of when deeper semantic output is reliable, so hierarchical specificity can increase at the same unsupported-semantic risk.

The author-frozen decisions activated here are:

- method `RC-HSG`; N2 multivariate common-phase reference primary when Gate R0 admits it, with N1 strict permutation as mechanism/robustness and pre-registered fallback only;
- primary features `s, delta, robust_z, empirical_upper_rank, MAD, structural_parent_features`; MAD is the sole primary spread;
- per-level L2-regularized binomial-logistic GLM, fixed lambda grid, deterministic inner-val selection, and cumulative typed unsupported-fraction target;
- candidate content shared across methods and selected only by absolute score on a parent-consistent path; reference features affect routing only;
- paired 95% upper bound guard `Delta M_sem <= 0.05`; Holm family RC-HSG versus Absolute-HSG, Flat-RC, and PMI;
- two-stage 34-group cal-select then independent 34-group cal-cert isolation, with the finite-sample theorem still blocked by a required feasibility review;
- Gate R0, Gate R, Gate C, Gate H, and non-blocking Mechanism A as the only active Gate architecture;
- primary A policy `RC_HSG_NATIVE_SPECTRAL_A1_V1`.

No decision above is a result or performance conclusion.

## A candidate decisions and native policy

All three existing candidates were rejected as primary under the exact frozen ledger reasons:

```text
TRUST_ALIGN_A1_SPECTRAL:
  REJECT_PRIMARY_EXTERNAL_SOURCE_LICENSE_NOT_FOUND_NO_CODE_COPY
TRUST_ALIGN_LABRAM_A3:
  REJECT_PRIMARY_UNIT_CHANNEL_FILTER_CHECKPOINT_INTERFACE_UNRESOLVED
OFFICIAL_NEUROLM_B_VQ:
  REJECT_PRIMARY_MICROVOLT_CHANNEL_ADAPTER_AND_UNDOWNLOADED_WEIGHT_GAPS
```

`artifacts/backbone_a_policy.yaml` materializes the project-native clean-room spectral policy with no external code copy, pretrained checkpoint, weight download, physical-unit conversion, or channel interpolation. It freezes 105 channels at 500 Hz, common-average release-native input, robust per-trial scaling/clipping, 500/250 Hann windows, eight bands, 840-dimensional log-relative-bandpower tokens, a 256-dimensional projection, two Transformer encoder layers, masks, and a 256-dimensional pooled embedding. Short or invalid segments fail future admission; no silent padding or silent backbone switch is allowed. The artifact SHA256 is `034a523119f12f648266d94e0499179882fbe181584d10c1af17a3502a797425`.

The policy selects an interface only. No frontend, decoder F, schema, reference generator, reliability model, GLM, or training path was implemented.

## Task and blocker migration

The task graph moved from 54 tasks / 26 DONE / one READY to exactly 67 tasks / 29 DONE / one READY. `SPEC_V21_REVIEW`, `S0_SCIENTIFIC_REDESIGN_FREEZE`, and `S0_A_POLICY_REVIEW` are DONE. `S0_A_INTERFACE` is the sole READY, owner `CODEX`.

Historical `GATE_A1`, `GATE_A`, `GATE_B`, `S0_NC_HSG_CORE`, `S0_DIRECT_C`, `STAGE1_PROBES`, and `SHAM_VALIDATION` retain their records but are `SKIPPED`, `critical_path=false`, with `SUPERSEDED_BY_RC_HSG_V21`. Thirteen new v2.1 task IDs were added, dependencies were rewritten to the section-20 graph, and the validator hardcodes the required IDs, dependency sets, supersession states, active Gates, counts, A policy, test lock, and run-011 hashes.

The old unit-sensitive/backbone-not-selected blockers moved to superseded evidence. Unknown physical unit remains an explicit limitation and conversion prohibition. Active `B_V7_A_INTERFACE_UNIMPLEMENTED` now blocks frontend-dependent work while leaving `S0_A_INTERFACE` itself READY. B_V3-B_V6 now reference RC-HSG schema, reference, reliability, calibration, and candidate-firewall work rather than old Gate A prerequisites.

## Frozen-artifact continuity

| Run-011 output | SHA256 |
|---|---|
| `artifacts/split_regimeI.json` | `e2c065e5b395053cd655670fede8a2b117f6eb9821af884ca31c6fed3842fbab` |
| `artifacts/split_regimeII.json` | `9643dd5abe953e863e7535989f2f65d0f013a1c775c167e49f7d107545016393` |
| `artifacts/split_manifest.yaml` | `56ccf23881c4e5dee2f3f00704a8af4847636d116783a9da8c2526fdb5c2549f` |
| `artifacts/gate_a_population.yaml` | `279e3edf1c41971b6967f74657ec531533977d90ea4dc3d48a5efd63dd295d60` |
| `reports/joint_split_population.md` | `13755eac6198352b9c4dd6605f95a31b6e859db395bb5e6539a715427f742d09` |

All five remained byte-identical.

## Validation

- `test_project_memory.py`: 48/48 PASS.
- `test_build_joint_split.py`: 13/13 PASS.
- `test_build_stimulus_identity.py`: 12/12 PASS.
- `test_build_stimulus_similarity_diagnostic.py`: 12/12 PASS.
- `test_build_zuco2_nr_analysis_view.py`: 11/11 PASS.
- `test_audit_zuco2_nr.py`: 21/21 PASS.
- `test_audit_input_sources.py`: 8/8 PASS.
- Validator: PASS with 67 tasks, 29 DONE, and sole READY `S0_A_INTERFACE`.
- Status command, exact A-policy and dependency assertions, frozen-artifact hashes, test lock, and `git diff --check`: PASS.
- No test was skipped to claim success.

## Safety statement and hard stop

This run changed specification and governance only. It did not read real EEG values, stimulus/semantic outcomes, calibration or test results, predictions, or historical model metrics. It did not copy, import, or download trust_align, LaBraM, or NeuroLM code or weights. It did not implement or train A/F/schema/reference/reliability/GLM code, run the full leakage audit, execute any Gate, alter grouping/split/population/bootstrap, infer microvolts, interpolate channels, or unlock test.

Final state is active RC-HSG v2.1, stage 0 READY, `last_completed_task=S0_A_POLICY_REVIEW`, and `recommended_next_task=S0_A_INTERFACE`. Stop here.
