# Input Discovery Audit

Run: `2026-08-16_004_governance_hardening_input_discovery`  
Evidence baseline: `1b836fe56970d262f4e8f3ae8262fd0abb670dbe`

## Scope and safety

The audit recursively scanned only `/home/song/projects/trust_generative` and
`/home/song/projects/trust_align`. Git objects, virtual environments, caches,
temporary trees and node modules were excluded. Reference-project runs,
reports, artifacts, candidate/split ledgers and Stage-0 output directories
were recorded as `UNREAD_HISTORICAL_RESULT` without recursion. Unsafe
pickle/checkpoint formats were never deserialized. No result, prediction,
metric, stimulus, label or semantic-target value was printed or recorded.

## Data discovery

An authorized local ZuCo 2.0 tree exists under the reference root. Metadata
enumeration found 18 NR summary files and 18 TSR summary files. Safe HDF5
header inspection, limited to group names and shapes, confirmed 349 NR and 390
TSR sentence slots per summary and the presence of `content`, `rawData`, and
`word` fields. Array values and referenced text were not read.

NR remains `FOUND_LICENSE_UNVERIFIED`, not admitted. No local LICENSE, terms,
or author-authorization file was found; no channel-name/coordinate/montage
evidence was found; and sampling, units, reference, event and trial semantics
are not all recoverable from the safe headers. Because strict admission
conditions 2, 3 and 5 are unmet, no data card was generated and
`S0_DATA_CARD` remains blocked. TSR is recorded only as a later robustness
candidate and was not pooled with NR.

## Backbone discovery

Three candidate records were created without selecting a primary A:

- `TRUST_ALIGN_A1_SPECTRAL`: `STATICALLY_COMPATIBLE_UNVALIDATED`. Synthetic,
  data-free contract tests pass, but the reference project has no root license,
  no frozen checkpoint, and no NC-HSG common score interface.
- `TRUST_ALIGN_LABRAM_A3`: `FOUND_INCOMPLETE`. Local MIT source and checkpoint
  metadata/hash exist, but the checkpoint was not deserialized and the channel
  map, physical unit, filter order, notch Q and common score interface remain
  unresolved.
- `OFFICIAL_NEUROLM_B_VQ`: `FOUND_INCOMPLETE`. Official code commit, MIT
  license, Hugging Face revision, CC-BY-4.0 card metadata, sizes and LFS hashes
  match the frozen v1.3 values. The weights were not downloaded. Static source
  establishes 200 Hz, 200-sample patches, standard channel vocabulary, masks,
  and a frozen VQ tokenizer; the exact ZuCo channel intersection and NC-HSG
  adapter/score interface remain unverified.

The safe reference-project command was:

```text
cd /home/song/projects/trust_align/02_code && PYTHONPATH=src /home/song/projects/trust_generative/.venv/bin/python -m unittest tests.test_a1_contract tests.test_a3_contract
```

Result: 15 tests ran in 1.291 seconds, all passed. These are synthetic
contract tests only and are not real-data admission, training, or a Gate.

## ZuCo-NeuroLM compatibility

Overall status is `UNVERIFIED`. License metadata is compatible at the frozen
revisions. Every physical interface item that depends on local channel names,
coordinates, units, reference, event boundaries, resampling, segmentation or
padding remains unverified. No nearest-neighbor channel mapping, interpolation
threshold, adapter implementation, or performance conclusion was introduced.

## Decision and next action

The input discovery audit is complete as an outcome-blind candidate ledger,
but neither data nor a backbone is admitted. There is no valid READY scientific
task. The minimum user action is to provide a specific local ZuCo 2.0 license,
terms, or author-authorization file and the physical channel-name/coordinate
metadata for the audited local release. After those are available, rerun a
targeted admission audit; do not repeat broad discovery or select A from
historical results.
