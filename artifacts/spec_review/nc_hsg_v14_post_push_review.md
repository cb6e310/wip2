# NC-HSG v1.4 post-push review

Date: 2026-08-16  
Reviewed remote: `https://github.com/cb6e310/wip2`  
Reviewed commit: `250ca9a67cf386784005a1edbbfe502d7df6f192`

## Verdict

Run 004 is accepted as reproducible governance hardening and outcome-blind input discovery, but it is not accepted as a complete recovery state. The repository has one active-SPEC conflict that its validator misses, and its stated user blocker is partly false because the official OSF API exposes a named ZuCo 2.0 license.

The next run must be a narrow repair and targeted NR data admission. It must not repeat broad discovery, choose a backbone, download data/weights, train, or run a Gate.

## Independent checks reproduced

- `python3 -m unittest discover -s tests -p 'test_project_memory.py'`: 34/34 PASS.
- `python3 -m unittest discover -s tests -p 'test_audit_input_sources.py'`: 7/7 PASS.
- `python3 scripts/check_project_state.py`: PASS, 38 tasks, 7 DONE.
- `python3 scripts/project_status.py`: exit 0, stage 0 BLOCKED, no READY task.
- `git diff --check`: PASS.
- worktree was clean after fast-forward to the reviewed commit.

These checks reproduce the implementation. They do not erase the validator coverage gap below.

## Defects found

### D1 — active SPEC conflict

`AGENTS.md` declares `guide/NC_HSG_Paper_Spec_v1_2_2026-08-16.md` as the active scientific source. `AI_START_HERE.md`, `PROJECT_STATE.yaml`, `HANDOFF.md`, and the run-004 state declare v1.3. Under `AGENTS.md` itself this is `STATE_SPEC_CONFLICT` and work should stop. The validator fixture does not materialize/check `AGENTS.md`, so all tests pass despite this conflict.

Required repair: activate v1.4 in every entry point and add positive/negative tests proving that an AGENTS path/version drift fails closed.

### D2 — false external license blocker

Run 004 examined an empty `attributes.node_license` copyright holder/year and concluded that the OSF node had no recognizable license. The same node response contains `relationships.license`, which resolves as follows:

- node API: `https://api.osf.io/v2/nodes/2urht/`
- license id: `563c1cf88c5e4a3877f9e96a`
- license API: `https://api.osf.io/v2/licenses/563c1cf88c5e4a3877f9e96a/`
- official name: `CC-By Attribution 4.0 International`

Therefore the user does not need to supply a separate license file. The next run must save a compact, hashed response excerpt and prove that the local tree is the OSF tree.

### D3 — broad scanner skipped safe code under the dataset path

`scripts/audit_input_sources.py` classifies any file whose path contains a `datasets` component as data before considering its suffix. As a result, the two official `.py` readers under the ZuCo directory were not hashed/read. This is safe but too coarse for admission.

Official OSF reader identities:

| File | Bytes | SHA256 |
|---|---:|---|
| `scripts/python_reader/read_matlab_files.py` | 1,610 | `daf147dee64cf53ae55050a3d19d0ea37d8811057cd9de3cfb2bc7f29fb91712` |
| `scripts/python_reader/data_loading_helpers.py` | 10,137 | `90e3bab7d082891b4b53fcb154286d8a73eea0f3fa89a312176025f035cfa71c` |

The local inventory reports matching sizes. Targeted local hashes are sufficient; do not rerun the 8,020-entry scan.

### D4 — incorrect cross-reference

The current `CODEX_NEXT_TASK.md` says the six data-admission conditions are in “v1.3 section 6.2,” but SPEC §6.2 is the method fairness contract. The six conditions were in the previous handoff instruction. The next state must copy these six conditions into a task acceptance/evidence record or name the correct immutable artifact.

### D5 — evidence snapshot is unnecessarily noisy for daily use

`artifacts/admission/input_source_inventory.yaml` is about 1.9 MB and 54,129 lines. It is valid run-004 evidence, but its 8,020 entries mostly do not help the next decision. Preserve it; do not regenerate it. Add a compact NR-only manifest for active use.

## New outcome-blind source evidence

The official ZuCo 2.0 OSF file tree contains the same top-level folders seen locally and exposes the two reader hashes above. The official 2020 data paper reports 500 Hz, a 128-channel Geodesic HydroCel acquisition, Cz recording reference, and 105 scalp channels after preprocessing. The ZuCo-author 2023 benchmark additionally reports common-average reference for the processed data and the following 24 excluded EGI labels:

`E1,E8,E14,E17,E21,E25,E32,E48,E49,E56,E63,E68,E73,E81,E88,E94,E99,E107,E113,E119,E125,E126,E127,E128`.

This list is only an expected contract. The next run must read local `EEG.chanlocs` labels/coordinates and compare exactly; it may not copy the list into a data card as if it came from the physical files.

The OSF file API also exposes SHA256 for all 18 `task1 - NR/Matlab files/results*_NR.mat` files. Their official total is 34,591,109,519 bytes. Every local size recorded by run 004 matches its official counterpart exactly; local SHA256 remains to be computed in the next run. This makes a 34.6 GB one-pass hash audit sufficient and avoids touching the 117 GB archive or downloading data.

## Next decision

The next run is permitted to read non-outcome metadata from the existing NR files and the actual stimulus text needed to build stable stimulus IDs. It may not read historical model outputs or held-out/test metrics. If all six admission conditions pass, `S0_DATA_CARD` may be completed in the same run. `S0_A_INTERFACE` remains blocked pending a later ChatGPT/author choice based on the returned physical interface.

