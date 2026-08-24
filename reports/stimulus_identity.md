# ZuCo 2.0 NR Stimulus Identity

## Frozen policy

Policy `NC_HSG_STIMULUS_GROUP_POLICY_V1` groups an opaque identity pair when committed edit similarity is at least 0.95, token Jaccard is at least 0.90, or embedding cosine is at least 0.90.

The policy uses only the committed six-decimal candidate ledger. It does not recompute scores or treat high similarity as a verified paraphrase.

## Result

- Exact identities: 344
- Preserved occurrences: 349
- Final inter-identity edges: 2
- Unjoined broad candidates: 9
- Final groups: 342
- Group kinds: {'EXACT_DUPLICATE_OCCURRENCES': 5, 'NEAR_DUPLICATE_LEAKAGE_RISK': 2, 'SINGLETON': 335}
- Largest exact-ID component: 2

Document and paragraph metadata are unavailable. Every group and candidate remains `NOT_VERIFIED_NO_TEXT_REVIEW`.

No stimulus text, token, n-gram, embedding vector, EEG, event, outcome, or split artifact is present. No training or Gate ran.
