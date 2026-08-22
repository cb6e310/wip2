# NC-HSG v1.7 post-push review

Date: 2026-08-21  
Reviewed remote: `https://github.com/cb6e310/wip2`  
Reviewed commit: `bf958fe2fc543e6b5c465a9eed3c743d4b0d0aa7`

## Verdict

Run 007 is accepted as a successful schema-v3 event/segment audit and a conservative full-release diagnostic FAIL. It proves a reproducible 5,905-row analysis subset and a complete 377-row exclusion union. It does not prove physical storage unit, universal event correctness, backbone compatibility, training readiness, or any Gate result.

The active project is blocked by a policy mismatch, not by missing machine-operable evidence. `S0_DATA_CARD.acceptance` requires verified composition, fields, assignments, hashes, and exclusions; it does not require every release row to be usable or the absolute physical unit to be known. A data card should expose unknown unit and bad rows. Unit-sensitive model admission remains separately blocked.

SPEC v1.7 therefore authorizes a repository-only derivation: freeze the 5,905-row analysis view, generate the data card, narrow the unit blocker to A/frontend tasks, and make `S0_STIMULUS_ID` READY. No real EEG reread is needed.

## Independent checks

- Remote `main` resolves to `bf958fe2fc543e6b5c465a9eed3c743d4b0d0aa7`; commit message is `fix: verify ZuCo NR segment correspondence`.
- `python3 -m unittest discover -s tests -p 'test_project_memory.py'`: 38/38 PASS.
- `python3 -m unittest discover -s tests -p 'test_audit_input_sources.py'`: 8/8 PASS.
- `python3 scripts/check_project_state.py`: PASS, 45 tasks, 14 DONE.
- `python3 scripts/project_status.py`: PASS, stage 0 BLOCKED, no READY task.
- Independent environment lacks `h5py`; targeted tests were not falsely reported as independently rerun. Run 007 records 20/20 PASS on the server.
- The review checkout was clean before test execution. A test-created temporary directory was not treated as repository evidence.

## Evidence retained from run 007

- 18 subjects × 349 slots = 6,282 rows; all subject/material positions are recovered.
- 5,911 finite-multisample cells, 367 nonfinite placeholders, and 4 finite single-sample cells.
- Every subject has 303 ordinary and 46 control occurrences.
- Finish-inclusive is the unique global convention; all 5,905 event-valid comparable segments are exact.
- Summary layer/reference are bound to the preprocessed common-average layer.
- Current-array physical unit is unresolved; no unit conversion is authorized.
- Six admission conditions remain `PASS, PASS, FAIL, PASS, PASS, PASS` under the historical strict full-release definition.
- No data card, scientific model, training, A selection, or Gate exists.

## New defect: NR5 is omitted from active anomaly summaries

The schema-v3 machine ledger contains six finite-multisample `EVENT_UNRESOLVED` rows distributed across YTL blocks 3, 5, and 6 as `1,1,4`. The full manifest's `files_with_semantic_anomaly` also lists NR3, NR5, and NR6. However, `scripts/audit_zuco2_nr.py` hard-codes the compact `ytl_anomaly_verdicts` path set to NR3 and NR6, and run/state/handoff repeat only those two paths.

Run 007 and schema-v3 artifacts remain immutable. The next active review/data card must name NR3/NR5/NR6 and add a regression test that derives YTL anomaly summaries dynamically.

## Revised admission policy

Two statuses must coexist:

1. `full_release_diagnostic=FAIL`, retaining unit and event anomaly findings.
2. `analysis_view_admission=PASS`, if and only if the committed ledgers reproduce 5,905 admitted rows and 377 exclusions with complete reasons and provenance.

The analysis view uses the already committed final predicate:

```text
content present
AND valid finite multisample EEG
AND valid event occurrence
AND exact segment correspondence
AND no exclusion reason
```

The data card records `UNRESOLVED_RELEASE_NATIVE_AMPLITUDE` and prohibits unit-sensitive use until the A-interface task. This does not infer µV. NeuroLM's official repository explicitly requires preprocessing to 200 Hz and µV, so NeuroLM remains blocked rather than forcing the dataset documentation to fail.

## Corrected next action

Activate SPEC v1.7 and run only `SPEC_V17_REVIEW -> S0_DATA_ADMISSION_POLICY_REPAIR -> S0_DATA_CARD`. Build deterministic analysis-view/data-card artifacts from committed schema-v3 files, fix the future YTL summary regression, update governance state, and stop with `S0_STIMULUS_ID` as the recommended task. Do not reread real EEG, rerun the targeted audit, search for units, select A, build splits, train, inspect outcomes, download data/weights, or run a Gate.

## Research sources

- ZuCo 2.0 paper and dataset scope: https://aclanthology.org/2020.lrec-1.18/
- NeuroLM official implementation and µV preprocessing requirement: https://github.com/935963004/NeuroLM
- Datasheets as transparent documentation of composition, intended use, and limitations: https://arxiv.org/abs/1803.09010
