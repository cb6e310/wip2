# Current Handoff

## Current stage

Stage 0 is blocked at physical data and backbone admission.

## What was completed

- Installed the persistent project context, automatic `AGENTS.md` entry point,
  validator, deterministic status command, and focused governance tests.
- Initialized `main` for the previously empty `wip2` remote and preserved the
  two pre-existing server files.
- Audited the actual repository without reading held-out content.
- Recorded repository, environment, and SPEC-to-implementation inventories.

## What is not completed

- No dataset, license record, scientific source, backbone/checkpoint,
  dependency manifest, split, schema, null sampler, calibration method, Gate,
  training run, or scientific result is present or validated.
- No scientific task is READY.

## Active blockers

- `B_V1_DATA_NOT_PRESENT`: no authorized physical dataset location or license
  evidence was found.
- `B_V2_BACKBONE_NOT_PRESENT`: no scientific code, checkpoint, tensor contract,
  or license evidence was found.
- V3-V6 remain frozen downstream blockers exactly as recorded in
  `PROJECT_STATE.yaml`.

## Recommended next task

None is currently eligible. Resolve V1 by documenting/providing the authorized
dataset location and license evidence, and resolve V2 by documenting/providing
the intended backbone code/checkpoint source. Then rerun the validator so the
first admissible Stage-0 task can become `READY`.

## Do not do yet

Do not invent missing paths or contracts, implement scientific algorithms,
train, download data/checkpoints, read held-out metrics, or run any Gate/main
experiment.
