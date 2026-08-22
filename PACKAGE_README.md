# NC-HSG v1.7 iteration-6 handoff

Baseline: `wip2@bf958fe2fc543e6b5c465a9eed3c743d4b0d0aa7`  
Prepared: 2026-08-21

## Purpose

This package activates SPEC v1.7 and authorizes one bounded repository-only task: derive a 5,905-row ZuCo 2.0 NR analysis view and data card from committed schema-v3 evidence, while retaining the strict full-release diagnostic FAIL and unknown physical unit.

No real EEG needs to be reread. No unit inference, backbone selection, split, training, outcome access, download, or Gate is authorized.

## Files

- `guide/NC_HSG_Paper_Spec_v1_7_2026-08-21.md`: active scientific and governance contract.
- `artifacts/spec_review/nc_hsg_v17_post_push_review.md`: independent review of the pushed baseline and policy defect.
- `CODEX_NEXT_TASK.md`: exact executable Codex task.
- `PACKAGE_MANIFEST.sha256`: payload integrity manifest.

## Import rule

Verify `PACKAGE_MANIFEST.sha256` outside the repository, then copy only manifest-listed project files. `PACKAGE_README.md` and the manifest are package metadata; Codex may keep the repository's active `PACKAGE_README.md` synchronized to v1.7 as directed, but must not delete or rewrite historical SPECs, reviews, runs, or admission artifacts.
