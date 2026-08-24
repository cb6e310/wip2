# RC-HSG v2.5 Full Outer-Train A1 Admission

## Cumulative admission

The Regime-I outer-train ledger contains 3,541 rows: 3,497 eligible rows with 35,745 windows and 44 short rows retained as forced L0 without dereference.

Run 014 evidence is reused for 107 eligible rows and 1,452 windows without rereading those arrays. Run 016 performed one streaming scan of the remaining 3,390 distinct eligible rows and 34,293 windows through the frozen A1 frontend.

## Execution evidence

Selected device policy status: `CUDA_0_SELECTED`.
Audited-loader source dtype counts for run 016: float64=3390.
Every run-016 row passed source identity, shape, finite input, expected windows, mask, finite output, exact masked mean, eval mode, null-gradient, and parameter-immutability checks.

The same serialized ledger, freeze, and report bytes were atomically written to two repository-external verification roots and the canonical root after the single scan.

## Evidence reuse and limits

The run-014 repeat, padding, batch-parity, and CPU/CUDA-parity evidence remains frozen and was not regenerated. Physical units remain unresolved release-native amplitude; no unit inference, scaling, rereference, resampling, or interpolation was performed.

This admission is not training, representation-quality evidence, N1/N2 feasibility, semantic/reference/reliability/calibration evidence, a Gate result, method leakage completion, or test unlock.

## Stop boundary

`S0_N1_BLOCK_FEASIBILITY` requires a new ChatGPT/author-frozen contract and is not authorized by run 016.
