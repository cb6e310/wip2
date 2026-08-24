# Codex next task: STOP after run 015

Authoritative SPEC: `guide/RC_HSG_Paper_Spec_v2_4_2026-08-24.md`, especially §23.

Run 015 completed:

```text
SPEC_V24_REVIEW
-> S0_LEAKAGE_AUDIT
-> S0_A1_ADMISSION READY
-> STOP
```

The repository state is 71 tasks, 35 DONE, 8 SKIPPED, 27 BLOCKED, and sole
READY `S0_A1_ADMISSION`, owner `CODEX`. B_V9 remains active but does not block
its resolver. Test remains `LOCKED_UNTIL_ROUTE_LOCK`; route remains unlocked.

The early Regime-I split/data/frozen-A-path firewall passed through committed
metadata, function-scoped AST checks, synthetic fixtures, and all twelve
in-memory mutation probes. Production HDF5 was not opened, no new real EEG
value was read, and the real frontend validator was not imported or executed.

`S0_A1_ADMISSION` has not been executed and is not authorized by the run-015
package. A later ChatGPT/author instruction must freeze its exact streaming
order, counts, memory/CUDA sampling, failure ledger, deterministic outputs, and
B_V9 closure before Codex may proceed. Do not execute full admission, the
method leakage audit, training, schema/reference/calibration work, any Gate, or
test unlock under the current authorization.
