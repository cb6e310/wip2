# RC-HSG v2.3 real-frontend pre-execution review

Date: 2026-08-24  
Reviewed remote: clean `main@237788090dcb20e533f304f63ae8feb2f545fe0b`  
Decision scope: `S0_A1_FRONTEND` and leakage-task dependency repair only

## Verdict

Run 013 is accepted. The repository has the intended v2.2 state: 68 tasks, 31 DONE, sole READY
`S0_A1_FRONTEND`, locked test, exact 1,270,528-parameter native A interface, 5,832 eligible rows,
73 forced-L0 short rows, and no real EEG value read by run 013. Validator/status and all locally
available tests pass. The server run record's 147/147 full-suite result remains the authoritative
PyTorch/h5py execution evidence; the independent review environment does not contain those two
packages and does not mislabel static inspection as execution.

The next valid action is a bounded real-data loader/frontend self-check. It is not training and not
formal full admission.

## Interface review

The committed implementation matches the frozen v2.2 contract on the inspected points: exact
metadata constants, strict `[B,105,T]` API, valid-slice normalization, 500/250 full windows,
symmetric Hann, fixed rFFT denominator and bands, 840-dimensional channel-major tokens, exact
encoder, masks, pooling, deterministic CPU construction and error codes. Artifact and code hashes
match run 013. No algorithm change is authorized in run 014.

## Why the real read is bounded

Regime-I outer-train contains 3,541 rows: 3,497 eligible, 44 short and 35,745 full windows. Reading
all eligible arrays now would collapse `S0_A1_FRONTEND` into the later `S0_A1_ADMISSION`; reading
one arbitrary row would not test subject, role, length, batch padding or memory extremes.

The outcome-blind compromise is frozen before any new real value is read:

- one row per nonempty subject × outer-train-role × fixed window-count stratum: 105 rows;
- one maximum-window stress row per role: 2 additional distinct rows;
- total real panel: 107 rows, 18 subjects, train-fit/inner-val 55/52, 1,452 windows;
- all 44 outer-train short rows appear in the ledger but their HDF5 target is never dereferenced;
- no remaining outer-train, calibration or test array is read.

Selection uses only committed subject, role, occurrence ID, slot and window-count metadata. It never
uses amplitude, tensor output, text, outcome, model metric or searched seed. The audit seed
`20260824` is explicitly non-experimental.

## Loader and numerical contract

The production reader is restricted to the recorded ZuCo dataset root and the 18 summary files. It
reuses previously verified file hashes while checking current relative path and size. For each
selected cell it follows only the same-file `sentenceData/rawData[slot-1,0]` object reference,
requires exact `[samples,105]` floating data, checks finite values before and after a no-scale
float32 cast, and explicitly transposes to `[1,105,T]`. It cannot inspect other source fields or
silently transpose a wrong shape.

CPU eval must pass exact repeatability, finite output, expected masks/windows, parameter
immutability, batch-vs-individual tolerance and zero-tail-vs-NaN-tail isolation. CUDA parity is
required when CUDA is available and is a nonblocking availability diagnostic otherwise. No EEG,
token, embedding, waveform hash or value-derived summary is written.

## Task-graph issue and correction

The current `S0_LEAKAGE_AUDIT` acceptance mixes an early A/data firewall with candidate, schema,
reference, calibration and test-time code that does not yet exist. Running it immediately after
frontend validation would either fail for missing implementations or produce a false “full leakage
PASS.” v2.3 preserves rigor by splitting it:

- `S0_LEAKAGE_AUDIT`: early split/data/A-path audit, immediately after frontend self-check;
- `S0_METHOD_LEAKAGE_AUDIT`: later complete method/candidate/reference/calibration/test-time audit,
  required by route lock and the main experiment.

No leakage requirement is removed. Each audit is moved to the first point where its evidence exists.

## Expected run-014 stop state

Run 014 adds/completes `SPEC_V23_REVIEW`, completes `S0_A1_FRONTEND`, adds the blocked later method
audit, closes B_V8, and opens B_V9 for full outer-train admission. It must stop with 70 tasks,
33 DONE, 8 SKIPPED, 28 BLOCKED and sole READY `S0_LEAKAGE_AUDIT`. The remaining 3,390 eligible
outer-train rows are still unread, and test remains locked.

Any fixed-state conflict is `STATE_SPEC_CONFLICT`. Any source, loader, tensor, deterministic or
device failure is `A1_FRONTEND_VALIDATION_BLOCKED`; Codex may not repair it by changing A, the panel,
the tolerance, the source data or the scientific route.
