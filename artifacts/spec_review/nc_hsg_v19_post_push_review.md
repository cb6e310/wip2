# NC-HSG v1.9 post-push review

Date: 2026-08-23  
Reviewed remote: `https://github.com/cb6e310/wip2`  
Reviewed commit: `1252d0a24b6d4785e7f550464586c95f54f3cfa3`

## Verdict

Run 009 is accepted. Its seven-CSV source binding and all-pair diagnostic are internally consistent, deterministic, text-safe and outcome-blind. The repository is correctly stopped at `S0_STIMULUS_GROUP_POLICY_REVIEW`; no near-duplicate group or split has been emitted.

SPEC v1.9 completes the owner-only review. The final edge rule is `edit_similarity>=0.95 OR token_jaccard>=0.90 OR embedding_cosine>=0.90`, applied to committed six-decimal scores, followed by deterministic union-find over exact identities. It yields exactly two inter-identity edges and 342 groups. Embedding-based grouping is a conservative leakage-risk decision, not verified paraphrase evidence.

Codex is now authorized only to materialize this frozen policy as `artifacts/stimulus_identity.yaml` and `artifacts/stimulus_groups.json`, with code/tests/report/run/state updates. It is not authorized to choose thresholds, reread source text, rerun the embedding model or construct a split. On success, `S0_JOINT_SPLIT` becomes READY and run 010 stops.

## Independent checks

- Local and remote `main` both resolve to `1252d0a24b6d4785e7f550464586c95f54f3cfa3`; commit message is `chore: diagnose ZuCo NR stimulus similarity`; worktree is clean.
- `test_build_stimulus_similarity_diagnostic.py`: 12/12 PASS.
- `test_build_zuco2_nr_analysis_view.py`: 11/11 PASS.
- `test_project_memory.py`: 38/38 PASS.
- `test_audit_input_sources.py`: 8/8 PASS.
- Validator: PASS, 51 tasks and 20 DONE; status: stage 0 READY with sole recommendation `S0_STIMULUS_GROUP_POLICY_REVIEW`.
- `git diff --check`: PASS.
- The review environment lacks `h5py`; `test_audit_zuco2_nr.py` failed at import and was not falsely claimed as an independent pass. Run 009 records 21/21 on the server.
- Recomputed file hashes match run 009 for source binding, diagnostic, candidate ledger and report.
- Independent policy simulation gives 2 final edges, 342 connected groups, 2 multi-exact-ID groups, maximum component size 2, 335 one-occurrence groups, 7 two-occurrence groups and 9 unjoined broad candidates.

## Frozen decision details

The 11-row broad ledger is a complete superset because every final threshold is at least as strict as its diagnostic prefilter. One accepted edge has edit/Jaccard/cosine `1.000000/1.000000/0.998133`; the other has `0.693431/0.692308/0.959401`. The next-highest broad cosine is only `0.782380`, while the all-pair p99 is `0.414134`. The final rule therefore separates the two extreme-risk pairs without absorbing the nine low-lexical-overlap, moderate-cosine candidates.

No raw text was inspected. The second edge is deliberately named `GROUP_EMBEDDING_NEAR_DUPLICATE_LEAKAGE_RISK`, and every output must retain `paraphrase_verified=false` and `NOT_VERIFIED_NO_TEXT_REVIEW`.

## Required transition

```text
SPEC_V19_REVIEW
-> S0_STIMULUS_GROUP_POLICY_REVIEW (DONE by frozen SPEC)
-> S0_STIMULUS_ID (implement and verify)
-> S0_JOINT_SPLIT (READY, then stop)
```

Do not perform split construction, A selection, unit inference, null implementation, schema work, training, outcome reading or any Gate in run 010.
