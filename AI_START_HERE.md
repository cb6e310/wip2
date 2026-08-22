# AI Project Entry Point

This file is mandatory for every new AI/Codex session. Repository state comes from files and physical evidence, never chat history.

Active SPEC: `guide/NC_HSG_Paper_Spec_v1_7_2026-08-21.md` (version `v1.7`).

## Verified location

- Server: `song@10.244.144.87`
- Root: `/home/song/projects/trust_generative`
- Python: `/home/song/projects/trust_generative/.venv/bin/python`
- Remote/branch: `https://github.com/cb6e310/wip2` / `main`

## Source of truth

1. `guide/NC_HSG_Paper_Spec_v1_7_2026-08-21.md` (active version `v1.7`)
2. `PROJECT_STATE.yaml`
3. `HANDOFF.md`
4. `TASKS.yaml`
5. Current code, tests, artifacts, reports, and immutable runs

Older SPECs, runs 001-007, and schema-v1/v2/v3 admission artifacts are provenance only. Never import state, claims, routes, metrics, or DONE decisions from `trust_align` or example archives.

## Recovery sequence

Read the five sources above, then run:

```bash
.venv/bin/python scripts/check_project_state.py
.venv/bin/python scripts/project_status.py
```

Before changing files, record HEAD, branch, origin, and dirty state. If entry points and state disagree, report `STATE_SPEC_CONFLICT` and stop unless the current task explicitly authorizes repair.

## Current evidence boundary

Run 008 completed `SPEC_V17_REVIEW`, `S0_DATA_ADMISSION_POLICY_REPAIR`, and `S0_DATA_CARD` from committed schema-v3 artifacts without rereading real EEG. The source release retains strict diagnostic `FAIL`. The frozen analysis view separately passes with 5,905 admitted rows and a complete 377-row exclusion union: 367 nonfinite placeholders, 4 finite single-sample rows, and 6 additional finite-multisample event-unresolved rows. The four single-sample rows overlap the event-invalid set. YTL anomaly paths cover NR3, NR5, and NR6 with finite-multisample counts 1, 1, and 4.

Physical unit is `UNRESOLVED_RELEASE_NATIVE_AMPLITUDE`; no unit inference is authorized. This blocks only unit-sensitive A/frontend work. `S0_STIMULUS_ID` is the sole READY and recommended task. Do not treat analysis-view PASS as full-release, backbone, training, or Gate admission.

## End-of-session contract

For state-changing work, update `PROJECT_STATE.yaml`, `TASKS.yaml`, `HANDOFF.md`, `CODEX_NEXT_TASK.md`, affected artifacts, and one new immutable run. Then run focused tests, validator, status command, `git diff --check`, inspect the diff for sensitive or large content, and commit/push only validated files.

