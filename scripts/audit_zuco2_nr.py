#!/usr/bin/env python3
"""Schema-v3, outcome-blind event/segment admission audit for ZuCo 2.0 NR.

The auditor reads the 18 admitted NR summary files, seven material CSVs, and
events and bounded EEG windows from 126 preprocessed blocks. It reuses the immutable
run-005 27/27 identity evidence and never re-hashes the 34.6 GB summaries.
No stimulus text, event latency, or EEG numeric value is emitted.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import tempfile
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

import h5py
import numpy as np
import yaml


SUMMARY_RE = re.compile(r"results([A-Z0-9]+)_NR\.mat$")
EEG_RE = re.compile(r"(?:[a-z]+_)?([A-Z0-9]+)_NR([1-7])_EEG\.mat$")
MATERIAL_RE = re.compile(r"nr_([1-7])\.csv$")
EXPECTED_SUMMARY_FIELDS = (
    "allFixations", "content", "mean_a1", "mean_a1_diff", "mean_a2",
    "mean_a2_diff", "mean_b1", "mean_b1_diff", "mean_b2", "mean_b2_diff",
    "mean_g1", "mean_g1_diff", "mean_g2", "mean_g2_diff", "mean_t1",
    "mean_t1_diff", "mean_t2", "mean_t2_diff", "omissionRate", "rawData",
    "word", "wordbounds",
)
EXPECTED_EXCLUDED_CHANNELS = (
    "E1", "E8", "E14", "E17", "E21", "E25", "E32", "E48", "E49",
    "E56", "E63", "E68", "E73", "E81", "E88", "E94", "E99", "E107",
    "E113", "E119", "E125", "E126", "E127", "E128",
)
CELL_STATES = (
    "MISSING_REFERENCE", "EMPTY", "NONFINITE_PLACEHOLDER", "PARTIAL_NONFINITE",
    "INVALID_AXIS", "FINITE_SINGLE_SAMPLE_REVIEW_REQUIRED", "VALID_FINITE_MULTISAMPLE",
)
UNSAFE_SUFFIXES = {".pkl", ".pickle", ".joblib", ".pt", ".pth", ".ckpt"}
EXPECTED_STATE_COUNTS = {
    "NONFINITE_PLACEHOLDER": 367,
    "FINITE_SINGLE_SAMPLE_REVIEW_REQUIRED": 4,
    "VALID_FINITE_MULTISAMPLE": 5911,
}
EXPECTED_PLACEHOLDER_BY_SUBJECT = {
    "YAC": 102, "YAK": 51, "YDR": 3, "YFR": 106, "YFS": 13,
    "YLS": 6, "YMD": 7, "YMS": 3, "YRH": 52, "YRK": 10,
    "YRP": 6, "YSD": 1, "YSL": 6, "YTL": 1,
}
EXPECTED_PLACEHOLDER_BY_BLOCK = {1: 9, 2: 121, 3: 52, 4: 39, 5: 67, 6: 60, 7: 19}
EXPECTED_POST_PRACTICE_COUNTS = {1: 50, 2: 50, 3: 51, 4: 50, 5: 50, 6: 49, 7: 49}
EVENT_ROLE_VALUES = {
    "ORDINARY_ONSET", "ORDINARY_FINISH", "CONTROL_ONSET", "CONTROL_FINISH",
    "CONTROL_RESPONSE", "MARKER",
}
ENDPOINT_CONVENTIONS = (
    "EEGLAB_ONE_BASED_FINISH_EXCLUSIVE",
    "EEGLAB_ONE_BASED_FINISH_INCLUSIVE",
)
ALLOWED_SOURCE_URLS = {
    "https://api.osf.io/v2/wikis/s3nrk/content/",
    "https://api.osf.io/v2/wikis/kw2df/content/",
    "https://aclanthology.org/2020.lrec-1.18/",
    "https://aclanthology.org/2020.lrec-1.18.pdf",
    "https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.1028824/full",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC9878684/",
    "https://api.github.com/repos/norahollenstein/zuco-benchmark/issues/5",
    "https://api.github.com/repos/norahollenstein/zuco-benchmark/issues/5/comments",
}
OSF_DATA_FORMAT_SHA256 = "3cc1b85c021042d93db4f077145b84e6c3beebad3a474f6781746a6a40dbdbb4"


def normalize_stimulus(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).split())


def stimulus_id(value: str) -> str:
    return hashlib.sha256(normalize_stimulus(value).encode("utf-8")).hexdigest()


def stable_hash(value: Any) -> str:
    rendered = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def validate_release_source_evidence(cache: dict[str, Any]) -> dict[str, Any]:
    """Validate compact source evidence and derive event roles from the cache."""
    failures: list[str] = []
    sources = cache.get("sources")
    if cache.get("schema_version") != 1 or not isinstance(sources, list) or not sources:
        return {"valid": False, "failures": ["CACHE_SCHEMA_INVALID"], "event_mapping": {}}
    seen: set[str] = set()
    event_mapping: dict[str, str] = {}
    for index, source in enumerate(sources):
        prefix = f"source[{index}]"
        if not isinstance(source, dict):
            failures.append(prefix + ":NOT_MAPPING")
            continue
        required = (
            "source_id", "url", "retrieved_at_utc", "raw_response_sha256",
            "normalized_claim_sha256", "source_type", "release_applicability",
            "binds_array_or_event", "locator", "extracted_claim", "verdict",
        )
        missing = [key for key in required if source.get(key) in (None, "")]
        if missing:
            failures.append(prefix + ":MISSING:" + ",".join(missing))
            continue
        source_id = str(source["source_id"])
        if source_id in seen:
            failures.append(prefix + ":DUPLICATE_SOURCE_ID")
        seen.add(source_id)
        if source["url"] not in ALLOWED_SOURCE_URLS:
            failures.append(prefix + ":URL_NOT_ALLOWED")
        raw_hash = str(source["raw_response_sha256"])
        if not re.fullmatch(r"[0-9a-f]{64}", raw_hash):
            failures.append(prefix + ":RAW_HASH_INVALID")
        if source["normalized_claim_sha256"] != stable_hash(source["extracted_claim"]):
            failures.append(prefix + ":CLAIM_TAMPER")
        if source_id == "osf_wiki_data_format":
            if raw_hash != OSF_DATA_FORMAT_SHA256:
                failures.append(prefix + ":UPSTREAM_HASH_DRIFT")
            claim = source["extracted_claim"]
            mapping = claim.get("event_mapping") if isinstance(claim, dict) else None
            if not isinstance(mapping, dict) or set(mapping.values()) - EVENT_ROLE_VALUES:
                failures.append(prefix + ":EVENT_MAPPING_INVALID")
            else:
                event_mapping = {str(key): str(value) for key, value in mapping.items()}
            if source["release_applicability"] != "DIRECT_ZUCO2_TASK1":
                failures.append(prefix + ":EVENT_APPLICABILITY_INVALID")
    required_roles = {
        "10": "ORDINARY_ONSET", "11": "ORDINARY_FINISH",
        "12": "CONTROL_ONSET", "13": "CONTROL_FINISH", "15": "CONTROL_RESPONSE",
    }
    if event_mapping != required_roles:
        failures.append("EVENT_MAPPING_INCOMPLETE")
    return {
        "valid": not failures,
        "failures": failures,
        "event_mapping": event_mapping if not failures else {},
        "scientific_evidence_sha256": stable_hash([
            {key: value for key, value in source.items() if key != "retrieved_at_utc"}
            for source in sources if isinstance(source, dict)
        ]),
    }


def parse_task1_events(
    codes: Sequence[str],
    latencies: Sequence[float],
    semantic_mapping: dict[str, str],
) -> dict[str, Any]:
    """Pure strict parser for the ordered task-1 event state machine.

    Private sample boundaries are returned for in-memory comparison and must be
    removed from serialized artifacts.
    """
    occurrences: list[dict[str, Any]] = []
    anomalies: list[dict[str, Any]] = []
    stack: list[dict[str, Any]] = []
    pending_control: dict[str, Any] | None = None

    def anomaly(reason: str, event_ordinal: int, code: str, state: str) -> None:
        anomalies.append({
            "reason": reason, "event_ordinal": event_ordinal,
            "code": code, "state": state,
        })

    for event_ordinal, (raw_code, latency) in enumerate(zip(codes, latencies), 1):
        code = str(raw_code).strip()
        role = semantic_mapping.get(code)
        if role in {"ORDINARY_ONSET", "CONTROL_ONSET"}:
            if pending_control is not None:
                pending_control["control_response_present"] = False
                pending_control["event_pair_state"] = "INVALID"
                pending_control["anomaly_reasons"].append("MISSING_CONTROL_RESPONSE")
                anomaly("MISSING_CONTROL_RESPONSE", event_ordinal, code, "PENDING_CONTROL_RESPONSE")
                pending_control = None
            if stack:
                anomaly("NESTED_ONSET", event_ordinal, code, stack[-1]["sentence_class"])
                for item in stack:
                    item["nested"] = True
            stack.append({
                "sentence_class": "ORDINARY_SENTENCE" if role == "ORDINARY_ONSET" else "CONTROL_SENTENCE",
                "onset_code": code, "onset_sample": float(latency),
                "onset_event_ordinal": event_ordinal, "nested": bool(stack),
            })
        elif role in {"ORDINARY_FINISH", "CONTROL_FINISH"}:
            expected_class = "ORDINARY_SENTENCE" if role == "ORDINARY_FINISH" else "CONTROL_SENTENCE"
            if not stack:
                anomaly("ORPHAN_FINISH", event_ordinal, code, "NO_OPEN_SENTENCE")
                continue
            opened = stack.pop()
            reasons: list[str] = []
            if opened["sentence_class"] != expected_class:
                reasons.append("WRONG_FINISH_CLASS")
                anomaly("WRONG_FINISH_CLASS", event_ordinal, code, opened["sentence_class"])
            if opened.get("nested") or stack:
                reasons.append("NESTED_SENTENCE")
            occurrence = {
                "sentence_class": opened["sentence_class"],
                "onset_code": opened["onset_code"], "finish_code": code,
                "control_response_present": None if opened["sentence_class"] == "ORDINARY_SENTENCE" else False,
                "onset_latency_valid": True, "finish_latency_valid": True,
                "event_pair_state": "VALID" if not reasons else "INVALID",
                "anomaly_reasons": reasons,
                "_onset_sample": opened["onset_sample"], "_finish_sample": float(latency),
                "_onset_event_ordinal": opened["onset_event_ordinal"],
                "_finish_event_ordinal": event_ordinal,
            }
            occurrences.append(occurrence)
            if occurrence["sentence_class"] == "CONTROL_SENTENCE":
                if pending_control is not None:
                    pending_control["event_pair_state"] = "INVALID"
                    pending_control["anomaly_reasons"].append("MISSING_CONTROL_RESPONSE")
                pending_control = occurrence
        elif role == "CONTROL_RESPONSE":
            if pending_control is None or stack:
                anomaly("EXTRA_OR_MISPLACED_CONTROL_RESPONSE", event_ordinal, code, "OPEN_SENTENCE" if stack else "NO_PENDING_CONTROL")
            else:
                pending_control["control_response_present"] = True
                pending_control = None
        # Marker and unknown classes are retained in aggregate counts only.

    if stack:
        for opened in stack:
            anomaly("UNCLOSED_SENTENCE", opened["onset_event_ordinal"], opened["onset_code"], opened["sentence_class"])
    if pending_control is not None:
        pending_control["event_pair_state"] = "INVALID"
        pending_control["anomaly_reasons"].append("MISSING_CONTROL_RESPONSE")
        anomaly("MISSING_CONTROL_RESPONSE", len(codes), "END_OF_BLOCK", "PENDING_CONTROL_RESPONSE")
    occurrences.sort(key=lambda item: (item["_onset_sample"], item["_onset_event_ordinal"]))
    for index, occurrence in enumerate(occurrences, 1):
        occurrence["block_occurrence_index"] = index
    ordinary = sum(item["sentence_class"] == "ORDINARY_SENTENCE" for item in occurrences)
    control = sum(item["sentence_class"] == "CONTROL_SENTENCE" for item in occurrences)
    return {
        "occurrences": occurrences,
        "anomalies": anomalies,
        "ordinary_count": ordinary,
        "control_count": control,
        "control_response_count": sum(item["control_response_present"] is True for item in occurrences),
        "pair_contract_valid": not anomalies and all(item["event_pair_state"] == "VALID" for item in occurrences),
    }


def _within(root: Path, path: Path, *, must_exist: bool = True) -> Path:
    root = root.resolve(strict=True)
    candidate = path if path.is_absolute() else root / path
    try:
        lexical = Path(os.path.abspath(candidate))
        relative = lexical.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"PATH_OUTSIDE_DATASET_ROOT: {candidate}") from exc
    current = root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise ValueError(f"SYMLINK_REJECTED: {current}")
    resolved = lexical.resolve(strict=must_exist)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"PATH_OUTSIDE_DATASET_ROOT: {candidate}") from exc
    return resolved


def _decode_char_dataset(dataset: h5py.Dataset) -> str:
    if dataset.size == 0:
        return ""
    if dataset.dtype.kind in "ui":
        return "".join(chr(int(item)) for item in np.asarray(dataset[...]).reshape(-1) if int(item))
    if dataset.dtype.kind in "SU":
        return "".join(np.asarray(dataset.asstr()[...]).reshape(-1).tolist())
    raise ValueError(f"UNSUPPORTED_STRING_DTYPE: {dataset.dtype}")


def _reference_at(file: h5py.File, dataset: h5py.Dataset, index: int) -> tuple[bool, h5py.Dataset | None]:
    try:
        reference = dataset[index, 0]
        if not isinstance(reference, h5py.Reference) or not reference:
            return False, None
        target = file[reference]
        return True, target if isinstance(target, h5py.Dataset) else None
    except (KeyError, ValueError, RuntimeError, TypeError, IndexError):
        return False, None


def _finite_counts(dataset: h5py.Dataset, max_rows: int = 8192) -> tuple[int, int]:
    if dataset.dtype.kind not in "fiu" or dataset.size == 0:
        return 0, 0
    finite = total = 0
    if dataset.ndim == 0:
        array = np.asarray(dataset[()])
        return int(np.isfinite(array).sum()), int(array.size)
    step = max(1, min(max_rows, dataset.shape[0]))
    for start in range(0, dataset.shape[0], step):
        array = np.asarray(dataset[start : start + step])
        finite += int(np.isfinite(array).sum())
        total += int(array.size)
    return finite, total


def classify_eeg_cell(reference_present: bool, target: h5py.Dataset | None) -> dict[str, Any]:
    shape = list(target.shape) if target is not None else []
    nonempty = bool(target is not None and target.size > 0)
    numeric = bool(target is not None and target.dtype.kind in "fiu")
    finite_count, total = _finite_counts(target) if target is not None and numeric else (0, 0)
    nonfinite_count = total - finite_count
    samples = int(shape[0]) if len(shape) == 2 else None
    channels = int(shape[1]) if len(shape) == 2 else None
    axis_valid = len(shape) == 2 and channels == 105
    axis_contract = "samples_by_channels" if axis_valid else "unresolved"

    if not reference_present or target is None:
        state, reason = "MISSING_REFERENCE", "RAW_REFERENCE_MISSING_OR_INVALID"
    elif not nonempty:
        state, reason = "EMPTY", "RAW_DATASET_EMPTY"
    elif not numeric:
        state, reason = "INVALID_AXIS", "RAW_DATASET_NON_NUMERIC"
    elif finite_count == 0:
        state, reason = "NONFINITE_PLACEHOLDER", "NO_FINITE_EEG_TIMESERIES_VALUES"
    elif nonfinite_count > 0:
        state, reason = "PARTIAL_NONFINITE", "EEG_CELL_CONTAINS_NONFINITE_VALUES"
    elif not axis_valid:
        state, reason = "INVALID_AXIS", "EXPECTED_SAMPLES_BY_105_CHANNELS"
    elif samples == 1:
        state, reason = "FINITE_SINGLE_SAMPLE_REVIEW_REQUIRED", "FINITE_BUT_NOT_A_MULTISAMPLE_TIMESERIES"
    else:
        state, reason = "VALID_FINITE_MULTISAMPLE", None
    return {
        "raw_reference_present": reference_present,
        "raw_nonempty": nonempty,
        "raw_numeric": numeric,
        "raw_shape": shape,
        "raw_samples": samples,
        "raw_channels": channels,
        "raw_axis_contract": axis_contract,
        "raw_finite_count": finite_count,
        "raw_nonfinite_count": nonfinite_count,
        "eeg_cell_state": state,
        "admissible_sentence_eeg": state == "VALID_FINITE_MULTISAMPLE",
        "missing_or_exclusion_reason": reason,
    }


def audit_summary(path: Path, expected_slots: int = 349) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    match = SUMMARY_RE.search(path.name)
    if not match:
        raise ValueError(f"SUMMARY_NAME_INVALID: {path.name}")
    subject = match.group(1)
    rows: list[dict[str, Any]] = []
    with h5py.File(path, "r") as file:
        group = file.get("sentenceData")
        if not isinstance(group, h5py.Group):
            raise ValueError(f"SUMMARY_SCHEMA_MISSING: {path.name}:sentenceData")
        fields = sorted(group.keys())
        missing_fields = sorted(set(EXPECTED_SUMMARY_FIELDS) - set(fields))
        slot_counts = {name: int(group[name].shape[0]) for name in fields}
        wrong_slots = {name: count for name, count in slot_counts.items() if count != expected_slots}
        if wrong_slots or "content" not in group or "rawData" not in group:
            raise ValueError(f"SUMMARY_SLOT_OR_FIELD_MISMATCH: {path.name}:{wrong_slots}:{missing_fields}")
        state_counts: Counter[str] = Counter()
        shape_counts: Counter[str] = Counter()
        for slot in range(expected_slots):
            content_ref, content_target = _reference_at(file, group["content"], slot)
            raw_ref, raw_target = _reference_at(file, group["rawData"], slot)
            text = _decode_char_dataset(content_target) if content_ref and content_target is not None else ""
            normalized = normalize_stimulus(text)
            cell = classify_eeg_cell(raw_ref, raw_target)
            if not normalized and cell["missing_or_exclusion_reason"] is None:
                cell["missing_or_exclusion_reason"] = "STIMULUS_CONTENT_MISSING"
                cell["admissible_sentence_eeg"] = False
            state_counts[cell["eeg_cell_state"]] += 1
            shape_counts[str(cell["raw_shape"])] += 1
            rows.append({
                "subject": subject, "session": 1, "task": "NR", "slot": slot + 1,
                "block": None, "material_line": None, "occurrence_id": None,
                "stimulus_sha256": stimulus_id(normalized) if normalized else None,
                "stimulus_length_chars": len(normalized), "content_present": bool(normalized),
                **cell,
            })
    return ({
        "path": path.as_posix(), "subject": subject, "format": "MATLAB_v7.3_HDF5",
        "fields": fields, "missing_expected_fields": missing_fields,
        "slot_count": expected_slots, "cell_state_counts": dict(sorted(state_counts.items())),
        "raw_shape_counts": dict(sorted(shape_counts.items())),
    }, rows)


def read_material_contract(paths: Sequence[Path]) -> dict[str, Any]:
    all_rows: list[dict[str, Any]] = []
    practice: list[dict[str, Any]] = []
    ordered: list[dict[str, Any]] = []
    per_block_total: dict[int, int] = {}
    per_block_post: dict[int, int] = {}
    sorted_paths = sorted(paths, key=lambda path: int(MATERIAL_RE.fullmatch(path.name).group(1)))
    for path in sorted_paths:
        match = MATERIAL_RE.fullmatch(path.name)
        if not match:
            raise ValueError(f"MATERIAL_NAME_INVALID: {path.name}")
        block = int(match.group(1))
        block_rows: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for line, columns in enumerate(csv.reader(handle, delimiter=";"), 1):
                if not columns or not any(value.strip() for value in columns):
                    continue
                text = normalize_stimulus(columns[2] if len(columns) > 2 else "")
                record = {
                    "block": block, "material_line": line, "stimulus_sha256": stimulus_id(text),
                    "stimulus_length_chars": len(text), "practice": len(block_rows) < 3,
                }
                block_rows.append(record)
                all_rows.append(record)
                (practice if record["practice"] else ordered).append(record)
        per_block_total[block] = len(block_rows)
        per_block_post[block] = sum(not row["practice"] for row in block_rows)
    return {
        "total_rows": len(all_rows), "practice_rows_excluded": len(practice),
        "post_practice_rows": len(ordered), "per_block_total_rows": per_block_total,
        "per_block_post_practice_rows": per_block_post, "practice_ledger": practice,
        "ordered_rows": ordered,
    }


def apply_material_sequence(rows: list[dict[str, Any]], material: dict[str, Any]) -> dict[str, Any]:
    ordered = material["ordered_rows"]
    by_subject: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_subject[row["subject"]].append(row)
    mismatches: list[dict[str, Any]] = []
    exact = 0
    for subject in sorted(by_subject):
        subject_rows = sorted(by_subject[subject], key=lambda item: item["slot"])
        if len(subject_rows) != len(ordered):
            mismatches.append({"subject": subject, "reason": "SLOT_COUNT", "actual": len(subject_rows)})
            continue
        for row, source in zip(subject_rows, ordered):
            if row["stimulus_sha256"] == source["stimulus_sha256"]:
                exact += 1
            else:
                mismatches.append({"subject": subject, "slot": row["slot"], "reason": "HASH_MISMATCH"})
    passed = not mismatches and len(ordered) == 349
    if passed:
        for row in rows:
            source = ordered[row["slot"] - 1]
            row["block"] = source["block"]
            row["material_line"] = source["material_line"]
            row["occurrence_id"] = stable_hash({
                "task": row["task"], "block": row["block"],
                "material_line": row["material_line"], "slot": row["slot"],
            })
    return {
        "result": "PASS" if passed else "FAIL", "ordered_exact_match_count": exact,
        "ordered_expected_match_count": len(rows), "mismatches": mismatches,
    }


def duplicate_groups(material_rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for slot, row in enumerate(material_rows, 1):
        grouped[row["stimulus_sha256"]].append({**row, "slot": slot})
    output = []
    for key, values in grouped.items():
        blocks = sorted({item["block"] for item in values})
        if len(values) > 1:
            occurrences = [stable_hash({"task": "NR", "block": item["block"], "material_line": item["material_line"], "slot": item["slot"]}) for item in values]
            output.append({
                "stimulus_sha256": key, "slots": [item["slot"] for item in values],
                "blocks": blocks, "cross_block": len(blocks) > 1,
                "occurrence_ids": occurrences, "occurrence_ids_distinct": len(set(occurrences)) == len(occurrences),
            })
    return sorted(output, key=lambda item: item["stimulus_sha256"])


def _scalar(dataset: h5py.Dataset) -> float | int | None:
    if dataset.size != 1 or dataset.dtype.kind not in "fiu":
        return None
    value = float(np.asarray(dataset[...]).reshape(-1)[0])
    return int(value) if value.is_integer() else value


def _string_from_node(file: h5py.File, node: h5py.Dataset) -> str | None:
    if node.dtype.kind == "O":
        values = np.asarray(node[...]).reshape(-1)
        if len(values) != 1 or not isinstance(values[0], h5py.Reference) or not values[0]:
            return None
        target = file[values[0]]
        return _decode_char_dataset(target) if isinstance(target, h5py.Dataset) else None
    try:
        return _decode_char_dataset(node)
    except ValueError:
        return None


def _reference_vector(file: h5py.File, dataset: h5py.Dataset) -> list[h5py.Dataset | None]:
    output = []
    for reference in np.asarray(dataset[...]).reshape(-1):
        try:
            target = file[reference] if isinstance(reference, h5py.Reference) and reference else None
        except (KeyError, ValueError, RuntimeError):
            target = None
        output.append(target if isinstance(target, h5py.Dataset) else None)
    return output


def validate_event_values(latencies: Sequence[float], durations: Sequence[float], urevents: Sequence[float], *, pnts: int, urevent_count: int) -> dict[str, bool]:
    latency_array = np.asarray(latencies, dtype=float)
    duration_array = np.asarray(durations, dtype=float)
    urevent_array = np.asarray(urevents, dtype=float)
    return {
        "latency_finite": bool(np.isfinite(latency_array).all()),
        "latency_integer_samples": bool(np.isfinite(latency_array).all() and np.all(latency_array == np.floor(latency_array))),
        "latency_nondecreasing": bool(len(latency_array) < 2 or np.all(np.diff(latency_array) >= 0)),
        "latency_in_sample_bounds": bool(len(latency_array) > 0 and np.all((latency_array >= 1) & (latency_array <= pnts))),
        "duration_nonnegative_finite": bool(np.isfinite(duration_array).all() and np.all(duration_array >= 0)),
        "urevent_references_valid": bool(np.isfinite(urevent_array).all() and np.all(urevent_array == np.floor(urevent_array)) and np.all((urevent_array >= 1) & (urevent_array <= urevent_count))),
    }


def _event_field(file: h5py.File, dataset: h5py.Dataset, *, allow_strings: bool = False) -> tuple[list[Any], Counter[str], int]:
    values: list[Any] = []
    classes: Counter[str] = Counter()
    missing = 0
    for target in _reference_vector(file, dataset):
        if target is None or target.size == 0:
            missing += 1
            values.append(None)
            classes["missing"] += 1
        elif target.dtype.kind in "fiu" and target.size == 1:
            value = float(np.asarray(target[...]).reshape(-1)[0])
            values.append(value)
            classes[f"numeric_scalar:{target.dtype}"] += 1
        elif allow_strings and target.dtype.kind in "uiSU":
            text = _decode_char_dataset(target).strip()
            values.append(text if len(text) <= 64 else {"sha256": stimulus_id(text), "class": "long_string"})
            classes[f"short_string:{target.dtype}" if len(text) <= 64 else "long_string_hashed"] += 1
        else:
            values.append(None)
            classes[f"unsupported:{target.dtype}:{list(target.shape)}"] += 1
    return values, classes, missing


def audit_events(
    file: h5py.File,
    eeg: h5py.Group,
    *,
    semantic_mapping: dict[str, str] | None = None,
) -> dict[str, Any]:
    event = eeg.get("event")
    urevent_group = eeg.get("urevent")
    required = ("duration", "latency", "type", "urevent", "value")
    if not isinstance(event, h5py.Group):
        return {"event_structure_valid": False, "event_semantics_bound": False, "reason": "EVENT_GROUP_MISSING"}
    fields = sorted(event.keys())
    missing_fields = sorted(set(required) - set(fields))
    count = int(event[fields[0]].shape[0]) if fields else 0
    field_contracts: dict[str, Any] = {}
    decoded: dict[str, list[Any]] = {}
    for name in fields:
        values, classes, missing = _event_field(file, event[name], allow_strings=name in {"type", "value"})
        decoded[name] = values
        field_contracts[name] = {"count": len(values), "class_counts": dict(sorted(classes.items())), "missing_count": missing}
    urevent_count = 0
    if isinstance(urevent_group, h5py.Group) and len(urevent_group):
        first = next(iter(urevent_group.values()))
        urevent_count = int(first.shape[0])
    numeric_ready = all(name in decoded and all(isinstance(item, (int, float)) for item in decoded[name]) for name in ("latency", "duration", "urevent"))
    value_checks = validate_event_values(decoded.get("latency", []), decoded.get("duration", []), decoded.get("urevent", []), pnts=int(_scalar(eeg["pnts"]) or max(eeg["data"].shape)), urevent_count=urevent_count) if numeric_ready else {key: False for key in ("latency_finite", "latency_integer_samples", "latency_nondecreasing", "latency_in_sample_bounds", "duration_nonnegative_finite", "urevent_references_valid")}
    types = [str(item).strip() for item in decoded.get("type", []) if isinstance(item, str)]
    type_counts = dict(sorted(Counter(types).items()))
    values = [str(item).strip() for item in decoded.get("value", []) if isinstance(item, str)]
    value_counts = dict(sorted(Counter(values).items()))
    structure_valid = not missing_fields and count > 0 and all(item["count"] == count and item["missing_count"] == 0 for item in field_contracts.values()) and all(value_checks.values())
    parser_result = parse_task1_events(types, decoded.get("latency", []), semantic_mapping or {}) if numeric_ready else {
        "occurrences": [], "anomalies": [{"reason": "NUMERIC_EVENT_FIELDS_INVALID"}],
        "ordinary_count": 0, "control_count": 0, "control_response_count": 0,
        "pair_contract_valid": False,
    }
    mapping_bound = bool(semantic_mapping)
    semantics_bound = structure_valid and mapping_bound and parser_result["pair_contract_valid"]
    return {
        "event_count": count, "fields": fields, "missing_fields": missing_fields,
        "field_contracts": field_contracts, "value_checks": value_checks,
        "type_counts": type_counts, "value_counts": value_counts,
        "mapped_trigger_counts": {code: type_counts.get(code, 0) for code in (semantic_mapping or {})},
        "unmapped_trigger_codes": sorted(set(type_counts) - set(semantic_mapping or {})),
        "ordinary_count": parser_result["ordinary_count"],
        "control_count": parser_result["control_count"],
        "control_response_count": parser_result["control_response_count"],
        "sentence_occurrence_count": len(parser_result["occurrences"]),
        "sentence_onset_finish_pairs_valid": parser_result["pair_contract_valid"],
        "sanitized_anomalies": parser_result["anomalies"],
        "event_structure_valid": structure_valid,
        "event_semantics_bound": semantics_bound,
        "semantic_source": "release_source_evidence:osf_wiki_data_format" if mapping_bound else None,
        "_occurrences": parser_result["occurrences"],
    }


def _find_unit_metadata(file: h5py.File, roots: Iterable[h5py.Group]) -> tuple[str | None, list[str]]:
    unit: str | None = None
    candidates: set[str] = set()
    def walk(group: h5py.Group, depth: int = 0) -> None:
        nonlocal unit
        if depth > 6:
            return
        for key, value in group.attrs.items():
            if "unit" in str(key).lower():
                candidates.add(f"{group.name}@{key}")
                if isinstance(value, (str, bytes)):
                    unit = value.decode("utf-8", "replace") if isinstance(value, bytes) else value
        for name, node in group.items():
            if node.name.endswith("/data") or name in {"#refs#", "#subsystem#"}:
                continue
            if "unit" in name.lower():
                candidates.add(node.name)
                if isinstance(node, h5py.Dataset):
                    unit = _string_from_node(file, node) or unit
            if isinstance(node, h5py.Group):
                walk(node, depth + 1)
    for root in roots:
        walk(root)
    return unit, sorted(candidates)


def audit_eeg_metadata(path: Path, *, semantic_mapping: dict[str, str] | None = None) -> dict[str, Any]:
    match = EEG_RE.search(path.name)
    if not match:
        raise ValueError(f"EEG_NAME_INVALID: {path.name}")
    with h5py.File(path, "r") as file:
        eeg, automagic = file.get("EEG"), file.get("automagic")
        if not isinstance(eeg, h5py.Group) or not isinstance(automagic, h5py.Group):
            raise ValueError(f"EEG_SCHEMA_MISSING: {path.name}")
        data, chanlocs = eeg["data"], eeg["chanlocs"]
        labels = [_string_from_node(file, item) if item is not None else None for item in _reference_vector(file, chanlocs["labels"])]
        coordinate_input, missing_coordinates = [], []
        coordinate_fields = [name for name in ("X", "Y", "Z", "theta", "radius") if name in chanlocs]
        for name in coordinate_fields:
            values = [_scalar(item) if item is not None else None for item in _reference_vector(file, chanlocs[name])]
            if len(values) != len(labels) or any(value is None or not math.isfinite(float(value)) for value in values):
                missing_coordinates.append(name)
            coordinate_input.append([name, values])
        processed_raw = _string_from_node(file, eeg["ref"])
        processed = "common-average" if processed_raw in {"common", "common-average", "average"} else processed_raw
        acquisition = _string_from_node(file, automagic["EEGReference"])
        unit, unit_paths = _find_unit_metadata(file, (eeg, automagic))
        events = audit_events(file, eeg, semantic_mapping=semantic_mapping)
        return {
            "path": path.as_posix(), "subject": match.group(1), "block": int(match.group(2)),
            "data_shape": list(data.shape), "data_dtype": str(data.dtype),
            "channel_count": len(labels), "channel_labels_sha256": stable_hash(labels),
            "coordinate_fields": coordinate_fields,
            "coordinates_complete": len(coordinate_fields) == 5 and not missing_coordinates,
            "coordinates_sha256": stable_hash(coordinate_input),
            "expected_excluded_labels_present": sorted(set(labels) & set(EXPECTED_EXCLUDED_CHANNELS)),
            "sampling_hz": _scalar(eeg["srate"]), "unit": unit, "unit_candidate_paths": unit_paths,
            "acquisition_reference": acquisition, "processed_reference": processed,
            "trials": _scalar(eeg["trials"]), "events": events, "metadata_only": True,
        }


def derive_source_audit(
    cache: dict[str, Any], validation: dict[str, Any], *,
    local_summary: dict[str, Any], local_eeg: dict[str, Any],
    correspondence_complete: bool,
) -> dict[str, Any]:
    """Derive current-array verdicts from validated cache plus physical evidence."""
    direct_unit = False
    if validation["valid"]:
        for source in cache["sources"]:
            claim = source["extracted_claim"]
            if (
                source["release_applicability"] == "DIRECT_ZUCO2_NR_CURRENT_ARRAY"
                and isinstance(claim, dict) and claim.get("unit")
                and source["verdict"] == "DIRECT_ARRAY_UNIT_BOUND"
            ):
                direct_unit = True
    return {
        "schema_version": 2,
        "source_evidence_cache_valid": validation["valid"],
        "source_evidence_failures": validation["failures"],
        "source_evidence_scientific_sha256": validation.get("scientific_evidence_sha256"),
        "local_summary_metadata_sha256": local_summary["metadata_contract_sha256"],
        "local_preprocessed_metadata_sha256": local_eeg["metadata_contract_sha256"],
        "preprocessed_EEG_data_reference_status": "BOUND",
        "preprocessed_EEG_data_unit_status": "BOUND" if direct_unit else "UNRESOLVED",
        "summary_rawData_layer_status": "BOUND_BY_EXACT_CORRESPONDENCE" if correspondence_complete else "UNRESOLVED",
        "summary_rawData_reference_status": "BOUND_BY_EXACT_CORRESPONDENCE" if correspondence_complete else "UNRESOLVED",
        "summary_rawData_unit_status": "BOUND" if direct_unit and correspondence_complete else "UNRESOLVED",
        "event_semantics_source_status": "BOUND" if validation["valid"] else "UNRESOLVED",
        "stop_reason": None if direct_unit else "No direct current-release ZuCo 2.0 NR array unit binding in bounded evidence.",
    }


def _window_bounds(onset: float, finish: float, convention: str) -> tuple[int, int]:
    start = int(onset) - 1
    if convention == "EEGLAB_ONE_BASED_FINISH_EXCLUSIVE":
        return start, int(finish) - 1
    if convention == "EEGLAB_ONE_BASED_FINISH_INCLUSIVE":
        return start, int(finish)
    raise ValueError(f"UNKNOWN_ENDPOINT_CONVENTION: {convention}")


def compare_segment_arrays(
    preprocessed: np.ndarray,
    summary: np.ndarray,
) -> dict[str, Any]:
    """Compare two already-oriented finite arrays exactly without emitting values."""
    if preprocessed.shape != summary.shape:
        return {"state": "SHAPE_MISMATCH", "dtype_exact": False, "canonical_numeric_equal": False}
    dtype_exact = preprocessed.dtype == summary.dtype
    equal = bool(np.array_equal(preprocessed, summary, equal_nan=True))
    return {
        "state": "EXACT_MATCH" if equal else "VALUE_MISMATCH",
        "dtype_exact": bool(dtype_exact and equal),
        "canonical_numeric_equal": equal,
    }


def select_global_convention(results: dict[str, Counter[str]], comparable_rows: int) -> dict[str, Any]:
    matching = [
        name for name in ENDPOINT_CONVENTIONS
        if results.get(name, Counter()).get("EXACT_MATCH", 0) == comparable_rows
        and sum(results.get(name, Counter()).values()) == comparable_rows
    ]
    return {
        "result": "PASS" if len(matching) == 1 else "FAIL",
        "selected": matching[0] if len(matching) == 1 else None,
        "matching_conventions": matching,
    }


def finalize_row_admission(row: dict[str, Any], *, event_valid: bool, segment_state: str) -> None:
    row["event_occurrence_valid"] = event_valid
    row["segment_correspondence_state"] = segment_state
    row["final_admission_candidate"] = bool(
        row.get("content_present")
        and row.get("eeg_cell_state") == "VALID_FINITE_MULTISAMPLE"
        and event_valid
        and segment_state == "EXACT_MATCH"
    )
    reasons = []
    if not row.get("content_present"):
        reasons.append("STIMULUS_CONTENT_MISSING")
    if row.get("eeg_cell_state") != "VALID_FINITE_MULTISAMPLE":
        reasons.append(row.get("missing_or_exclusion_reason") or "EEG_CELL_NOT_VALID")
    if not event_valid:
        reasons.append("EVENT_OCCURRENCE_UNRESOLVED")
    if row.get("eeg_cell_state") == "VALID_FINITE_MULTISAMPLE" and segment_state != "EXACT_MATCH":
        reasons.append("SEGMENT_CORRESPONDENCE_NOT_EXACT")
    row["final_exclusion_reason"] = ";".join(dict.fromkeys(reasons)) or None


def _read_oriented_window(dataset: h5py.Dataset, start: int, end: int) -> np.ndarray:
    if start < 0 or end < start:
        return np.empty((0, 105), dtype=dataset.dtype)
    if dataset.ndim != 2:
        return np.empty((0, 0), dtype=dataset.dtype)
    if dataset.shape[1] == 105:
        return np.asarray(dataset[start:end, :])
    if dataset.shape[0] == 105:
        return np.asarray(dataset[:, start:end]).T
    return np.empty((0, 0), dtype=dataset.dtype)


def _read_oriented_summary(dataset: h5py.Dataset) -> np.ndarray:
    value = np.asarray(dataset[...])
    if value.ndim == 2 and value.shape[1] == 105:
        return value
    if value.ndim == 2 and value.shape[0] == 105:
        return value.T
    return value


def condition3_from_subpredicates(items: Sequence[dict[str, Any]]) -> tuple[str, list[str]]:
    failed = [item["id"] for item in items if item["result"] != "PASS"]
    return ("FAIL" if failed else "PASS"), failed


def _predicate(name: str, passed: bool, evidence: str, detail: str) -> dict[str, str]:
    return {"id": name, "result": "PASS" if passed else "FAIL", "evidence": evidence, "detail": detail}


def _quantiles(values: Sequence[int]) -> dict[str, int | None]:
    if not values:
        return {key: None for key in ("min", "q25", "median", "q75", "max")}
    array = np.asarray(sorted(values), dtype=int)
    result = np.quantile(array, [0, .25, .5, .75, 1], method="nearest")
    return dict(zip(("min", "q25", "median", "q75", "max"), (int(item) for item in result)))


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"YAML_MAPPING_REQUIRED: {path}")
    return value


def reuse_run005_hashes(root: Path, cache: Path, prior_manifest: Path) -> dict[str, Any]:
    official = {item["path"]: item for item in _load_yaml(cache).get("files", [])}
    prior = _load_yaml(prior_manifest)
    prior_files = {item["path"]: item for item in prior.get("files", [])}
    files, failures = [], []
    for path in sorted(official):
        source = prior_files.get(path)
        current = root / path
        okay = bool(source and source.get("comparison") == "MATCH" and source.get("local_sha256") == official[path].get("sha256") and current.is_file() and current.stat().st_size == official[path].get("size_bytes"))
        if not okay:
            failures.append(path)
        files.append({
            "path": path, "size_bytes": current.stat().st_size if current.is_file() else None,
            "local_sha256": source.get("local_sha256") if source else None,
            "osf_sha256": official[path].get("sha256"),
            "identity_status": "REUSED_VERIFIED_RUN005_NO_REHASH" if okay else "PROVENANCE_DRIFT",
        })
    return {"result": "PASS" if not failures and len(files) == 27 else "FAIL", "files": files, "failures": failures, "large_files_rehashed": False, "evidence": "run 005 schema-v1 manifest plus current size stat and OSF cache"}


def _prior_null_count(path: Path) -> int:
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if json.loads(line).get("block") is None:
                count += 1
    return count


def audit(
    dataset_root: Path,
    osf_cache: Path,
    release_source_evidence: Path,
    *,
    prior_manifest: Path | None = None,
    prior_stimulus_manifest: Path | None = None,
    enforce_frozen_expectations: bool = True,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    root = dataset_root.resolve(strict=True)
    repo = Path(__file__).resolve().parents[1]
    prior_manifest = prior_manifest or repo / "artifacts/admission/zuco2_nr_targeted_manifest.yaml"
    prior_stimulus_manifest = prior_stimulus_manifest or repo / "artifacts/admission/zuco2_nr_stimulus_manifest.jsonl"
    source_cache = _load_yaml(release_source_evidence.resolve(strict=True))
    source_validation = validate_release_source_evidence(source_cache)
    semantic_mapping = source_validation["event_mapping"]
    summary_paths = sorted(_within(root, item) for item in root.glob("task1 - NR/Matlab files/results*_NR.mat"))
    csv_paths = sorted((_within(root, item) for item in root.glob("task_materials/nr_[1-7].csv")), key=lambda item: int(MATERIAL_RE.fullmatch(item.name).group(1)))
    eeg_paths = sorted(_within(root, item) for item in root.glob("task1 - NR/Preprocessed/*/*_EEG.mat"))
    if (len(summary_paths), len(csv_paths), len(eeg_paths)) != (18, 7, 126):
        raise ValueError(f"SCOPE_COUNT_MISMATCH: {len(summary_paths)}/{len(csv_paths)}/{len(eeg_paths)}")

    summaries, rows = [], []
    for path in summary_paths:
        item, subject_rows = audit_summary(path)
        item["path"] = path.relative_to(root).as_posix()
        summaries.append(item)
        rows.extend(subject_rows)
    material = read_material_contract(csv_paths)
    sequence = apply_material_sequence(rows, material)
    duplicates = duplicate_groups(material["ordered_rows"])
    eeg_files = [audit_eeg_metadata(path, semantic_mapping=semantic_mapping) for path in eeg_paths]
    for item, path in zip(eeg_files, eeg_paths):
        item["path"] = path.relative_to(root).as_posix()

    state_counts = Counter(row["eeg_cell_state"] for row in rows)
    by_subject = {subject: dict(sorted(Counter(row["eeg_cell_state"] for row in rows if row["subject"] == subject).items())) for subject in sorted({row["subject"] for row in rows})}
    by_block = {block: dict(sorted(Counter(row["eeg_cell_state"] for row in rows if row["block"] == block).items())) for block in range(1, 8)}
    cell_valid_count = state_counts["VALID_FINITE_MULTISAMPLE"]
    valid_lengths = [row["raw_samples"] for row in rows if row["eeg_cell_state"] == "VALID_FINITE_MULTISAMPLE"]
    placeholder_subject = {key: value.get("NONFINITE_PLACEHOLDER", 0) for key, value in by_subject.items() if value.get("NONFINITE_PLACEHOLDER", 0)}
    placeholder_block = {key: value.get("NONFINITE_PLACEHOLDER", 0) for key, value in by_block.items()}
    channel_hashes = sorted({item["channel_labels_sha256"] for item in eeg_files})
    coordinate_hashes = sorted({item["coordinates_sha256"] for item in eeg_files})
    unit_values = sorted({item["unit"] for item in eeg_files if item["unit"]})
    event_structure = all(item["events"]["event_structure_valid"] for item in eeg_files)

    summary_meta = {"files": 18, "missing_fields": sorted({field for item in summaries for field in item["missing_expected_fields"]}), "metadata_contract_sha256": stable_hash([{"subject": item["subject"], "fields": item["fields"], "slots": item["slot_count"]} for item in summaries])}
    eeg_meta = {"files": 126, "unit_values": unit_values, "unit_candidate_paths": sorted({path for item in eeg_files for path in item["unit_candidate_paths"]}), "metadata_contract_sha256": stable_hash([{"subject": item["subject"], "block": item["block"], "shape": item["data_shape"], "reference": item["processed_reference"], "unit": item["unit"]} for item in eeg_files])}
    hash_provenance = reuse_run005_hashes(root, osf_cache.resolve(strict=True), prior_manifest.resolve(strict=True))
    prior_null = _prior_null_count(prior_stimulus_manifest.resolve(strict=True))

    block_offsets: dict[int, int] = {}
    running = 0
    for block in range(1, 8):
        block_offsets[block] = running
        running += EXPECTED_POST_PRACTICE_COUNTS[block]
    event_by_row: dict[tuple[str, int], dict[str, Any]] = {}
    event_occurrences: list[dict[str, Any]] = []
    by_subject_event_counts: dict[str, Counter[str]] = defaultdict(Counter)
    by_block_event_counts: dict[int, Counter[str]] = defaultdict(Counter)
    for item in eeg_files:
        subject, block = item["subject"], item["block"]
        parsed = item["events"].pop("_occurrences", [])
        for occurrence in parsed:
            slot = block_offsets[block] + occurrence["block_occurrence_index"]
            occurrence["subject"] = subject
            occurrence["block"] = block
            occurrence["global_slot"] = slot
            occurrence["event_pair_state"] = (
                occurrence["event_pair_state"] if item["events"]["event_structure_valid"] else "INVALID"
            )
            event_by_row[(subject, slot)] = occurrence
            event_occurrences.append(occurrence)
            by_subject_event_counts[subject][occurrence["sentence_class"]] += 1
            by_block_event_counts[block][occurrence["sentence_class"]] += 1

    rows_by_key = {(row["subject"], row["slot"]): row for row in rows}
    eeg_path_by_key = {(item["subject"], item["block"]): root / item["path"] for item in eeg_files}
    summary_path_by_subject = {item["subject"]: path for item, path in zip(summaries, summary_paths)}
    comparison_by_convention: dict[str, Counter[str]] = {name: Counter() for name in ENDPOINT_CONVENTIONS}
    comparison_details: dict[tuple[str, int], dict[str, dict[str, Any]]] = {}
    bytes_read = 0

    comparable_keys = [
        (row["subject"], row["slot"]) for row in rows
        if row["eeg_cell_state"] == "VALID_FINITE_MULTISAMPLE"
        and (row["subject"], row["slot"]) in event_by_row
        and event_by_row[(row["subject"], row["slot"])]["event_pair_state"] == "VALID"
    ]
    unresolved_keys = {
        (row["subject"], row["slot"]) for row in rows
        if row["eeg_cell_state"] == "VALID_FINITE_MULTISAMPLE"
        and (row["subject"], row["slot"]) not in set(comparable_keys)
    }
    pilot_keys: set[tuple[str, int]] = set()
    grouped_comparable: dict[tuple[str, int], list[tuple[str, int]]] = defaultdict(list)
    for key in comparable_keys:
        grouped_comparable[(key[0], rows_by_key[key]["block"])].append(key)
    for values in grouped_comparable.values():
        values.sort(key=lambda key: key[1])
        pilot_keys.update({values[0], values[len(values) // 2], values[-1]})
    for key, occurrence in event_by_row.items():
        if key[0] == "YTL" and occurrence["event_pair_state"] != "VALID":
            for delta in (-2, -1, 0, 1, 2):
                neighbor = (key[0], key[1] + delta)
                if neighbor in comparable_keys:
                    pilot_keys.add(neighbor)

    def compare_keys(keys: Sequence[tuple[str, int]]) -> tuple[dict[str, Counter[str]], int]:
        local_counts = {name: Counter() for name in ENDPOINT_CONVENTIONS}
        local_bytes = 0
        by_subject_block: dict[tuple[str, int], list[tuple[str, int]]] = defaultdict(list)
        for key in keys:
            by_subject_block[(key[0], rows_by_key[key]["block"])].append(key)
        for (subject, block), block_keys in sorted(by_subject_block.items()):
            with h5py.File(summary_path_by_subject[subject], "r") as summary_file, h5py.File(eeg_path_by_key[(subject, block)], "r") as eeg_file:
                references = summary_file["sentenceData/rawData"]
                data = eeg_file["EEG/data"]
                for key in sorted(block_keys, key=lambda value: value[1]):
                    row = rows_by_key[key]
                    occurrence = event_by_row[key]
                    present, target = _reference_at(summary_file, references, row["slot"] - 1)
                    if not present or target is None:
                        for convention in ENDPOINT_CONVENTIONS:
                            local_counts[convention]["SHAPE_MISMATCH"] += 1
                        continue
                    summary_value = _read_oriented_summary(target)
                    local_bytes += int(summary_value.nbytes)
                    detail: dict[str, dict[str, Any]] = {}
                    for convention in ENDPOINT_CONVENTIONS:
                        start, end = _window_bounds(occurrence["_onset_sample"], occurrence["_finish_sample"], convention)
                        segment = _read_oriented_window(data, start, end)
                        local_bytes += int(segment.nbytes)
                        verdict = compare_segment_arrays(segment, summary_value)
                        detail[convention] = {**verdict, "segment_samples": int(segment.shape[0]) if segment.ndim == 2 else None}
                        local_counts[convention][verdict["state"]] += 1
                    comparison_details[key] = detail
        return local_counts, local_bytes

    pilot_counts, pilot_bytes = compare_keys(sorted(pilot_keys))
    pilot_selection = select_global_convention(pilot_counts, len(pilot_keys))
    full_scan_completed = pilot_selection["result"] == "PASS"
    if full_scan_completed:
        comparison_by_convention, bytes_read = compare_keys(comparable_keys)
        bytes_read += pilot_bytes
    else:
        comparison_by_convention, bytes_read = pilot_counts, pilot_bytes
    convention = select_global_convention(comparison_by_convention, len(comparable_keys)) if full_scan_completed else pilot_selection
    selected = convention["selected"]

    selected_counts: Counter[str] = Counter()
    equality_mode_counts: Counter[str] = Counter()
    for key in comparable_keys:
        selected_detail = comparison_details.get(key, {}).get(selected or "", {})
        state = selected_detail.get("state", "EVENT_UNRESOLVED")
        rows_by_key[key]["segment_correspondence_state"] = state
        selected_counts[state] += 1
        if selected_detail.get("dtype_exact"):
            equality_mode_counts["DTYPE_EXACT_AND_EQUAL"] += 1
        if selected_detail.get("canonical_numeric_equal"):
            equality_mode_counts["CANONICAL_NUMERIC_EQUAL"] += 1
    for key in unresolved_keys:
        rows_by_key[key]["segment_correspondence_state"] = "EVENT_UNRESOLVED"
        selected_counts["EVENT_UNRESOLVED"] += 1
    for row in rows:
        if row["eeg_cell_state"] != "VALID_FINITE_MULTISAMPLE":
            row["segment_correspondence_state"] = "NOT_APPLICABLE_EXCLUDED_CELL"
        occurrence = event_by_row.get((row["subject"], row["slot"]))
        event_valid = bool(occurrence and occurrence["event_pair_state"] == "VALID")
        finalize_row_admission(row, event_valid=event_valid, segment_state=row["segment_correspondence_state"])

    valid_count = sum(row["final_admission_candidate"] for row in rows)
    excluded_count = len(rows) - valid_count
    ledger_consistent = (
        valid_count + excluded_count == len(rows)
        and all(row["final_exclusion_reason"] for row in rows if not row["final_admission_candidate"])
        and all(not row["final_exclusion_reason"] for row in rows if row["final_admission_candidate"])
    )
    block_complete = sequence["result"] == "PASS" and all(row["block"] is not None and row["material_line"] is not None and row["occurrence_id"] for row in rows)
    subject_partition_complete = all(
        by_subject_event_counts[subject]["ORDINARY_SENTENCE"] == 303
        and by_subject_event_counts[subject]["CONTROL_SENTENCE"] == 46
        for subject in sorted(by_subject)
    )
    control_response_valid = all(
        occurrence["control_response_present"] is True
        for occurrence in event_occurrences if occurrence["sentence_class"] == "CONTROL_SENTENCE"
    ) and not any(
        anomaly["reason"] in {"MISSING_CONTROL_RESPONSE", "EXTRA_OR_MISPLACED_CONTROL_RESPONSE"}
        for item in eeg_files for anomaly in item["events"].get("sanitized_anomalies", [])
    )
    event_count_exact = (
        len(event_occurrences) == 6282
        and all(sum(by_subject_event_counts[subject].values()) == 349 for subject in by_subject)
        and all(sum(by_block_event_counts[block].values()) == EXPECTED_POST_PRACTICE_COUNTS[block] * 18 for block in range(1, 8))
    )
    event_alignment_exact = event_count_exact and len(event_by_row) == 6282 and all(
        occurrence["event_pair_state"] == "VALID" for occurrence in event_occurrences
    )
    correspondence_complete = (
        convention["result"] == "PASS"
        and full_scan_completed
        and selected_counts["EXACT_MATCH"] == len(comparable_keys)
    )
    source_audit = derive_source_audit(
        source_cache, source_validation, local_summary=summary_meta,
        local_eeg=eeg_meta, correspondence_complete=correspondence_complete,
    )
    event_semantics = source_validation["valid"] and event_structure and event_alignment_exact and control_response_valid
    subpredicates = [
        _predicate("identity_and_slot_complete", len(rows) == 6282 and len(summaries) == 18 and all(item["slot_count"] == 349 for item in summaries), "counts + summary_schema", "18 subjects x 349 slots"),
        _predicate("material_sequence_exact", sequence["result"] == "PASS" and sequence["ordered_exact_match_count"] == 6282, "material_contract.sequence", f"{sequence['ordered_exact_match_count']}/6282 ordered hashes"),
        _predicate("block_line_occurrence_complete", block_complete, "stimulus_manifest_v2", "block/material_line/occurrence_id non-null after exact sequence only"),
        _predicate("summary_expected_fields_complete", not summary_meta["missing_fields"], "summary_schema", f"missing={summary_meta['missing_fields']}"),
        _predicate("all_eeg_cells_classified", set(state_counts).issubset(CELL_STATES) and sum(state_counts.values()) == 6282, "eeg_cell_ledger.overall", "mutually exclusive seven-state contract"),
        _predicate("missing_exclusion_ledger_consistent", ledger_consistent, "eeg_cell_ledger", f"final_valid={valid_count}; excluded={excluded_count}"),
        _predicate("channel_contract_consistent", len(channel_hashes) == 1 and all(item["channel_count"] == 105 for item in eeg_files), "physical_schema.channel_contract_hashes", f"contracts={len(channel_hashes)}"),
        _predicate("coordinate_contract_complete", len(coordinate_hashes) == 1 and all(item["coordinates_complete"] for item in eeg_files), "physical_schema.coordinate_contract_hashes", f"contracts={len(coordinate_hashes)}"),
        _predicate("sampling_contract_consistent", {item["sampling_hz"] for item in eeg_files} == {500}, "physical_schema.sampling_hz_values", "all 126 blocks at 500 Hz"),
        _predicate("acquisition_reference_bound", {item["acquisition_reference"] for item in eeg_files} == {"Cz"}, "physical_schema.acquisition_reference_values", "local automagic metadata"),
        _predicate("processed_reference_bound", {item["processed_reference"] for item in eeg_files} == {"common-average"}, "physical_schema.processed_reference_values", "local EEG/ref and author processing context"),
        _predicate("event_structure_valid", event_structure, "event_contract.files", "finite monotone bounded latency, nonnegative duration, valid urevent"),
        _predicate("event_semantics_bound", event_semantics, "release_source_evidence + event_occurrence_manifest", "source mapping plus complete physical occurrence contract"),
        _predicate("summary_layer_bound", source_audit["summary_rawData_layer_status"].startswith("BOUND"), "segment_correspondence", source_audit["summary_rawData_layer_status"]),
        _predicate("summary_reference_bound", source_audit["summary_rawData_reference_status"].startswith("BOUND"), "segment_correspondence", source_audit["summary_rawData_reference_status"]),
        _predicate("preprocessed_unit_bound", source_audit["preprocessed_EEG_data_unit_status"] == "BOUND", "unit_source_audit", source_audit["preprocessed_EEG_data_unit_status"]),
        _predicate("summary_unit_bound", source_audit["summary_rawData_unit_status"] == "BOUND", "unit_source_audit", source_audit["summary_rawData_unit_status"]),
        _predicate("admissible_cell_policy_frozen", ledger_consistent, "final row predicate", "content + valid cell + valid occurrence + exact segment"),
        _predicate("ordinary_control_event_partition_complete", subject_partition_complete, "event_occurrence_manifest", "303 ordinary + 46 control per subject"),
        _predicate("control_response_contract_valid", control_response_valid, "event_occurrence_manifest", "one response 15 after every control finish and before next onset"),
        _predicate("event_occurrence_count_exact", event_count_exact, "event_occurrence_manifest", f"occurrences={len(event_occurrences)}"),
        _predicate("event_to_material_slot_alignment_exact", event_alignment_exact, "event_occurrence_manifest + material_contract", "349 ordered event occurrences aligned to 349 material slots per subject"),
        _predicate("segment_convention_global_unique", convention["result"] == "PASS", "segment_correspondence", f"selected={selected}"),
        _predicate("segment_correspondence_complete", correspondence_complete, "segment_correspondence", f"counts={dict(sorted(selected_counts.items()))}"),
        _predicate("source_evidence_cache_valid", source_validation["valid"], "release_source_evidence", f"failures={source_validation['failures']}"),
    ]
    condition3, failed_subpredicates = condition3_from_subpredicates(subpredicates)
    conditions = [
        {"id": 1, "result": "PASS", "evidence": ["run 005 authorized local path"]},
        {"id": 2, "result": "PASS", "evidence": ["artifacts/admission/zuco2_osf_license.yaml"]},
        {"id": 3, "result": condition3, "evidence": ["condition_3_subpredicates"], "detail": "failed=" + ",".join(failed_subpredicates) if failed_subpredicates else "all subpredicates PASS"},
        {"id": 4, "result": "PASS", "evidence": ["HDF5 summaries", "two official readers", "run 005"]},
        {"id": 5, "result": hash_provenance["result"], "evidence": ["run 005 27/27 manifest reused without rehash"]},
        {"id": 6, "result": "PASS", "evidence": ["bounded auditor path and safety declarations"]},
    ]

    drift = []
    if len(rows) != 6282: drift.append(f"rows={len(rows)}")
    for key, expected in EXPECTED_STATE_COUNTS.items():
        if state_counts[key] != expected: drift.append(f"state:{key}={state_counts[key]} expected={expected}")
    if placeholder_subject != EXPECTED_PLACEHOLDER_BY_SUBJECT: drift.append(f"placeholder_by_subject={placeholder_subject}")
    if placeholder_block != EXPECTED_PLACEHOLDER_BY_BLOCK: drift.append(f"placeholder_by_block={placeholder_block}")
    if material["total_rows"] != 370 or material["practice_rows_excluded"] != 21 or material["post_practice_rows"] != 349: drift.append("material_counts")
    if material["per_block_post_practice_rows"] != EXPECTED_POST_PRACTICE_COUNTS: drift.append(f"post_practice={material['per_block_post_practice_rows']}")
    if sequence["ordered_exact_match_count"] != 6282: drift.append(f"ordered_matches={sequence['ordered_exact_match_count']}")
    if prior_null != 180: drift.append(f"prior_block_null_rows={prior_null}")
    if enforce_frozen_expectations and drift:
        raise ValueError("FROZEN_EXPECTATION_DRIFT: " + "; ".join(drift))

    event_type_counts: Counter[str] = Counter()
    event_unknown_counts: Counter[str] = Counter()
    for item in eeg_files:
        event_type_counts.update(item["events"].get("type_counts", {}))
        for code in item["events"].get("unmapped_trigger_codes", []):
            event_unknown_counts[code] += item["events"]["type_counts"].get(code, 0)
    ytl_paths = {
        "task1 - NR/Preprocessed/YTL/gip_YTL_NR3_EEG.mat",
        "task1 - NR/Preprocessed/YTL/oip_YTL_NR6_EEG.mat",
    }
    ytl_verdicts = []
    for item in eeg_files:
        if item["path"] in ytl_paths:
            resolved = item["events"]["event_semantics_bound"]
            ytl_verdicts.append({
                "path": item["path"],
                "verdict": "OLD_PROJECTION_FALSE_ANOMALY" if resolved else "PHYSICAL_ANOMALY_RETAINED",
                "sanitized_anomalies": item["events"].get("sanitized_anomalies", []),
            })
    correspondence = {
        "schema_version": 1,
        "endpoint_convention_grid": list(ENDPOINT_CONVENTIONS),
        "pilot": {"rows": len(pilot_keys), "bytes_read": pilot_bytes, "result": pilot_selection["result"], "selected": pilot_selection["selected"]},
        "full_scan": {"completed": full_scan_completed, "comparable_rows": len(comparable_keys), "bytes_read_total_including_pilot": bytes_read},
        "segment_convention_global_unique": convention,
        "counts": dict(sorted(selected_counts.items())),
        "equality_mode_counts": dict(sorted(equality_mode_counts.items())),
        "counts_by_subject": {
            subject: dict(sorted(Counter(row["segment_correspondence_state"] for row in rows if row["subject"] == subject and row["eeg_cell_state"] == "VALID_FINITE_MULTISAMPLE").items()))
            for subject in sorted(by_subject)
        },
        "counts_by_block": {
            block: dict(sorted(Counter(row["segment_correspondence_state"] for row in rows if row["block"] == block and row["eeg_cell_state"] == "VALID_FINITE_MULTISAMPLE").items()))
            for block in range(1, 8)
        },
        "comparison_policy": {
            "matlab_logical_orientation": {"preprocessed_EEG_data": "channels_by_samples", "summary_rawData": "samples_by_channels"},
            "hdf5_oriented_comparison": "samples_by_channels; transpose_only_when_105_is_first_axis",
            "exact_only": True, "tolerance": None, "scaling": False,
            "rereference": False, "waveform_hashes_emitted": False,
        },
    }
    manifest = {
        "schema_version": 3, "audit_mode": "TARGETED_NR_OUTCOME_BLIND_EVENT_SEGMENT_CORRESPONDENCE",
        "supersedes_active_conclusion_from": "artifacts/admission/zuco2_nr_targeted_manifest_v2.yaml",
        "retains_runs_005_006_and_schema_v1_v2_as_immutable_history": True,
        "dataset": "ZuCo 2.0", "task": "NR",
        "authorized_dataset_root_recorded": "/home/song/projects/trust_align/01_data_protocol/datasets/zuco_2.0",
        "counts": {"subjects": 18, "sessions": 1, "summary_files": 18, "slots_per_subject": 349, "rows": len(rows), "preprocessed_eeg_blocks": 126, "material_rows": material["total_rows"], "practice_rows_excluded": material["practice_rows_excluded"], "post_practice_rows": material["post_practice_rows"]},
        "frozen_expectation_assertions": {"result": "PASS" if not drift else "FAIL", "drift": drift, "prior_block_null_rows": prior_null, "repaired_block_null_rows": sum(row["block"] is None for row in rows)},
        "hash_provenance": hash_provenance,
        "material_contract": {key: value for key, value in material.items() if key != "ordered_rows"} | {"sequence": sequence, "cross_block_duplicate_groups": [item for item in duplicates if item["cross_block"]]},
        "summary_schema": summaries,
        "eeg_cell_ledger": {"overall": dict(sorted(state_counts.items())), "by_subject": by_subject, "by_block": by_block, "cell_valid_count": cell_valid_count, "final_valid_count": valid_count, "final_excluded_count": excluded_count, "final_valid_plus_excluded": valid_count + excluded_count, "valid_sample_length_quantiles": _quantiles(valid_lengths)},
        "physical_schema": {
            "channel_contract_hashes": channel_hashes, "coordinate_contract_hashes": coordinate_hashes,
            "sampling_hz_values": sorted({item["sampling_hz"] for item in eeg_files}),
            "acquisition_reference_values": sorted({item["acquisition_reference"] for item in eeg_files}),
            "processed_reference_values": sorted({item["processed_reference"] for item in eeg_files}),
            "unit_values": unit_values, "unit_candidate_paths": eeg_meta["unit_candidate_paths"],
            "files_with_incomplete_coordinates": [item["path"] for item in eeg_files if not item["coordinates_complete"]],
            "files_with_expected_excluded_labels_present": [item["path"] for item in eeg_files if item["expected_excluded_labels_present"]],
        },
        "event_contract": {
            "event_structure_valid": event_structure, "event_semantics_bound": event_semantics,
            "semantic_mapping_evidence": "artifacts/admission/zuco2_nr_release_source_evidence.yaml:osf_wiki_data_format", "type_counts": dict(sorted(event_type_counts.items())),
            "unmapped_trigger_counts": dict(sorted(event_unknown_counts.items())),
            "files_with_structure_anomaly": [item["path"] for item in eeg_files if not item["events"]["event_structure_valid"]],
            "files_with_semantic_anomaly": [item["path"] for item in eeg_files if not item["events"]["event_semantics_bound"]],
            "ordinary_control_by_subject": {subject: dict(sorted(counts.items())) for subject, counts in sorted(by_subject_event_counts.items())},
            "ytl_anomaly_verdicts": ytl_verdicts,
            "files": [{"path": item["path"], "subject": item["subject"], "block": item["block"], **item["events"]} for item in eeg_files],
        },
        "segment_correspondence": correspondence,
        "source_evidence_contract": source_validation,
        "unit_layer_contract": {key: source_audit[key] for key in ("preprocessed_EEG_data_reference_status", "preprocessed_EEG_data_unit_status", "summary_rawData_layer_status", "summary_rawData_reference_status", "summary_rawData_unit_status")},
        "condition_3_subpredicates": subpredicates,
        "admission_conditions": conditions,
        "admission_result": "PASS" if all(item["result"] == "PASS" for item in conditions) else "FAIL",
        "data_card_generated": False,
        "audit_boundaries": {"historical_or_test_outcome_read": False, "broad_auditor_run": False, "large_summary_files_rehashed": False, "data_or_weights_downloaded": False, "unsafe_format_deserialized": False, "training_or_gate_run": False, "backbone_selected": False, "eeg_values_emitted": False, "event_latencies_emitted": False, "stimulus_text_emitted": False},
    }
    rows.sort(key=lambda item: (item["subject"], item["slot"]))
    occurrence_rows: list[dict[str, Any]] = []
    for row in rows:
        occurrence = event_by_row.get((row["subject"], row["slot"]))
        occurrence_rows.append({
            "subject": row["subject"], "block": row["block"],
            "block_occurrence_index": occurrence.get("block_occurrence_index") if occurrence else None,
            "global_slot": row["slot"], "material_line": row["material_line"],
            "sentence_class": occurrence.get("sentence_class") if occurrence else None,
            "onset_code": occurrence.get("onset_code") if occurrence else None,
            "finish_code": occurrence.get("finish_code") if occurrence else None,
            "control_response_present": occurrence.get("control_response_present") if occurrence else None,
            "onset_latency_valid": occurrence.get("onset_latency_valid", False) if occurrence else False,
            "finish_latency_valid": occurrence.get("finish_latency_valid", False) if occurrence else False,
            "event_pair_state": occurrence.get("event_pair_state", "UNRESOLVED") if occurrence else "UNRESOLVED",
            "anomaly_reason": ";".join(occurrence.get("anomaly_reasons", [])) if occurrence and occurrence.get("anomaly_reasons") else None,
            "summary_cell_state": row["eeg_cell_state"], "summary_samples": row["raw_samples"],
            "segment_samples": comparison_details.get((row["subject"], row["slot"]), {}).get(selected or "", {}).get("segment_samples"),
            "segment_correspondence_state": row["segment_correspondence_state"],
            "final_admission_candidate": row["final_admission_candidate"],
            "exclusion_reason": row["final_exclusion_reason"],
        })
    return manifest, rows, occurrence_rows, correspondence, source_audit


def _write_jsonl(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def write_outputs(
    manifest: dict[str, Any], rows: list[dict[str, Any]], occurrence_rows: list[dict[str, Any]],
    correspondence: dict[str, Any], manifest_path: Path, stimulus_path: Path,
    occurrence_path: Path, correspondence_path: Path,
) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    correspondence_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8", newline="\n")
    correspondence_path.write_text(yaml.safe_dump(correspondence, sort_keys=False, allow_unicode=True), encoding="utf-8", newline="\n")
    _write_jsonl(stimulus_path, rows)
    _write_jsonl(occurrence_path, occurrence_rows)


def write_conditional_data_card(
    manifest: dict[str, Any], output_yaml: Path, output_report: Path,
) -> bool:
    passed = all(item["result"] == "PASS" for item in manifest["admission_conditions"])
    if not passed:
        if output_yaml.exists() or output_report.exists():
            raise ValueError("STALE_DATA_CARD_PRESENT_WHILE_ACTIVE_ADMISSION_FAILS")
        return False
    ledger = manifest["eeg_cell_ledger"]
    card = {
        "schema_version": 1,
        "dataset": "ZuCo 2.0 NR",
        "source_admission_manifest": "artifacts/admission/zuco2_nr_targeted_manifest_v3.yaml",
        "admission_result": "PASS",
        "subjects": manifest["counts"]["subjects"],
        "occurrences": manifest["counts"]["rows"],
        "admitted_rows": ledger["final_valid_count"],
        "excluded_rows": ledger["final_excluded_count"],
        "cell_policy": "content present AND VALID_FINITE_MULTISAMPLE AND valid event occurrence AND exact segment correspondence",
        "segment_convention": manifest["segment_correspondence"]["segment_convention_global_unique"]["selected"],
        "channel_count": 105,
        "sampling_hz": 500,
        "processed_reference": "common-average",
        "unit": manifest["unit_layer_contract"]["preprocessed_EEG_data_unit_status"],
        "outcome_content_read": False,
    }
    output_yaml.parent.mkdir(parents=True, exist_ok=True)
    output_report.parent.mkdir(parents=True, exist_ok=True)
    output_yaml.write_text(yaml.safe_dump(card, sort_keys=False, allow_unicode=True), encoding="utf-8", newline="\n")
    output_report.write_text(
        "# ZuCo 2.0 NR Data Card\n\n"
        "Admission: **PASS**. This card admits only rows satisfying the frozen content, "
        "finite multisample EEG, event-occurrence, and exact segment-correspondence predicates.\n\n"
        f"- Admitted rows: {card['admitted_rows']}\n"
        f"- Excluded rows: {card['excluded_rows']}\n"
        f"- Global endpoint convention: `{card['segment_convention']}`\n"
        "- No held-out or test outcome was read.\n",
        encoding="utf-8", newline="\n",
    )
    manifest["data_card_generated"] = True
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--osf-metadata-cache", required=True, type=Path)
    parser.add_argument("--output-manifest", required=True, type=Path)
    parser.add_argument("--output-stimulus-manifest", required=True, type=Path)
    parser.add_argument("--release-source-evidence", required=True, type=Path)
    parser.add_argument("--output-event-occurrence-manifest", required=True, type=Path)
    parser.add_argument("--output-segment-correspondence", required=True, type=Path)
    parser.add_argument("--output-data-card", required=True, type=Path)
    parser.add_argument("--output-data-card-report", required=True, type=Path)
    args = parser.parse_args()
    manifest, rows, occurrence_rows, correspondence, _source_audit = audit(
        args.dataset_root, args.osf_metadata_cache, args.release_source_evidence,
    )
    generated = write_conditional_data_card(manifest, args.output_data_card, args.output_data_card_report)
    manifest["data_card_generated"] = generated
    write_outputs(
        manifest, rows, occurrence_rows, correspondence,
        args.output_manifest, args.output_stimulus_manifest,
        args.output_event_occurrence_manifest, args.output_segment_correspondence,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
