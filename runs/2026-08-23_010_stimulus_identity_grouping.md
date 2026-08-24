# Run 010: ZuCo 2.0 NR Stimulus Identity Grouping

Date: 2026-08-23  
Task: `SPEC_V19_REVIEW` -> `S0_STIMULUS_GROUP_POLICY_REVIEW` -> `S0_STIMULUS_ID` -> stop with `S0_JOINT_SPLIT` READY  
Baseline: `1252d0a24b6d4785e7f550464586c95f54f3cfa3` on clean `main`  
Origin: `https://github.com/cb6e310/wip2`

## Package and governance

The v1.9 handoff ZIP SHA256 was `5b36d9acde51a60ffeeb07d94a933a81b6a2c88d255237a65ba1be645d6906bc`. It was extracted outside the repository after rejecting absolute paths, traversal, symlinks, duplicate entries, and case conflicts. All six package-manifest hashes verified. Only the three project-import-manifest paths entered the repository: active SPEC v1.9, its post-push review, and the root next-task instruction. Older SPECs, reviews, runs 001-009, and committed artifacts remained unchanged.

The clean baseline recovery confirmed `main`, `HEAD=origin/main=1252d0a24b6d4785e7f550464586c95f54f3cfa3`, and the sole READY/recommended task `S0_STIMULUS_GROUP_POLICY_REVIEW`. SPEC v1.9 freezes the policy; run 010 executes it without selecting or tuning thresholds.

## Fixed read boundary

The production builder reads only these three committed inputs after exact SHA256 validation:

| Input | SHA256 |
|---|---|
| `artifacts/stimulus_source_binding_v1.yaml` | `d1feb8e46b69074693173594ccdc4f7c3e014ca113594701131fe460f205b941` |
| `artifacts/stimulus_similarity_diagnostic_v1.yaml` | `878d9ea68c9f5c42cc2f8d441da3117681b354d9869e1238011f6f8d7522a66d` |
| `artifacts/stimulus_similarity_candidates_v1.jsonl` | `6645369f6cfc173683c825de71d12689faa6ff75a4544c68ab018875e6d7be6b` |

No material CSV, MAT/HDF5, EEG, event, TSR, outcome, historical result, tokenizer, or embedding model was read or run.

## Frozen policy

Policy ID is `NC_HSG_STIMULUS_GROUP_POLICY_V1`. An inter-identity edge exists when the committed six-decimal candidate ledger satisfies:

```text
edit_similarity >= 0.95
OR token_jaccard >= 0.90
OR embedding_cosine >= 0.90
```

The builder exposes no input-path or threshold parameter. It uses deterministic union-find over all 344 exact stimulus IDs. Group IDs are exactly `sg_v1_` plus SHA256 of the frozen domain separator, NUL byte, and newline-joined sorted ASCII exact IDs. Occurrences remain distinct even when they share a group.

The 11 broad candidates all have decisions. Slots 97/327 are `GROUP_LEXICAL_EQUIVALENCE_RISK`; slots 307/308 are `GROUP_EMBEDDING_NEAR_DUPLICATE_LEAKAGE_RISK`; the other nine are `UNJOINED_BELOW_FROZEN_POLICY`. No candidate or group is treated as a verified paraphrase.

## Deterministic outputs

| Output | SHA256 |
|---|---|
| `artifacts/stimulus_identity.yaml` | `f6b94449d58c0e26d7da972968943f0eca0fa2bfc16cf2495ce8c41da80a69ea` |
| `artifacts/stimulus_groups.json` | `4408e57defbdc7ac5bd503c35489d68941d231d56009550a2bb17d0973b1fded` |
| `reports/stimulus_identity.md` | `de83ea580479fb3a8b94d2ebdfd55c3bf52c93b327b6434e67a9daedf314a465` |

Two production CLI builds used distinct repository-external roots `/tmp/nc_hsg_v19_a.2fTs8O` and `/tmp/nc_hsg_v19_b.Ecyo2h`. All three corresponding files were byte-identical and had the hashes above. The formal repository build reproduced the same hashes.

Machine assertions confirm two inter-identity edges, nine unjoined broad candidates, 342 final groups, two multi-exact-ID groups, and largest exact-ID component size two. Group-kind counts are 335 `SINGLETON`, five `EXACT_DUPLICATE_OCCURRENCES`, and two `NEAR_DUPLICATE_LEAKAGE_RISK`. All 349 occurrences map exactly once; occurrence group sizes are 335 groups of one and seven groups of two, with none larger than two.

Every candidate and group records `paraphrase_verified=false`, `paraphrase_status=NOT_VERIFIED_NO_TEXT_REVIEW`, null document/paragraph IDs, and `SOURCE_METADATA_NOT_AVAILABLE` statuses. Machine artifacts contain no split field. No split artifact was created.

## Validation

- `test_build_stimulus_identity.py`: 12/12 PASS.
- `test_build_stimulus_similarity_diagnostic.py`: 12/12 PASS.
- `test_build_zuco2_nr_analysis_view.py`: 11/11 PASS.
- `test_audit_zuco2_nr.py`: 21/21 PASS.
- `test_project_memory.py`: 38/38 PASS.
- `test_audit_input_sources.py`: 8/8 PASS.
- Fixed-input and production-output machine assertions: PASS.
- Two-build byte stability: PASS.
- State validator, status command, `git diff --check`, origin equality, and clean-worktree checks: PASS after synchronization, commit, and push.

No test was skipped to claim success.

## State transition and hard stop

`SPEC_V19_REVIEW`, `S0_STIMULUS_GROUP_POLICY_REVIEW`, and `S0_STIMULUS_ID` are DONE. `S0_JOINT_SPLIT` is READY and the sole recommendation. Run 010 stops here and root `CODEX_NEXT_TASK.md` requires the next exact ChatGPT or author split instruction.

No `split_regimeI.json`, `split_regimeII.json`, or `split_manifest.yaml` was created. No stimulus text, lexical text, token, n-gram, embedding vector, EEG, event, outcome, or reversible text fragment was emitted. No EEG unit was inferred, no backbone A was selected, no later-stage method was implemented, no training occurred, and no Gate ran.
