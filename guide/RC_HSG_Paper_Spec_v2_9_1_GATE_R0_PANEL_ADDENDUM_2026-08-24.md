# RC-HSG v2.9.1 Gate R0 panel-law author addendum（2026-08-24）

> **Authority and scope.** This author-frozen addendum resolves the
> `STATE_SPEC_CONFLICT / TECHNICAL_ABORT_NO_OUTCOME` raised before run-020 read
> authorization. It supersedes only the v2.9 §28.4 assertion that the Gate R0
> panel must contain all `18 × 2 × 3 × 2 = 216` role-cells and every dependent
> expected panel count/hash. All other v2.9 §28 contracts—including fixed
> inputs, 3,497-row one-read allowlist, replicates `1/2/199`, transform and
> frontend paths, classifier/model/thresholds, nuisance and numerical audits,
> outcome rules, safety boundaries, state transitions, tests, commit/push, and
> hard stop—remain unchanged unless explicitly restated below.

> This is an outcome-blind contract repair. At adjudication time there had been
> zero production HDF5 dataset dereferences, zero EEG/text/outcome/test-identity
> reads, no Gate CLI execution, no scientific outcome, and no repository
> modification. The remote baseline remains
> `4fa6fadc8bdee0d163acc8bf9ee48aeac4d3095d`.

## 29.1 Conflict adjudication

The v2.9 216-row assertion incorrectly treated a theoretical Cartesian grid as
if every role-cell were physically populated. The frozen assignment proves:

```text
assignment path             artifacts/nulls/n1_block_assignment_v1.jsonl
assignment SHA256           d0acc5e5fe78bc36a69cb04b6f605983c675e49a764538ae1665f86a28acee04
assignment rows             3,541 = 3,497 eligible + 44 short
eligible rows               3,497
power_edge_status=PASS      3,493
INSUFFICIENT_TRAIN_CELL     4
theoretical role-cells      216
non-empty PASS role-cells   192
empty role-cells            24
```

The 216 grid is retained only as a structural-coverage diagnostic. It is not a
required panel row count and empty cells are not Gate failures. No row may be
borrowed across subject, role, length bin, or power bin; no row may be duplicated
or sampled with replacement to manufacture a missing cell.

Using all 192 non-empty role-cells would still be scientifically wrong for the
real-vs-N2 classifier: 16 strata occur in `train_fit` but not in `inner_val`.
The classifier panel therefore uses **cross-role matched support**, not the
union of role-specific support.

## 29.2 Frozen matched-support domain

Define a nuisance stratum

```text
q = (subject, length_bin, power_bin)
```

over the fixed domains:

```text
subject     = the 18 lexicographically sorted frozen subjects
length_bin  = W01_04, W05_16, W17_PLUS
power_bin   = P_LOW, P_HIGH
role        = train_fit, inner_val
```

A row is panel-eligible iff all of the following are true in the frozen
assignment:

```text
a_interface_status == ELIGIBLE
action == RUN_FRONTEND
role in {train_fit, inner_val}
length_bin in {W01_04, W05_16, W17_PLUS}
power_bin in {P_LOW, P_HIGH}
power_edge_status == PASS
```

For every one of the `18 × 3 × 2 = 108` theoretical nuisance strata, compute
`train_fit_n` and `inner_val_n` from those rows and assign exactly one status:

```text
MATCHED_SUPPORT  train_fit_n > 0 and inner_val_n > 0
TRAIN_ONLY       train_fit_n > 0 and inner_val_n == 0
INNER_ONLY       train_fit_n == 0 and inner_val_n > 0
ABSENT_BOTH      train_fit_n == 0 and inner_val_n == 0
```

The fixed expected result is:

```text
support-ledger rows         108
MATCHED_SUPPORT              88
TRAIN_ONLY                   16
INNER_ONLY                    0
ABSENT_BOTH                   4
```

The four `ABSENT_BOTH` strata are `YAK/W17_PLUS/P_LOW`,
`YAK/W17_PLUS/P_HIGH`, `YHS/W17_PLUS/P_LOW`, and
`YHS/W17_PLUS/P_HIGH`. The 16 `TRAIN_ONLY` strata and all counts must be derived
from the frozen assignment rather than copied from prose.

The matched-support ledger is written as UTF-8 JSONL to:

```text
artifacts/gates/gate_r0_matched_support_v1.jsonl
```

Rows are ordered by subject lexicographically, then length order
`W01_04 < W05_16 < W17_PLUS`, then power order `P_LOW < P_HIGH`. Each compact
JSON object has keys in this exact order:

```text
subject, length_bin, power_bin, train_fit_n, inner_val_n, support_status
```

There is exactly one LF after every row and no BOM. Its expected SHA256 is:

```text
3f2eb411e54c730453d1dd8a39c5bfeff0aa34ee278c545ac66d2f24b2af2246
```

Any count or digest mismatch is `TECHNICAL_ABORT_NO_OUTCOME` before any real
dataset dereference.

## 29.3 Deterministic 176-row panel law

For each of the 88 `MATCHED_SUPPORT` strata and each role, select exactly one
row. Candidate ranking uses no RNG and no outcome:

1. Build a canonical JSON object with fields
   `subject, role, length_bin, power_bin, slot, occurrence_id`.
2. Encode it as UTF-8 JSON with keys sorted lexicographically, no insignificant
   whitespace, `ensure_ascii=false`, and JSON integer encoding for `slot`.
3. Compute

   ```text
   SHA256(UTF8("RC_HSG_GATE_R0_MATCHED_PANEL_V1") || 0x00 || canonical_json)
   ```

4. Within a role-cell, choose the lexicographically smallest tuple
   `(selection_sha256, slot, occurrence_id)`.

The panel is written as UTF-8 JSONL to:

```text
artifacts/gates/gate_r0_panel_v1.jsonl
```

Panel order is subject lexicographically, then the frozen length order, then the
frozen power order, then role order `train_fit < inner_val`, then
`slot, occurrence_id`. Each compact JSON object has keys in this exact order:

```text
subject, session, role, length_bin, power_bin, slot, occurrence_id,
raw_samples, window_count, source_file, source_field, selection_sha256
```

There is exactly one LF after every row and no BOM. The fixed expected result is:

```text
panel rows                  176
train_fit rows               88
inner_val rows               88
subjects                     18
matched strata               88
panel SHA256                 2cffa7699e7a29eee4996172a20707678ba1ec3529d35e32b2ca453ad79aa806
```

Expected panel rows per subject, counting both roles, are:

```text
YAC 10  YAG 12  YAK 8   YDG 10  YDR 10  YFR 10
YFS 10  YHS 8   YIS 10  YLS 12  YMD 6   YMS 12
YRH 10  YRK 10  YRP 10  YSD 10  YSL 10  YTL 8
```

Codex must implement two independent metadata-only reconstructions—production
builder and test/oracle code—and require byte-identical ledgers and panel
digests before authorizing any real read. Neither implementation may contain a
literal list of selected row keys.

## 29.4 Relation to the 3,497-row full audit

The panel repair does **not** reduce the full Gate scope:

```text
full numerical / safety audit              all 3,497 eligible rows
matched classifier/nuisance panel             176 rows
eligible rows outside matched panel         3,321 rows
short rows                                    44 rows, zero array reads
calibration/test arrays                         0 reads
text/outcome/test identity                       0 reads
```

The four eligible `INSUFFICIENT_TRAIN_CELL` rows—YAK train-fit slot 307, YAK
inner-val slot 323, and YHS train-fit slots 11 and 16—remain in the 3,497-row
full numerical/safety audit. They are excluded only from the matched panel
because they have no frozen power bin. Their exclusion from the panel is not an
EEG exclusion and must not be reported as loss of the admitted population.

During the single authorized read of each eligible array, v2.9 replicates
`1, 2, 199` and all v2.9 full diagnostics remain unchanged. Panel-specific A1
tokens/features are retained only under the original v2.9 in-memory and
no-persistence rules, and only for the 176 pre-authorized panel keys.

## 29.5 Classifier and nuisance audit interpretation

The frozen v2.9 classifier, feature families, preprocessing, labels, model,
hyperparameters, bootstrap, thresholds, and decision rule are unchanged.
Training uses the 88 selected `train_fit` rows and evaluation uses the 88
selected `inner_val` rows, with the same real/N2 replicate construction already
specified by v2.9. Subject-macro evaluation still covers all 18 subjects.

The matched-support restriction is part of the pre-registered nuisance control:
every included `(subject, length_bin, power_bin)` stratum occurs in both roles.
Missing theoretical strata must be reported as structural support limitations,
not imputed, borrowed, silently dropped from denominators, or interpreted as a
scientific Gate failure. The support ledger and per-subject matched-stratum
counts must appear in the Gate report.

Gate thresholds remain exactly those in v2.9, including subject-macro AUC and
its bootstrap upper bound `<= 0.65`. The smaller, honest matched panel may widen
the bootstrap bound; that is a legitimate scientific result and must not be
countered by tuning, resampling, threshold changes, or panel expansion.

## 29.6 Mechanical outcome and state law

The prior abort remains provenance only:

```text
prior attempt status       TECHNICAL_ABORT_NO_OUTCOME
scientific Gate outcome    null
repository mutation        none
authorized retry           run-020 under v2.9.1
```

After the support/panel preflight passes, run-020 resumes the unchanged v2.9
Gate chain. Scientific PASS/FAIL and technical abort semantics remain v2.9
§28.7. The panel count repair alone is not a PASS and does not relax any Gate
threshold.

Importing v2.9 and v2.9.1 adds both review tasks. On a completed scientific
PASS or FAIL, the exact final task counts are:

```text
77 total / 46 DONE / 8 SKIPPED / 22 BLOCKED / 1 READY
```

The sole READY remains `S0_SEMANTIC_ITEM`, owner=`CHATGPT_OR_AUTHOR`; route
remains unlocked, test remains locked, all later Gate outcomes remain null, and
the v2.9 hard stop remains mandatory. `SPEC_V291_REVIEW` has prerequisite
`SPEC_V29_REVIEW` and is completed by run-020. A technical abort produces no
scientific outcome and must not perform this final state transition.

## 29.7 Active-spec assembly

This addendum is distributed beside the author-frozen original v2.9 package.
Before repository import, construct the cumulative active file mechanically:

```text
base = bytes(guide/RC_HSG_Paper_Spec_v2_9_2026-08-24.md).rstrip(CR/LF)
addendum = bytes(this file).lstrip(CR/LF)
active = base || LF || LF || addendum
output = guide/RC_HSG_Paper_Spec_v2_9_1_2026-08-24.md
```

The original v2.9 package SHA256 must be
`6d5e0327a1d8fc0477a787d014b01218a9427b1794a3830e81b020468c8ec2fc`.
Record the cumulative active-spec SHA256 in run-020 and all active entrypoints.
Historical specs, reviews, runs, and artifacts remain append-only.
