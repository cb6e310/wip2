# Run 005 — Active SPEC Guard and ZuCo 2.0 NR Targeted Admission

Date: 2026-08-16  
Mode: outcome-blind governance repair and physical-input metadata audit

## Package and baseline

- v1.4 handoff ZIP SHA256: `8e8cdedc34fc1fd52be2f39c9cca2845a7f46aef3ba159490131d3a2e0cca70a`.
- All 4 manifest-listed payloads matched; path traversal, symlink, special-file, duplicate, and case-collision checks passed.
- Starting HEAD: `250ca9a67cf386784005a1edbbfe502d7df6f192`; branch `main`; origin `https://github.com/cb6e310/wip2`; worktree clean.
- Starting conflict reproduced: `AGENTS.md` named v1.2 while state, `AI_START_HERE.md`, and `HANDOFF.md` named v1.3. Recorded as `STATE_SPEC_CONFLICT` and repaired under explicit authorization.

## Active SPEC repair

- Activated `guide/NC_HSG_Paper_Spec_v1_4_2026-08-16.md`, reviewed against baseline `250ca9a67cf386784005a1edbbfe502d7df6f192`.
- Synchronized `AGENTS.md`, `AI_START_HERE.md`, `PROJECT_STATE.yaml`, `HANDOFF.md`, package handoff, and governance matrix.
- Validator now dynamically checks state path/version in all three recovery entry points and uses `ENTRYPOINT_SPEC_MISMATCH`; missing files fail closed.
- Fixture now materializes all three entry points. Added consistent-state, wrong AGENTS path, wrong AI entry version, and missing AGENTS tests.
- Fixed the narrow broad-scanner bug: small safe `.py`, README, and LICENSE text under dataset paths may be hashed; `.mat/.set/.fdt/.pkl/.pt` remain unopened. No broad scan was rerun.

## Official metadata evidence

- Node API: `https://api.osf.io/v2/nodes/2urht/`
- License API: `https://api.osf.io/v2/licenses/563c1cf88c5e4a3877f9e96a/`
- OSF file metadata: `https://api.osf.io/v2/nodes/2urht/files/osfstorage/`
- Official dataset paper inspected for acquisition/preprocessing metadata: `https://aclanthology.org/2020.lrec-1.18/`
- Retrieval UTC: `2026-08-16T10:14:54.843256+00:00`
- License relationship/name: `563c1cf88c5e4a3877f9e96a` / `CC-By Attribution 4.0 International`
- Raw response SHA256: node `9c2be2df138fce2ac9917b7dc416b897940cc77b8391de4c8742f22614cd4a13`; license `32fb3d7b32be0843803f96424fe7739f69574481211a2d323e16f8da8536c635`.

## Targeted physical audit

- Implemented `scripts/audit_zuco2_nr.py` and 8 focused synthetic tests.
- Local-to-OSF: 27/27 exact SHA256 matches; 0 mismatches; 0 missing official hashes. The 18 summary files total 34,591,109,519 bytes.
- MAT boundary: MATLAB v7.3 HDF5 selective access only. Summary numeric leaves were checked by HDF5 reference/chunk for shape and finite aggregates; no complete EEG struct was loaded or value emitted.
- Summary schema: 18 subjects × 349 slots = 6,282 assignments; 22 consistent sentence fields; 0 missing assignments.
- Preprocessed metadata: 126 blocks; 105 channels; one label/order hash; one coordinate hash; complete X/Y/Z/theta/radius; 500 Hz; acquisition reference `Cz`; processed reference `common-average`; event `type`/`latency` present; trials 1.
- Expected peripheral exclusion labels remaining: 0/24.
- Unit metadata: not recoverable (`unit_values: []`, `unit_candidate_paths: []`). The paper's microvolt-scale artifact criteria/figures do not explicitly bind the stored arrays to a storage unit. This is the exact V1 blocker.
- Stimuli: 344 unique normalized identities, 5 exact cross-block duplicate groups, 0 unmatched identities, and no committed source text.
- Byte stability: second full real audit matched both final output files byte-for-byte.

## Admission decision

Six conditions: `PASS, PASS, FAIL, PASS, PASS, PASS`. Overall `FAIL` solely because the physical EEG unit is not recoverable. `S0_ZUCO2_NR_TARGETED_ADMISSION` is DONE because the bounded audit is complete; this does not mean data admission passed. `S0_DATA_CARD` remains BLOCKED and no data card files were generated.

## Safety declarations

- `historical_metric_content_read: false`
- `held_out_or_test_metric_content_read: false`
- `training_run: false`
- `weights_or_data_downloaded: false`
- `backbone_selected: false`
- `gate_run: false`
- `broad_scanner_rerun: false`
