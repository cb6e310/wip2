# ZuCo 2.0 NR Stimulus Similarity Diagnostic

## Scope

The bounded source binding recovered 370 material rows, excluded 21 practice rows, and bound 349 task slots to 344 opaque exact identities. 5 exact duplicate groups remain separate from the all-pair diagnostic.

All 58,996 unordered pairs were scored with normalized edit similarity, token-set Jaccard, and cosine from `sentence-transformers/all-MiniLM-L6-v2@c9745ed1d9f207416be6d2e6f8de32d1f16199bf`. No stimulus sentence, token, n-gram, or embedding vector is present in committed outputs.

## Frozen model

- License: `Apache-2.0`
- Dimension: 384
- Wordpieces including special tokens: min 8, max 82; no truncation
- Safe files: 11, all hash-verified; `model.safetensors` only

## Broad diagnostic prefilter

The committed candidate ledger uses the preregistered OR rule: edit >= 0.80, token Jaccard >= 0.70, or embedding cosine >= 0.70.

- Candidate union: 11
- Edit trigger: 1
- Jaccard trigger: 1
- Embedding trigger: 11

Histograms, registered quantiles, top-1000 opaque pairs, trigger intersections, and single-metric component-risk summaries are recorded in the machine-readable diagnostic.

## Decision boundary

No final near-duplicate threshold or grouping policy was selected. High similarity is not a verified paraphrase label. Document and paragraph metadata are unavailable from the bound source contract. The next action is ChatGPT/author policy review; Codex must not create groups or splits from this diagnostic.

No EEG, event, TSR, outcome, historical result, prediction, checkpoint, or trust_align result tree was read. No A was selected, no training occurred, and no Gate ran.
