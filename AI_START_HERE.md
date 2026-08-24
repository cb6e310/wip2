# AI Project Entry Point

This file is mandatory for every new AI/Codex session. Repository state comes from files and physical evidence, never chat history.

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_6_2026-08-24.md` (version `v2.6`).

## Verified location

- Server: `song@10.244.144.87`
- Root: `/home/song/projects/trust_generative`
- Python: `/home/song/projects/trust_generative/.venv/bin/python`
- Remote/branch: `https://github.com/cb6e310/wip2` / `main`

## Source of truth

1. `guide/RC_HSG_Paper_Spec_v2_6_2026-08-24.md` (active version `v2.6`)
2. `PROJECT_STATE.yaml`
3. `HANDOFF.md`
4. `TASKS.yaml`
5. Current code, tests, artifacts, reports, and immutable runs

Sections 20-25 are authoritative for the RC-HSG scientific question, method, A interface, Gates,
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

Run 017 completed the outcome-blind outer-train N1 block-feasibility audit. Exactly
3,497 eligible arrays were read once on CPU through the audited loader and exact A1
spectral tokenizer; 44 short arrays and all calibration/test arrays remained unread.
Structural checks passed, 199/199 joint mapping hashes were unique, and the minimum
subject-role population coverage was 0.777777777778. The frozen decision is
`DEGRADED_COVERAGE`, so N1 is ineligible as the primary fallback.

`S0_N1_SAMPLER` is the sole READY and recommended task, owned by
`CHATGPT_OR_AUTHOR`, only for mechanism/robustness under a new exact contract. B_V9
is closed; B_V4 remains active without blocking this resolver. Test identities remain
`LOCKED_UNTIL_ROUTE_LOCK`; run 017 did not implement a sampler, train, run the method
leakage audit, execute any Gate, lock the route, or unlock test.

## End-of-session contract

For state-changing work, update `PROJECT_STATE.yaml`, `TASKS.yaml`,
`HANDOFF.md`, `CODEX_NEXT_TASK.md`, affected artifacts, and one new immutable
run. Then run focused tests, validator, status command, `git diff --check`,
inspect the diff for sensitive or large content, and commit/push only validated
files.
