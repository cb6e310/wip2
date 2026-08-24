# AI Project Entry Point

This file is mandatory for every new AI/Codex session. Repository state comes from files and physical evidence, never chat history.

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_1_2026-08-24.md` (version `v2.1`).

## Verified location

- Server: `song@10.244.144.87`
- Root: `/home/song/projects/trust_generative`
- Python: `/home/song/projects/trust_generative/.venv/bin/python`
- Remote/branch: `https://github.com/cb6e310/wip2` / `main`

## Source of truth

1. `guide/RC_HSG_Paper_Spec_v2_1_2026-08-24.md` (active version `v2.1`)
2. `PROJECT_STATE.yaml`
3. `HANDOFF.md`
4. `TASKS.yaml`
5. Current code, tests, artifacts, reports, and immutable runs

Section 20 is authoritative for the RC-HSG scientific question, method, Gates,
task graph, and A policy. Sections 14-19 and run-011 artifacts remain
authoritative for physical data, identity, grouping, split, population, and
test-lock facts. Older SPECs and runs remain immutable provenance.

## Recovery sequence

Read the five sources above, `artifacts/backbone_a_policy.yaml`, run 012, and
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

Run 012 activated RC-HSG v2.1 and materialized the author-frozen
`RC_HSG_NATIVE_SPECTRAL_A1_V1` policy. The policy is a project-native clean-room
spectral frontend trained from scratch, with no external source-code copy,
pretrained checkpoint, weight download, guessed physical unit, or channel
interpolation. This is a feasibility/control decision, not a performance
conclusion.

The frontend and tensor/admission checks are not implemented. `S0_A_INTERFACE`
is the sole READY and recommended task, owned by `CODEX`. Test identities remain
`LOCKED_UNTIL_ROUTE_LOCK`; no EEG value, semantic outcome, calibration/test
result, historical model metric, training result, or Gate outcome has been read
or produced.

## End-of-session contract

For state-changing work, update `PROJECT_STATE.yaml`, `TASKS.yaml`,
`HANDOFF.md`, `CODEX_NEXT_TASK.md`, affected artifacts, and one new immutable
run. Then run focused tests, validator, status command, `git diff --check`,
inspect the diff for sensitive or large content, and commit/push only validated
files.
