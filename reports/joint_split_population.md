# ZuCo 2.0 NR Joint Split and Gate-A Population

## Frozen assignment

Policy `NC_HSG_JOINT_SPLIT_POLICY_V1` uses fixed hash initialization and integer pair-swap balancing. No seed or alternative split was searched.

- Primary swaps: 25
- Primary objective: (201, 804726, 344, 651510, 201, 76266)
- Primary ledger SHA256: `531539ff3592cc28d89c5e3ef568d019eaab733ccdb1053c1fcf1c471e9dac1c`
- Calibration-reserve swaps: 6
- Calibration-reserve objective: (34, 30056, 34, 2312, 34, 2312)
- Calibration-reserve ledger SHA256: `5f464d97e695ab6bc58d10ac2342351195fa936144487bd9e78f96e5e7a8442c`

## Regime I

- train_fit: 164 groups, 167 occurrences, 2832 rows
- inner_val: 41 groups, 42 occurrences, 709 rows
- cal: 68 groups, 69 occurrences, 1171 rows
- test: 69 groups, 71 occurrences, 1193 rows

All 342 groups and 5,905 admitted assignment rows are covered once. Test identities are `LOCKED_UNTIL_ROUTE_LOCK`.

## Regime II and population

Regime II contains 18 LOSO folds that reuse the frozen group roles and prohibit held-out-subject adaptation.
Gate-A population policy `NC_HSG_GATE_A_POPULATION_V1` freezes equal-weight subject macro aggregation and a 10,000 x 18 paired subject bootstrap.
Bootstrap index-byte SHA256: `e77ca92b29c414a17c1e66edf4075edd470c007dfe2019487c36758f5f99c86d`

No random split, source text, raw signal metadata, scientific statistic, test result, training, backbone selection, leakage audit, or Gate execution is present.
