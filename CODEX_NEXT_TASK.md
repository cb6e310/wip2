# Codex Next Task - RC-HSG v2.2 / S0_A1_FRONTEND

## Current state

Run 013 completed `SPEC_V22_REVIEW -> S0_A_INTERFACE`. The exact clean-room
`RC_HSG_NATIVE_SPECTRAL_A1_V1` interface is implemented and synthetic-tested;
the metadata overlay retains all 5,905 rows, with 5,832 eligible and 73 forced
to L0 without frontend invocation. `S0_A1_FRONTEND` is the sole READY and
recommended task, owned by `CODEX`.

## Required next instruction

Wait for a new exact execution directive for `S0_A1_FRONTEND`. That task may
validate the frozen interface on authorized outer-train real tensors, including
finite-value, mask, device, memory, and deterministic tensor checks. It may not
alter the API, preprocessing, bands, windows, model architecture, short-row
route, split, population, or test lock.

## Evidence boundary

Run 013 used only generated synthetic tensors and committed metadata. It is not
real-data frontend admission, training, representation-quality, reference,
performance, or Gate evidence. `B_V8_A_REAL_FRONTEND_UNVALIDATED` remains
active. Test remains `LOCKED_UNTIL_ROUTE_LOCK`.

## Hard stop

Do not execute `S0_A1_FRONTEND` without the next exact directive. Do not infer
units, train, implement admission/F/schema/candidates/N1/N2/reference/
reliability/calibration/baselines, run the full leakage audit or any Gate,
change split/population/bootstrap, read semantic/calibration/test outcomes, or
unlock test.
