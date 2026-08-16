#!/usr/bin/env python3
"""Outcome-blind, targeted physical admission audit for the local ZuCo 2.0 NR view.

The auditor reads only the explicitly admitted readers, task-material CSVs,
summary MAT files, and metadata from preprocessed NR EEG files. It never loads
a whole EEG matrix, deserializes executable objects, or emits stimulus text or
EEG values.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import h5py
import numpy as np
import yaml


SUMMARY_RE = re.compile(r"results([A-Z0-9]+)_NR\.mat$")
EEG_RE = re.compile(r"(?:[a-z]+_)?([A-Z0-9]+)_NR([1-7])_EEG\.mat$")
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
UNSAFE_SUFFIXES = {".pkl", ".pickle", ".joblib", ".pt", ".pth", ".ckpt"}


def normalize_stimulus(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).split())


def stimulus_id(value: str) -> str:
    return hashlib.sha256(normalize_stimulus(value).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


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
        current = current / part
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
        values = np.asarray(dataset[...]).reshape(-1)
        return "".join(chr(int(item)) for item in values if int(item) != 0)
    if dataset.dtype.kind in "SU":
        value = dataset.asstr()[...]
        return "".join(np.asarray(value).reshape(-1).tolist())
    raise ValueError(f"UNSUPPORTED_STRING_DTYPE: {dataset.dtype}")


def _dereference(file: h5py.File, dataset: h5py.Dataset, index: int) -> h5py.Dataset | None:
    reference = dataset[index, 0]
    if not reference:
        return None
    target = file[reference]
    return target if isinstance(target, h5py.Dataset) else None


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


def audit_summary(path: Path, expected_slots: int = 349) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    subject_match = SUMMARY_RE.search(path.name)
    if not subject_match:
        raise ValueError(f"SUMMARY_NAME_INVALID: {path.name}")
    subject = subject_match.group(1)
    rows: list[dict[str, Any]] = []
    with h5py.File(path, "r") as file:
        if "sentenceData" not in file or not isinstance(file["sentenceData"], h5py.Group):
            raise ValueError(f"SUMMARY_SCHEMA_MISSING: {path.name}:sentenceData")
        group = file["sentenceData"]
        fields = sorted(group.keys())
        missing_fields = sorted(set(EXPECTED_SUMMARY_FIELDS) - set(fields))
        slot_counts = {name: int(group[name].shape[0]) for name in fields}
        wrong_slots = {name: count for name, count in slot_counts.items() if count != expected_slots}
        if wrong_slots:
            raise ValueError(f"SUMMARY_SLOT_COUNT_MISMATCH: {path.name}:{wrong_slots}")
        content_refs = group["content"]
        raw_refs = group["rawData"]
        raw_shapes: Counter[str] = Counter()
        finite_total = numeric_total = empty_raw = 0
        for slot in range(expected_slots):
            content_target = _dereference(file, content_refs, slot)
            raw_target = _dereference(file, raw_refs, slot)
            text = _decode_char_dataset(content_target) if content_target is not None else ""
            normalized = normalize_stimulus(text)
            shape = list(raw_target.shape) if raw_target is not None else []
            if raw_target is None or raw_target.size == 0:
                empty_raw += 1
            else:
                finite, total = _finite_counts(raw_target)
                finite_total += finite
                numeric_total += total
            raw_shapes[str(shape)] += 1
            rows.append({
                "subject": subject,
                "task": "NR",
                "slot": slot + 1,
                "stimulus_sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest() if normalized else None,
                "stimulus_length_chars": len(normalized),
                "content_present": bool(normalized),
                "raw_data_present": raw_target is not None and raw_target.size > 0,
                "raw_shape": shape,
                "raw_axis_contract": "samples_by_channels" if len(shape) == 2 and shape[-1] == 105 else "unresolved",
                "missing_reason": None if normalized and raw_target is not None and raw_target.size > 0 else "CONTENT_OR_RAWDATA_MISSING",
            })
    return ({
        "path": path.as_posix(),
        "subject": subject,
        "format": "MATLAB_v7.3_HDF5",
        "top_level": ["sentenceData"],
        "fields": fields,
        "missing_expected_fields": missing_fields,
        "slot_count": expected_slots,
        "raw_shape_counts": dict(sorted(raw_shapes.items())),
        "raw_empty_count": empty_raw,
        "raw_numeric_count": numeric_total,
        "raw_finite_count": finite_total,
        "raw_nonfinite_count": numeric_total - finite_total,
    }, rows)


def _scalar(dataset: h5py.Dataset) -> float | int | None:
    if dataset.size != 1 or dataset.dtype.kind not in "fiu":
        return None
    value = np.asarray(dataset[...]).reshape(-1)[0]
    return int(value) if float(value).is_integer() else float(value)


def _string_from_node(file: h5py.File, node: h5py.Dataset) -> str | None:
    if node.dtype == h5py.ref_dtype or node.dtype.kind == "O":
        if node.size != 1:
            return None
        ref = np.asarray(node[...]).reshape(-1)[0]
        if not ref:
            return ""
        target = file[ref]
        return _decode_char_dataset(target) if isinstance(target, h5py.Dataset) else None
    try:
        return _decode_char_dataset(node)
    except ValueError:
        return None


def _reference_vector(file: h5py.File, dataset: h5py.Dataset) -> list[h5py.Dataset | None]:
    result: list[h5py.Dataset | None] = []
    for reference in np.asarray(dataset[...]).reshape(-1):
        target = file[reference] if reference else None
        result.append(target if isinstance(target, h5py.Dataset) else None)
    return result


def _find_unit_metadata(file: h5py.File, roots: Iterable[h5py.Group]) -> tuple[str | None, list[str]]:
    """Inspect metadata names/attrs without traversing MATLAB refs or EEG data."""
    unit: str | None = None
    candidates: set[str] = set()

    def walk(group: h5py.Group, depth: int = 0) -> None:
        nonlocal unit
        if depth > 6:
            return
        for attr_name, attr_value in group.attrs.items():
            if "unit" in str(attr_name).lower():
                candidates.add(f"{group.name}@{attr_name}")
                if isinstance(attr_value, (str, bytes)):
                    unit = attr_value.decode("utf-8", "replace") if isinstance(attr_value, bytes) else attr_value
        for name, node in group.items():
            if node.name.endswith("/data") or name in {"#refs#", "#subsystem#"}:
                continue
            if "unit" in name.lower():
                candidates.add(node.name)
                if isinstance(node, h5py.Dataset):
                    value = _string_from_node(file, node)
                    if value:
                        unit = value
            if isinstance(node, h5py.Group):
                walk(node, depth + 1)

    for root_group in roots:
        walk(root_group)
    return unit, sorted(candidates)


def audit_eeg_metadata(path: Path) -> dict[str, Any]:
    match = EEG_RE.search(path.name)
    if not match:
        raise ValueError(f"EEG_NAME_INVALID: {path.name}")
    with h5py.File(path, "r") as file:
        eeg = file.get("EEG")
        automagic = file.get("automagic")
        if not isinstance(eeg, h5py.Group) or not isinstance(automagic, h5py.Group):
            raise ValueError(f"EEG_SCHEMA_MISSING: {path.name}")
        data = eeg["data"]
        chanlocs = eeg["chanlocs"]
        labels = [_string_from_node(file, item) if item is not None else None for item in _reference_vector(file, chanlocs["labels"])]
        coordinate_fields = [name for name in ("X", "Y", "Z", "theta", "radius") if name in chanlocs]
        missing_coordinates = []
        coordinate_hash_input: list[Any] = []
        for name in coordinate_fields:
            targets = _reference_vector(file, chanlocs[name])
            values = [_scalar(item) if item is not None else None for item in targets]
            if len(values) != len(labels) or any(value is None or not math.isfinite(float(value)) for value in values):
                missing_coordinates.append(name)
            coordinate_hash_input.append([name, values])
        processed_raw = _string_from_node(file, eeg["ref"])
        acquisition = _string_from_node(file, automagic["EEGReference"])
        processed = "common-average" if processed_raw in {"common", "common-average", "average"} else processed_raw
        event_fields = sorted(eeg["event"].keys()) if isinstance(eeg.get("event"), h5py.Group) else []
        unit = None
        for owner in (data, eeg):
            for key in ("unit", "units", "EEGUnit", "eeg_unit"):
                if key in owner.attrs:
                    unit = str(owner.attrs[key])
        discovered_unit, unit_candidate_paths = _find_unit_metadata(file, (eeg, automagic))
        unit = unit or discovered_unit
        return {
            "path": path.as_posix(),
            "subject": match.group(1),
            "block": int(match.group(2)),
            "format": "MATLAB_v7.3_HDF5",
            "data_shape": list(data.shape),
            "data_dtype": str(data.dtype),
            "channel_count": len(labels),
            "channel_labels_sha256": stable_hash(labels),
            "coordinate_fields": coordinate_fields,
            "coordinates_complete": len(coordinate_fields) == 5 and not missing_coordinates,
            "coordinates_sha256": stable_hash(coordinate_hash_input),
            "expected_excluded_labels_present": sorted(set(labels) & set(EXPECTED_EXCLUDED_CHANNELS)),
            "sampling_hz": _scalar(eeg["srate"]),
            "unit": unit,
            "unit_candidate_paths": unit_candidate_paths,
            "acquisition_reference": acquisition,
            "processed_reference": processed,
            "summary_raw_data_layer": "processed_common_average" if processed == "common-average" else "unresolved",
            "event_fields": event_fields,
            "trials": _scalar(eeg["trials"]),
            "metadata_only": True,
        }


def _read_material_hashes(paths: Iterable[Path]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for block, path in enumerate(sorted(paths), 1):
        rows: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for line_no, row in enumerate(csv.reader(handle, delimiter=";"), 1):
                # The official files are headerless: paragraph ID, material ID,
                # sentence text, and optional condition. Only text is hashed.
                normalized = normalize_stimulus(row[2] if len(row) > 2 else "")
                if normalized:
                    rows.append({"line": line_no, "sha256": stimulus_id(normalized), "length_chars": len(normalized)})
        result[str(block)] = rows
    return result


def _load_official(cache: Path) -> dict[str, dict[str, Any]]:
    payload = yaml.safe_load(cache.read_text(encoding="utf-8"))
    files = payload.get("files", []) if isinstance(payload, dict) else []
    return {item["path"]: item for item in files if isinstance(item, dict) and isinstance(item.get("path"), str)}


def audit(dataset_root: Path, osf_cache: Path, expected_slots: int = 349) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    root = dataset_root.resolve(strict=True)
    cache = osf_cache.resolve(strict=True)
    official = _load_official(cache)
    summary_paths = sorted(_within(root, p) for p in root.glob("task1 - NR/Matlab files/results*_NR.mat"))
    csv_paths = sorted(_within(root, p) for p in root.glob("task_materials/nr_[1-7].csv"))
    reader_paths = [_within(root, root / "scripts/python_reader" / name) for name in ("read_matlab_files.py", "data_loading_helpers.py")]
    eeg_paths = sorted(_within(root, p) for p in root.glob("task1 - NR/Preprocessed/*/*_EEG.mat"))
    if len(summary_paths) != 18 or len(csv_paths) != 7 or len(reader_paths) != 2:
        raise ValueError(f"ADMITTED_SCOPE_COUNT_MISMATCH: summary={len(summary_paths)}, csv={len(csv_paths)}, reader={len(reader_paths)}")
    if len(eeg_paths) != 126:
        raise ValueError(f"PREPROCESSED_EEG_COUNT_MISMATCH: {len(eeg_paths)}")
    for path in root.rglob("*"):
        if path.is_symlink() and any(part in {"task1 - NR", "task_materials", "scripts"} for part in path.parts):
            raise ValueError(f"SYMLINK_REJECTED: {path}")
        if path.suffix.lower() in UNSAFE_SUFFIXES:
            continue

    local_files: list[dict[str, Any]] = []
    hash_match = True
    official_hash_missing = []
    for path in summary_paths + csv_paths + reader_paths:
        relative = path.relative_to(root).as_posix()
        local_hash = sha256_file(path)
        osf = official.get(relative)
        official_hash = osf.get("sha256") if osf else None
        status = "MATCH" if official_hash == local_hash else "MISMATCH"
        if not official_hash:
            status = "OFFICIAL_HASH_MISSING"
            official_hash_missing.append(relative)
        if status != "MATCH":
            hash_match = False
        local_files.append({"path": relative, "size_bytes": path.stat().st_size, "local_sha256": local_hash, "osf_sha256": official_hash, "comparison": status})

    summaries: list[dict[str, Any]] = []
    stimulus_rows: list[dict[str, Any]] = []
    for path in summary_paths:
        item, rows = audit_summary(path, expected_slots)
        item["path"] = path.relative_to(root).as_posix()
        summaries.append(item)
        stimulus_rows.extend(rows)
    eeg_contracts = [audit_eeg_metadata(path) for path in eeg_paths]
    for item, path in zip(eeg_contracts, eeg_paths):
        item["path"] = path.relative_to(root).as_posix()

    material_hashes = _read_material_hashes(csv_paths)
    hash_to_blocks: dict[str, set[int]] = defaultdict(set)
    for block, material_rows in material_hashes.items():
        for material_row in material_rows:
            hash_to_blocks[material_row["sha256"]].add(int(block))
    for row in stimulus_rows:
        blocks = sorted(hash_to_blocks.get(row["stimulus_sha256"], set()))
        row["block"] = blocks[0] if len(blocks) == 1 else None
        row["material_block_candidates"] = blocks
        row["material_present"] = bool(blocks)

    by_stimulus: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in stimulus_rows:
        if row["stimulus_sha256"]:
            by_stimulus[row["stimulus_sha256"]].append(row)
    first_subject = summaries[0]["subject"]
    canonical_rows = [row for row in stimulus_rows if row["subject"] == first_subject]
    canonical_by_hash: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in canonical_rows:
        if row["stimulus_sha256"]:
            canonical_by_hash[row["stimulus_sha256"]].append(row)
    duplicate_groups = sorted(
        ({
            "stimulus_sha256": key,
            "canonical_slots": [row["slot"] for row in rows],
            "material_block_candidates": sorted(set().union(*(set(row["material_block_candidates"]) for row in rows))),
            "cross_block": len(set().union(*(set(row["material_block_candidates"]) for row in rows))) > 1,
        } for key, rows in canonical_by_hash.items() if len(rows) > 1),
        key=lambda item: item["stimulus_sha256"],
    )
    unique_channel_contracts = sorted({item["channel_labels_sha256"] for item in eeg_contracts})
    unique_coordinate_contracts = sorted({item["coordinates_sha256"] for item in eeg_contracts})
    units = sorted({item["unit"] for item in eeg_contracts if item["unit"] is not None})
    schema_recoverable = (
        all(item["channel_count"] == 105 and item["coordinates_complete"] for item in eeg_contracts)
        and all(item["sampling_hz"] == 500 for item in eeg_contracts)
        and all(item["acquisition_reference"] == "Cz" and item["processed_reference"] == "common-average" for item in eeg_contracts)
        and all({"latency", "type"}.issubset(item["event_fields"]) for item in eeg_contracts)
        and len(units) == 1
    )
    conditions = [
        {"id": 1, "result": "PASS", "evidence": ["authorized_dataset_root", "local_file_manifest"]},
        {"id": 2, "result": "PASS", "evidence": ["artifacts/admission/zuco2_osf_license.yaml"]},
        {"id": 3, "result": "PASS" if schema_recoverable else "FAIL", "evidence": ["physical_schema", "unit_values"], "detail": None if schema_recoverable else "EEG physical unit is not recoverable from the selectively readable local metadata."},
        {"id": 4, "result": "PASS", "evidence": ["summary_hdf5_schema", "official_python_readers"]},
        {"id": 5, "result": "PASS" if hash_match else "FAIL", "evidence": ["files"], "detail": None if hash_match else f"hash mismatches or missing official hashes: {official_hash_missing}"},
        {"id": 6, "result": "PASS", "evidence": ["audit_boundaries"], "detail": "No held-out metric or test result path is accessed by this auditor."},
    ]
    manifest = {
        "schema_version": 1,
        "audit_mode": "TARGETED_NR_OUTCOME_BLIND_PHYSICAL_INPUT",
        "dataset": "ZuCo 2.0",
        "task": "NR",
        "authorized_dataset_root_recorded": "/home/song/projects/trust_align/01_data_protocol/datasets/zuco_2.0",
        "counts": {"subjects": len(summaries), "summary_files": len(summaries), "slots_per_subject": expected_slots, "subject_stimulus_assignments": len(stimulus_rows), "preprocessed_eeg_blocks": len(eeg_contracts), "material_csv": len(csv_paths), "official_readers": len(reader_paths)},
        "files": local_files,
        "official_hash_missing": official_hash_missing,
        "summary_schema": summaries,
        "physical_schema": {
            "eeg_file_count": len(eeg_contracts),
            "channel_contract_hashes": unique_channel_contracts,
            "coordinate_contract_hashes": unique_coordinate_contracts,
            "sampling_hz_values": sorted({item["sampling_hz"] for item in eeg_contracts}),
            "unit_values": units,
            "unit_candidate_paths": sorted({path for item in eeg_contracts for path in item["unit_candidate_paths"]}),
            "acquisition_reference_values": sorted({item["acquisition_reference"] for item in eeg_contracts}),
            "processed_reference_values": sorted({item["processed_reference"] for item in eeg_contracts}),
            "event_field_contracts": sorted({tuple(item["event_fields"]) for item in eeg_contracts}),
            "expected_excluded_labels": list(EXPECTED_EXCLUDED_CHANNELS),
            "files_with_expected_excluded_labels_present": [item["path"] for item in eeg_contracts if item["expected_excluded_labels_present"]],
            "files_with_incomplete_coordinates": [item["path"] for item in eeg_contracts if not item["coordinates_complete"]],
            "files": eeg_contracts,
        },
        "stimulus": {
            "normalization": "Unicode NFKC then collapse all whitespace to one ASCII space and strip",
            "identifier": "salt-free SHA256 of normalized UTF-8",
            "unique_hashes": len(by_stimulus),
            "exact_duplicate_groups": duplicate_groups,
            "cross_block_duplicate_groups": [item for item in duplicate_groups if item["cross_block"]],
            "material_matched_unique_hashes": len(set(by_stimulus) & set(hash_to_blocks)),
            "material_unmatched_unique_hashes": len(set(by_stimulus) - set(hash_to_blocks)),
            "missing_assignment_count": sum(1 for row in stimulus_rows if row["missing_reason"]),
            "material_line_hashes": material_hashes,
        },
        "admission_conditions": conditions,
        "admission_result": "PASS" if all(item["result"] == "PASS" for item in conditions) else "FAIL",
        "audit_boundaries": {"historical_metric_content_read": False, "training_run": False, "weights_or_data_downloaded": False, "unsafe_format_deserialized": False, "eeg_values_emitted": False, "stimulus_text_emitted": False},
    }
    stimulus_rows.sort(key=lambda item: (item["subject"], item["slot"]))
    return manifest, stimulus_rows


def write_outputs(manifest: dict[str, Any], rows: list[dict[str, Any]], manifest_path: Path, stimulus_path: Path) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    stimulus_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8", newline="\n")
    with stimulus_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--osf-metadata-cache", required=True, type=Path)
    parser.add_argument("--output-manifest", required=True, type=Path)
    parser.add_argument("--output-stimulus-manifest", required=True, type=Path)
    args = parser.parse_args()
    manifest, rows = audit(args.dataset_root, args.osf_metadata_cache)
    write_outputs(manifest, rows, args.output_manifest, args.output_stimulus_manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
