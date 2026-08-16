# Current Handoff

## Current stage

Stage 0 remains blocked after the completed v1.3 governance hardening and
outcome-blind physical input discovery audit. No scientific task is READY.

## Completed this run

- Activated `guide/NC_HSG_Paper_Spec_v1_3_2026-08-16.md` without changing the
  v1.2 scientific thresholds, Gates, routes, data order, or backbone order.
- Hardened generic SPEC/version, bidirectional route-lock, DONE evidence,
  run/state, reviewed-commit, snapshot-provenance, and stale-next-task checks.
- Added a deterministic metadata-first scanner and focused tests.
- Scanned only `/home/song/projects/trust_generative` and
  `/home/song/projects/trust_align`; reference results/runs/reports/artifacts
  were metadata-only and unread.
- Recorded local ZuCo 2.0 NR/TSR candidates, trust_align A1/LaBraM candidates,
  and official NeuroLM-B+VQ frozen metadata without selecting primary A.
- Verified the official NeuroLM code commit/license and Hugging Face revision,
  sizes and LFS SHA256 values without downloading weights.

## Admission decisions

- ZuCo 2.0 task 1 NR: `FOUND_LICENSE_UNVERIFIED`; strict data-card admission
  fails because no local license/terms/author authorization or channel-name and
  coordinate evidence exists, with additional sampling/unit/reference/event
  gaps. No data card was generated.
- ZuCo 2.0 task 2 TSR: same classification, retained only for later robustness.
- trust_align A1: `STATICALLY_COMPATIBLE_UNVALIDATED`.
- trust_align LaBraM and official NeuroLM-B+VQ: `FOUND_INCOMPLETE`.
- ZuCo-NeuroLM compatibility: `UNVERIFIED`; no adapter or mapping was written.

## Required next action

`NO_READY_TASK`. The user must provide the specific license, terms, or
author-authorization file applicable to the audited local ZuCo 2.0 release and
the matching physical channel-name/coordinate or montage metadata. Then rerun
targeted admission only. Keep `S0_A_INTERFACE` BLOCKED until a later
outcome-blind author/ChatGPT decision selects exactly one A.

## Safety boundary

Do not read historical results, metrics, predictions, stimulus/label values,
deserialize checkpoints/pickles, download data/weights, implement scientific
algorithms, train, or run any Gate.
