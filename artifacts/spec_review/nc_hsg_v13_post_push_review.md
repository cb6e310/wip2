# NC-HSG v1.3 Post-Push Review

Date: 2026-08-16  
Review mode: outcome-blind repository, governance, and public-source review  
Reviewed remote: `https://github.com/cb6e310/wip2`  
Reviewed commit: `1b836fe56970d262f4e8f3ae8262fd0abb670dbe`

## Verdict

The first Codex iteration successfully converted an empty remote into a recoverable project and correctly kept all scientific tasks blocked. The push is accepted as governance/environment evidence, not as evidence for EEG data, a backbone, null validity, a Gate, or a paper claim.

The repository is not ready for N1/N2 or model implementation. Its next high-value operation is a combined governance-hardening and restricted physical-input discovery run. This removes a real state-machine deadlock and collects the exact data/backbone facts needed for the next scientific decision without spending a run on speculative code.

## Independently reproduced checks

- Remote `main`: `1b836fe56970d262f4e8f3ae8262fd0abb670dbe`.
- Governance bootstrap commit: `76504c6bef46664b9fb265cbdba544de9d37da99`.
- Latest commit: `1b836fe56970d262f4e8f3ae8262fd0abb670dbe`, environment sync only.
- `python3 -m unittest discover -s tests -p 'test_project_memory.py'`: 19 tests, all PASS.
- `python3 scripts/check_project_state.py`: PASS, 35 tasks, 4 DONE.
- `python3 scripts/project_status.py`: PASS; Stage 0 BLOCKED; no READY task.
- `git diff --check`: PASS.
- Repository has no scientific source, physical dataset, checkpoint, or result path.

## Accepted progress

1. `AGENTS.md`, `AI_START_HERE.md`, state/tasks/handoff, immutable run records, validator, deterministic status output, and focused tests exist.
2. `S0_GOVERNANCE_BOOTSTRAP` and `S0_REPOSITORY_AUDIT` have physical evidence and conservative state.
3. The 103-entry `trust_align` package environment was synchronized and CUDA smoke-tested on the server. Its run record explicitly avoids claiming backbone/data admission.
4. Held-out/test metric content was reported unread, and no scientific implementation was added.

## Defects to repair before more science

| Severity | Finding | Required repair |
|---|---|---|
| Critical workflow | No task represents blocker resolution, so a valid state has zero READY tasks and cannot progress | Add `SPEC_V13_REVIEW`, `S0_GOVERNANCE_HARDENING`, and `S0_INPUT_DISCOVERY_AUDIT` with deterministic transitions |
| High | Root `CODEX_NEXT_TASK.md` still requests the completed bootstrap/audit | Replace it with the current task; archive only if provenance is needed |
| High | Three governance snapshots were modified by run 003 but still say `generated_by_run: ...002` with no revision marker | Add `updated_by_run`, `evidence_as_of_commit`, and run linkage, or make run-scoped immutable copies |
| High | Validator hardcodes `v1.2`/`v1_2` | Validate declared version against the active filename and spec header generically |
| High | `ROUTE_LOCK=DONE` can pass while `route.locked` is empty | Require exactly one allowed route, a valid `locked_by_run`, and no route before task completion |
| Medium | DONE checks prove paths exist but not which files satisfy acceptance | Add non-empty path-based `acceptance_evidence` for every DONE task and backfill governance tasks |
| Medium | `PROJECT_STATE.updated_by_run` is not required to match `last_run` | Add a consistency check and regression test |
| Medium | The mutable repository inventory mixes bootstrap-time and later dependency paths | Separate baseline facts from current snapshot revision facts |

## Outcome-blind data decision

The primary dataset candidate is now ZuCo 2.0 task 1 Natural Reading. Task 2 TSR is a task-shift robustness panel because it explicitly asks participants to search for semantic relations. The official paper reports 18 valid participants, 349 NR sentences, 390 TSR sentences, a single session per participant, 500 Hz/128-channel acquisition, and 105 scalp channels in the preprocessed analysis. These facts are expectations for physical verification, not an admitted data card.

The official OSF node `2urht` is public and the paper calls the data freely available, but the OSF license metadata available in this review did not expose a recognizable license name. The paper's publication license cannot be silently reused as the dataset license. Therefore full EEG download and `S0_DATA_CARD=DONE` remain forbidden until a local LICENSE/README, explicit OSF terms, or author authorization is preserved as evidence.

## Outcome-blind backbone decision

The next run must first audit whether `/home/song/projects/trust_align` contains a licensed, reproducible candidate backbone without opening historical metrics. It may not import that project's results or state.

The public fallback candidate is frozen as official NeuroLM-B + VQ:

- Code: `935963004/NeuroLM@0cda9876d8ce6ee07ed0c43eee5e9a6f5c24b177`, MIT.
- Model repository: `Weibang/NeuroLM@eddfff5c64a4139442f826d6c67c8369fd00f45a`, model card CC-BY-4.0.
- `NeuroLM-B.pt`: 2,377,399,148 bytes, SHA256 `ffe098bc138b89f8817d3710a3604498d8ecd15135080e2ca27735d05c6d29ab`.
- `VQ.pt`: 1,904,671,888 bytes, SHA256 `e792c39a6a9e6d1bf4604cf63090730424f1d37f942597883d0c0a1375a2663a`.
- Public code contract: 0.1–75 Hz, 50/60 Hz notch, 200 Hz, µV, 200-sample token patches, named `standard_1020` channel indices, time indices, and masks.

ZuCo's EGI HydroCel montage is not automatically compatible with NeuroLM's named channel embedding. Downloading the 4.28 GB fallback weights before a physical channel/montage compatibility audit would be premature. The next run therefore creates a compatibility matrix but does not download weights or invent an adapter.

## Next decision after Codex returns

Use the produced candidate ledgers to select exactly one A and either admit ZuCo 2.0 NR or issue one concrete data-license/path action. Only after V1 and V2 are physically resolved should the project execute `S0_DATA_CARD`, `S0_A_INTERFACE`, stimulus identity, split, and leakage work. N1/N2 remain downstream.

## Safety declarations

- Held-out/test metric content read: NO.
- Historical `trust_align` result content read: NO.
- Scientific implementation changed: NO.
- Scientific thresholds/Gates changed: NO.
- Training or model/data download performed: NO.
