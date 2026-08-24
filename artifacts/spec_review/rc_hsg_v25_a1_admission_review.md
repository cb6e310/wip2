# RC-HSG v2.5 full A1 admission pre-execution review

Date: 2026-08-24  
Reviewed remote: clean `main@07c37b3bb77c3cf396116078b64687dcebb9ee03`  
Decision scope: full Regime-I outer-train A1 admission only

## Verdict

Run 015 is accepted. The repository has the exact intended v2.4 stop state: 71 tasks, 35 DONE,
8 SKIPPED, 27 BLOCKED, sole READY `S0_A1_ADMISSION`, early A-path leakage PASS, route unlocked,
and test locked. The audit outputs independently rebuild byte-identically. Locally available audit
20/20 and project-memory 52/52 tests pass; the server run record reports 182/182 full discovery.

The follow-up executable-mode commit changes no source content and is accepted as the new baseline.

## Scientific decision

Full admission must cover the whole outer-train population without repeating already accepted
data exposure. Run 014 already performed the strongest loader, repeat, batch, padding and CUDA
checks on 107 frozen rows. Run 016 therefore reuses those exact committed results and reads only
the remaining 3,390 eligible rows.

Every remaining row must traverse the complete frozen A1 frontend. A shape-only loader scan would
not establish full frontend admission. Conversely, repeat, padding and CPU/CUDA parity need not be
repeated on every row because those are interface-behavior checks already established by the
bounded panel.

## Single-pass design

The remaining rows are sorted deterministically by window count and length and processed in
batches of at most four. CUDA is selected once when available, otherwise CPU is selected once;
device fallback during the scan is forbidden. Each source array is dereferenced exactly once,
checked by the already audited loader, processed under eval/inference mode, and released after its
batch.

The scan constructs metadata-only evidence in memory. The same serialized ledger, freeze and
report bytes are written to two external roots and the canonical repository root. Determinism is
therefore checked without performing two additional real-data scans.

## Complete ledger

The canonical ledger contains all 3,541 outer-train rows:

- 107 eligible rows reuse run-014 PASS and are not reread;
- 3,390 eligible rows are read once and execute full A1 inference;
- 44 short rows remain forced L0 and are never dereferenced.

The cumulative admitted frontend population is 3,497 eligible rows and 35,745 windows. The ledger
contains only keys, roles, source schema, dtype and PASS/NOT_APPLICABLE statuses. It contains no
EEG value, embedding, waveform hash, amplitude/power statistic, text, outcome, metric or timing.

## Claim and unit boundary

A successful run may conclude only
`FULL_REGIME_I_OUTER_TRAIN_A1_FRONTEND_ADMISSION_PASS`. It does not identify physical units,
validate representation quality, admit calibration/test signals, train a model, establish null or
reference validity, or support a Gate or paper result.

## Expected run-016 stop state

Run 016 adds/completes `SPEC_V25_REVIEW`, completes `S0_A1_ADMISSION`, closes B_V9, and stops with
72 tasks, 37 DONE, 8 SKIPPED, 26 BLOCKED and sole READY `S0_N1_BLOCK_FEASIBILITY`, owner
`CHATGPT_OR_AUTHOR`. Test remains locked. N1 bins, power summaries, permutations and feasibility
checks are not authorized in this run.

Fixed-state conflicts are `STATE_SPEC_CONFLICT`. Source, tensor, frontend, scope, one-pass or
determinism failures are `A1_FULL_ADMISSION_BLOCKED`; they may not be repaired by rereading the
panel, skipping rows, guessing units, changing the device/batch policy or weakening acceptance.
