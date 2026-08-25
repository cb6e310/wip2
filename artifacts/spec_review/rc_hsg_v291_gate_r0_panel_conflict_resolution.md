# RC-HSG v2.9.1 Gate R0 panel conflict resolution

## Decision

The reported `STATE_SPEC_CONFLICT / TECHNICAL_ABORT_NO_OUTCOME` is valid. Codex
stopped at the correct boundary: the fixed assignment contains only 192
non-empty PASS role-cells, so a 216-unique-row panel cannot be constructed
without violating the frozen no-borrow/no-duplication law.

The repair is **not** to change 216 to 192. The 192 role-cells are not
cross-role balanced: 16 `(subject, length_bin, power_bin)` strata exist only in
`train_fit`, four are absent in both roles, and none exist only in `inner_val`.
Using all 192 would change the training nuisance distribution relative to the
validation distribution.

The author-level replacement is a 176-row matched-support panel:

```text
108 theoretical subject/length/power strata
 88 present in both train_fit and inner_val -> 176 selected rows
 16 train_fit-only                         -> full audit only
  0 inner_val-only
  4 absent in both roles
```

One deterministic row is selected from each role in each of the 88 matched
strata. This preserves the original scientific intent—equal role counts and
identical subject/length/power support—while representing the actual frozen
data rather than an impossible Cartesian product.

## Evidence checked

Remote `main` remains
`4fa6fadc8bdee0d163acc8bf9ee48aeac4d3095d`. The assignment artifact SHA256 is
`d0acc5e5fe78bc36a69cb04b6f605983c675e49a764538ae1665f86a28acee04`.
Metadata-only reconstruction gives:

```text
3,541 assignment rows
3,497 eligible rows
3,493 PASS power-edge rows
4 INSUFFICIENT_TRAIN_CELL rows
192 non-empty role-cells
24 missing role-cells
88 matched strata
176 matched panel rows (88/88 by role)
```

The frozen selection law in the addendum gives panel SHA256
`2cffa7699e7a29eee4996172a20707678ba1ec3529d35e32b2ca453ad79aa806`
and 108-row support-ledger SHA256
`3f2eb411e54c730453d1dd8a39c5bfeff0aa34ee278c545ac66d2f24b2af2246`.

## Scientific consequences

- Full numerical/safety auditing still covers all 3,497 eligible arrays exactly
  once; the Gate is not reduced to 176 rows.
- The four rows without a power bin remain in the full audit and are excluded
  only from the nuisance-matched classifier panel.
- The classifier keeps 88 independent `inner_val` panel rows, the same count
  that the naïve 192-role-cell union would have supplied; it drops only 16
  train-only rows that lack validation support.
- Subject-macro evaluation still includes all 18 subjects. YMD has the smallest
  matched support (three strata, six panel rows across roles), which must be
  disclosed.
- The `<=0.65` AUC/UCB threshold is unchanged. Reduced honest support can widen
  uncertainty; that is not grounds for post-hoc tuning.

## Safety/provenance conclusion

No outcome existed when this decision was made. The prior attempt performed no
production dataset dereference, EEG/text/outcome/test-identity read, Gate CLI,
repository edit, commit, or push. The correction is therefore outcome-blind
and author-frozen before the first scientific read.
