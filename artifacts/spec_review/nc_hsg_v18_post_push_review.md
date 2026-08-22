# NC-HSG v1.8 post-push review

Date: 2026-08-22  
Reviewed remote: `https://github.com/cb6e310/wip2`  
Reviewed commit: `b72ed5ab9720b7a922f7d1c6d8681cb646c344ab`

## Verdict

Run 008 is accepted. The repository deterministically reproduces the 5,905-row analysis view, 377-row exclusion union and data card while retaining `full_release_diagnostic=FAIL`, `analysis_view_admission=PASS`, NR3/NR5/NR6 anomaly scope and `UNRESOLVED_RELEASE_NATIVE_AMPLITUDE`.

The next declared task is not executable as written. Committed stimulus artifacts contain hashes and lengths but no text, document ID or paragraph ID. Hashes can establish five exact duplicate groups; they cannot support edit distance, token overlap, semantic embedding or paraphrase decisions. Letting Codex fill that gap autonomously would violate the project rule that research and threshold decisions are frozen before execution.

SPEC v1.8 therefore replaces the one-step grouping task with a bounded two-part evidence run: bind the seven already verified NR material CSVs to the committed hashes, then compute a text-free all-pair similarity diagnostic. Final near-duplicate thresholds and grouping remain a later ChatGPT/author decision. No split is authorized.

## Independent checks

- Remote `main` resolves to `b72ed5ab9720b7a922f7d1c6d8681cb646c344ab`; commit message is `fix: admit bounded ZuCo NR analysis view`.
- `test_build_zuco2_nr_analysis_view.py`: 11/11 PASS.
- `test_project_memory.py`: 38/38 PASS.
- `test_audit_input_sources.py`: 8/8 PASS.
- Validator: PASS, 47 tasks and 17 DONE.
- Status: stage 0 READY; sole recommendation `S0_STIMULUS_ID`.
- The review environment lacks `h5py`; `test_audit_zuco2_nr.py` was not falsely claimed as an independent pass. Run 008 records 21/21 on the server.
- A repository-only rebuild of the analysis view, summary, data card and report is byte-identical to the commit and reproduces all four recorded SHA256 values.
- The detached review worktree was clean after validation.

## Exact stimulus evidence already available

- 349 post-practice material slots.
- 344 unique NFKC-plus-whitespace normalized stimulus SHA256 identities.
- Five cross-block exact duplicate groups.
- Seven task-material CSVs already have local SHA256 equal to OSF SHA256 under run-005 provenance.
- No committed raw stimulus text, document metadata or paragraph metadata.

## Frozen diagnostic choice

The diagnostic uses three complementary, outcome-blind pair scores: normalized Levenshtein similarity, token-set Jaccard and a frozen sentence embedding cosine. The embedding model is `sentence-transformers/all-MiniLM-L6-v2` at exact revision `c9745ed1d9f207416be6d2e6f8de32d1f16199bf`, loaded only from `model.safetensors` and documented config/tokenizer files. Its official model card identifies a 384-dimensional sentence/short-paragraph representation for clustering and similarity, with mean pooling, L2 normalization and a 256-wordpiece truncation boundary.

The broad diagnostic cutoffs (`edit>=0.80`, `Jaccard>=0.70`, or cosine `>=0.70`) select pairs for inspection only. They are deliberately not declared final near-duplicate thresholds. The next ChatGPT/author review must use the committed distribution, candidate counts, intersections and component-risk diagnostics to freeze the actual grouping policy before split construction.

## Corrected next action

Activate SPEC v1.8 and run only:

```text
SPEC_V18_REVIEW
-> S0_STIMULUS_SOURCE_BINDING
-> S0_STIMULUS_SIMILARITY_DIAGNOSTIC
-> S0_STIMULUS_GROUP_POLICY_REVIEW (READY; stop)
```

Do not finish `S0_STIMULUS_ID`, choose final thresholds, label candidates as verified paraphrases, build Regime I/II splits, read EEG/outcomes, select A, train or run a Gate.

## Research sources

- ZuCo 2.0 dataset scope and primary NR task: https://aclanthology.org/2020.lrec-1.18/
- Official sentence-embedding model card: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- Frozen model revision and safe weight inventory: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/tree/c9745ed1d9f207416be6d2e6f8de32d1f16199bf
