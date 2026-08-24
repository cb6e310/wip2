# RC-HSG v2.4 A-path leakage pre-execution review

Date: 2026-08-24  
Reviewed remote: clean `main@dc105709563cf9eb216f1c28f82fdf754e7b0683`  
Decision scope: early Regime-I split/data/A-path leakage firewall only

## Verdict

Run 014 is accepted. The repository is in the exact intended v2.3 stop state: 70 tasks, 33 DONE,
8 SKIPPED, 28 BLOCKED, sole READY `S0_LEAKAGE_AUDIT`, owner `CODEX`, and test locked. The
bounded real frontend read 107 authorized outer-train rows, ledgered 44 short rows without source
dereference, passed CPU and conditional CUDA checks, and left 3,390 eligible outer-train rows plus
all calibration/test arrays unread.

The next valid action is a no-new-real-value audit of the already frozen A path. It is not another
frontend run and not full admission.

## Scientific decision

Reopening the 107 rows would add data exposure without strengthening the leakage conclusion.
Opening the remaining 3,390 rows would improperly merge this task with `S0_A1_ADMISSION`.
Therefore the production audit reads only committed code and metadata. It must not import or run
the frontend validator, open HDF5, or access the production dataset root.

The audit uses three complementary evidence types:

- committed split, eligibility, panel and frontend-freeze cross-checks;
- function-scoped AST assertions over the actual value path and per-row A preprocessing;
- in-memory negative mutations plus repository-external synthetic fixtures.

Static inspection alone is not treated as proof. A PASS requires all three evidence types, exact
hashes, deterministic outputs, and the existing synthetic loader tests.

## Frozen firewall

The audit mechanically checks 12 domains: split roles, row keys, short bypass, dereference scope,
source identity, exact HDF5 field/slot, numeric transforms, per-row preprocessing, inference-only
execution, no value/text/outcome/cache writes, fail-closed determinism, and test/downstream lock.

It also injects 12 prohibited changes in memory. Examples include adding `cal` to the real-read
roles, deleting the selected-key/read-flag guard, switching HDF5 to write mode, reading `content`,
using another slot, removing the valid-length slice, fitting across rows, training/backward, saving
a cache, adding a dataset CLI override, and dereferencing short rows. Every mutation must be
rejected by the corresponding semantic assertion.

## Claim boundary

A successful run may conclude only:

`EARLY_REGIME_I_SPLIT_DATA_AND_FROZEN_A_PATH_LEAKAGE_FIREWALL_PASS`.

It does not establish full outer-train admission, full method leakage safety, semantic schema
validity, candidate/reference/calibration safety, model quality, or any Gate result. The later
`S0_METHOD_LEAKAGE_AUDIT` remains mandatory before route lock and the main experiment.

## Expected run-015 stop state

Run 015 adds/completes `SPEC_V24_REVIEW`, completes `S0_LEAKAGE_AUDIT`, leaves B_V9 active, and
stops with 71 tasks, 35 DONE, 8 SKIPPED, 27 BLOCKED and sole READY `S0_A1_ADMISSION`, owner
`CODEX`. The 3,390 remaining eligible outer-train arrays are still unread and test remains locked.

Any fixed-state/hash conflict is `STATE_SPEC_CONFLICT`. Any audit input, assertion, mutation,
determinism or output failure is `A_PATH_LEAKAGE_AUDIT_BLOCKED`. Neither may be repaired by
changing the scientific scope, relaxing a guard, reading real data, or skipping a negative test.
