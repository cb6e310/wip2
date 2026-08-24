# RC-HSG v2.7 N1 Mechanism Sampler Self-Check

## Frozen scope

The committed assignment contains 3,541 rows: 3,481 evaluable rows in 180 blocks and 60 canonical exclusions.
N1 remains a mechanism/robustness family because run 017 froze DEGRADED_COVERAGE; it is not a primary fallback.

## Permutation parity

All 199 metadata-only joint permutations match the run-017 hashes and fixed-point counts.
The hashes are 199/199 unique; fixed points total 35,529 with range 145..214.
Fixed points are retained. Adjacent-block borrowing, cross-scope mapping, RNG, and persisted mapping relations are absent.

## Selection-aware boundary

Real and pseudo-real sources use the same complete select-then-score callback in canonical row order.
Candidate selection, the L1-L2-L3 parent-consistent path, and scoring must be recomputed inside every callback invocation.
This run creates no semantic candidates, reference scores, donor values, or paper p-values.

## Safety and stop

The build reads committed metadata only. EEG, short, calibration, test, text, outcome, frontend, token, proxy, embedding, and waveform reads are zero.
No N2 implementation or Gate is executed. The next task is `S0_N2_SAMPLER`, owner `CHATGPT_OR_AUTHOR`.
