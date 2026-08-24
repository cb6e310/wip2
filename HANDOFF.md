# Current Handoff

Active SPEC: `guide/NC_HSG_Paper_Spec_v1_9_2026-08-23.md` (version `v1.9`).

## Current state

Run 010 completed `SPEC_V19_REVIEW -> S0_STIMULUS_GROUP_POLICY_REVIEW -> S0_STIMULUS_ID`. The frozen `NC_HSG_STIMULUS_GROUP_POLICY_V1` was applied only to the committed six-decimal candidate ledger. It produced two inter-identity edges, nine unjoined broad candidates, and 342 deterministic stimulus groups covering all 349 occurrences exactly once.

`S0_JOINT_SPLIT` is READY and is the sole recommended next task. Run 010 intentionally stopped before split construction. Root `CODEX_NEXT_TASK.md` requires the next exact ChatGPT or author split directive.

## Frozen grouping evidence

- Exact identities: 344; final groups: 342; multi-exact-ID groups: two; largest exact-ID component: two.
- Group kinds: 335 `SINGLETON`, five `EXACT_DUPLICATE_OCCURRENCES`, two `NEAR_DUPLICATE_LEAKAGE_RISK`.
- Occurrence group sizes: 335 groups of one plus seven groups of two; no group exceeds two occurrences.
- Candidate decisions: slots 97/327 are lexical-equivalence risk, slots 307/308 are embedding near-duplicate leakage risk, and the remaining nine are below policy.
- All candidates and groups are explicitly not paraphrase-verified. Document and paragraph IDs remain null and unavailable.
- Two repository-external production builds were byte-identical, and the formal build reproduced the same hashes.

## Output hashes

| Output | SHA256 |
|---|---|
| `artifacts/stimulus_identity.yaml` | `f6b94449d58c0e26d7da972968943f0eca0fa2bfc16cf2495ce8c41da80a69ea` |
| `artifacts/stimulus_groups.json` | `4408e57defbdc7ac5bd503c35489d68941d231d56009550a2bb17d0973b1fded` |
| `reports/stimulus_identity.md` | `de83ea580479fb3a8b94d2ebdfd55c3bf52c93b327b6434e67a9daedf314a465` |

## Safety boundary

No split artifact or split field was created. No material CSV, MAT/HDF5, EEG, event, TSR, outcome, historical result, tokenizer, or embedding model was read or run. Outputs contain no stimulus text, lexical text, tokens, n-grams, embedding vectors, or reversible text fragments. No EEG unit was inferred, no backbone A was selected, no training occurred, and no Gate ran.

## Required next action

Wait for an exact ChatGPT or author instruction before executing `S0_JOINT_SPLIT`. Do not infer split implementation details from current files or alter the frozen grouping policy.
