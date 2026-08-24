# AI Project Entry Point

This file is mandatory for every new AI/Codex session. Repository state comes from files and physical evidence, never chat history.

Active SPEC: `guide/NC_HSG_Paper_Spec_v2_0_2026-08-23.md` (version `v2.0`).

## Verified location

- Server: `song@10.244.144.87`
- Root: `/home/song/projects/trust_generative`
- Python: `/home/song/projects/trust_generative/.venv/bin/python`
- Remote/branch: `https://github.com/cb6e310/wip2` / `main`

## Source of truth

1. `guide/NC_HSG_Paper_Spec_v2_0_2026-08-23.md` (active version `v2.0`)
2. `PROJECT_STATE.yaml`
3. `HANDOFF.md`
4. `TASKS.yaml`
5. Current code, tests, artifacts, reports, and immutable runs

Older SPECs, runs 001-010, and schema-v1/v2/v3 admission artifacts are provenance only. Never import state, claims, routes, metrics, or DONE decisions from `trust_align` or example archives.

## Recovery sequence

Read the five sources above, then run:

```bash
.venv/bin/python scripts/check_project_state.py
.venv/bin/python scripts/project_status.py
```

Before changing files, record HEAD, branch, origin, and dirty state. If entry points and state disagree, report `STATE_SPEC_CONFLICT` and stop unless the current task explicitly authorizes repair.

## Current evidence boundary

Run 011 completed `SPEC_V20_REVIEW`, `S0_JOINT_SPLIT`, and `S0_GATE_A_POPULATION_E5`. The fixed integer algorithm assigns all 342 stimulus groups to 164 train-fit, 41 inner-val, 68 calibration, and 69 locked-test groups after exactly 25 swaps. Calibration has two frozen 34-group reserves after six swaps. Regime I covers all 5,905 admitted rows once; Regime II contains 18 LOSO folds that reuse the frozen group roles and prohibit held-out-subject adaptation. The population contract freezes equal-weight subject macro aggregation and the 10,000 x 18 paired subject-bootstrap index hash without computing any scientific statistic.

Physical unit remains `UNRESOLVED_RELEASE_NATIVE_AMPLITUDE`; no unit inference is authorized. `S0_A_POLICY_REVIEW` is the sole READY and recommended task and is owned by `CHATGPT_OR_AUTHOR`. Run 011 stops before selecting, downloading, or implementing backbone A. Test identities remain `LOCKED_UNTIL_ROUTE_LOCK`; do not read test values, execute the full leakage audit, train, or run any Gate.

## End-of-session contract

For state-changing work, update `PROJECT_STATE.yaml`, `TASKS.yaml`, `HANDOFF.md`, `CODEX_NEXT_TASK.md`, affected artifacts, and one new immutable run. Then run focused tests, validator, status command, `git diff --check`, inspect the diff for sensitive or large content, and commit/push only validated files.
