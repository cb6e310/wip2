# NC-HSG Iteration 4 Handoff Package

Purpose: update the project from verified remote state
`wip2@d6751eadd96b2f651e5dbd1bfd5366679688ce4d` to SPEC v1.5 and repair the
ZuCo 2.0 NR targeted-admission predicates.

This is a delta package, not a replacement repository. Verify
`PACKAGE_MANIFEST.sha256`, import only manifest-listed files into the existing
clean checkout, and execute `CODEX_NEXT_TASK.md`.

The package contains no EEG, stimulus text, checkpoint, result, scientific
model code, or claim that the dataset is admitted. It preserves run 005 as
historical evidence and freezes a bounded correction for invalid/missing EEG
cells, exact block occurrence, event semantics, and storage-unit/layer binding.

Contents:

- `guide/NC_HSG_Paper_Spec_v1_5_2026-08-16.md`: next active SPEC.
- `artifacts/spec_review/nc_hsg_v15_post_push_review.md`: independent review.
- `CODEX_NEXT_TASK.md`: exact executable Codex task.
- `PACKAGE_MANIFEST.sha256`: integrity allowlist.

Execution result: package integrity passed and SPEC v1.5 was activated at
baseline `d6751eadd96b2f651e5dbd1bfd5366679688ce4d`. Run 006 generated the
schema-v2 targeted evidence. Admission remains FAIL on event semantics,
summary layer/reference, and preprocessed/summary unit bindings, so no data
card or downstream scientific task was created.
