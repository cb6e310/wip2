# Run 016: full outer-train A1 admission

Date: 2026-08-24

## Authorization and baseline

- Task chain: `SPEC_V25_REVIEW -> S0_A1_ADMISSION -> S0_N1_BLOCK_FEASIBILITY READY -> STOP`.
- Repository baseline: clean `main@07c37b3bb77c3cf396116078b64687dcebb9ee03`, equal to `origin/main` after fetch.
- Package SHA256: `00645ea626b8c3df58b12a1ce31bd82997c3809a06987e427077ddc8c38f61dc`.
- The package was safely extracted outside the repository and every entry in `PACKAGE_MANIFEST.sha256` passed.
- Only the three paths listed by `PROJECT_IMPORT_MANIFEST.txt` were imported: the v2.5 SPEC, its review, and the root next-task instruction.
- Imported SPEC SHA256: `b225a1528a05d2c0b83b31114347cd045ccc5b9a746df1ae6f06241d976b55ae`.
- Imported review SHA256: `4d5f5bc95c53d86abf809544d406a1faf7075dbb5a452b7ce2722de95b2638ec`.

## Zero-read preflight

The production metadata preflight completed before any new array dereference. A patched zero-read check rejected every attempted HDF5 open and reproduced the frozen scope:

- 3,541 outer-train rows: 3,497 eligible and 44 short forced-L0 rows.
- 35,745 cumulative full windows.
- 107 run-014 panel rows and 1,452 panel windows reused without reread.
- 3,390 remaining rows and 34,293 windows selected for run 016.
- Remaining role rows/windows: train-fit 2,742/28,411; inner-val 648/5,882.
- 18 subjects, 18 source files, eligible sample range 513 through 18,436, maximum 72 windows.
- CUDA was available before the scan.

## Single production scan

Exactly one planned production scan was started and completed. It used `CUDA_0_SELECTED`, the frozen audited loader, deterministic order `(window_count, raw_samples, subject, slot, occurrence_id)`, maximum batch size four, `NativeSpectralA1(20260824).eval()`, and inference-only execution.

The scan read each of the 3,390 remaining distinct eligible arrays exactly once. It did not reread the 107 run-014 panel arrays and did not dereference any short, calibration, or test array. The actual run-016 source dtype count was `float64=3390`. Every scanned row passed source identity, shape, finite-input, expected-window, mask, finite-output, masked-pool, eval-mode, null-gradient, and parameter-immutability checks.

The scan serialized one in-memory result to two repository-external verification roots and the canonical root. All three files were byte-identical across all three roots; no second scan was used for determinism.

## Canonical outputs

- `scripts/admit_a1_outer_train.py`: `6ce68ad66e8fdc51224d3723054ca01b0b13b558d9d6e81932e6e3b6636a8795`
- `tests/test_admit_a1_outer_train.py`: `1ff787eb830b4dae8bbd332d6cb8af03d6879410ce6ed22713ae1e17b818fd25`
- `artifacts/a1_outer_train_admission_v1.jsonl`: `b3c1b4e11855ef4c51c5bd0c2c0009f8a24e390c511d97118c48082fc7febfd5`
- `artifacts/a1_outer_train_admission_freeze.yaml`: `e973fbbe841a47f027cbf0f8a8ad65e66d106d675e8ed838dd0daf4a08dcab12`
- `reports/a1_admission.md`: `c2dc97d886d31fdc93e82778981fdf3a2dc1fd382c850d4035fdba3487513eac`

The canonical ledger has 3,541 rows in exact key order: 3,390 run-016 streaming PASS rows, 107 reused run-014 PASS rows, and 44 short no-read rows. Cumulative admission is 3,497 eligible rows and 35,745 windows.

## Validation

The server project environment produced these actual results, all with zero skips:

- Admission synthetic-HDF5 tests: 13/13 PASS.
- Frontend synthetic-HDF5 tests: 13/13 PASS.
- Native spectral tests: 12/12 PASS.
- A-interface builder tests: 8/8 PASS.
- A-path leakage audit tests: 20/20 PASS.
- Joint-split tests: 13/13 PASS.
- Project-memory tests: 55/55 PASS.
- Full repository discovery: 198/198 PASS.

The state validator reported `PROJECT STATE VALID | tasks=72 | done=37`; the status renderer showed the sole READY task and owner required below. Output hash checks and `git diff --check` also passed.

## State transition and limits

- Final task state: 72 tasks, 37 DONE, 8 SKIPPED, 26 BLOCKED, one READY.
- Sole READY/recommended task: `S0_N1_BLOCK_FEASIBILITY`, owner `CHATGPT_OR_AUTHOR`.
- `B_V9_A_FULL_OUTER_TRAIN_ADMISSION_PENDING` is closed by `S0_A1_ADMISSION`; the outer-train-only, short-forced-L0, unresolved-unit, unread-cal/test, and no-performance limitations remain.
- `B_V4_NULL_CONTRACT_UNVERIFIED` remains active but does not block its resolver.
- Route remains unlocked and test remains `LOCKED_UNTIL_ROUTE_LOCK`.

No stimulus text, semantic/calibration/test outcome, prediction, metric, or historical result was read. No training, backward pass, optimizer, checkpoint, representation/value cache, amplitude/power/frequency summary, unit inference, N1/N2 work, method leakage audit, Gate, route lock, or test unlock was performed. Run 016 stops here; `S0_N1_BLOCK_FEASIBILITY` requires a new ChatGPT/author-frozen contract.
