# AI Project Entry Point

This file is mandatory for every new AI/Codex session. Repository state comes from files and physical evidence, never chat history.

Active SPEC: `guide/NC_HSG_Paper_Spec_v1_8_2026-08-22.md` (version `v1.8`).

## Verified location

- Server: `song@10.244.144.87`
- Root: `/home/song/projects/trust_generative`
- Python: `/home/song/projects/trust_generative/.venv/bin/python`
- Remote/branch: `https://github.com/cb6e310/wip2` / `main`

## Source of truth

1. `guide/NC_HSG_Paper_Spec_v1_8_2026-08-22.md` (active version `v1.8`)
2. `PROJECT_STATE.yaml`
3. `HANDOFF.md`
4. `TASKS.yaml`
5. Current code, tests, artifacts, reports, and immutable runs

Older SPECs, runs 001-008, and schema-v1/v2/v3 admission artifacts are provenance only. Never import state, claims, routes, metrics, or DONE decisions from `trust_align` or example archives.

## Recovery sequence

Read the five sources above, then run:

```bash
.venv/bin/python scripts/check_project_state.py
.venv/bin/python scripts/project_status.py
```

Before changing files, record HEAD, branch, origin, and dirty state. If entry points and state disagree, report `STATE_SPEC_CONFLICT` and stop unless the current task explicitly authorizes repair.

## Current evidence boundary

Run 009 completed `SPEC_V18_REVIEW`, `S0_STIMULUS_SOURCE_BINDING`, and `S0_STIMULUS_SIMILARITY_DIAGNOSTIC`. Seven frozen material CSVs bind 370 rows, exclude 21 practice rows, and reproduce 349 task slots, 344 exact identities, and five exact duplicate groups. All 58,996 unordered identity pairs have text-free edit, token-Jaccard, and frozen all-MiniLM-L6-v2 cosine diagnostics. Document and paragraph metadata remain unavailable.

Physical unit remains `UNRESOLVED_RELEASE_NATIVE_AMPLITUDE`; no unit inference is authorized. `S0_STIMULUS_GROUP_POLICY_REVIEW` is the sole READY and recommended task, owned by ChatGPT or the author. `S0_STIMULUS_ID` is BLOCKED. Do not select a threshold, emit groups, construct a split, or treat the diagnostic as paraphrase verification, backbone, training, or Gate admission.

## End-of-session contract

For state-changing work, update `PROJECT_STATE.yaml`, `TASKS.yaml`, `HANDOFF.md`, `CODEX_NEXT_TASK.md`, affected artifacts, and one new immutable run. Then run focused tests, validator, status command, `git diff --check`, inspect the diff for sensitive or large content, and commit/push only validated files.
