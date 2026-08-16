# Run 004 — Governance Hardening and Input Discovery

Date: 2026-08-16  
Mode: outcome-blind governance and physical-input metadata audit  
Baseline commit: `1b836fe56970d262f4e8f3ae8262fd0abb670dbe`  
Final commit: the immutable Git commit containing this run record; exact hash is reported after commit/push because a commit cannot contain its own SHA-1  
Delivery package SHA256: `66d13c23ff7a51cd721a7f099c0ab631f936513449ba699b096c603132bcc4f6`

## Baseline and package

- Branch and local/remote baseline: `main` at the expected baseline.
- Baseline worktree was clean before importing the four manifest payloads.
- Existing governance tests: 19/19 PASS.
- Existing validator: `PROJECT STATE VALID | tasks=35 | done=4`.
- Existing status: Stage 0 BLOCKED, no READY task.
- ZIP safety: no absolute/traversal/symlink/special/duplicate/case-conflict or
  unmanifested payload; all four manifest hashes matched.
- Imported only `CODEX_NEXT_TASK.md`, `PACKAGE_README.md`, the v1.3 SPEC, and
  the v1.3 post-push review. v1.2 remains historical.

## Governance defects repaired

- Replaced v1.2 hard-coding with generic version/path/header agreement.
- Added bidirectional route-lock value and run-record enforcement.
- Required real safe repository paths as acceptance evidence for every DONE task.
- Bound `updated_by_run` and `last_completed_task.completed_by_run` to `last_run`.
- Required a lowercase 40-hex reviewed baseline commit.
- Added generated/updated run and evidence-commit provenance to mutable snapshots.
- Added stale `CODEX_NEXT_TASK.md` protection.
- Added the v1.3 review, governance hardening, and input discovery tasks.

## Authorized scan

Roots scanned exactly:

- `/home/song/projects/trust_generative`
- `/home/song/projects/trust_align`

Exclusions: `.git`, `.venv`, caches, `node_modules`, temporary directories.
Reference-project `runs`, `reports`, `artifacts`, candidate/split ledgers,
Stage-0 output directories, result/output/log/W&B/prediction/eval paths were
metadata-only and not recursively opened. Data formats were metadata-only;
pickle/checkpoint formats were not deserialized.

Reference Git identity:

- root: `/home/song/projects/trust_align`
- remote: `https://github.com/cb6e310/wip.git`
- branch: `main`
- HEAD: `31164dc3d70b00fb383862f88b6404bd616db696`
- dirty paths: four modified governance files plus untracked v3.15/failure-
  diagnosis source, artifact, result and run paths; none were modified or read
  as historical-result content by this run.

## Physical findings

- Local ZuCo 2.0 NR: `FOUND_LICENSE_UNVERIFIED`; 18 summary files and safe
  header shape 349 per participant. No text or numeric array values read.
- Local ZuCo 2.0 TSR: `FOUND_LICENSE_UNVERIFIED`; 18 summary files and safe
  header shape 390 per participant; robustness only.
- No local dataset LICENSE/terms/author authorization and no channel-name or
  coordinate/montage file was found.
- trust_align A1: `STATICALLY_COMPATIBLE_UNVALIDATED`.
- trust_align LaBraM: `FOUND_INCOMPLETE`; checkpoint size 96,612,769 bytes,
  SHA256 `7c50583826afac76c4ab18f43d958df40496c8229accc09ed6a227c9bb57c37c`,
  content not deserialized.
- Official NeuroLM-B+VQ: `FOUND_INCOMPLETE`; frozen code commit and MIT license
  verified; Hugging Face revision/license, file sizes and LFS hashes match v1.3;
  no weight downloaded.
- ZuCo-NeuroLM compatibility: `UNVERIFIED`; license metadata compatible, all
  physical channel/unit/reference/event/adapter items remain unverified.

Unread historical paths include `/home/song/projects/trust_align/03_runs`,
`/home/song/projects/trust_align/04_results`, reference `runs`, `reports`, and
`artifacts`, plus scanner-classified result/output/log/W&B/prediction/eval
directories. `content_read: false` applies to these paths.

## Commands and exact results

- Safe reference contract tests:
  `cd /home/song/projects/trust_align/02_code && PYTHONPATH=src /home/song/projects/trust_generative/.venv/bin/python -m unittest tests.test_a1_contract tests.test_a3_contract`
  — 15 tests, 1.291 s, OK.
- Local scanner tests before remote use — 7 tests, OK, one Windows symlink test
  skipped because symlink creation was unavailable; the same test is expected
  to run on Linux in final validation.
- Final required governance/scanner tests, validator, status and diff check are
  recorded below.
- `.venv/bin/python -m unittest discover -s tests -p 'test_project_memory.py'`
  — 34 tests, 5.107 s, OK.
- `.venv/bin/python -m unittest discover -s tests -p 'test_audit_input_sources.py'`
  — 7 tests, 0.011 s, OK; Linux symlink boundary test executed.
- `.venv/bin/python scripts/check_project_state.py`
  — `PROJECT STATE VALID | tasks=38 | done=7`.
- `.venv/bin/python scripts/project_status.py`
  — Stage 0 BLOCKED, zero READY tasks, recommendation none.
- `git diff --check` — PASS with no output.

## State transitions

- `SPEC_V13_REVIEW`: DONE.
- `S0_GOVERNANCE_HARDENING`: READY to DONE.
- `S0_INPUT_DISCOVERY_AUDIT`: BLOCKED to READY to DONE.
- `S0_DATA_CARD`: remains BLOCKED; strict conditions 2, 3 and 5 are unmet.
- `S0_A_INTERFACE`: remains BLOCKED; candidate discovery does not select A.
- No scientific task changed to DONE or IN_PROGRESS.
- Recommended next task: null; `NO_READY_TASK`.
- Minimum user action: provide the applicable local ZuCo license/authorization
  file and matching physical channel-name/coordinate metadata.

## Files changed and artifacts

Governance/entry files, current task/state/handoff, active v1.3 SPEC/review,
validator/status tests, scanner/tests, three mutable snapshots, four admission
artifacts, this run, and the discovery report were added or updated. No old run
record, scientific source, data, checkpoint, result content or model code was
changed.

Artifact SHA256 values:

- `input_source_inventory.yaml`: `8cf4a50e24382118490eb51c8c3789afab095c589b1603ea26b6c0452fb65ec3`
- `data_source_candidates.yaml`: `7f8907f7e7956d47f7ced8e8bb4724c13372478a941b7875118c5714951abbbb`
- `backbone_source_candidates.yaml`: `37f22c45fe0c805ec757bea47e5ddeff0c441bf2f2ec55a1beda030045b7f865`
- `zuco_neurolm_compatibility.yaml`: `d49d75a58982eebc24ced29c5cd1bf5bc4f3de391eb404997a95bf4f32a36d0e`
- `input_discovery_audit.md`: `45858234818fc4c8087ead430cabef0909eeff52664bbe3aadabb3b7c3c9cc12`

## Safety declarations

- Historical result content read: NO
- Held-out/test metric content read: NO
- Stimulus/test text printed: NO
- Large data/checkpoint downloaded: NO
- Scientific implementation changed: NO
- Training/Gate run: NO
