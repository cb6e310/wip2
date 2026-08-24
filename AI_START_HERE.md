# AI Project Entry Point

This file is mandatory for every new AI/Codex session. Repository state comes from files and physical evidence, never chat history.

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_5_2026-08-24.md` (version `v2.5`).

## Verified location

- Server: `song@10.244.144.87`
- Root: `/home/song/projects/trust_generative`
- Python: `/home/song/projects/trust_generative/.venv/bin/python`
- Remote/branch: `https://github.com/cb6e310/wip2` / `main`

## Source of truth

1. `guide/RC_HSG_Paper_Spec_v2_5_2026-08-24.md` (active version `v2.5`)
2. `PROJECT_STATE.yaml`
3. `HANDOFF.md`
4. `TASKS.yaml`
5. Current code, tests, artifacts, reports, and immutable runs

Sections 20-24 are authoritative for the RC-HSG scientific question, method, A interface, Gates,
task graph, and A policy. Sections 14-19 and run-011 artifacts remain
authoritative for physical data, identity, grouping, split, population, and
test-lock facts. Older SPECs and runs remain immutable provenance.

## Recovery sequence

Read the five sources above, `artifacts/backbone_a_policy.yaml`, `artifacts/backbone_a_contract.yaml`, runs 014-016, and
the committed split/population manifests, then run:

```bash
.venv/bin/python scripts/check_project_state.py
.venv/bin/python scripts/project_status.py
```

Before changing files, record HEAD, branch, origin, and dirty state. If entry
points, state, task graph, A policy, or committed split artifacts disagree,
report `STATE_SPEC_CONFLICT` and stop unless the current task explicitly
authorizes repair.

## Current evidence boundary

Run 016 completed full outer-train A1 admission. It reused the 107-row run-014
panel evidence without rereading it and scanned the remaining 3,390 eligible
rows once through the audited loader and frozen frontend. The cumulative ledger
covers 3,497 eligible rows and 35,745 windows; all 44 short rows remain no-read
forced L0. This is input/frontend admission, not representation quality or a
performance conclusion.

`S0_N1_BLOCK_FEASIBILITY` is the sole READY and recommended task, owned by
`CHATGPT_OR_AUTHOR`. B_V9 is closed; B_V4 remains active without blocking this
resolver. Test identities remain `LOCKED_UNTIL_ROUTE_LOCK`; run 016 did not
execute power binning, N1/N2, training, method leakage audit, any Gate, or test unlock.

## End-of-session contract

For state-changing work, update `PROJECT_STATE.yaml`, `TASKS.yaml`,
`HANDOFF.md`, `CODEX_NEXT_TASK.md`, affected artifacts, and one new immutable
run. Then run focused tests, validator, status command, `git diff --check`,
inspect the diff for sensitive or large content, and commit/push only validated
files.
