# AI Project Entry Point

This file is mandatory for every new AI/Codex session. Repository state comes from files and physical evidence, never chat history.

Active SPEC: `guide/RC_HSG_Paper_Spec_v2_8_2026-08-24.md` (version `v2.8`).

## Verified location

- Server: `song@10.244.144.87`
- Root: `/home/song/projects/trust_generative`
- Python: `/home/song/projects/trust_generative/.venv/bin/python`
- Remote/branch: `https://github.com/cb6e310/wip2` / `main`

## Source of truth

1. `guide/RC_HSG_Paper_Spec_v2_8_2026-08-24.md` (active version `v2.8`)
2. `PROJECT_STATE.yaml`
3. `HANDOFF.md`
4. `TASKS.yaml`
5. Current code, tests, artifacts, reports, and immutable runs

Sections 20-27 are authoritative for the RC-HSG scientific question, method, A interface, Gates,
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

Run 019 completed the synthetic-only N2 common-phase sampler. The transform uses one
phase increment per positive frequency across all 105 channels, fixes DC/even Nyquist,
and transforms only each valid unpadded prefix. The analytic grid and 199-replicate replay
pass the frozen PSD, covariance, mean, cross-spectrum, mask, replay, and safety contract.

`GATE_R0` is the sole READY and recommended task, owned by `CHATGPT_OR_AUTHOR`, but
requires a new exact real outcome-blind audit contract. B_V9 is closed; B_V4 remains active
without blocking this resolver. Test identities remain `LOCKED_UNTIL_ROUTE_LOCK`; run 019
read zero real EEG/text/outcome/test content and did not load A1/frontend, generate a score
or p-value, train, execute any Gate, lock the route, or unlock test. Synthetic PASS does not
admit N2 as the primary reference.

## End-of-session contract

For state-changing work, update `PROJECT_STATE.yaml`, `TASKS.yaml`,
`HANDOFF.md`, `CODEX_NEXT_TASK.md`, affected artifacts, and one new immutable
run. Then run focused tests, validator, status command, `git diff --check`,
inspect the diff for sensitive or large content, and commit/push only validated
files.
