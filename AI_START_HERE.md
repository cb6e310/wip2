# AI Project Entry Point

This file is mandatory for every new AI/Codex session. Repository state comes from files and physical evidence, never chat history.

Active SPEC: `guide/NC_HSG_Paper_Spec_v1_6_2026-08-16.md` (version `v1.6`).

## Verified location

- Server: `song@10.244.144.87`
- Root: `/home/song/projects/trust_generative`
- Python: `/home/song/projects/trust_generative/.venv/bin/python`
- Remote/branch: `https://github.com/cb6e310/wip2` / `main`

## Source of truth

1. `guide/NC_HSG_Paper_Spec_v1_6_2026-08-16.md` (active version `v1.6`)
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

Runs 005-006 and schema v1/v2 artifacts remain immutable history. Run 007 completed `SPEC_V16_REVIEW` and `S0_ZUCO2_NR_SEGMENT_CORRESPONDENCE`; schema v3 supersedes only the active admission conclusion. All subjects retain 303 ordinary plus 46 control occurrences. The unique finish-inclusive convention gives 5,905 exact comparable segments and 6 event-unresolved valid cells in two YTL blocks. Summary layer/reference are bound by exact identity; both current-array units and the strict YTL event contract remain unresolved. Conditions are `PASS, PASS, FAIL, PASS, PASS, PASS`; `S0_DATA_CARD` is BLOCKED, no scientific task is READY, and no data card exists.

Do not infer unresolved unit/layer/reference semantics, repeat broad discovery, select primary A, read historical/test outcomes, deserialize unsafe objects, download data/weights, train, or run a Gate.

## End-of-session contract

For state-changing work, update `PROJECT_STATE.yaml`, `TASKS.yaml`, `HANDOFF.md`, `CODEX_NEXT_TASK.md`, the affected artifacts, and one new immutable run. Then run focused tests, validator, status command, `git diff --check`, inspect the diff for sensitive or large content, and commit/push only validated files.
