# AI Project Entry Point

This file is mandatory for every new AI/Codex session. Repository state comes from files and physical evidence, never chat history.

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_4_2026-08-24.md` (version `v2.4`).

## Verified location

- Server: `song@10.244.144.87`
- Root: `/home/song/projects/trust_generative`
- Python: `/home/song/projects/trust_generative/.venv/bin/python`
- Remote/branch: `https://github.com/cb6e310/wip2` / `main`

## Source of truth

1. `guide/RC_HSG_Paper_Spec_v2_4_2026-08-24.md` (active version `v2.4`)
2. `PROJECT_STATE.yaml`
3. `HANDOFF.md`
4. `TASKS.yaml`
5. Current code, tests, artifacts, reports, and immutable runs

Sections 20-23 are authoritative for the RC-HSG scientific question, method, A interface, Gates,
task graph, and A policy. Sections 14-19 and run-011 artifacts remain
authoritative for physical data, identity, grouping, split, population, and
test-lock facts. Older SPECs and runs remain immutable provenance.

## Recovery sequence

Read the five sources above, `artifacts/backbone_a_policy.yaml`, `artifacts/backbone_a_contract.yaml`, runs 014-015, and
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

Run 014 validated the frozen clean-room spectral interface on a bounded
107-row outer-train panel and ledgered all 44 outer-train short rows as no-read.
CPU and conditional CUDA checks passed. The remaining 3,390 eligible
outer-train rows are unread, so this is not full admission or a performance
conclusion.

The early A-path leakage firewall passed through static code, committed metadata,
synthetic fixtures, and twelve in-memory mutation probes without opening production
HDF5 or reading new real values. `S0_A1_ADMISSION` is the sole READY and recommended
task, owned by `CODEX`; B_V9 remains active but does not block this resolver. Test
identities remain `LOCKED_UNTIL_ROUTE_LOCK`, and run 015 did not execute admission,
the later method leakage audit, training, any Gate, or test unlock.

## End-of-session contract

For state-changing work, update `PROJECT_STATE.yaml`, `TASKS.yaml`,
`HANDOFF.md`, `CODEX_NEXT_TASK.md`, affected artifacts, and one new immutable
run. Then run focused tests, validator, status command, `git diff --check`,
inspect the diff for sensitive or large content, and commit/push only validated
files.
