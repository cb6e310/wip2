# Run 003 — Synchronize dependencies from trust_align

- Date: 2026-08-16
- Task: `S0_ENVIRONMENT_SYNC`
- Baseline commit: `76504c6bef46664b9fb265cbdba544de9d37da99`
- Source environment: `/home/song/projects/trust_align/.venv`
- Target environment: `/home/song/projects/trust_generative/.venv`
- Evidence scope: environment only; no backbone, checkpoint, data, Gate, or
  scientific result admission

## Compatibility preflight

- Source Python: 3.12.3
- Target Python: 3.12.3
- Editable/local path dependencies: none
- Available disk before synchronization: 257GB

## Files changed

- `requirements-trust-align.lock.txt`
- `artifacts/governance/trust_align_dependency_sync.yaml`
- `artifacts/governance/environment_snapshot.yaml`
- `artifacts/governance/repository_inventory.yaml`
- `artifacts/governance/spec_implementation_matrix.yaml`
- `AI_START_HERE.md`
- `PROJECT_STATE.yaml`
- `TASKS.yaml`
- `HANDOFF.md`
- this run record

## Installation and verification

- Installed all 103 `pip freeze --all` entries at their exact source versions.
- Sorted source freeze SHA-256:
  `a206926b920df228f2697363a0edce925a6ecc6995fc9eb6e134399c70e6ff51`.
- Sorted target freeze SHA-256: identical.
- Lock SHA-256:
  `72a2a3274ef9516dba95a4f4022cacfba0e02d10445e1618da2a569f59381910`.
- `pip check`: no broken requirements.
- Key scientific imports: PASS.
- Torch: `2.13.0+cu130`; CUDA available; 4 devices detected.
- CUDA tensor smoke on device 0: PASS; device is RTX 4090.
- Final environment size: 3.5GB.

## State transition

- Added `S0_ENVIRONMENT_SYNC=DONE`.
- Updated V2 to distinguish an admitted package environment from the still
  missing backbone code, checkpoint, tensor/preprocessing contract, and
  license evidence.
- No scientific task changed status and no blocker was removed.

## Safety declarations

- Held-out/test metric content read: **NO**
- Scientific implementation changed: **NO**
- Training, model/checkpoint download, Gate, or experiment run: **NO**
