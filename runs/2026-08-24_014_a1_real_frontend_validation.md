# Run 014: Bounded A1 Real-Frontend Validation

Date: 2026-08-24  
Task: `SPEC_V23_REVIEW -> S0_A1_FRONTEND -> stop with S0_LEAKAGE_AUDIT READY`  
Baseline: `237788090dcb20e533f304f63ae8feb2f545fe0b` on clean `main`

## Baseline and package

A real `git fetch origin main` preceded all changes. The server repository
confirmed `main`, `HEAD=origin/main=237788090dcb20e533f304f63ae8feb2f545fe0b`,
and an empty porcelain status. Baseline recovery passed with 68 tasks, 31 DONE,
8 SKIPPED, 28 BLOCKED, sole READY `S0_A1_FRONTEND`, and test locked.

The handoff ZIP SHA256 was
`a77c66ef3acc8fd2aa70fe07729ba88b6a5d850e5bc2a9baf4e9e59c3b7b8dec`.
It was safely extracted outside the repository after rejecting absolute paths,
traversal, symlinks, duplicate entries, and case conflicts. Every package
manifest entry passed. Only the three import-manifest paths entered the
repository:

| Imported path | SHA256 |
|---|---|
| `guide/RC_HSG_Paper_Spec_v2_3_2026-08-24.md` | `f5fdb4f9815cb519cc44a214c5c75812d3ebffdd007314304f20e544ae15ba9a` |
| `artifacts/spec_review/rc_hsg_v23_real_frontend_review.md` | `53aa8a848fce0ecca8377abb44b0d56e8a3c73fb1d95fd0bf11a06bf0cb466d7` |
| root `CODEX_NEXT_TASK.md` at import | `ac44c8e5d1098228237957f67557b6d8b793aea0ab8dc8607d3629e788333c04` |

The root next-task file was then advanced to the post-run stop state.

## Frozen panel and read boundary

The metadata-only selector reproduced 3,541 outer-train rows, 3,497 eligible
rows, 44 short rows, and 35,745 full windows before any HDF5 dereference. The
canonical ledger has 151 rows: 107 real reads and all 44 short rows as explicit
no-read entries. The real panel covers 18 subjects, 1,452 windows, 55 train-fit
rows, and 52 inner-val rows. Its strata are 34 `W01_04`, 36 `W05_16`, and 35
`W17_PLUS` rows, plus two distinct role stress rows.

Only each selected row's exact `sentenceData/rawData[slot-1,0]` same-file object
reference was dereferenced. All 107 selected sources were float64 arrays with
logical shape `[raw_samples,105]`; each was checked finite, cast contiguously to
float32 without scaling, and explicitly transposed to `[1,105,T]`. No short,
calibration, test, other-slot, stimulus-text, outcome, or panel-external EEG
array was read. The remaining 3,390 eligible outer-train rows remain unread.

## CPU and CUDA self-check

CPU individual exact repeat, full-window count, mask, finite output, masked
mean, zero-versus-NaN padding isolation, batch parity at `2e-5`, parameter
immutability, null gradients, and eval/inference-only checks passed.

CUDA was available on four devices; device 0 was an NVIDIA GeForce RTX 4090.
The frozen 20-row/199-window subset passed CPU/CUDA parity at the unchanged
`rtol=2e-4, atol=2e-4` with TF32 disabled. The validator disables Torch native
JIT routing, MHA fastpath, Flash SDP, and memory-efficient SDP, and uses the
installed ATen math path. This avoids runtime compilation/cache writes and
keeps the model, parameters, bands, windows, inputs, and tolerances unchanged.

## Deterministic outputs

Two repository-external full production builds were byte-identical for all
three outputs, followed by a byte-identical canonical build:

| Output | SHA256 |
|---|---|
| `artifacts/a1_frontend_audit_panel_v1.jsonl` | `95db4e18501ae25f559bb6446621b6c062a7f36936ca0f4eec3236dc57ca43ed` |
| `artifacts/a1_frontend_freeze.yaml` | `817b1be11d3545f1279e87fd40d391b71dd3347d0eed57c174abdfc6bf760d66` |
| `reports/a1_frontend_selfcheck.md` | `703e999bc9903183dd019df853e92558a81ba8526945e32a24ae926d95af4503` |

The canonical environment records Python 3.12.3, Torch 2.13.0+cu130, NumPy
2.5.2, and h5py 3.16.0. No tensor, embedding, waveform, value summary, output
hash, cache, performance result, or timing is emitted.

## State migration

`SPEC_V23_REVIEW` and `S0_A1_FRONTEND` are DONE. B_V8 moved to closed evidence.
B_V9 records that the bounded panel is not full admission and does not block its
future resolver `S0_A1_ADMISSION`. Early `S0_LEAKAGE_AUDIT` now covers only the
Regime-I data/A-path firewall. The new `S0_METHOD_LEAKAGE_AUDIT` remains BLOCKED
until all method components exist; route lock and main experiment depend on it.

Final state is 70 tasks, 33 DONE, 8 SKIPPED, 28 BLOCKED, and sole READY
`S0_LEAKAGE_AUDIT`, owner `CODEX`. Test remains `LOCKED_UNTIL_ROUTE_LOCK`.

## Validation

- A1 frontend suite: 13/13 PASS, including the real conditional CUDA branch.
- Native spectral suite: 12/12 PASS.
- A-interface builder suite: 8/8 PASS.
- Project-memory suite: 51/51 PASS.
- Joint split / stimulus identity / similarity / analysis view: 13/13,
  12/12, 12/12, and 11/11 PASS.
- Targeted audit / input audit: 21/21 and 8/8 PASS.
- Full server discovery: 161/161 PASS with no skip.
- Validator, status, exact task counts, test lock, three-build determinism,
  and `git diff --check`: PASS.

## Safety boundary and stop

Run 014 performed no full outer-train admission, leakage audit, training,
backward pass, optimizer step, representation save, unit inference, channel
interpolation, schema/candidate/null/reference/reliability/calibration/baseline
implementation, Gate, test unlock, or test/outcome/result read. Stop at
`S0_LEAKAGE_AUDIT`.
