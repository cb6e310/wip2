# NC-HSG v1.6 post-push review

Date: 2026-08-16  
Reviewed remote: `https://github.com/cb6e310/wip2`  
Reviewed commit: `c807a2e83fad02763193a6c1db81fd26db19fd97`

## Verdict

Run 006 is accepted as a conservative schema-v2 repair. Its 6,282-row occurrence ledger, EEG-cell classification, explicit condition-3 conjunction, admission FAIL, and absence of a data card are internally consistent. It did not authorize model selection, training, or a Gate.

The targeted admission is not complete. The event auditor validates only `10→11`, although the committed physical counts show that every subject has 303 ordinary sentences (`10/11`) and 46 control sentences (`12/13/15`), which together form the 349 task-1 sentence occurrences. The code also never compares event-defined preprocessed `EEG/data` segments with summary `sentenceData/rawData`, so summary layer/reference remain unresolved without testing the strongest available local evidence.

The next run is a bounded event/segment correspondence audit. It is not another broad discovery or unit search.

## Independent checks

- Remote `main` resolves to `c807a2e83fad02763193a6c1db81fd26db19fd97`; commit message is `fix: repair ZuCo NR admission predicates`.
- `python3 -m unittest discover -s tests -p 'test_project_memory.py'`: 38/38 PASS.
- `python3 -m unittest discover -s tests -p 'test_audit_input_sources.py'`: 8/8 PASS.
- `python3 scripts/check_project_state.py`: PASS, 43 tasks, 12 DONE.
- `python3 scripts/project_status.py`: exit 0, stage 0 BLOCKED, no READY task.
- `git diff --check` and worktree state: PASS/clean.
- Independent environment lacks `h5py`; `test_audit_zuco2_nr.py` therefore was not independently rerun. Run 006 records 12/12 PASS on the server.
- OSF Data format wiki bytes independently hash to `3cc1b85c021042d93db4f077145b84e6c3beebad3a474f6781746a6a40dbdbb4`, matching the run-006 source audit.

## Correct work retained from run 006

- Active SPEC entry points agree on v1.5 and validator/status pass.
- 18 × 349 = 6,282 material occurrences match in exact ordered position; 21 practice rows are excluded.
- Cell classes are 5,911 `VALID_FINITE_MULTISAMPLE`, 367 `NONFINITE_PLACEHOLDER`, and 4 `FINITE_SINGLE_SAMPLE_REVIEW_REQUIRED`.
- Every row has non-null block, material line, and canonical occurrence ID.
- 126 blocks retain one 105-channel order, complete coordinate contract, 500 Hz sampling, Cz acquisition reference, and common-average processed reference.
- Six admission conditions are `PASS, PASS, FAIL, PASS, PASS, PASS`; no data card exists.
- No historical/test outcome, checkpoint, download, model training, A selection, or Gate is evidenced.

## Material findings for v1.6

### R1 — event occurrence is partitioned across two sentence-code families

For each of all 18 subjects, aggregate counts are exactly:

```text
10 = 303, 11 = 303
12 = 46, 13 = 46, 15 = 46
303 + 46 = 349 sentence occurrences
```

The official OSF wiki identifies 10/11 as ordinary sentence onset/finish, 12/13 as control sentence onset/finish, and 15 as control-question answer/finish. A task-1 occurrence contract that checks only 10/11 is incomplete. Code 15 is response metadata, not an extra sentence.

### R2 — two YTL booleans are not a sufficient anomaly ledger

Run 006 lists `gip_YTL_NR3_EEG.mat` and `oip_YTL_NR6_EEG.mat` as non-pairable under the 10/11-only projection. It does not record the sanitized occurrence ordinal or test whether the complete 10/11 + 12/13/15 state machine resolves the apparent anomaly. The next audit must do that without printing latencies or values.

### R3 — the strongest local layer test was not run

The summary arrays and preprocessed blocks can be compared safely by streaming an event-defined segment and the corresponding summary cell. Exact equality under one global, predeclared EEGLAB endpoint convention would bind summary layer/reference to the preprocessed array. Shape similarity, correlation, magnitude, per-row convention selection, scaling, or re-referencing are not acceptable substitutes.

### R4 — external evidence verdicts are hard-coded

`SOURCE_RETRIEVED_AT_UTC`, source hashes, applicability, and verdicts are returned by `build_unit_source_audit()` as Python constants. The CLI accepts only OSF file metadata, not a release-source evidence cache. This is byte-stable but not fail-closed evidence processing.

### R5 — the conditional success branch is absent

If all six conditions unexpectedly pass, `main()` exits with `DATA_CARD_GENERATION_NOT_IMPLEMENTED_FOR_UNEXPECTED_ALL_PASS_RESULT`; the manifest always writes `data_card_generated: false`. This contradicts the frozen conditional data-card requirement even though the current real result is FAIL.

### R6 — final admission counts should use the final row flag

The cell class and final admission flag can diverge when content or segment evidence fails. Valid/excluded totals must be derived from the final admission predicate, then checked against class/content/event/segment reasons.

## Unit evidence boundary

The author-maintained issue #5 now has a repository-collaborator reply saying the unit is microvolt, but the question's concrete file is ZuCo 1.0 SR. The reply is important context, not a direct ZuCo 2.0 NR array binding. The next run must not repeat the same unit search or promote this cross-version example by assertion. Exact summary↔preprocessed identity can bind layer/reference and transfer a unit only if a direct unit binding for either current array is separately established.

## Corrected next action

Activate SPEC v1.6 and execute only `S0_ZUCO2_NR_SEGMENT_CORRESPONDENCE`. Produce schema-v3 event-occurrence and segment-correspondence artifacts, make source evidence an input, implement the real conditional data-card branch, and update active state according to the physical result. Preserve runs 005–006 and all v1/v2 artifacts. Do not select A, create splits, implement scientific algorithms, train, inspect outcomes, download data/weights, or run a Gate.
