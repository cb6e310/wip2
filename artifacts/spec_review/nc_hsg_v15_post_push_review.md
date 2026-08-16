# NC-HSG v1.5 post-push review

Date: 2026-08-16  
Reviewed remote: `https://github.com/cb6e310/wip2`  
Reviewed commit: `d6751eadd96b2f651e5dbd1bfd5366679688ce4d`

## Verdict

Run 005 is accepted as a reproducible active-SPEC repair, license/hash audit, and first bounded pass over ZuCo 2.0 NR metadata. Its data-admission conclusion is not accepted: the committed script and artifacts contradict the claims that there are zero missing assignments and that condition 3 fails only on the physical unit.

The next run must correct the targeted auditor and active state before any data card, backbone selection, split, training, or Gate. This is a bounded evidence repair, not a new broad discovery.

## Independent checks

- Remote `main` and HEAD resolve to `d6751eadd96b2f651e5dbd1bfd5366679688ce4d`; local fast-forwarded worktree is clean.
- `python3 -m unittest discover -s tests -p 'test_project_memory.py'`: 38/38 PASS.
- `python3 -m unittest discover -s tests -p 'test_audit_input_sources.py'`: 8/8 PASS.
- `python3 scripts/check_project_state.py`: PASS, 41 tasks, 10 DONE.
- `python3 scripts/project_status.py`: exit 0, stage 0 BLOCKED, no READY task.
- `git diff --check`: PASS.
- The independent client environment does not contain `h5py`; therefore `test_audit_zuco2_nr.py` was not locally reproduced. Run 005 records 8/8 PASS on the server, but that record is not silently upgraded into an independent check.

## Correct work retained from run 005

- All active-SPEC entry points now agree on v1.4, and the validator covers drift/missing entry points.
- The official OSF node license is CC BY 4.0.
- The 18 NR summary MATs, 7 NR material CSVs, and 2 official readers are 27/27 local SHA256 matches to OSF metadata.
- The view contains 18 subjects × 349 summary slots, 126 preprocessed NR block files, 105 stable channels with complete coordinates, 500 Hz sampling, Cz acquisition reference, and common-average processed reference.
- No historical result metric, model prediction, training, checkpoint deserialization, data download, or Gate is evidenced in run 005.

## Material defects

### D1 — non-finite placeholders are reported as EEG present

`audit_summary()` defines presence as a non-null reference with `size > 0`. The committed JSONL therefore marks every row `raw_data_present: true` and every `missing_reason: null`.

The same artifacts show 367 rows with `raw_shape: [1,1]`, `raw_axis_contract: unresolved`, and an aggregate 367 non-finite numeric elements. These are non-finite placeholders, not usable EEG time series. A truthful ledger must distinguish reference presence, structural validity, finiteness, and model-usable sequence presence.

Affected subject counts are YFR 106, YAC 102, YRH 52, YAK 51, YFS 13, YRK 10, YMD 7, YLS 6, YRP 6, YSL 6, YDR 3, YMS 3, YSD 1, and YTL 1.

### D2 — four one-sample rows are hidden in the valid-axis total

Four YTL rows have shape `[1,105]`. They satisfy the current last-axis test but are not a multi-sample sentence time series. They must be a separate `FINITE_SINGLE_SAMPLE_REVIEW_REQUIRED` class. No backbone-specific 200-sample cutoff is authorized here.

### D3 — 180 block-null rows are deterministically recoverable

The current code maps a text hash to a set of blocks. Five repeated texts occur in multiple blocks, leaving 180 subject-slot rows with `block: null`.

The material CSVs contain 370 rows. The author paper states that each of seven blocks is preceded by three practice sentences. Removing the first three rows of every CSV yields exactly 349 material rows with block counts 50/50/51/50/50/49/49. Their ordered hashes equal slots 1–349 for every one of the 18 subjects: 6,282/6,282 exact position matches. This is the correct fail-closed occurrence mapping. Repeated text remains one stimulus group but has distinct block/line occurrences.

### D4 — event recoverability is asserted from field names only

The auditor records the names `duration, latency, type, urevent, value`; the admission predicate checks only that `latency` and `type` names exist. It does not validate values, finite/monotone/in-range latency, trigger vocabulary, or a mapping to sentence boundaries. The report must not claim event semantics are recovered until a bounded event contract passes.

### D5 — summary layer/reference is inferred from a different file

For every preprocessed block, `summary_raw_data_layer` is assigned from that block's `EEG.ref`. This does not bind summary `sentenceData/rawData` to `EEG/data`, common-average reference, or a physical unit. The two stored layers need their own release-applicable provenance or a verified physical mapping.

### D6 — condition 3 omits the facts that could falsify it

The predicate currently checks channel count/coordinates, 500 Hz, reference values, event field names, and one unit value. It omits summary expected fields, raw shape, finiteness, missingness, ordered material mapping, exact block occurrence, event semantics, and summary-layer binding. Adding a unit string alone would therefore produce a false PASS.

## Unit evidence review

The official 2020 data paper and the ZuCo-author 2023 benchmark establish a 500 Hz acquisition, Cz reference, μV-valued artifact thresholds, and common-average processed reference. They do not explicitly say that the released `sentenceData/rawData` and `EEG/data` arrays are stored in μV or that no later scale transform occurred.

An open issue in the author-maintained benchmark repository asks this exact `rawData` unit question and has no answer. That is negative evidence against pretending the release binding is documented. The next run may inspect only small release-applicable metadata, scripts, wiki/README text, or an author answer; generic EEGLAB convention, plot units, thresholds, or numeric magnitude are insufficient alone.

## Corrected decision

Run 005 remains immutable evidence of the first audit. Active state must supersede, not rewrite, its conclusion:

- conditions 1, 2, 4, 5, and 6 remain supported;
- condition 3 remains FAIL, presently for unresolved stored-array unit/layer binding and unverified event semantics, plus an incorrect cell/missingness predicate that must be repaired;
- 367 non-finite invalid placeholders and 4 finite single-sample cells must be enumerated; missing cells are allowed only with an explicit exclusion contract, never by calling them present;
- exact block occurrence is recoverable and should be closed by the ordered practice-excluded sequence assertion;
- `S0_DATA_CARD` stays BLOCKED unless every corrected condition-3 subpredicate passes.

## Next action

Activate SPEC v1.5 and execute only `S0_ZUCO2_NR_ADMISSION_REPAIR`. Update code, synthetic tests, versioned admission artifacts/report, state, tasks, handoff, and one new immutable run record. If all six strict conditions pass, a data card may be generated in the same run; otherwise stop with an exact blocker. Do not select A, create splits, download data/weights, train, inspect outcomes, or run a Gate.
