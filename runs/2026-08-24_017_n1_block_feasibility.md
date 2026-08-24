# Run 017: outcome-blind N1 block feasibility

Date: 2026-08-24

## Authorization and baseline

- Task chain: `SPEC_V26_REVIEW -> S0_N1_BLOCK_FEASIBILITY -> DEGRADED_COVERAGE branch -> STOP`.
- Repository: `/home/song/projects/trust_generative`, branch `main`.
- Fetched clean baseline: `HEAD=origin/main=1c432a02f50cacda99359f630f14cfbfdfb439a1`.
- Baseline state: 72 tasks, 37 DONE, 8 SKIPPED, 26 BLOCKED, sole READY `S0_N1_BLOCK_FEASIBILITY`; B_V9 closed, B_V4 active, route unlocked, test locked.
- Package ZIP SHA256: `8e32733de196743cf928d793e58203a1984980578d18519f186d3e273265054b`.
- Safe repository-external extraction and every `PACKAGE_MANIFEST.sha256` entry passed.
- Only the three `PROJECT_IMPORT_MANIFEST.txt` files were imported:
  - `guide/RC_HSG_Paper_Spec_v2_6_2026-08-24.md`: `174f0ee08870cc045a75336d3fc7138c97a99e78e5adfb109aed74b5c5144aaa`
  - `artifacts/spec_review/rc_hsg_v26_n1_block_feasibility_review.md`: `b44e0a97c57d8e51e3e8365c56781c88b37328acc28d21f40f070e876d421e87`
  - package-source `CODEX_NEXT_TASK.md`: `af15833cd2765a906d1f668c898722316f348874a8ef045ca315c19927613b13`

## Implementation and execution

- Implementation: `scripts/audit_n1_block_feasibility.py`, SHA256 `beb4c739c05a225b5fe41e796a6d7a7c0fa60239d6b14dab51f28ba6d83d75ad`.
- Tests: `tests/test_audit_n1_block_feasibility.py`, SHA256 `e5aba6f3218c2faf44c8196e80d6d34774a91e0e5a910144c1bf18f24615c743`.
- The one permitted production scan ran once on CPU through the audited `_read_raw` loader and exact `NativeSpectralA1(20260824).eval()._spectral_tokens` path.
- Exactly 3,497 eligible outer-train arrays were read once, covering 35,745 windows from 18 subjects and 18 source files.
- Exactly 44 short forced-L0 arrays, every calibration array, and every test array had zero reads.
- The full encoder was not executed. CUDA was not selected or initialized for the production tokenizer path.
- No row proxy, spectral token, waveform, embedding, donor mapping, text, outcome, prediction, metric, or value cache was persisted or read beyond the authorized EEG-derived proxy computation.
- The complete ledger contains 3,541 rows. There are 192 populated role-scoped blocks, 180 evaluable blocks, 12 singleton blocks, and 3,481 evaluable rows.
- All 199 frozen index-only joint-bijection replicates completed with 199 unique joint mapping hashes, zero bijection violations, and zero cross-block violations.

## Decision

- Structural status: `PASS`.
- Minimum subject-by-role complete-population coverage: `0.7777777777777778`.
- Frozen threshold: `0.90`.
- Decision: `DEGRADED_COVERAGE`.
- Evidence label: `N1_OUTER_TRAIN_BLOCK_FEASIBILITY_DEGRADED_COVERAGE`.
- Primary fallback status: `INELIGIBLE_DUE_TO_OUTER_TRAIN_COVERAGE_BELOW_0_90`.
- Mechanical next task: `S0_N1_SAMPLER`, owner `CHATGPT_OR_AUTHOR`, for mechanism/robustness only under a new exact contract.

No alternative power proxy, bin, threshold, permutation law, split, seed search, or production rescan was attempted to improve this decision.

## Canonical outputs

- `artifacts/nulls/n1_block_assignment_v1.jsonl`: `d0acc5e5fe78bc36a69cb04b6f605983c675e49a764538ae1665f86a28acee04`
- `artifacts/nulls/n1_block_feasibility.yaml`: `90a6178100f507299e12223d15291699aad84e4b58bb52e29843dbf99ee6f771`
- `reports/n1_block_feasibility.md`: `5bf77b8282d0938d59104b5e4e615c30c3b4fbdc089dab2ccc1bbd019da14098`

The canonical build and both repository-external verification builds are byte-identical for all three outputs.

## Validation

Using `/home/song/projects/trust_generative/.venv/bin/python`:

- N1 block-feasibility tests: 17/17 PASS.
- Full A1 admission tests: 13/13 PASS.
- A1 frontend synthetic-HDF5 tests: 13/13 PASS.
- Native spectral A1 tests: 12/12 PASS.
- A-interface builder tests: 8/8 PASS.
- Early A-path leakage tests: 20/20 PASS.
- Joint-split tests: 13/13 PASS.
- Project-memory/state tests: 59/59 PASS.
- Full repository discovery: 219/219 PASS, 0 skipped.
- `scripts/check_project_state.py`: PASS.
- `scripts/project_status.py`: PASS.
- `git diff --check`: PASS.

## Final state and hard stop

- 73 tasks: 39 DONE, 8 SKIPPED, 25 BLOCKED, 1 READY.
- Sole READY/recommended task: `S0_N1_SAMPLER`, owner `CHATGPT_OR_AUTHOR`.
- B_V9 remains closed. B_V4 remains active without blocking the branch resolver.
- Route remains unlocked. Test remains `LOCKED_UNTIL_ROUTE_LOCK`.
- Gate R0 remains BLOCKED with null outcome; its stale blocker text and the N2 stale text were corrected without changing outcomes or routing.

Run 017 did not implement N1/N2 sampling, execute the full encoder, train, run the method leakage audit, execute any Gate, lock the route, or unlock/read test. It stops before `S0_N1_SAMPLER`.
