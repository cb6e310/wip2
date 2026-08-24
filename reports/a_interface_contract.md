# RC-HSG Native Spectral A1 Interface Contract

## Scope

The frozen clean-room A interface is implemented and synthetic-tested. Real EEG traversal, physical-data frontend admission, representation quality, training, performance, reference feasibility, and Gate evidence remain unvalidated.

## Frozen interface

- Input: floating `[B,105,T]`, explicit valid lengths, 500 Hz, common-average, release-native unresolved amplitude.
- Tokenizer: per-trial/channel robust normalization; 500/250 symmetric-Hann full windows; eight fixed log-relative-bandpower bands.
- Encoder: 840-to-256 projection and two pre-norm Transformer layers; 1,270,528 trainable parameters.
- Short segments: no frontend call, padding, imputation, or removal; forced L0 while retained in the paired population.

## Eligibility overlay

| role | rows | eligible | forced L0 | full windows |
|---|---:|---:|---:|---:|
| train_fit | 2832 | 2797 | 35 | 29263 |
| inner_val | 709 | 700 | 9 | 6482 |
| cal | 1171 | 1156 | 15 | 11558 |
| test | 1193 | 1179 | 14 | 13219 |
| total | 5905 | 5832 | 73 | 60522 |

Eligibility JSONL SHA256: `8eded8fb2786747e96b8388d4d91315e39db9f8a9eb25ea69056d219e1e8e1ad`.

## Evidence boundary

`SYNTHETIC_INTERFACE_AND_COMMITTED_METADATA_ONLY_NO_REAL_EEG_VALUES_NO_OUTCOMES`

No real EEG value, semantic/calibration/test outcome, prediction, metric, historical model result, external implementation, checkpoint, or downloaded weight was read or used.
