# Run 019: synthetic-only N2 common-phase sampler

Date: 2026-08-24

## Authorization and baseline

- Task chain: `SPEC_V28_REVIEW -> S0_N2_SAMPLER -> GATE_R0 READY -> STOP`.
- Repository: `/home/song/projects/trust_generative`, branch `main`.
- Fetched clean baseline: `HEAD=origin/main=06e3e5f9b5c720bbb29074ca1cae1109add5b1b9`.
- Baseline state: 74 tasks, 41 DONE, 8 SKIPPED, 24 BLOCKED, sole READY `S0_N2_SAMPLER`.
- Package ZIP SHA256: `b07537cf3410d426a129db0b057ca1ee8c7f49177078bbcc5e0691feaef13202`.
- Safe repository-external extraction and every `PACKAGE_MANIFEST.sha256` entry passed.
- Only the three `PROJECT_IMPORT_MANIFEST.txt` files were imported:
  - `guide/RC_HSG_Paper_Spec_v2_8_2026-08-24.md`: `f718fc37875a6dac7c539260de054d9f9c52966905b1912cf193d573a0424f23`
  - `artifacts/spec_review/rc_hsg_v28_n2_common_phase_sampler_review.md`: `66edb1aca13e01f87d1a162b86254bbad87ce207ae208474f46a326e53948ea7`
  - package-source `CODEX_NEXT_TASK.md`: `d842bc2c640e87967e35ad1da66d19dfa35e50dc059938d58b754350920f81ab`
- The canonical root `CODEX_NEXT_TASK.md` was mechanically updated to the required stop state and has SHA256 `f37aa94c16c1b09b1980dba038100162804b7d9365b981191eb3db94e10caf23`.

## Implementation

- Package exports: `src/rc_hsg/references/__init__.py`, SHA256 `9e53c4a8acbe2e965eff422a17f29cb5fa0471a9113914da76c13a498882fc6d`.
- Sampler: `src/rc_hsg/references/n2_common_phase.py`, SHA256 `65fc0c3215a2b289c498e989795db74002642388ca64caa2fea93d7780a5aa7e`.
- Builder: `scripts/build_n2_sampler_contract.py`, SHA256 `baebfa04bf2381075786d9375e78a741ded32f157ea21da37885bc4001530252`.
- Sampler tests: `tests/test_n2_common_phase.py`, SHA256 `27b2d1e53123f3af1cd4b78a6fc77ae940afa3978baafa57bf8e99a3a7d157fe`.
- Builder tests: `tests/test_build_n2_sampler_contract.py`, SHA256 `3e052367fa95bfd6f3a5a9b5d720c9132dd7f7c55a6b57e9149cfa1c955f376e`.
- Policy ID: `RC_HSG_N2_MULTIVARIATE_COMMON_PHASE_FOURIER_V1`.
- The public API requires a CPU, contiguous, `torch.float32` tensor with 105 channels and a valid prefix of at least 500 samples. Stable error prefixes and the frozen result dataclass are implemented.
- Each valid prefix is transformed through NumPy float64 `rfft`/`irfft` and returned as float32. One SHA256-seeded PCG64 phase increment is shared by all 105 channels at each positive interior frequency. DC and even-length Nyquist bins remain fixed.
- Padding never enters the FFT, output tails are exact zero, masks are exact true-prefix/false-tail, inputs are not modified, and neither global RNG nor filesystem state is touched.

## Append-only run-018 provenance correction

- `artifacts/governance/run018_provenance_correction.yaml` records the run-018 value `667b36d04a5e91fd314bf44b1e7ce0a145ed0e9a45286c36c56c8eb8c9d2b0e7` and corrected value `667b8bc2af414673e09d9d2011446db502fbca305fb26e6c558bd0a762d51ef6`.
- The correction binds run-018 package ZIP SHA256 `934d7bb625b6a5183d251ae0d7b5255053adaebef17a0883394a371f3f5b5c24` and states `scientific_state_changed: false`.
- Run 018 and all historical specifications, reviews, artifacts, and reports remain unchanged.

## Synthetic replay and preservation evidence

- Fifteen frozen even/odd, length, waveform, and replicate cases were evaluated.
- Maximum stable global relative norms: PSD `3.631308340874624e-09`, covariance `2.5397669519814525e-09`, mean `5.521334759509954e-09`, and cross-spectrum `4.46085033176357e-09`; all are below `1e-6`.
- Amplitude KS/quantile shift, endpoint jump/slip, and waveform correlation are diagnostic-only and introduce no extra cutoff.
- Replicates 1-199 replay bitwise; all 199 seed hashes and all 199 output fingerprints are unique and finite.
- The two padded fixtures have valid lengths 513 and 501. Prefix parity, exact masks, exact-zero tails, and ignored nonfinite input tails all pass.
- Mutation tests reject independent-channel phases, rotating DC/Nyquist, and including padding in the FFT.

## Canonical outputs and determinism

- `artifacts/governance/run018_provenance_correction.yaml`: `1ec0274f6604df1fb2691ff67d4a4f03e1a60fc508a87796e01b5d81d5415e01`
- `artifacts/nulls/n2_contract.yaml`: `c2713dc4fbe989c1680e02e88c336541482bfcb9e828170b3a225d2466d1377d`
- `reports/n2_selfcheck.md`: `042fc06f0627d4b29ead30075bb003800b0305ceb7d67387bc3f3e9d2f15f13c`

The canonical build and two repository-external verification builds are byte-identical for all three outputs. Atomic-write, symlink, destination-boundary, and command-line failure checks pass.

## Validation

Using `/home/song/projects/trust_generative/.venv/bin/python` in a clean temporary clone of the exact baseline plus the run-019 overlay:

- N2 common-phase tests: 17/17 PASS.
- N2 contract-builder tests: 10/10 PASS.
- N1 joint-permutation regression tests: 9/9 PASS.
- N1 contract-builder regression tests: 9/9 PASS.
- Native-spectral regression tests: 12/12 PASS.
- Project-memory/state tests: 63/63 PASS.
- Full repository discovery: 268/268 PASS, 0 skipped.
- `scripts/check_project_state.py`: PASS, `tasks=75`, `done=43`.
- `scripts/project_status.py`: PASS, sole READY/recommended `GATE_R0`.
- `git diff --check`: PASS.

## Safety and final state

- Production `.mat`, `.h5`, and `.hdf5` opens: 0.
- Production outer-train, short, calibration, and test EEG reads: 0.
- Text, semantic label, outcome, prediction, historical metric, and test identity reads: 0.
- A1, frontend, encoder, and dataset-reader loads: 0.
- Embedding, reference score, candidate, donor value, recipient-donor relation, and p-value generation or persistence: 0.
- No training, classifier, Gate execution, route lock, test unlock, or historical artifact modification occurred.
- Final task state: 75 total, 43 DONE, 8 SKIPPED, 23 BLOCKED, 1 READY.
- `S0_N2_SAMPLER=DONE`; sole READY/recommended task is `GATE_R0`, owner `CHATGPT_OR_AUTHOR`.
- B_V4 remains active. Every Gate outcome remains null; `GATE_R0` is READY and all later Gates remain BLOCKED.
- Route remains unlocked. Test remains `LOCKED_UNTIL_ROUTE_LOCK`.
- Repository status: `RC_HSG_V28_N2_COMMON_PHASE_SAMPLER_IMPLEMENTED_GATE_R0_PENDING`.

Run 019 stops before Gate R0, schema/candidate/reference work, training, calibration, or test work.
