# Run 018: metadata-only N1 mechanism sampler

Date: 2026-08-24

## Authorization and baseline

- Task chain: `SPEC_V27_REVIEW -> S0_N1_SAMPLER -> S0_N2_SAMPLER READY -> STOP`.
- Repository: `/home/song/projects/trust_generative`, branch `main`.
- Fetched clean baseline: `HEAD=origin/main=082ed4f72f1b8bbc18096a5f0caea2075b2783c4`.
- Baseline state: 73 tasks, 39 DONE, 8 SKIPPED, 25 BLOCKED, sole READY `S0_N1_SAMPLER`, owner `CHATGPT_OR_AUTHOR`; B_V4 active, route unlocked, test locked.
- Package ZIP SHA256: `934d7bb625b6a5183d251ae0d7b5255053adaebef17a0883394a371f3f5b5c24`.
- Safe repository-external extraction and every `PACKAGE_MANIFEST.sha256` entry passed.
- Only the three `PROJECT_IMPORT_MANIFEST.txt` files were imported:
  - `guide/RC_HSG_Paper_Spec_v2_7_2026-08-24.md`: `80d613bcb1eb5e3d3948f71f225ffcab5be52c6593fb141fdf410eb0bd753951`
  - `artifacts/spec_review/rc_hsg_v27_n1_mechanism_sampler_review.md`: `bd245a03d4244f18381b1008ddbd0504cf7ea28f19407cb254747c20150894eb`
  - package-source `CODEX_NEXT_TASK.md`: `667b36d04a5e91fd314bf44b1e7ce0a145ed0e9a45286c36c56c8eb8c9d2b0e7`
- The canonical root `CODEX_NEXT_TASK.md` was then mechanically updated to the required stop state and has SHA256 `f14ad7b08b3cfe2b590bfb3b1357e0ecde3922a80c41b6ad4236bfc5549189cb`.

## Implementation

- Package: `src/rc_hsg/references/__init__.py`, SHA256 `fc18441cc3803ea12e6638abc60e929319fb14f31c6605e5232e5dfdbf4190d9`.
- Sampler: `src/rc_hsg/references/n1_joint_permutation.py`, SHA256 `888c6965c89c007e7edb4d0bcf513a8cdcaf4201dff6b05a3f7bf75bf7a94ca6`.
- Builder: `scripts/build_n1_sampler_contract.py`, SHA256 `6b65480881bb1e8988bd1c63c2aa50780f9279e3e0378fa25aed691d5cd0706b`.
- Sampler tests: `tests/test_n1_joint_permutation.py`, SHA256 `c0b65d1263dc8e887c4b90b850b3708c6bd1d68244b5887705b5c290fb5633eb`.
- Builder tests: `tests/test_build_n1_sampler_contract.py`, SHA256 `9ade824954aa897d29dfbbe045b3d47bceb0109ff4947b5db51a680996f45e4b`.
- The implementation uses the frozen SHA256 hash-sort law directly. It does not use RNG, `random`, Python `hash()`, the feasibility production script, A1/frontend code, or any EEG reader.
- Inputs are restricted to the committed run-017 assignment metadata and fixed-hash contract files. Assignment hash, schema, row key, role, block, status, count, and symlink/path boundaries fail closed.
- The sampler retains fixed points and permits neither adjacent-block borrowing nor cross-role/subject/session/length/power mapping.
- No recipient-donor relation is persisted.

## Sampler parity and selection boundary

- Assignment scope: 3,541 outer-train rows, 3,481 evaluable rows, 180 evaluable blocks, 60 exclusions.
- Exclusions: 44 short forced-L0, 12 singleton, and 4 power-edge-unavailable rows.
- All 199 replicates exactly match the run-017 frozen joint mapping hash and fixed-point count.
- Joint mapping hashes: 199/199 unique.
- Fixed points: 35,529 total; per-replicate range 145-214; retained by policy.
- Bijection violations: 0. Cross-block violations: 0.
- Synthetic selection-aware tests call the same complete `select_then_score` callback for real and pseudo-real observations, each in canonical 3,481-recipient order.
- Tests prove that donor source values can change the selected winner and that every pseudo source recomputes its L1-L2-L3 parent-consistent path, candidate, and score.
- No real-selected candidate, winner, path, or score is reused. No candidate-specific p-value shortcut exists, and no paper p-value is computed.

## Canonical outputs

- `artifacts/nulls/n1_contract.yaml`: `4fee63f743936db06eea41164f85f67228785872d3fca2098e657b1dc0383729`
- `artifacts/nulls/n1_permutation_manifest_v1.jsonl`: `b7e68368799be446af60dcec029458e4e769f6605c1c56c032b76fb069f38c06`
- `reports/n1_selfcheck.md`: `53fdb1a08a8f9cc7363a03ddf600ed221eaee85b94744c4ca000e1099cf2943e`

The canonical build and both repository-external verification builds are byte-identical for all three outputs. The manifest contains exactly 199 summary rows and no block, recipient, donor, or mapping relation.

## Validation

Using `/home/song/projects/trust_generative/.venv/bin/python` in a clean temporary clone of the exact baseline plus the run-018 overlay:

- N1 joint-permutation tests: 9/9 PASS.
- N1 sampler builder tests: 9/9 PASS.
- Run-017 N1 block-feasibility regression tests: 17/17 PASS.
- Project-memory/state tests: 61/61 PASS.
- Full repository discovery: 239/239 PASS, 0 skipped.
- `scripts/check_project_state.py`: PASS, `tasks=74`, `done=41`.
- `scripts/project_status.py`: PASS, sole READY/recommended `S0_N2_SAMPLER`.
- `git diff --check`: PASS.

## Safety and final state

- Production `.mat`, `.h5`, and `.hdf5` opens: 0.
- Production EEG, short, calibration, and test array reads: 0.
- Text, semantic outcome, prediction, metric, and test identity reads: 0.
- Frontend/tokenizer/A1 loads: 0.
- Proxy, token, embedding, waveform, donor value, recipient-donor mapping, candidate, reference score, and p-value persistence: 0.
- No training, N2 implementation, Gate execution, route lock, test unlock, or historical artifact change occurred.
- Final task state: 74 total, 41 DONE, 8 SKIPPED, 24 BLOCKED, 1 READY.
- `S0_N1_SAMPLER=DONE`; sole READY/recommended task is `S0_N2_SAMPLER`, owner `CHATGPT_OR_AUTHOR`.
- B_V4 remains active and does not block its N2 resolver. Every Gate remains BLOCKED with null outcome.
- Route remains unlocked. Test remains `LOCKED_UNTIL_ROUTE_LOCK`.
- Repository status: `RC_HSG_V27_N1_MECHANISM_SAMPLER_IMPLEMENTED_N2_PENDING`.

Run 018 stops before N2, Gate R0, schema/candidate/reference work, training, calibration, or test work.
