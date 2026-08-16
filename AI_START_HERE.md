# AI Project Entry Point

This file is mandatory for every new AI/Codex session. Repository state comes from files and physical evidence, never chat history.

Active SPEC: `guide/NC_HSG_Paper_Spec_v1_5_2026-08-16.md` (version `v1.5`).

## Verified location

- Server: `song@10.244.144.87`
- Root: `/home/song/projects/trust_generative`
- Python: `/home/song/projects/trust_generative/.venv/bin/python`
- Remote/branch: `https://github.com/cb6e310/wip2` / `main`

## Source of truth

1. `guide/NC_HSG_Paper_Spec_v1_5_2026-08-16.md` (active version `v1.5`)
2. `PROJECT_STATE.yaml`
3. `HANDOFF.md`
4. `TASKS.yaml`
5. Current code, tests, artifacts, reports, and immutable runs

Older SPECs and runs are provenance only. Never import state, claims, routes, metrics, or DONE decisions from `trust_align` or example archives.

## Recovery sequence

Read the five sources above, then run:

```bash
.venv/bin/python scripts/check_project_state.py
.venv/bin/python scripts/project_status.py
```

Before changing files, record HEAD, branch, origin, and dirty state. If entry points and state disagree, report `STATE_SPEC_CONFLICT` and stop unless the current task explicitly authorizes repair.

## Current evidence boundary

Run 005 remains immutable history. Run 006 completed `SPEC_V15_REVIEW` and `S0_ZUCO2_NR_ADMISSION_REPAIR`; schema v2 supersedes only run 005's active admission conclusion. It classifies all 6,282 cells as 5,911 valid finite multisample, 367 nonfinite placeholders, and 4 finite single-sample exclusions, and proves 6,282/6,282 ordered block occurrences. Conditions are `PASS, PASS, FAIL, PASS, PASS, PASS`: event structure passes but event semantics fails in two YTL blocks, and summary layer/reference plus both stored-array units remain unresolved. Therefore `S0_DATA_CARD` is BLOCKED, no scientific task is READY, and no data card exists.

Do not infer unresolved unit/layer/reference semantics, repeat broad discovery, select primary A, read historical/test outcomes, deserialize unsafe objects, download data/weights, train, or run a Gate.

## End-of-session contract

For state-changing work, update `PROJECT_STATE.yaml`, `TASKS.yaml`, `HANDOFF.md`, `CODEX_NEXT_TASK.md`, the affected artifacts, and one new immutable run. Then run focused tests, validator, status command, `git diff --check`, inspect the diff for sensitive or large content, and commit/push only validated files.
