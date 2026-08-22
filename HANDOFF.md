# Current Handoff

Active SPEC: `guide/NC_HSG_Paper_Spec_v1_8_2026-08-22.md` (version `v1.8`).

## Current state

Run 009 completed `SPEC_V18_REVIEW -> S0_STIMULUS_SOURCE_BINDING -> S0_STIMULUS_SIMILARITY_DIAGNOSTIC`. Seven frozen ZuCo 2.0 NR CSVs produced 370 material rows, 21 excluded practice rows, 349 task slots, 344 exact identities, five exact duplicate groups, and 58,996 all-pair diagnostics. `S0_STIMULUS_GROUP_POLICY_REVIEW` is READY and the sole recommendation. `S0_STIMULUS_ID` and `S0_JOINT_SPLIT` remain BLOCKED.

## Diagnostic evidence

- Source binding: 349/349 slot hashes match schema v3; all 344 identities occur in the 5,905-row analysis view.
- Metadata: `document_id=null`, `paragraph_id=null`, both `SOURCE_METADATA_NOT_AVAILABLE`; no block/line inference was performed.
- Model: `sentence-transformers/all-MiniLM-L6-v2@c9745ed1d9f207416be6d2e6f8de32d1f16199bf`, Apache-2.0, 384 dimensions, CPU/eval/no-grad, safe files only. Wordpieces are 8-82, below the frozen 256 limit, with no truncation.
- Score min/median/p99/max: edit `0.062130/0.240506/0.317832/1.000000`; Jaccard `0/0.052632/0.162162/1.000000`; cosine `-0.203407/0.108270/0.414134/0.998133`.
- Broad OR candidates: 11. Trigger counts are edit=1, Jaccard=1, cosine=11; every pairwise intersection and the triple intersection is 1.
- Component risk: edit cuts 0.80-0.95 and Jaccard cuts 0.70-0.90 each show one size-2 non-singleton component. Cosine cut 0.70 shows 10 non-singleton components with largest size 3; cut 0.75 shows 4 with largest size 2; cuts 0.80-0.90 show 2 with largest size 2. These are diagnostics, not formal groups.

## Output hashes

| Output | SHA256 |
|---|---|
| `artifacts/stimulus_source_binding_v1.yaml` | `d1feb8e46b69074693173594ccdc4f7c3e014ca113594701131fe460f205b941` |
| `artifacts/stimulus_similarity_diagnostic_v1.yaml` | `878d9ea68c9f5c42cc2f8d441da3117681b354d9869e1238011f6f8d7522a66d` |
| `artifacts/stimulus_similarity_candidates_v1.jsonl` | `6645369f6cfc173683c825de71d12689faa6ff75a4544c68ab018875e6d7be6b` |
| `reports/stimulus_similarity_diagnostic_v1.md` | `93a5d2ab09f803cde06eb4d1927923675f669a1258ba6566ef5e9620593d200b` |

Two complete real builds were byte-identical. Machine assertions passed for counts, source coverage, model allowlist, histogram totals, candidate allowlist/order, pending policy, no formal groups, and output hashes.

## Required next action

ChatGPT or the author must review the committed opaque diagnostic and freeze a versioned final grouping policy. Codex must not choose a threshold, label high similarity as verified paraphrase, emit near-duplicate groups, merge exact occurrences, or construct a split.

## Safety boundary

No committed output contains stimulus sentences, lexical text, tokens, n-grams, or embedding vectors. No EEG, event, TSR, outcome, historical result, prediction, checkpoint, or `trust_align` result tree was read. No backbone A was selected, no split was built, no training occurred, and no Gate ran.
