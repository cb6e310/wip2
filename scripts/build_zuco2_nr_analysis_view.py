#!/usr/bin/env python3
"""Build the frozen ZuCo 2.0 NR analysis view and data card.

Only the four committed schema-v3 admission artifacts are read.  The builder
does not open dataset files and emits no stimulus text, event latency, EEG
value, finite-value count, or waveform hash.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_INPUT_SHA256 = {
    "targeted_manifest": "50806a60937b28ae36207509c44d606af6f6b6b1be2a69c06081672f0931bfaf",
    "stimulus_manifest": "2512c55bb7471896aad7bfa7ba96843fbce8a46067abffda6c16ad87ce3e44be",
    "event_manifest": "44fa6ce6f797a6ca26c889c5e754419f3091ba937718af52ae07355617cab68d",
    "segment_correspondence": "28612065ecba93b0e63f8e8c1b604076c63a398b799d5a45d4f437205a07b84e",
}
EXPECTED_BASENAMES = {
    "targeted_manifest": "zuco2_nr_targeted_manifest_v3.yaml",
    "stimulus_manifest": "zuco2_nr_stimulus_manifest_v3.jsonl",
    "event_manifest": "zuco2_nr_event_occurrence_manifest_v1.jsonl",
    "segment_correspondence": "zuco2_nr_segment_correspondence_v1.yaml",
}
VIEW_FIELDS = (
    "subject", "session", "task", "block", "slot", "material_line",
    "occurrence_id", "stimulus_sha256", "raw_shape", "raw_samples",
    "raw_channels", "source_locator",
)
EXPECTED_ANOMALY_FILES = (
    "task1 - NR/Preprocessed/YTL/gip_YTL_NR3_EEG.mat",
    "task1 - NR/Preprocessed/YTL/gip_YTL_NR5_EEG.mat",
    "task1 - NR/Preprocessed/YTL/oip_YTL_NR6_EEG.mat",
)


class BuildError(RuntimeError):
    """A fail-closed builder error with a stable machine-readable code."""

    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


@dataclass(frozen=True)
class Expectations:
    all_rows: int = 6282
    valid_finite_multisample: int = 5911
    admitted: int = 5905
    excluded: int = 377
    nonfinite_placeholder: int = 367
    finite_single_sample: int = 4
    finite_multisample_event_unresolved: int = 6
    subjects: int = 18
    sessions: int = 1
    slots_per_subject: int = 349
    channels: int = 105
    blocks: int = 7
    identity_files: int = 27
    ytl_finite_event_unresolved_by_block: tuple[tuple[int, int], ...] = (
        (3, 1), (5, 1), (6, 4),
    )
    anomaly_files: tuple[str, ...] = EXPECTED_ANOMALY_FILES


DEFAULT_EXPECTATIONS = Expectations()


def _fail(code: str, detail: str) -> None:
    raise BuildError(code, detail)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_input_path(path: Path, root: Path, label: str, basename: str | None) -> Path:
    root = root.resolve()
    candidate = path if path.is_absolute() else root / path
    current = candidate
    while True:
        if current.is_symlink():
            _fail("INPUT_SYMLINK", label)
        if current == root or current.parent == current:
            break
        current = current.parent
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        _fail("INPUT_PATH_ESCAPE", label)
    if not resolved.is_file():
        _fail("INPUT_NOT_FILE", label)
    if basename is not None and resolved.name != basename:
        _fail("INPUT_VERSION_MISMATCH", f"{label} basename={resolved.name}")
    return resolved


def _validate_output_path(path: Path, root: Path, label: str) -> Path:
    root = root.resolve()
    candidate = path if path.is_absolute() else root / path
    if candidate.exists() and candidate.is_symlink():
        _fail("OUTPUT_SYMLINK", label)
    resolved_parent = candidate.parent.resolve()
    try:
        resolved_parent.relative_to(root)
    except ValueError:
        _fail("OUTPUT_PATH_ESCAPE", label)
    return resolved_parent / candidate.name


def _load_yaml(path: Path, label: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        _fail("INPUT_PARSE_ERROR", f"{label}:{type(exc).__name__}")
    if not isinstance(value, dict):
        _fail("INPUT_SCHEMA_MISMATCH", label)
    return value


def _load_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                value = json.loads(line)
                if not isinstance(value, dict):
                    _fail("INPUT_SCHEMA_MISMATCH", f"{label}:{line_number}")
                rows.append(value)
    except BuildError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail("INPUT_PARSE_ERROR", f"{label}:{type(exc).__name__}")
    return rows


def _counter_dict(counter: Counter[Any]) -> dict[Any, int]:
    return {key: counter[key] for key in sorted(counter, key=lambda item: (str(type(item)), str(item)))}


def _nested_counts(rows: Iterable[dict[str, Any]], dimension: str) -> dict[Any, dict[str, int]]:
    grouped: dict[Any, Counter[str]] = defaultdict(Counter)
    for row in rows:
        grouped[row[dimension]]["admitted" if row["final_admission_candidate"] else "excluded"] += 1
    return {key: _counter_dict(grouped[key]) for key in sorted(grouped)}


def _yaml_bytes(value: Any) -> bytes:
    return yaml.safe_dump(
        value, sort_keys=False, allow_unicode=False, default_flow_style=False,
    ).encode("utf-8")


def _jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(
        (json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")
        for row in rows
    )


def _report_bytes(card: dict[str, Any]) -> bytes:
    counts = card["analysis_view"]["counts"]
    overlap = card["analysis_view"]["exclusion_overlap"]
    paths = card["limitations"]["event_anomaly_files"]
    failed = card["source_release"]["full_release_diagnostic"]["failed_subpredicates"]
    lines = [
        "# ZuCo 2.0 NR Data Card", "",
        "## Scope and verdicts", "",
        f"The source release contains {card['source_release']['physical_assignments']:,} physical subject-slot assignments. Its strict full-release diagnostic remains **FAIL**; failed subpredicates are `{', '.join(failed)}`.", "",
        f"The frozen analysis view is **PASS** with {counts['admitted']:,} admitted rows and {counts['excluded_union']:,} excluded rows ({counts['all_rows']:,} total). This subset verdict does not imply a gap-free source release or model/Gate readiness.", "",
        "## Composition", "",
        f"- Dataset/revision: {card['dataset']['name']} / {card['dataset']['revision']}",
        f"- License: {card['provenance']['license_name']} (OSF node `{card['provenance']['osf_node_id']}`)",
        f"- Subjects/sessions/task: {card['composition']['subjects']} / {card['composition']['sessions']} / {card['composition']['task']}",
        f"- Blocks and slots: {card['composition']['blocks']} blocks, {card['composition']['slots_per_subject']} slots per subject",
        f"- Signal contract: {card['signal']['channels']} channels at {card['signal']['sampling_hz']} Hz; acquisition reference `{card['signal']['acquisition_reference']}`, processed reference `{card['signal']['processed_reference']}`",
        f"- Segment convention: `{card['signal']['segment_convention']}`; summary layer/reference `{card['signal']['summary_layer_reference_status']}`", "",
        "## Exclusions and limitations", "",
        f"The exclusion union is recomputed row by row. It contains {counts['nonfinite_placeholder']} nonfinite placeholders, {counts['finite_single_sample_review_required']} finite single-sample rows, and {counts['additional_finite_multisample_event_unresolved']} additional finite-multisample event-unresolved rows. The event-invalid total is {overlap['event_invalid_total']}; {overlap['finite_single_sample_and_event_invalid']} single-sample rows overlap that set.", "",
        "YTL anomaly files:", "",
        *[f"- `{path}`" for path in paths], "",
        f"Physical unit status is `{card['unit_policy']['physical_unit_status']}`. Unit inference was not performed, and unit-sensitive use is `{card['unit_policy']['unit_sensitive_use']}`.", "",
        "## Intended and prohibited use", "",
        card["use_policy"]["intended_use"], "",
        card["use_policy"]["prohibited_use"], "",
        card["use_policy"]["tsr_policy"], "",
        "## Safety declaration", "",
        "No outcome was read; no data or weights were downloaded; no backbone was selected; no split, training, or Gate was run. The artifacts contain no stimulus text, event latency, EEG value, finite-value count, or waveform hash.", "",
    ]
    return "\n".join(lines).encode("utf-8")


def _atomic_write(outputs: dict[Path, bytes]) -> None:
    temporary: list[tuple[Path, Path]] = []
    try:
        for destination, content in outputs.items():
            destination.parent.mkdir(parents=True, exist_ok=True)
            fd, temporary_name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
            temporary_path = Path(temporary_name)
            with os.fdopen(fd, "wb") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            temporary.append((temporary_path, destination))
        for temporary_path, destination in temporary:
            os.replace(temporary_path, destination)
    finally:
        for temporary_path, _ in temporary:
            temporary_path.unlink(missing_ok=True)


def build(
    *,
    targeted_manifest: Path,
    stimulus_manifest: Path,
    event_manifest: Path,
    segment_correspondence: Path,
    output_view: Path,
    output_summary: Path,
    output_data_card: Path,
    output_data_card_report: Path,
    root: Path = PROJECT_ROOT,
    expectations: Expectations = DEFAULT_EXPECTATIONS,
    expected_hashes: dict[str, str] | None = None,
    enforce_basenames: bool = False,
) -> dict[str, Any]:
    input_values = {
        "targeted_manifest": targeted_manifest,
        "stimulus_manifest": stimulus_manifest,
        "event_manifest": event_manifest,
        "segment_correspondence": segment_correspondence,
    }
    inputs = {
        label: _validate_input_path(path, root, label, EXPECTED_BASENAMES[label] if enforce_basenames else None)
        for label, path in input_values.items()
    }
    output_values = {
        "view": output_view,
        "summary": output_summary,
        "data_card": output_data_card,
        "data_card_report": output_data_card_report,
    }
    outputs = {label: _validate_output_path(path, root, label) for label, path in output_values.items()}
    if len(set(outputs.values())) != len(outputs):
        _fail("OUTPUT_PATH_DUPLICATE", "output destinations must be unique")

    hashes = {label: _sha256(path) for label, path in inputs.items()}
    if expected_hashes is not None:
        for label, expected in expected_hashes.items():
            if hashes.get(label) != expected:
                _fail("INPUT_HASH_MISMATCH", label)

    targeted = _load_yaml(inputs["targeted_manifest"], "targeted_manifest")
    correspondence = _load_yaml(inputs["segment_correspondence"], "segment_correspondence")
    rows = _load_jsonl(inputs["stimulus_manifest"], "stimulus_manifest")
    events = _load_jsonl(inputs["event_manifest"], "event_manifest")
    if targeted.get("schema_version") != 3 or targeted.get("admission_result") != "FAIL":
        _fail("TARGETED_SCHEMA_MISMATCH", "requires schema_version=3 and admission_result=FAIL")
    if correspondence.get("schema_version") != 1:
        _fail("CORRESPONDENCE_SCHEMA_MISMATCH", "requires schema_version=1")
    manifest_counts = targeted.get("counts", {})
    if manifest_counts.get("rows") != expectations.all_rows:
        _fail("TARGETED_COUNT_MISMATCH", "rows")
    if len(rows) != expectations.all_rows or len(events) != expectations.all_rows:
        _fail("ROW_COUNT_MISMATCH", f"stimulus={len(rows)} event={len(events)}")

    summary_paths: dict[str, str] = {}
    for item in targeted.get("summary_schema", []):
        if not isinstance(item, dict) or not isinstance(item.get("subject"), str) or not isinstance(item.get("path"), str):
            _fail("TARGETED_SCHEMA_MISMATCH", "summary_schema")
        if item["subject"] in summary_paths:
            _fail("TARGETED_SCHEMA_MISMATCH", "duplicate summary subject")
        summary_paths[item["subject"]] = item["path"]

    event_by_key: dict[tuple[str, int], dict[str, Any]] = {}
    for event in events:
        key = (event.get("subject"), event.get("global_slot"))
        if not isinstance(key[0], str) or not isinstance(key[1], int):
            _fail("EVENT_KEY_INVALID", repr(key))
        if key in event_by_key:
            _fail("EVENT_KEY_DUPLICATE", repr(key))
        event_by_key[key] = event

    row_keys: set[tuple[str, int]] = set()
    state_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    admitted_rows: list[dict[str, Any]] = []
    event_invalid = 0
    single_event_overlap = 0
    finite_event_by_block: Counter[int] = Counter()
    for row in rows:
        key = (row.get("subject"), row.get("slot"))
        if not isinstance(key[0], str) or not isinstance(key[1], int):
            _fail("STIMULUS_KEY_INVALID", repr(key))
        if key in row_keys:
            _fail("STIMULUS_KEY_DUPLICATE", repr(key))
        row_keys.add(key)
        event = event_by_key.get(key)
        if event is None:
            _fail("EVENT_KEY_MISSING", repr(key))
        for stimulus_name, event_name in (
            ("block", "block"), ("slot", "global_slot"), ("material_line", "material_line"),
            ("eeg_cell_state", "summary_cell_state"),
            ("segment_correspondence_state", "segment_correspondence_state"),
            ("final_admission_candidate", "final_admission_candidate"),
            ("final_exclusion_reason", "exclusion_reason"),
        ):
            if row.get(stimulus_name) != event.get(event_name):
                _fail("JOIN_FIELD_MISMATCH", f"{key}:{stimulus_name}")
        state = row.get("eeg_cell_state")
        state_counts[state] += 1
        final = row.get("final_admission_candidate")
        if not isinstance(final, bool):
            _fail("FINAL_FLAG_INVALID", repr(key))
        predicate = (
            row.get("content_present") is True
            and state == "VALID_FINITE_MULTISAMPLE"
            and row.get("event_occurrence_valid") is True
            and row.get("segment_correspondence_state") == "EXACT_MATCH"
            and row.get("final_exclusion_reason") is None
        )
        if final and not predicate:
            _fail("ADMITTED_PREDICATE_FAILED", repr(key))
        if not final and not isinstance(row.get("final_exclusion_reason"), str):
            _fail("EXCLUSION_REASON_MISSING", repr(key))
        if final != predicate:
            _fail("FINAL_FLAG_PREDICATE_MISMATCH", repr(key))
        if not final:
            reason_counts[row["final_exclusion_reason"]] += 1
        invalid_event = row.get("event_occurrence_valid") is not True
        event_invalid += int(invalid_event)
        if state == "FINITE_SINGLE_SAMPLE_REVIEW_REQUIRED" and invalid_event:
            single_event_overlap += 1
        if state == "VALID_FINITE_MULTISAMPLE" and invalid_event:
            if row.get("subject") != "YTL":
                _fail("EVENT_ANOMALY_SCOPE_MISMATCH", repr(key))
            finite_event_by_block[row["block"]] += 1
        if final:
            if row["subject"] not in summary_paths:
                _fail("SOURCE_LOCATOR_MISSING", row["subject"])
            view_row = {name: row[name] for name in VIEW_FIELDS if name != "source_locator"}
            view_row["source_locator"] = {
                "summary_file": summary_paths[row["subject"]],
                "field": "rawData",
                "slot": row["slot"],
            }
            if set(view_row) != set(VIEW_FIELDS):
                _fail("VIEW_FIELD_MISSING", repr(key))
            admitted_rows.append(view_row)

    extra_event_keys = set(event_by_key) - row_keys
    if extra_event_keys:
        _fail("EVENT_KEY_EXTRA", repr(sorted(extra_event_keys)[0]))

    admitted_count = len(admitted_rows)
    excluded_count = len(rows) - admitted_count
    expected_states = {
        "VALID_FINITE_MULTISAMPLE": expectations.valid_finite_multisample,
        "NONFINITE_PLACEHOLDER": expectations.nonfinite_placeholder,
        "FINITE_SINGLE_SAMPLE_REVIEW_REQUIRED": expectations.finite_single_sample,
    }
    if state_counts != Counter(expected_states):
        _fail("EEG_CLASS_COUNT_MISMATCH", repr(_counter_dict(state_counts)))
    if admitted_count != expectations.admitted or excluded_count != expectations.excluded:
        _fail("ANALYSIS_COUNT_MISMATCH", f"admitted={admitted_count} excluded={excluded_count}")
    if admitted_count + excluded_count != expectations.all_rows:
        _fail("EXCLUSION_UNION_MISMATCH", "admitted plus excluded")
    if sum(finite_event_by_block.values()) != expectations.finite_multisample_event_unresolved:
        _fail("FINITE_EVENT_COUNT_MISMATCH", repr(_counter_dict(finite_event_by_block)))
    if dict(finite_event_by_block) != dict(expectations.ytl_finite_event_unresolved_by_block):
        _fail("YTL_EVENT_BLOCK_COUNT_MISMATCH", repr(_counter_dict(finite_event_by_block)))

    anomaly_files = targeted.get("event_contract", {}).get("files_with_semantic_anomaly")
    if not isinstance(anomaly_files, list) or tuple(anomaly_files) != expectations.anomaly_files:
        _fail("YTL_ANOMALY_PATH_MISMATCH", repr(anomaly_files))
    file_contract = targeted.get("event_contract", {}).get("files", [])
    dynamic_anomaly_files = sorted(
        item["path"] for item in file_contract
        if isinstance(item, dict) and item.get("subject") == "YTL" and item.get("event_semantics_bound") is False
    )
    if dynamic_anomaly_files != sorted(expectations.anomaly_files):
        _fail("YTL_ANOMALY_PATH_MISMATCH", repr(dynamic_anomaly_files))

    if targeted.get("eeg_cell_ledger", {}).get("overall") != expected_states:
        _fail("TARGETED_LEDGER_MISMATCH", "overall class counts")
    physical = targeted.get("physical_schema", {})
    if (
        physical.get("sampling_hz_values") != [500]
        or physical.get("acquisition_reference_values") != ["Cz"]
        or physical.get("processed_reference_values") != ["common-average"]
        or physical.get("unit_values") != []
    ):
        _fail("PHYSICAL_CONTRACT_MISMATCH", repr(physical))
    unit_layer = targeted.get("unit_layer_contract", {})
    if (
        unit_layer.get("preprocessed_EEG_data_unit_status") != "UNRESOLVED"
        or unit_layer.get("summary_rawData_unit_status") != "UNRESOLVED"
        or unit_layer.get("summary_rawData_layer_status") != "BOUND_BY_EXACT_CORRESPONDENCE"
        or unit_layer.get("summary_rawData_reference_status") != "BOUND_BY_EXACT_CORRESPONDENCE"
    ):
        _fail("UNIT_LAYER_CONTRACT_MISMATCH", repr(unit_layer))
    identity = targeted.get("hash_provenance", {})
    identity_files = identity.get("files", [])
    if (
        identity.get("result") != "PASS"
        or len(identity_files) != expectations.identity_files
        or any(item.get("identity_status") != "REUSED_VERIFIED_RUN005_NO_REHASH" for item in identity_files)
        or identity.get("large_files_rehashed") is not False
    ):
        _fail("HASH_IDENTITY_CONTRACT_MISMATCH", "run-005 identity evidence")
    if correspondence.get("counts") != {
        "EVENT_UNRESOLVED": expectations.finite_multisample_event_unresolved,
        "EXACT_MATCH": expectations.admitted,
    }:
        _fail("CORRESPONDENCE_COUNT_MISMATCH", repr(correspondence.get("counts")))
    convention = correspondence.get("segment_convention_global_unique", {})
    if convention.get("result") != "PASS" or convention.get("selected") != "EEGLAB_ONE_BASED_FINISH_INCLUSIVE":
        _fail("SEGMENT_CONVENTION_MISMATCH", repr(convention))

    subjects = sorted({row["subject"] for row in rows})
    sessions = sorted({row.get("session") for row in rows})
    blocks = sorted({row.get("block") for row in rows})
    channels = sorted({row.get("raw_channels") for row in rows if row["final_admission_candidate"]})
    if (
        len(subjects) != expectations.subjects
        or len(sessions) != expectations.sessions
        or sessions != [1]
        or len(blocks) != expectations.blocks
        or {row.get("task") for row in rows} != {"NR"}
    ):
        _fail("COMPOSITION_COUNT_MISMATCH", "subjects or sessions")
    if channels != [expectations.channels]:
        _fail("CHANNEL_COUNT_MISMATCH", repr(channels))
    subject_slots = Counter(row["subject"] for row in rows)
    if set(subject_slots.values()) != {expectations.slots_per_subject}:
        _fail("SLOTS_PER_SUBJECT_MISMATCH", repr(_counter_dict(subject_slots)))

    failed_subpredicates = [
        item.get("id") for item in targeted.get("condition_3_subpredicates", [])
        if isinstance(item, dict) and item.get("result") == "FAIL"
    ]
    if not failed_subpredicates:
        _fail("FULL_DIAGNOSTIC_MISMATCH", "failed subpredicates absent")
    input_evidence = {
        label: {
            "path": inputs[label].relative_to(root.resolve()).as_posix(),
            "sha256": hashes[label],
        }
        for label in input_values
    }
    overlap = {
        "event_invalid_total": event_invalid,
        "finite_single_sample_and_event_invalid": single_event_overlap,
        "additional_finite_multisample_event_unresolved": sum(finite_event_by_block.values()),
        "excluded_union_recomputed_from_final_flags": excluded_count,
    }
    composition_counts = {
        "all_rows": len(rows),
        "valid_finite_multisample": state_counts["VALID_FINITE_MULTISAMPLE"],
        "admitted": admitted_count,
        "excluded_union": excluded_count,
        "nonfinite_placeholder": state_counts["NONFINITE_PLACEHOLDER"],
        "finite_single_sample_review_required": state_counts["FINITE_SINGLE_SAMPLE_REVIEW_REQUIRED"],
        "additional_finite_multisample_event_unresolved": sum(finite_event_by_block.values()),
    }
    unit_policy = {
        "physical_unit_status": "UNRESOLVED_RELEASE_NATIVE_AMPLITUDE",
        "unit_inference_performed": False,
        "unit_sensitive_use": "PROHIBITED_UNTIL_S0_A_INTERFACE",
    }
    safety = {
        "real_eeg_read": False,
        "historical_or_test_outcome_read": False,
        "data_or_weights_downloaded": False,
        "backbone_selected": False,
        "split_built": False,
        "training_run": False,
        "gate_run": False,
        "stimulus_text_emitted": False,
        "event_latency_emitted": False,
        "eeg_values_emitted": False,
        "waveform_hashes_emitted": False,
    }
    summary = {
        "schema_version": 1,
        "artifact": "ZUCO2_NR_ANALYSIS_VIEW_V1",
        "input_evidence": input_evidence,
        "full_release_diagnostic": {"status": "FAIL", "failed_subpredicates": failed_subpredicates},
        "analysis_view_admission": {
            "status": "PASS",
            "predicate": "content_present AND VALID_FINITE_MULTISAMPLE AND event_occurrence_valid AND EXACT_MATCH AND no exclusion reason",
        },
        "counts": composition_counts,
        "eeg_cell_class_counts": _counter_dict(state_counts),
        "exclusion_reason_counts": _counter_dict(reason_counts),
        "exclusion_overlap": overlap,
        "counts_by_subject": _nested_counts(rows, "subject"),
        "counts_by_block": _nested_counts(rows, "block"),
        "dataset_contract": {
            "dataset": "ZuCo 2.0", "task": "NR", "subjects": subjects,
            "subject_count": len(subjects), "sessions": sessions,
            "session_count": len(sessions), "blocks": blocks,
            "slots_per_subject": expectations.slots_per_subject,
        },
        "signal_contract": {
            "channels": expectations.channels, "sampling_hz": 500,
            "acquisition_reference": "Cz", "processed_reference": "common-average",
            "summary_layer_status": "BOUND_BY_EXACT_CORRESPONDENCE",
            "summary_reference_status": "BOUND_BY_EXACT_CORRESPONDENCE",
            "segment_convention": "EEGLAB_ONE_BASED_FINISH_INCLUSIVE",
        },
        "hash_identity_evidence": {
            "status": "PASS", "matched_files": expectations.identity_files,
            "reference": "runs/2026-08-16_005_active_spec_guard_zuco2_nr_admission.md",
            "identity_status": "REUSED_VERIFIED_RUN005_NO_REHASH",
            "large_files_rehashed": False,
        },
        "unit_policy": unit_policy,
        "event_anomalies": {
            "subject": "YTL", "files": list(anomaly_files),
            "finite_multisample_event_unresolved_by_block": _counter_dict(finite_event_by_block),
        },
        "safety": safety,
    }
    card = {
        "schema_version": 1,
        "dataset": {"name": "ZuCo 2.0", "revision": "OSF node revision modified 2023-08-25"},
        "provenance": {
            "osf_node_id": "2urht",
            "license_name": "CC-By Attribution 4.0 International",
            "license_relationship_id": "563c1cf88c5e4a3877f9e96a",
            "license_evidence": "artifacts/admission/zuco2_osf_license.yaml",
            "file_metadata_evidence": "artifacts/admission/zuco2_osf_file_metadata.yaml",
            "run005_identity_evidence": f"{expectations.identity_files}/{expectations.identity_files} SHA256 matches reused without re-hash",
            "license_evidence_sha256": "e88412447528cf0a887e6cae0f992bd1b14a6955722454d966361c6f386cb7c4",
            "file_metadata_evidence_sha256": "85a8c89eeb7a523c06fb7f38aa1c371e042413087e66dcc338c16833bd8bb721",
        },
        "source_release": {
            "physical_assignments": len(rows),
            "full_release_diagnostic": summary["full_release_diagnostic"],
        },
        "analysis_view": {
            "status": "PASS", "counts": composition_counts,
            "exclusion_reason_counts": summary["exclusion_reason_counts"],
            "exclusion_overlap": overlap,
            "input_evidence": input_evidence,
        },
        "composition": {
            "subjects": len(subjects), "sessions": len(sessions), "task": "NR",
            "blocks": len(blocks), "slots_per_subject": expectations.slots_per_subject,
            "subject_ids": subjects,
        },
        "signal": {
            "source_fields": sorted({field for item in targeted["summary_schema"] for field in item.get("fields", [])}),
            "eeg_fields": ["rawData"],
            "text_fields": ["content", "word"],
            "text_metadata_fields": ["wordbounds"],
            "channels": expectations.channels, "sampling_hz": 500,
            "acquisition_reference": "Cz", "processed_reference": "common-average",
            "summary_layer_reference_status": "BOUND_BY_EXACT_CORRESPONDENCE",
            "segment_convention": "EEGLAB_ONE_BASED_FINISH_INCLUSIVE",
        },
        "assignment_contract": {
            "key": ["subject", "slot"],
            "stimulus_identity": "stimulus_sha256",
            "source_locator": "summary_file + rawData + one-based slot",
            "missing_and_exclusion_policy": "Every physical assignment is ledgered; only rows satisfying the frozen conjunction enter the analysis view.",
        },
        "unit_policy": unit_policy,
        "limitations": {
            "event_anomaly_files": list(anomaly_files),
            "ytl_finite_multisample_event_unresolved_by_block": _counter_dict(finite_event_by_block),
            "unknown_physical_unit": True,
            "source_release_not_gap_free": True,
        },
        "use_policy": {
            "intended_use": "Use only as the frozen outcome-blind input inventory for future NC-HSG work after the required stimulus-disjoint split and downstream admissions.",
            "prohibited_use": "Do not infer physical units, admit a unit-sensitive frontend, treat excluded rows as usable, read outcomes, or claim model or Gate validity from this data-card PASS.",
            "tsr_policy": "TSR may be used only as a later robustness task, not as a substitute for the primary NR analysis view.",
        },
        "safety": safety,
    }
    admitted_rows.sort(key=lambda item: (item["subject"], item["slot"]))
    rendered = {
        outputs["view"]: _jsonl_bytes(admitted_rows),
        outputs["summary"]: _yaml_bytes(summary),
        outputs["data_card"]: _yaml_bytes(card),
        outputs["data_card_report"]: _report_bytes(card),
    }
    _atomic_write(rendered)
    return {"summary": summary, "data_card": card, "output_sha256": {path.name: hashlib.sha256(content).hexdigest() for path, content in rendered.items()}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--targeted-manifest", type=Path, required=True)
    parser.add_argument("--stimulus-manifest", type=Path, required=True)
    parser.add_argument("--event-manifest", type=Path, required=True)
    parser.add_argument("--segment-correspondence", type=Path, required=True)
    parser.add_argument("--output-view", type=Path, required=True)
    parser.add_argument("--output-summary", type=Path, required=True)
    parser.add_argument("--output-data-card", type=Path, required=True)
    parser.add_argument("--output-data-card-report", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = build(
            **vars(args), root=PROJECT_ROOT, expected_hashes=EXPECTED_INPUT_SHA256,
            enforce_basenames=True,
        )
    except BuildError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    for name, digest in sorted(result["output_sha256"].items()):
        print(f"{name} {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
