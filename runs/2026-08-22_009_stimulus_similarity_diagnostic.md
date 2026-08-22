# Run 009: ZuCo 2.0 NR Stimulus Similarity Diagnostic

Date: 2026-08-22  
Task: `SPEC_V18_REVIEW` -> `S0_STIMULUS_SOURCE_BINDING` -> `S0_STIMULUS_SIMILARITY_DIAGNOSTIC`  
Baseline: `b72ed5ab9720b7a922f7d1c6d8681cb646c344ab` on clean `main`  
Origin: `https://github.com/cb6e310/wip2`

## Package and governance

The v1.8 handoff ZIP SHA256 was `9f764149c7b37fe016bace44e4fefc069b82e4cc6f2c188081dab98491423ec7`. It was extracted outside the repository and every entry in `PACKAGE_MANIFEST.sha256` verified `OK`. Only the three manifest-listed project files were imported; package metadata was not copied into the repository. SPEC v1.8 and its review were activated with `reviewed_commit=b72ed5ab9720b7a922f7d1c6d8681cb646c344ab`. Older SPECs, reviews, runs 001-008, schema-v1/v2/v3 admission artifacts, the analysis view, and the data card were retained unchanged.

## Read boundary and source binding

Only seven `task_materials/nr_*.csv` files under the previously authorized ZuCo 2.0 root were read. Their SHA256 values were:

| File | SHA256 |
|---|---|
| `nr_1.csv` | `77291d9fe66797781efa7c093824a16198f38e92ac34067e8bf20d76d5c50386` |
| `nr_2.csv` | `68a6885dd96d4fa386297d7f30352c2077b565577c68dcb2205b19d506042132` |
| `nr_3.csv` | `1a1ead3a1dfa12d8ff73dbe619db94b6ce202b35a3d19358d67f01c3115553ba` |
| `nr_4.csv` | `d7b5c9b3a0e6d55958b976b0ea2cc6c236720ead947d6851d15de798e712965f` |
| `nr_5.csv` | `2ca84d88f3267ecc4686f357cc97f2c077a2b90534ecbc8615b2197e2f93b5bc` |
| `nr_6.csv` | `3722ba205f8b63e801791ef3303dcdbf52bbef3c6bd157bd11a16ccd40e1861a` |
| `nr_7.csv` | `575a938092ca1db20d883fed180cb48fa66deca53097267874fe784fdc44cf9b` |

The read-only committed contracts were targeted manifest `50806a60937b28ae36207509c44d606af6f6b6b1be2a69c06081672f0931bfaf`, stimulus manifest `2512c55bb7471896aad7bfa7ba96843fbce8a46067abffda6c16ad87ce3e44be`, analysis-view ledger `0751259f9f9455cba72bd7d027ffa1423e790e631ac0f5174c38da65d7cd12ff`, analysis summary `5e387ef3dc9e930e3ca3e4b6ccb6a009a3cc719281f1ac183cfbf56ac7b66181`, and data card `d9331bfe34937c264b7b8c667a2b831569c4440120e1d445011aeaf419c30f84`.

`N_exact` uses UTF-8-sig decoding, NFKC, strip, and Unicode-whitespace collapse. `N_lex` additionally uses casefold and maximal non-alphanumeric-run replacement. Only opaque exact and lexical hashes were emitted. The binding reproduced 370 total rows, 21 practices, 349 task slots, per-block counts 50/50/51/50/50/49/49, 344 unique exact identities, five exact duplicate groups, and 349/349 schema-v3 matches. Every exact identity is represented in the 5,905-row analysis view. Document and paragraph IDs remain null and unavailable.

## Frozen embedding model

The exact model was `sentence-transformers/all-MiniLM-L6-v2@c9745ed1d9f207416be6d2e6f8de32d1f16199bf`, Apache-2.0, dimension 384. The exact revision was absent, so one allowlisted download obtained only the following files into the external Hugging Face cache:

| File | SHA256 |
|---|---|
| `1_Pooling/config.json` | `4be450dde3b0273bb9787637cfbd28fe04a7ba6ab9d36ac48e92b11e350ffc23` |
| `README.md` | `7dfc82496ec33f906b5b0d6750c1e2397da6530c74d1ae3568c55bc2739125e7` |
| `config.json` | `953f9c0d463486b10a6871cc2fd59f223b2c70184f49815e7efbcab5d8908b41` |
| `config_sentence_transformers.json` | `061ca9d39661d6c6d6de5ba27f79a1cd5770ea247f8d46412a68a498dc5ac9f3` |
| `model.safetensors` | `53aa51172d142c89d9012cce15ae4d6cc0ca6895895114379cacb4fab128d9db` |
| `modules.json` | `84e40c8e006c9b1d6c122e02cba9b02458120b5fb0c87b746c41e0207cf642cf` |
| `sentence_bert_config.json` | `fc1993fde0a95c24ec6c022539d41cf6e2f7c9721e5415d6fb6897472a9cd4b7` |
| `special_tokens_map.json` | `303df45a03609e4ead04bc3dc1536d0ab19b5358db685b6f3da123d05ec200e3` |
| `tokenizer.json` | `be50c3628f2bf5bb5e3a7f17b1f74611b2561a3a27eeab05e5aa30f411572037` |
| `tokenizer_config.json` | `acb92769e8195aabd29b7b2137a9e6d6e25c476a4f15aa4355c233426c61576b` |
| `vocab.txt` | `07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3` |

Versions were Python 3.12.3, Torch 2.13.0, Transformers 5.15.0, tokenizers 0.22.2, and safetensors 0.8.0. Loading was local-only, `use_safetensors=True`, `trust_remote_code=False`, CPU/eval/no-grad, attention-mask mean pooling, and float32 L2 normalization. Wordpiece counts including special tokens were 8-82; the limit was 256 and no truncation occurred. No model file entered Git and no stimulus text was sent to a remote service.

## All-pair diagnostic

All `344*343/2=58,996` unordered pairs were scored. Score min/median/p99/max were edit `0.062130/0.240506/0.317832/1.000000`, Jaccard `0/0.052632/0.162162/1.000000`, and cosine `-0.203407/0.108270/0.414134/0.998133`. Stable width-0.01 histograms each sum to 58,996.

The broad diagnostic OR prefilter produced 11 candidates: edit trigger 1, Jaccard trigger 1, cosine trigger 11, all pairwise intersections 1, and triple intersection 1. Edit cuts 0.80-0.95 and Jaccard cuts 0.70-0.90 each yielded one size-2 non-singleton component. Cosine cut 0.70 yielded 10 non-singleton components with largest size 3; 0.75 yielded 4 with largest size 2; 0.80-0.90 yielded 2 with largest size 2. No component received a formal group ID.

## Deterministic outputs

| Output | SHA256 |
|---|---|
| `artifacts/stimulus_source_binding_v1.yaml` | `d1feb8e46b69074693173594ccdc4f7c3e014ca113594701131fe460f205b941` |
| `artifacts/stimulus_similarity_diagnostic_v1.yaml` | `878d9ea68c9f5c42cc2f8d441da3117681b354d9869e1238011f6f8d7522a66d` |
| `artifacts/stimulus_similarity_candidates_v1.jsonl` | `6645369f6cfc173683c825de71d12689faa6ff75a4544c68ab018875e6d7be6b` |
| `reports/stimulus_similarity_diagnostic_v1.md` | `93a5d2ab09f803cde06eb4d1927923675f669a1258ba6566ef5e9620593d200b` |

Two complete real builds produced the same four hashes. Separate machine assertions passed for counts, 349/349 binding, identity coverage, exact groups, model allowlist, wordpiece limit, histogram totals, candidate schema/order/OR membership, pending policy, absence of formal groups/split, and output hashes.

## Validation

- `test_build_stimulus_similarity_diagnostic.py`: 12/12 PASS.
- `test_build_zuco2_nr_analysis_view.py`: 11/11 PASS.
- `test_audit_zuco2_nr.py`: 21/21 PASS.
- `test_project_memory.py`: 38/38 PASS.
- `test_audit_input_sources.py`: 8/8 PASS.
- Real diagnostic machine assertions: PASS.
- Two-build byte stability: PASS.
- State validator, status command, `git diff --check`, and final clean/push checks are recorded after the governance files are synchronized.

## State transition and stop boundary

`SPEC_V18_REVIEW`, `S0_STIMULUS_SOURCE_BINDING`, and `S0_STIMULUS_SIMILARITY_DIAGNOSTIC` are DONE. `S0_STIMULUS_GROUP_POLICY_REVIEW` is READY, owned by ChatGPT or the author, and is the sole recommendation. `S0_STIMULUS_ID` and `S0_JOINT_SPLIT` remain BLOCKED.

No final threshold was selected; no near-duplicate grouping or split was produced. No EEG, event, TSR, outcome, historical result, prediction, checkpoint, or result tree was read. No A was selected, no training occurred, and no Gate ran.
