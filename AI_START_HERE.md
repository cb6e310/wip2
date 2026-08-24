# AI Project Entry Point

This file is mandatory for every new AI/Codex session. Repository state comes from files and physical evidence, never chat history.

Active SPEC: `guide/NC_HSG_Paper_Spec_v1_9_2026-08-23.md` (version `v1.9`).

## Verified location

- Server: `song@10.244.144.87`
- Root: `/home/song/projects/trust_generative`
- Python: `/home/song/projects/trust_generative/.venv/bin/python`
- Remote/branch: `https://github.com/cb6e310/wip2` / `main`

## Source of truth

1. `guide/NC_HSG_Paper_Spec_v1_9_2026-08-23.md` (active version `v1.9`)
2. `PROJECT_STATE.yaml`
3. `HANDOFF.md`
4. `TASKS.yaml`
5. Current code, tests, artifacts, reports, and immutable runs

Older SPECs, runs 001-009, and schema-v1/v2/v3 admission artifacts are provenance only. Never import state, claims, routes, metrics, or DONE decisions from `trust_align` or example archives.

## Recovery sequence

Read the five sources above, then run:

```bash
.venv/bin/python scripts/check_project_state.py
.venv/bin/python scripts/project_status.py
```

Before changing files, record HEAD, branch, origin, and dirty state. If entry points and state disagree, report `STATE_SPEC_CONFLICT` and stop unless the current task explicitly authorizes repair.

## Current evidence boundary

Run 010 completed `SPEC_V19_REVIEW`, `S0_STIMULUS_GROUP_POLICY_REVIEW`, and `S0_STIMULUS_ID`. The frozen `NC_HSG_STIMULUS_GROUP_POLICY_V1` applies only the committed six-decimal candidate scores. It records two inter-identity edges, nine unjoined broad candidates, and 342 deterministic groups covering all 349 occurrences exactly once. Group kinds are 335 `SINGLETON`, five `EXACT_DUPLICATE_OCCURRENCES`, and two `NEAR_DUPLICATE_LEAKAGE_RISK`; no group exceeds two occurrences. Stimulus text was not emitted or reviewed, so every candidate and group remains explicitly not paraphrase-verified. Document and paragraph metadata remain unavailable.

Physical unit remains `UNRESOLVED_RELEASE_NATIVE_AMPLITUDE`; no unit inference is authorized. `S0_JOINT_SPLIT` is the sole READY and recommended task, but run 010 intentionally stops before constructing a split. Wait for the next exact ChatGPT or author split instruction. Do not alter grouping thresholds, infer paraphrases, select a backbone, train, or run any Gate.

## End-of-session contract

For state-changing work, update `PROJECT_STATE.yaml`, `TASKS.yaml`, `HANDOFF.md`, `CODEX_NEXT_TASK.md`, affected artifacts, and one new immutable run. Then run focused tests, validator, status command, `git diff --check`, inspect the diff for sensitive or large content, and commit/push only validated files.
