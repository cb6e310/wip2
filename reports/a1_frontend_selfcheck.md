# RC-HSG A1 Bounded Real-Frontend Self-Check

## Scope

The frozen native A1 loader and frontend passed a bounded outer-train real-data self-check. This is not full admission, training, representation quality, performance, reference, leakage-audit, or Gate evidence.

## Audit panel

- Ledger rows: 151
- Real arrays read: 107 distinct rows across 18 subjects
- Roles: train-fit 55, inner-val 52
- Full windows: 1452
- Short rows: 44 retained with no source-array dereference

## Checks

- CPU canonical path: `PASS`
- CPU repeat / batch parity / padding isolation / parameter immutability: `PASS` / `PASS` / `PASS` / `PASS`
- CUDA: `PASS` (20 rows, 199 windows)
- Source dtype schema: `{'float64': 107}`

## Downstream boundary

Full outer-train admission is incomplete. The remaining 3,390 eligible outer-train arrays were not read. The next task is `S0_LEAKAGE_AUDIT`; test remains locked.

No EEG value, tensor, token, embedding, waveform hash, output hash, amplitude/frequency summary, text, outcome, prediction, metric, checkpoint, or cache was emitted.
