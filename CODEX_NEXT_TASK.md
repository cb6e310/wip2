# Codex next task: STOP after run 016

Authoritative SPEC: `guide/RC_HSG_Paper_Spec_v2_5_2026-08-24.md`, especially §24.

Run 016 completed:

```text
SPEC_V25_REVIEW
-> S0_A1_ADMISSION
-> S0_N1_BLOCK_FEASIBILITY READY
-> STOP
```

The repository state is 72 tasks, 37 DONE, 8 SKIPPED, 26 BLOCKED, and sole
READY `S0_N1_BLOCK_FEASIBILITY`, owner `CHATGPT_OR_AUTHOR`. B_V9 is closed;
B_V4 remains active but does not block its resolver. Route remains unlocked and
test remains `LOCKED_UNTIL_ROUTE_LOCK`.

Full outer-train A1 admission passed. Run 014 panel evidence covers 107 rows
without run-016 rereads; run 016 scanned the remaining 3,390 eligible rows once.
The cumulative ledger covers 3,497 eligible rows, 35,745 windows, and 44 short
forced-L0 rows with no short dereference.

`S0_N1_BLOCK_FEASIBILITY` has not been executed and is not authorized by the
run-016 package. A new ChatGPT/author contract must freeze length and
train-frozen power bins, feasibility metrics, K=199 thresholds, tolerances,
singleton handling, no-adjacent-borrowing behavior, and failure routing. Do not
compute power summaries, implement N1/N2, train, execute any Gate, run the
method leakage audit, or unlock test under the current authorization.
