# Run 015: A-Path Leakage Audit

Date: 2026-08-24  
Task: `SPEC_V24_REVIEW -> S0_LEAKAGE_AUDIT -> stop with S0_A1_ADMISSION READY`  
Baseline: `dc105709563cf9eb216f1c28f82fdf754e7b0683` on clean `main`

## Baseline and package

A real `git fetch origin main` preceded all changes. The server repository
confirmed `main`, `HEAD=origin/main=dc105709563cf9eb216f1c28f82fdf754e7b0683`,
an empty porcelain status, 70 tasks, 33 DONE, 8 SKIPPED, 28 BLOCKED, sole READY
`S0_LEAKAGE_AUDIT`, unlocked route, and test `LOCKED_UNTIL_ROUTE_LOCK`.

The handoff ZIP SHA256 was
`c8282a8c5c600ec1838153c349f3f3d119a3df4dd5e017b7aad5c260ff933555`.
It was safely extracted outside the repository after rejecting absolute paths,
traversal, symlinks, duplicate entries, and case conflicts. Every package
manifest entry passed. Only the three import-manifest paths entered the
repository:

| Imported path | SHA256 |
|---|---|
| `guide/RC_HSG_Paper_Spec_v2_4_2026-08-24.md` | `5878fa84db5abb380c71e6257a4a7c30e0587ab8d505ba0d9446c110d47426b5` |
| `artifacts/spec_review/rc_hsg_v24_a_path_leakage_review.md` | `2527c73ad5bb75c351e38cd64651c35f6e7559400d5255804f1f72c51dd138ca` |
| root `CODEX_NEXT_TASK.md` at import | `ca85d09a39544e306c0a621e948d93377e92e30325d3ccdfc41438b8d8265c32` |

The root next-task file was then advanced to the post-run stop state.

## Audit boundary and evidence

The production audit parsed only allowlisted source code and committed
metadata. It did not import or execute the real frontend validator or A model,
did not access the production dataset root, and opened no `.mat`, HDF5, or
other signal-value file. It read no new real EEG value, stimulus text, outcome,
prediction, metric, or historical result.

All twelve §23 machine assertions passed in frozen order. All twelve M01-M12
in-memory mutation probes returned `PASS_REJECTED` under their corresponding
assertion. Mutated source was never written or executed.

The supported conclusion is limited to
`EARLY_REGIME_I_SPLIT_DATA_AND_FROZEN_A_PATH_LEAKAGE_FIREWALL_PASS`. This is not
full admission or full method leakage evidence.

## Deterministic outputs

Two repository-external production builds and the canonical build were
byte-identical:

| Output | SHA256 |
|---|---|
| `artifacts/a_path_leakage_assertions.yaml` | `eb60565b40991f19856673acc030ec7a7dcab6c520c6af5c1b1c39167f864f70` |
| `reports/a_path_leakage_audit.md` | `491986e4caed53623069b26918b9be232aff74416c8e4ef973955a6810b7fd27` |

## State migration

`SPEC_V24_REVIEW` and `S0_LEAKAGE_AUDIT` are DONE. Final state is 71 tasks,
35 DONE, 8 SKIPPED, 27 BLOCKED, and sole READY `S0_A1_ADMISSION`, owner
`CODEX`. B_V9 remains active but does not block its resolver. Route remains
unlocked and test remains `LOCKED_UNTIL_ROUTE_LOCK`.

## Validation

- A-path leakage audit suite: 20/20 PASS, including all twelve mutation probes.
- Frontend synthetic-HDF5 suite: 13/13 PASS.
- Native spectral A suite: 12/12 PASS.
- A-interface builder suite: 8/8 PASS.
- Joint-split suite: 13/13 PASS.
- Project-memory/state suite: 52/52 PASS.
- Full server discovery: 182/182 PASS with no skip.
- State validator, status command, exact task counts, only-ready set, test lock,
  three-build determinism, and `git diff --check`: PASS.

## Safety boundary and stop

Run 015 performed zero production HDF5 opens and zero new real EEG reads. It
did not execute full admission, the method leakage audit, training, backward,
optimizer, cache writing, N1/N2, schema, reference, calibration, any Gate, or
test unlock. Stop at `S0_A1_ADMISSION`; a separate author-frozen contract is
required before that task may run.
