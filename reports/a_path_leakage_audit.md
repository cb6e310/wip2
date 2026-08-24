# RC-HSG v2.4 A-Path Leakage Audit

## Evidence boundary

This audit combines committed metadata cross-checks, function-scoped AST semantics, synthetic-fixture tests, and twelve in-memory mutation probes. Production data files were not opened and the real frontend validator was not imported or executed.

## Machine assertions

### SPLIT_ROLE_FIREWALL

Split roles are closed to four frozen labels; runtime and real panel are outer-train only.

### ROW_KEY_FIREWALL

The exact (subject,slot,occurrence_id) key uniquely joins 5905 rows; panel rows=151.

### SHORT_BYPASS_FIREWALL

Short ledger rows=44; all are forced L0 with zero windows and no source read.

### DEREFERENCE_SCOPE_FIREWALL

Only 107 distinct read-true outer-train panel keys can reach the single dereference call; set equality closes coverage.

### SOURCE_IDENTITY_FIREWALL

Dataset root is a module constant; CLI has no dataset override; symlink, escape, file-set, and size guards are present.

### SOURCE_FIELD_SLOT_FIREWALL

The reader opens one HDF5 file read-only and follows the same-file hard reference at sentenceData/rawData[slot-1,0] with floating [raw_samples,105] checks.

### NUMERIC_TRANSFORM_FIREWALL

Finite checks bracket a no-scale contiguous float32 cast followed by one explicit transpose; no unit or sampling transform is called.

### PER_ROW_PREPROCESSING_FIREWALL

Native A slices each valid prefix, computes channel-wise median/MAD/RMS per row, and tokenizes rows independently before padding.

### INFERENCE_ONLY_FIREWALL

Frozen runtime constructs eval-mode models under inference_mode and contains no optimizer, loss, backward, update, train, or checkpoint call.

### NO_VALUE_TEXT_OUTCOME_CACHE

The runtime reader accesses only rawData and contains no value, token, embedding, prediction, metric, checkpoint, or feature-cache writer.

### FAIL_CLOSED_AND_DETERMINISTIC

Inputs and outputs are path-closed; failures use stable prefixes; serialization precedes same-directory temp, flush, fsync, and replace.

### TEST_AND_DOWNSTREAM_LOCK

Route remains unlocked, test remains LOCKED_UNTIL_ROUTE_LOCK, 3,390 eligible rows remain unread, and no downstream method or Gate is executed.

## Epistemic limits

The evidence supports only the early Regime-I split/data/frozen-A-path firewall. It does not complete full outer-train admission, the later method leakage audit, schema or reference work, calibration, any Gate, or test unlock. The remaining 3,390 eligible rows and all short/cal/test signal arrays remain outside this run.

## Stop boundary

The next task is `S0_A1_ADMISSION`, which requires a separate author-frozen execution contract and is not authorized by run 015.
