# Run 013: Native Spectral A Interface

Date: 2026-08-24  
Task: `SPEC_V22_REVIEW -> S0_A_INTERFACE -> stop with S0_A1_FRONTEND READY`  
Baseline: `91997faa1de1616d1eb662cd36edc1547613206d` on clean `main`

## Baseline and package

A real `git fetch origin main` preceded all changes. The server repository
confirmed `main`, `HEAD=origin/main=91997faa1de1616d1eb662cd36edc1547613206d`,
and an empty porcelain status. Baseline recovery passed with 67 tasks, 29 DONE,
8 SKIPPED, 29 BLOCKED, sole READY `S0_A_INTERFACE`, and test locked.

The handoff ZIP SHA256 was
`e756edef18a821524ebe22e4e494a56832a8762f3a95481dbb3572279c0b91ea`.
It was safely extracted outside the repository after rejecting absolute paths,
traversal, symlinks, duplicate entries, and case conflicts. Every
`PACKAGE_MANIFEST.sha256` entry passed. Only the three import-manifest paths
entered the repository:

| Imported path | SHA256 |
|---|---|
| `guide/RC_HSG_Paper_Spec_v2_2_2026-08-24.md` | `a5d6d695f21a72dd2e3d8445771b6b3d772f0a42282ad5ce9feaa6e43da01911` |
| `artifacts/spec_review/rc_hsg_v22_a_interface_review.md` | `7ca7353ba64229f29b2fbb2634e6d53e6dc03f8ef3f63a3fd00a342cb96344dd` |
| root `CODEX_NEXT_TASK.md` at import | `593b117ed699839fcfca03d1c461cf5e78f90880f8ba44f46e772860a5ea18e2` |

The root next-task file was then advanced to the post-run stop state.

## Fixed inputs and implementation

All six v2.2 fixed input hashes matched before implementation. The clean-room
module exposes only the frozen `AInterfaceContractError`,
`NativeSpectralA1Output`, and `NativeSpectralA1(init_seed: int)` contract. It
implements valid-prefix-only median/MAD-or-RMS normalization, clipping,
500/250 symmetric-Hann full windows, exact 1-Hz rFFT band-power sums, 840-d
channel-major tokens, the frozen two-layer encoder, explicit masks, zeroed
masked output, and masked arithmetic pooling.

Trainable parameter count is exactly 1,270,528. Construction is CPU-only,
explicitly seeded, restores caller RNG state, and uses Xavier-uniform matrix
weights, zero bias, and unit LayerNorm weights. No main experiment seed was
selected. Implementation SHA256:
`71ae12d65cc0acc6fd5870434e141ee7d849eb8befa718a84fb99cb86ed533d9`.

## Metadata-only eligibility overlay

The builder never follows `source_locator` and reads only the six committed
metadata inputs. It preserves all 5,905 rows. Exactly 5,832 rows are eligible;
73 rows shorter than 500 samples have zero windows and route to
`A_INTERFACE_SHORT_SEGMENT/FORCED_L0_NO_FRONTEND`. Total full-window count is
60,522. Role counts are 2,797/35/29,263 train-fit, 700/9/6,482 inner-val,
1,156/15/11,558 calibration, and 1,179/14/13,219 locked test
(eligible/forced-L0/windows). Calibration reserves are 582/9 select and 574/6
cert.

Two explicit repository-external production builds were byte-identical for all
three outputs, followed by the canonical build:

| Output | SHA256 |
|---|---|
| `artifacts/backbone_a_contract.yaml` | `4c9ccddf4d5c208870422c7e5ceee65ee184d812fce662bb885998b0dad65cac` |
| `artifacts/a_interface_eligibility_v1.jsonl` | `8eded8fb2786747e96b8388d4d91315e39db9f8a9eb25ea69056d219e1e8e1ad` |
| `reports/a_interface_contract.md` | `925af0e2ccc95fb01c8479beac8901632ddfd4c180682af0e4f3b0a886133295` |

The canonical environment recorded Python 3.12.3, Torch 2.13.0+cu130, and
NumPy 2.5.2.

## State migration

`SPEC_V22_REVIEW` and `S0_A_INTERFACE` are DONE. B_V7 moved to closed evidence;
B_V8 records that real outer-train tensor, finite-value, device/memory, and
admission behavior remain unvalidated. `S0_LEAKAGE_AUDIT` now depends exactly
on `S0_A1_FRONTEND` and `S0_JOINT_SPLIT`. Final state is 68 tasks, 31 DONE,
8 SKIPPED, 28 BLOCKED, and sole READY `S0_A1_FRONTEND`, owner `CODEX`. Test
remains `LOCKED_UNTIL_ROUTE_LOCK`.

## Validation

- Native spectral synthetic suite: 12/12 PASS.
- A-interface builder suite: 8/8 PASS.
- Project-memory suite: 50/50 PASS.
- Joint split / stimulus identity / similarity / analysis view: 13/13,
  12/12, 12/12, and 11/11 PASS.
- Targeted audit / input audit: 21/21 and 8/8 PASS.
- Full server discovery: 147/147 PASS with no skip.
- Validator: PASS with 68 tasks, 31 DONE, 8 SKIPPED, 28 BLOCKED, and sole
  READY `S0_A1_FRONTEND`.
- Status, exact eligibility assertions, test lock, and `git diff --check`: PASS.

## Safety boundary and stop

Run 013 read no real EEG array or value, stimulus/semantic outcome,
calibration/test result, prediction, metric, or historical model result. It did
not train or perform an optimizer step, select a main seed/optimizer, copy or
import external model code, load/download a checkpoint or weight, infer units,
interpolate channels, implement F/schema/candidates/N1/N2/reference/
reliability/calibration/baselines, run the full leakage audit or any Gate,
change split/population/bootstrap, remove or pad short rows, or unlock test.
Stop at `S0_A1_FRONTEND`.
