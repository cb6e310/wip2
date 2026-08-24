# RC-HSG v2.6 N1 Block Feasibility

## Decision

The outcome-blind outer-train decision is `DEGRADED_COVERAGE` with evidence label `N1_OUTER_TRAIN_BLOCK_FEASIBILITY_DEGRADED_COVERAGE`.
The minimum subject-by-role population coverage is 0.777777777778; the frozen threshold is 0.90.

## Population denominator

The complete ledger contains 3,541 rows. The primary denominator includes eligible, short forced-L0, unavailable-edge, and singleton rows; it does not remove difficult rows to increase coverage.
Exactly 3,497 eligible arrays were read once. All 44 short arrays and all calibration/test arrays were not read.

## Blocks and index-only probe

The frozen train-fit edges produced 192 populated role-scoped blocks, including 12 singleton blocks. Only blocks of size at least two were evaluable.
All 199 index-only replicates were evaluated; 199/199 joint mapping hashes were unique.
Fixed points are retained and reported because forcing derangements would change the frozen randomization law. No recipient-donor mapping or donor EEG was persisted or read.

## Evidence boundary

Power edges use train-fit only and are serialized as float.hex strings. Row proxies, spectral tokens, waveforms, embeddings, and value hashes are absent from every output.
This outer-train feasibility decision does not validate calibration/test coverage, implement an N1 sampler, admit N1 as the primary fallback, execute Gate R0, establish semantic/reference utility, or unlock test.

## Stop

The mechanical next task is `S0_N1_SAMPLER`, owner `CHATGPT_OR_AUTHOR`, under a new exact contract. Run 017 stops before that task.
