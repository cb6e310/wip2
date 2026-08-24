# RC-HSG v2.8 N2 Common-Phase Sampler Self-Check

## Scope

This is a synthetic-only implementation check. No real EEG, text, outcome, test identity, frontend, encoder, score, p-value, or training path was used.
Policy: `RC_HSG_N2_MULTIVARIATE_COMMON_PHASE_FOURIER_V1`; fixtures=5 lengths x 3 replicates plus a 199-replicate replay.

## Preservation

All 15 grid cases pass the frozen global relative-norm threshold 1.0e-06 for PSD, covariance, mean, and cross-spectrum.
The T=513 replay has 199/199 unique seed hashes and bitwise deterministic replay.
The common phase preserves circular second-order structure. It does not guarantee amplitude distribution, endpoint behavior, real-EEG exchangeability, or an exact null.

## Stop

N2 is implemented but not admitted. Gate R0 remains unexecuted and requires a new author-frozen outcome-blind real-data audit contract.
Route remains unlocked and test remains `LOCKED_UNTIL_ROUTE_LOCK`.
