# NC-HSG v1.8 iteration-7 active handoff

Baseline: `wip2@b72ed5ab9720b7a922f7d1c6d8681cb646c344ab`  
Activated: 2026-08-22

## Purpose

SPEC v1.8 authorizes a bounded, outcome-blind binding of seven frozen ZuCo 2.0 NR material CSVs and a text-free all-pair similarity diagnostic. Run 009 binds 349 post-practice slots to 344 exact identities and scores all 58,996 unordered identity pairs without selecting a final threshold or grouping policy.

The active repository does not contain material CSV copies, stimulus text, tokens, embedding vectors, or model weights. Document and paragraph metadata remain unavailable. No EEG, event, TSR, outcome, historical result, checkpoint, backbone selection, split, training, or Gate is part of this work.

## Active files

- `guide/NC_HSG_Paper_Spec_v1_8_2026-08-22.md`: active scientific and governance contract.
- `artifacts/spec_review/nc_hsg_v18_post_push_review.md`: independent baseline review.
- `artifacts/stimulus_source_binding_v1.yaml`: opaque source-to-identity binding.
- `artifacts/stimulus_similarity_diagnostic_v1.yaml`: text-free score and component-risk summaries.
- `artifacts/stimulus_similarity_candidates_v1.jsonl`: broad diagnostic OR-prefilter ledger.
- `runs/2026-08-22_009_stimulus_similarity_diagnostic.md`: immutable execution record.

## Stop state

`S0_STIMULUS_GROUP_POLICY_REVIEW` is the sole READY recommendation and is owned by ChatGPT or the author. Codex must not choose a final threshold, create near-duplicate groups, or construct a split until that policy review is versioned.
