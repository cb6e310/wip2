# NC-HSG v2.0 post-push review

Date: 2026-08-23  
Reviewed remote: `https://github.com/cb6e310/wip2`  
Reviewed commit: `e852e7de24c31410387ad46d75fb44a5cac9e850`

## Verdict

Run 010 is accepted. The frozen stimulus policy is reproduced by fresh tests and two repository-external builds: 349 occurrences map exactly once through 344 exact identities into 342 groups; kinds are 335 singleton, five exact-duplicate-occurrence and two near-duplicate-leakage-risk groups. No split, text, model or outcome was introduced.

SPEC v2.0 authorizes the next executable chain. Regime I uses exact group capacities 205/68/69 for outer-train/cal/test, with outer train divided 164/41 into train-fit/inner-val. The split is not a searched random seed: a fixed hash initialization plus integer, deterministic pair-swap objective balances subject coverage, block occurrences and occurrence count. Calibration receives two frozen 34-group reserves without prematurely selecting the later calibration theorem.

Regime II is fixed to 18 LOSO folds because the admitted dataset has one session. Every fold holds out both one subject and the frozen test stimulus groups; no held-out-subject adaptation is allowed. The same run may freeze the already-required subject-macro population and bootstrap-index contract because both are derivable from the split without outcomes. It must then stop at owner-only `S0_A_POLICY_REVIEW`.

## Independent checks

- Fresh clone `HEAD=origin/main=e852e7de24c31410387ad46d75fb44a5cac9e850`; worktree clean before review artifacts.
- Entry points, state, tasks, run 010 and physical evidence agree; validator reports 52 tasks, 23 DONE and sole READY task `S0_JOINT_SPLIT`.
- Identity 12/12, similarity 12/12, analysis-view 11/11, governance 38/38 and input-audit 8/8 tests PASS; `git diff --check` PASS.
- Local environment lacks `h5py`, so targeted audit import fails here and is not claimed as reproduced; run 010 records server 21/21 PASS.
- Two new identity production builds reproduce SHA256 `f6b94449...a69ea`, `4408e57d...fded`, and `de83ea58...a465`.
- Independent split simulation reproduces 25 primary swaps, objective `(201,804726,344,651510,201,76266)`, group-role SHA256 `531539ff...ac1c`; calibration reserve uses six swaps, objective `(34,30056,34,2312,34,2312)`, SHA256 `5f464d97...42c`.
- Frozen role counts are 164/41/68/69 groups, 167/42/69/71 occurrences and 2,832/709/1,171/1,193 rows. Every role covers all 18 subjects.
- The 10,000×18 counter-hash bootstrap index bytes reproduce SHA256 `e77ca92b...c86d`.

## Required transition

```text
SPEC_V20_REVIEW
-> S0_JOINT_SPLIT
-> S0_GATE_A_POPULATION_E5
-> S0_A_POLICY_REVIEW (READY; ChatGPT/author; stop)
```

Do not execute full leakage audit, choose backbone A, infer physical units, read test outcomes, train, implement later-stage methods or run a Gate.
