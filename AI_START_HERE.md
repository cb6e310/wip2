# AI Project Entry Point

This file is the mandatory entry point for every new AI or Codex session.
Repository state comes from files and physical evidence, never chat history.
The root `AGENTS.md` makes this recovery contract automatically discoverable.

## Verified project location

- Server: `song@10.244.144.87`
- Project root: `/home/song/projects/trust_generative`
- Python: `/home/song/projects/trust_generative/.venv/bin/python`
- Git remote: `https://github.com/cb6e310/wip2`
- Branch: `main`

## Source of truth

1. `guide/NC_HSG_Paper_Spec_v1_2_2026-08-16.md`
2. `PROJECT_STATE.yaml`
3. `HANDOFF.md`
4. `TASKS.yaml`
5. The current task's code, tests, artifacts, and run records

The active scientific route is NC-HSG. Older SPEC files are retained for
provenance but are not active. The example archive named
`wip_v3_11_711340d_review_n10_common_support.zip` belongs to another project
and is only a formatting reference. Never import its routes, task statuses,
blockers, commit IDs, hashes, dataset findings, or evidence.

## Required recovery sequence

Read in this order:

1. `PROJECT_STATE.yaml`
2. `HANDOFF.md`
3. `TASKS.yaml`
4. Relevant v1.2 SPEC sections
5. The current task's physical evidence paths

Then run:

```bash
.venv/bin/python scripts/check_project_state.py
.venv/bin/python scripts/project_status.py
```

Before changing files, print:

```text
PROJECT SNAPSHOT

Current stage:
Current route:
Completed prerequisites:
Active blockers:
Ready tasks:
Recommended next task:
Why:
Do not do yet:
```

If state, tasks, evidence, and the SPEC disagree, report
`STATE_SPEC_CONFLICT` and stop rather than guessing.

## Current boundary

- This is the first NC-HSG iteration.
- The GitHub remote was empty before this governance bootstrap.
- The pre-bootstrap server directory contained only the management contract
  and an older v1 SPEC; no scientific source, dependency manifest, dataset,
  checkpoint, result path, or pre-existing test was found.
- `SPEC_V12_REVIEW`, `S0_GOVERNANCE_BOOTSTRAP`, and
  `S0_REPOSITORY_AUDIT` are governance/specification evidence only. They are
  not model, data, Gate, or result evidence.
- No scientific task is READY until its recorded physical-evidence blocker is
  resolved. Do not invent a dataset path or backbone.
- Do not implement scientific modules, train, download data, read held-out
  metrics, or run a Gate under the governance task.

## State discipline

- Allowed statuses are `TODO`, `READY`, `IN_PROGRESS`, `DONE`, `BLOCKED`,
  `FAILED`, `SKIPPED`, and `TERMINATED`.
- `READY` requires every prerequisite `DONE` and no active blocker naming the
  task.
- `DONE` requires existing `produces`, satisfied acceptance criteria, a
  `completed_by_run`, and a corresponding physical run record.
- Code that exists but has not been validated is `IN_PROGRESS`, never `DONE`.
- Missing or ambiguous facts create a blocker; they are not guessed from
  filenames or documentation claims.
- Gate A1 precedes semantic work; Gate A precedes calibration/method
  comparison; Gate B precedes route lock; route lock precedes the test/main
  experiment.

## End-of-session contract

Before ending any state-changing session:

1. Update `PROJECT_STATE.yaml`.
2. Update affected entries in `TASKS.yaml`.
3. Replace `HANDOFF.md` with a concise current handoff.
4. Add one immutable `runs/YYYY-MM-DD_<id>.md` record.
5. Run `scripts/check_project_state.py`, `scripts/project_status.py`, relevant
   tests, and `git diff --check`.
6. Record exact tests, artifacts, hashes, state transitions, blockers, and the
   next task.

Scientific thresholds may only change through a new versioned SPEC before the
affected results are read. Never change a Gate merely to make it pass.
