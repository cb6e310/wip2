#!/usr/bin/env python3
"""Validate the frozen A1 frontend on the bounded real-data audit panel."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import platform
import sys
import tempfile
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable

import h5py
import numpy as np

# Keep the reference math attention path on installed ATen kernels. This also
# prevents Torch's optional native DSL route from compiling or writing a cache.
os.environ["TORCH_DISABLE_NATIVE_JIT"] = "1"
import torch
import yaml

try:
    from torch._native import triton_utils as _torch_native_triton
except ImportError:  # pragma: no cover - the frozen Torch build provides it
    _torch_native_triton = None
else:
    _torch_native_triton.deregister_op_overrides()


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from rc_hsg.backbones.native_spectral_a1 import (  # noqa: E402
    CHANNEL_ORDER_HASH,
    PROCESSED_REFERENCE,
    SAMPLING_HZ,
    UNIT_STATUS,
    NativeSpectralA1,
)


BASELINE_COMMIT = "237788090dcb20e533f304f63ae8feb2f545fe0b"
POLICY_ID = "RC_HSG_NATIVE_SPECTRAL_A1_V1"
AUDIT_SEED = 20260824
PRODUCTION_DATASET_ROOT = Path("/home/song/projects/trust_align/01_data_protocol/datasets/zuco_2.0")
EVIDENCE_SCOPE = "BOUNDED_OUTER_TRAIN_REAL_EEG_FRONTEND_SELF_CHECK_NO_OUTCOMES_NO_TRAINING_NOT_FULL_ADMISSION"
FIXED_INPUTS = {
    "spec_v22": ("guide/RC_HSG_Paper_Spec_v2_2_2026-08-24.md", "a5d6d695f21a72dd2e3d8445771b6b3d772f0a42282ad5ce9feaa6e43da01911"),
    "a_policy": ("artifacts/backbone_a_policy.yaml", "034a523119f12f648266d94e0499179882fbe181584d10c1af17a3502a797425"),
    "a_contract": ("artifacts/backbone_a_contract.yaml", "4c9ccddf4d5c208870422c7e5ceee65ee184d812fce662bb885998b0dad65cac"),
    "eligibility": ("artifacts/a_interface_eligibility_v1.jsonl", "8eded8fb2786747e96b8388d4d91315e39db9f8a9eb25ea69056d219e1e8e1ad"),
    "a_code": ("src/rc_hsg/backbones/native_spectral_a1.py", "71ae12d65cc0acc6fd5870434e141ee7d849eb8befa718a84fb99cb86ed533d9"),
    "analysis_view": ("artifacts/admission/zuco2_nr_analysis_view_v1.jsonl", "0751259f9f9455cba72bd7d027ffa1423e790e631ac0f5174c38da65d7cd12ff"),
    "split_regime_i": ("artifacts/split_regimeI.json", "e2c065e5b395053cd655670fede8a2b117f6eb9821af884ca31c6fed3842fbab"),
    "data_card": ("artifacts/data_card.yaml", "d9331bfe34937c264b7b8c667a2b831569c4440120e1d445011aeaf419c30f84"),
    "targeted_manifest_v3": ("artifacts/admission/zuco2_nr_targeted_manifest_v3.yaml", "50806a60937b28ae36207509c44d606af6f6b6b1be2a69c06081672f0931bfaf"),
    "osf_file_metadata": ("artifacts/admission/zuco2_osf_file_metadata.yaml", "85a8c89eeb7a523c06fb7f38aa1c371e042413087e66dcc338c16833bd8bb721"),
    "requirements_lock": ("requirements-trust-align.lock.txt", "72a2a3274ef9516dba95a4f4022cacfba0e02d10445e1618da2a569f59381910"),
}
OUTPUTS = {
    "panel": "artifacts/a1_frontend_audit_panel_v1.jsonl",
    "freeze": "artifacts/a1_frontend_freeze.yaml",
    "report": "reports/a1_frontend_selfcheck.md",
}
PANEL_FIELDS = (
    "subject", "slot", "occurrence_id", "role", "raw_samples", "window_count",
    "selection_reason", "a_interface_status", "action", "source_file",
    "source_field", "source_dataset_read",
)
OUTER_ROLES = {"train_fit", "inner_val"}
EXPECTED_OUTER = {"total": 3541, "eligible": 3497, "short": 44, "windows": 35745}
EXPECTED_PANEL = {
    "ledger_rows": 151,
    "real_rows": 107,
    "short_no_read": 44,
    "windows": 1452,
    "subjects": 18,
    "role_counts": {"train_fit": 90, "inner_val": 61},
    "real_role_counts": {"train_fit": 55, "inner_val": 52},
    "stratum_counts": {"W01_04": 34, "W05_16": 36, "W17_PLUS": 35},
    "minimum_raw_samples": 572,
    "maximum_raw_samples": 18436,
    "maximum_windows": 72,
}
EXPECTED_CUDA = {"rows": 20, "windows": 199}
METADATA = {
    "channel_order_hash": CHANNEL_ORDER_HASH,
    "sampling_hz": SAMPLING_HZ,
    "unit_status": UNIT_STATUS,
    "processed_reference": PROCESSED_REFERENCE,
}


class A1FrontendValidationError(RuntimeError):
    """Fail-closed real-frontend validation error."""


def _fail(code: str, detail: str) -> None:
    raise A1FrontendValidationError(f"{code}: {detail}")


@contextmanager
def _strict_execution_kernels() -> Iterable[None]:
    """Use the same unfused attention path for the CPU/CUDA parity check."""
    old_fastpath = torch.backends.mha.get_fastpath_enabled()
    old_flash = torch.backends.cuda.flash_sdp_enabled()
    old_mem_efficient = torch.backends.cuda.mem_efficient_sdp_enabled()
    old_math = torch.backends.cuda.math_sdp_enabled()
    old_matmul_tf32 = torch.backends.cuda.matmul.allow_tf32
    old_cudnn_tf32 = torch.backends.cudnn.allow_tf32
    torch.backends.mha.set_fastpath_enabled(False)
    torch.backends.cuda.enable_flash_sdp(False)
    torch.backends.cuda.enable_mem_efficient_sdp(False)
    torch.backends.cuda.enable_math_sdp(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    try:
        yield
    finally:
        torch.backends.mha.set_fastpath_enabled(old_fastpath)
        torch.backends.cuda.enable_flash_sdp(old_flash)
        torch.backends.cuda.enable_mem_efficient_sdp(old_mem_efficient)
        torch.backends.cuda.enable_math_sdp(old_math)
        torch.backends.cuda.matmul.allow_tf32 = old_matmul_tf32
        torch.backends.cudnn.allow_tf32 = old_cudnn_tf32


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_symlink_chain(path: Path, label: str) -> None:
    current = path.absolute()
    while True:
        if current.exists() and current.is_symlink():
            _fail("SYMLINK_REJECTED", label)
        if current.parent == current:
            return
        current = current.parent


def _safe_input(root: Path, relative: str, label: str) -> Path:
    root = root.resolve()
    candidate = root / relative
    _reject_symlink_chain(candidate, label)
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        _fail("PATH_OUTSIDE_DATASET_ROOT", label)
    if not resolved.is_file():
        _fail("SOURCE_IDENTITY_MISMATCH", f"missing {label}")
    return resolved


def _safe_output_paths(output_root: Path) -> dict[str, Path]:
    _reject_symlink_chain(output_root, "output_root")
    root = output_root.absolute().resolve()
    paths: dict[str, Path] = {}
    for label, relative in OUTPUTS.items():
        candidate = root / relative
        _reject_symlink_chain(candidate, label)
        parent = candidate.parent.resolve()
        try:
            parent.relative_to(root)
        except ValueError:
            _fail("PATH_OUTSIDE_DATASET_ROOT", label)
        paths[label] = parent / candidate.name
    return paths


def _load_yaml(path: Path, label: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        _fail("INPUT_HASH_MISMATCH", f"{label}:{type(exc).__name__}")
    if not isinstance(value, dict):
        _fail("INPUT_HASH_MISMATCH", f"{label}:schema")
    return value


def _load_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                value = json.loads(line)
                if not isinstance(value, dict):
                    _fail("PANEL_CONTRACT_MISMATCH", f"{label}:{line_number}")
                rows.append(value)
    except A1FrontendValidationError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail("INPUT_HASH_MISMATCH", f"{label}:{type(exc).__name__}")
    return rows


def _verify_inputs(project_root: Path, enforce: bool) -> tuple[dict[str, Path], dict[str, str]]:
    paths = {label: _safe_input(project_root, relative, label) for label, (relative, _) in FIXED_INPUTS.items()}
    hashes = {label: _sha256(path) for label, path in paths.items()}
    if enforce:
        for label, (_, expected) in FIXED_INPUTS.items():
            if hashes[label] != expected:
                _fail("INPUT_HASH_MISMATCH", label)
    return paths, hashes


def _row_key(row: dict[str, Any]) -> tuple[str, int, str]:
    subject, slot, occurrence = row.get("subject"), row.get("slot"), row.get("occurrence_id")
    if not isinstance(subject, str) or not isinstance(slot, int) or not isinstance(occurrence, str):
        _fail("PANEL_CONTRACT_MISMATCH", "invalid row key")
    return subject, slot, occurrence


def _stratum(window_count: int) -> str:
    if 1 <= window_count <= 4:
        return "W01_04"
    if 5 <= window_count <= 16:
        return "W05_16"
    if window_count >= 17:
        return "W17_PLUS"
    _fail("PANEL_CONTRACT_MISMATCH", f"eligible window_count={window_count}")


def select_audit_panel(
    eligibility_rows: list[dict[str, Any]],
    analysis_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Select the frozen outcome-blind real panel plus every outer-train short row."""
    analysis_by_key: dict[tuple[str, int, str], dict[str, Any]] = {}
    for row in analysis_rows:
        key = _row_key(row)
        if key in analysis_by_key:
            _fail("PANEL_CONTRACT_MISMATCH", f"duplicate analysis key {key!r}")
        analysis_by_key[key] = row

    outer: list[tuple[dict[str, Any], dict[str, Any]]] = []
    seen: set[tuple[str, int, str]] = set()
    for row in eligibility_rows:
        key = _row_key(row)
        if key in seen:
            _fail("PANEL_CONTRACT_MISMATCH", f"duplicate eligibility key {key!r}")
        seen.add(key)
        if row.get("role") not in OUTER_ROLES:
            continue
        analysis = analysis_by_key.get(key)
        if analysis is None:
            _fail("PANEL_CONTRACT_MISMATCH", f"missing analysis row {key!r}")
        if analysis.get("raw_samples") != row.get("raw_samples") or analysis.get("raw_channels") != 105:
            _fail("PANEL_CONTRACT_MISMATCH", f"analysis join {key!r}")
        locator = analysis.get("source_locator")
        if (
            not isinstance(locator, dict)
            or locator.get("field") != "rawData"
            or locator.get("slot") != row.get("slot")
            or not isinstance(locator.get("summary_file"), str)
        ):
            _fail("PANEL_CONTRACT_MISMATCH", f"source locator {key!r}")
        outer.append((row, analysis))

    eligible = [(row, analysis) for row, analysis in outer if row.get("a_interface_status") == "ELIGIBLE"]
    short = [(row, analysis) for row, analysis in outer if row.get("a_interface_status") == "A_INTERFACE_SHORT_SEGMENT"]
    if any(row.get("action") != "RUN_FRONTEND" or not isinstance(row.get("window_count"), int) for row, _ in eligible):
        _fail("PANEL_CONTRACT_MISMATCH", "eligible status/action")
    if any(row.get("action") != "FORCED_L0_NO_FRONTEND" or row.get("window_count") != 0 for row, _ in short):
        _fail("PANEL_CONTRACT_MISMATCH", "short status/action")
    if len(eligible) + len(short) != len(outer):
        _fail("PANEL_CONTRACT_MISMATCH", "unknown outer-train status")

    cells: dict[tuple[str, str, str], list[tuple[dict[str, Any], dict[str, Any]]]] = {}
    for row, analysis in eligible:
        cell = (row["subject"], row["role"], _stratum(row["window_count"]))
        cells.setdefault(cell, []).append((row, analysis))
    selected: dict[tuple[str, int, str], tuple[dict[str, Any], dict[str, Any], set[str]]] = {}
    for candidates in cells.values():
        row, analysis = min(candidates, key=lambda item: (item[0]["occurrence_id"], item[0]["slot"]))
        selected[_row_key(row)] = (row, analysis, {"STRATIFIED_CELL"})
    for role in sorted(OUTER_ROLES):
        candidates = [(row, analysis) for row, analysis in eligible if row["role"] == role]
        if not candidates:
            _fail("PANEL_CONTRACT_MISMATCH", f"empty role {role}")
        row, analysis = min(
            candidates,
            key=lambda item: (
                -item[0]["window_count"], -item[0]["raw_samples"],
                item[0]["occurrence_id"], item[0]["subject"], item[0]["slot"],
            ),
        )
        key = _row_key(row)
        if key in selected:
            selected[key][2].add("ROLE_MAX_STRESS")
        else:
            selected[key] = (row, analysis, {"ROLE_MAX_STRESS"})

    output: list[dict[str, Any]] = []
    for row, analysis, reasons in selected.values():
        if reasons == {"STRATIFIED_CELL"}:
            reason = "STRATIFIED_CELL"
        elif reasons == {"ROLE_MAX_STRESS"}:
            reason = "ROLE_MAX_STRESS"
        elif reasons == {"STRATIFIED_CELL", "ROLE_MAX_STRESS"}:
            reason = "STRATIFIED_AND_ROLE_MAX"
        else:  # pragma: no cover - set construction above is closed
            _fail("PANEL_CONTRACT_MISMATCH", "selection reason")
        output.append({
            "subject": row["subject"], "slot": row["slot"], "occurrence_id": row["occurrence_id"],
            "role": row["role"], "raw_samples": row["raw_samples"], "window_count": row["window_count"],
            "selection_reason": reason, "a_interface_status": "ELIGIBLE", "action": "RUN_FRONTEND",
            "source_file": analysis["source_locator"]["summary_file"], "source_field": "rawData",
            "source_dataset_read": True,
        })
    for row, analysis in short:
        output.append({
            "subject": row["subject"], "slot": row["slot"], "occurrence_id": row["occurrence_id"],
            "role": row["role"], "raw_samples": row["raw_samples"], "window_count": 0,
            "selection_reason": "ALL_OUTER_TRAIN_SHORT", "a_interface_status": "A_INTERFACE_SHORT_SEGMENT",
            "action": "FORCED_L0_NO_FRONTEND", "source_file": analysis["source_locator"]["summary_file"],
            "source_field": "rawData", "source_dataset_read": False,
        })
    output.sort(key=lambda row: (row["subject"], row["slot"], row["occurrence_id"]))
    if any(tuple(row) != PANEL_FIELDS for row in output):
        _fail("PANEL_CONTRACT_MISMATCH", "panel field order")
    return output


def _panel_counts(panel: list[dict[str, Any]], outer: list[dict[str, Any]]) -> dict[str, Any]:
    eligible_outer = [row for row in outer if row["a_interface_status"] == "ELIGIBLE"]
    short_outer = [row for row in outer if row["a_interface_status"] == "A_INTERFACE_SHORT_SEGMENT"]
    real = [row for row in panel if row["source_dataset_read"]]
    short = [row for row in panel if not row["source_dataset_read"]]
    strata = Counter(
        _stratum(row["window_count"])
        for row in real
        if row["selection_reason"] in {"STRATIFIED_CELL", "STRATIFIED_AND_ROLE_MAX"}
    )
    return {
        "outer_train": {
            "total": len(outer), "eligible": len(eligible_outer), "short": len(short_outer),
            "windows": sum(row["window_count"] for row in eligible_outer),
        },
        "panel": {
            "ledger_rows": len(panel), "real_rows": len(real), "short_no_read": len(short),
            "windows": sum(row["window_count"] for row in real),
            "subjects": len({row["subject"] for row in real}),
            "role_counts": dict(sorted(Counter(row["role"] for row in panel).items())),
            "real_role_counts": dict(sorted(Counter(row["role"] for row in real).items())),
            "stratum_counts": {key: strata[key] for key in ("W01_04", "W05_16", "W17_PLUS")},
            "minimum_raw_samples": min((row["raw_samples"] for row in real), default=0),
            "maximum_raw_samples": max((row["raw_samples"] for row in real), default=0),
            "maximum_windows": max((row["window_count"] for row in real), default=0),
        },
    }


def _assert_frozen_panel(counts: dict[str, Any], panel: list[dict[str, Any]]) -> None:
    if counts["outer_train"] != EXPECTED_OUTER or counts["panel"] != EXPECTED_PANEL:
        _fail("PANEL_CONTRACT_MISMATCH", repr(counts))
    real = [row for row in panel if row["source_dataset_read"]]
    if Counter(row["selection_reason"] for row in real) != Counter({"STRATIFIED_CELL": 105, "ROLE_MAX_STRESS": 2}):
        _fail("PANEL_CONTRACT_MISMATCH", "baseline stress rows must be distinct")


def _dataset_files(
    dataset_root: Path,
    targeted: dict[str, Any],
    osf_metadata: dict[str, Any],
    *,
    enforce: bool,
) -> tuple[Path, dict[str, Path], list[dict[str, Any]]]:
    _reject_symlink_chain(dataset_root, "dataset_root")
    try:
        root = dataset_root.resolve(strict=True)
    except OSError as exc:
        _fail("SOURCE_IDENTITY_MISMATCH", f"dataset_root:{type(exc).__name__}")
    if not root.is_dir():
        _fail("SOURCE_IDENTITY_MISMATCH", "dataset root is not a directory")
    recorded = targeted.get("authorized_dataset_root_recorded")
    if not isinstance(recorded, str) or Path(recorded).resolve() != root:
        _fail("SOURCE_IDENTITY_MISMATCH", "authorized dataset root")
    if enforce and root != PRODUCTION_DATASET_ROOT:
        _fail("SOURCE_IDENTITY_MISMATCH", "production dataset root")

    summary = targeted.get("summary_schema")
    if not isinstance(summary, list):
        _fail("SOURCE_IDENTITY_MISMATCH", "summary schema")
    subjects: dict[str, str] = {}
    for item in summary:
        if not isinstance(item, dict) or not isinstance(item.get("subject"), str) or not isinstance(item.get("path"), str):
            _fail("SOURCE_IDENTITY_MISMATCH", "summary schema item")
        if item["subject"] in subjects:
            _fail("SOURCE_IDENTITY_MISMATCH", "duplicate summary subject")
        subjects[item["subject"]] = item["path"]
    osf_files = {
        item.get("path"): item
        for item in osf_metadata.get("files", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    expected_paths = set(subjects.values())
    if enforce and len(expected_paths) != 18:
        _fail("SOURCE_IDENTITY_MISMATCH", f"summary files={len(expected_paths)}")
    if any(path not in osf_files for path in expected_paths):
        _fail("SOURCE_IDENTITY_MISMATCH", "OSF summary metadata")
    summary_dir = root / "task1 - NR" / "Matlab files"
    actual_paths = {
        path.relative_to(root).as_posix()
        for path in summary_dir.glob("results*_NR.mat")
        if path.is_file()
    }
    if actual_paths != expected_paths:
        _fail("SOURCE_IDENTITY_MISMATCH", "missing or unexpected summary file")

    paths: dict[str, Path] = {}
    identities: list[dict[str, Any]] = []
    for subject, relative in sorted(subjects.items()):
        relative_path = Path(relative)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            _fail("PATH_OUTSIDE_DATASET_ROOT", subject)
        candidate = root / relative_path
        _reject_symlink_chain(candidate, subject)
        resolved = candidate.resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            _fail("PATH_OUTSIDE_DATASET_ROOT", subject)
        metadata = osf_files[relative]
        if not resolved.is_file() or resolved.stat().st_size != metadata.get("size_bytes"):
            _fail("SOURCE_IDENTITY_MISMATCH", subject)
        paths[relative] = resolved
        identities.append({
            "subject": subject,
            "relative_path": relative,
            "size_bytes": metadata["size_bytes"],
            "sha256_status": "REUSED_VERIFIED_RUN005_NO_REHASH",
        })
    return root, paths, identities


def _read_raw(
    row: dict[str, Any],
    dataset_root: Path,
    allowed_files: dict[str, Path],
    allowed_keys: set[tuple[str, int, str]],
) -> tuple[torch.Tensor, str]:
    key = _row_key(row)
    if key not in allowed_keys or not row.get("source_dataset_read") or row.get("role") not in OUTER_ROLES:
        _fail("FORBIDDEN_CELL_DEREFERENCE", repr(key))
    relative = row.get("source_file")
    path = allowed_files.get(relative)
    if path is None:
        _fail("PATH_OUTSIDE_DATASET_ROOT", repr(relative))
    try:
        path.resolve().relative_to(dataset_root)
    except ValueError:
        _fail("PATH_OUTSIDE_DATASET_ROOT", repr(relative))

    try:
        with h5py.File(path, "r") as handle:
            sentence_link = handle.get("sentenceData", getlink=True)
            if not isinstance(sentence_link, h5py.HardLink):
                _fail("HDF5_SCHEMA_MISMATCH", "sentenceData link")
            sentence = handle["sentenceData"]
            if not isinstance(sentence, h5py.Group):
                _fail("HDF5_SCHEMA_MISMATCH", "sentenceData group")
            raw_link = sentence.get("rawData", getlink=True)
            if not isinstance(raw_link, h5py.HardLink):
                _fail("HDF5_SCHEMA_MISMATCH", "rawData link")
            references = sentence["rawData"]
            if (
                not isinstance(references, h5py.Dataset)
                or h5py.check_dtype(ref=references.dtype) is None
                or references.ndim != 2
                or references.shape[1] != 1
                or row["slot"] < 1
                or row["slot"] > references.shape[0]
            ):
                _fail("HDF5_SCHEMA_MISMATCH", "rawData reference table")
            reference = references[row["slot"] - 1, 0]
            if not reference:
                _fail("HDF5_SCHEMA_MISMATCH", "null selected reference")
            target = handle[reference]
            if not isinstance(target, h5py.Dataset):
                _fail("HDF5_SCHEMA_MISMATCH", "rawData target")
            dtype = np.dtype(target.dtype)
            if dtype.kind != "f" or dtype.itemsize not in {4, 8}:
                _fail("HDF5_SCHEMA_MISMATCH", f"dtype={dtype}")
            if target.shape != (row["raw_samples"], 105):
                _fail("REAL_TENSOR_CONTRACT_MISMATCH", f"shape={target.shape}")
            array = target[()]
    except A1FrontendValidationError:
        raise
    except (OSError, KeyError, TypeError, ValueError) as exc:
        _fail("HDF5_SCHEMA_MISMATCH", type(exc).__name__)
    if not np.isfinite(array).all():
        _fail("REAL_TENSOR_NONFINITE", repr(key))
    converted = np.asarray(array, dtype=np.float32, order="C")
    if not converted.flags.c_contiguous or not np.isfinite(converted).all():
        _fail("REAL_TENSOR_NONFINITE", f"float32 cast {key!r}")
    transposed = np.ascontiguousarray(converted.T)
    if transposed.shape != (105, row["raw_samples"]):
        _fail("REAL_TENSOR_CONTRACT_MISMATCH", "explicit transpose")
    return torch.from_numpy(transposed).unsqueeze(0), f"float{dtype.itemsize * 8}"


def _check_single_output(output: Any, expected_windows: int) -> None:
    if (
        output.window_embeddings.shape != (1, expected_windows, 256)
        or output.window_mask.shape != (1, expected_windows)
        or output.pooled_embedding.shape != (1, 256)
        or output.window_mask.dtype != torch.bool
        or not output.window_mask.all().item()
        or not torch.isfinite(output.window_embeddings).all().item()
        or not torch.isfinite(output.pooled_embedding).all().item()
    ):
        _fail("REAL_TENSOR_CONTRACT_MISMATCH", "single output")
    expected_pool = output.window_embeddings.sum(dim=1) / output.window_mask.sum(dim=1, keepdim=True)
    if not torch.equal(output.pooled_embedding, expected_pool):
        _fail("REAL_TENSOR_CONTRACT_MISMATCH", "masked mean")


def _equal_output(first: Any, second: Any) -> bool:
    return (
        torch.equal(first.window_embeddings, second.window_embeddings)
        and torch.equal(first.window_mask, second.window_mask)
        and torch.equal(first.pooled_embedding, second.pooled_embedding)
    )


def _cuda_panel(real_panel: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: dict[tuple[str, int, str], dict[str, Any]] = {}
    subjects = sorted({row["subject"] for row in real_panel})
    for subject in subjects:
        row = min(
            (item for item in real_panel if item["subject"] == subject),
            key=lambda item: (item["occurrence_id"], item["role"], item["slot"]),
        )
        selected[_row_key(row)] = row
    for role in sorted(OUTER_ROLES):
        stress = [row for row in real_panel if row["role"] == role and row["selection_reason"] in {"ROLE_MAX_STRESS", "STRATIFIED_AND_ROLE_MAX"}]
        if len(stress) != 1:
            _fail("CUDA_PARITY_MISMATCH", f"stress role {role}")
        selected[_row_key(stress[0])] = stress[0]
    return sorted(selected.values(), key=lambda row: (row["subject"], row["slot"], row["occurrence_id"]))


def _validate_cuda(
    model: NativeSpectralA1,
    real_panel: list[dict[str, Any]],
    retained_inputs: dict[tuple[str, int, str], torch.Tensor],
    retained_outputs: dict[tuple[str, int, str], Any],
    *,
    enforce: bool,
) -> dict[str, Any]:
    if not torch.cuda.is_available():
        return {"status": "NOT_AVAILABLE_NONBLOCKING", "available": False, "rows": 0, "windows": 0, "device_count": 0}
    subset = _cuda_panel(real_panel)
    windows = sum(row["window_count"] for row in subset)
    if enforce and {"rows": len(subset), "windows": windows} != EXPECTED_CUDA:
        _fail("CUDA_PARITY_MISMATCH", f"subset rows={len(subset)} windows={windows}")
    old_matmul = torch.backends.cuda.matmul.allow_tf32
    old_cudnn = torch.backends.cudnn.allow_tf32
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    try:
        gpu_model = copy.deepcopy(model).to("cuda").eval()
        with torch.inference_mode():
            for row in subset:
                key = _row_key(row)
                tensor = retained_inputs[key].to("cuda")
                lengths = torch.tensor([row["raw_samples"]], dtype=torch.int64, device="cuda")
                output = gpu_model(tensor, lengths, **METADATA)
                cpu = retained_outputs[key]
                torch.testing.assert_close(output.window_embeddings.cpu(), cpu.window_embeddings, rtol=2.0e-4, atol=2.0e-4)
                torch.testing.assert_close(output.pooled_embedding.cpu(), cpu.pooled_embedding, rtol=2.0e-4, atol=2.0e-4)
                if not torch.equal(output.window_mask.cpu(), cpu.window_mask):
                    _fail("CUDA_PARITY_MISMATCH", f"mask {key!r}")
        if gpu_model.training or any(parameter.grad is not None for parameter in gpu_model.parameters()):
            _fail("PARAMETER_MUTATION", "CUDA model state")
    except A1FrontendValidationError:
        raise
    except (AssertionError, RuntimeError) as exc:
        _fail("CUDA_PARITY_MISMATCH", type(exc).__name__)
    finally:
        torch.backends.cuda.matmul.allow_tf32 = old_matmul
        torch.backends.cudnn.allow_tf32 = old_cudnn
    return {
        "status": "PASS", "available": True, "rows": len(subset), "windows": windows,
        "device_count": torch.cuda.device_count(), "device_name": torch.cuda.get_device_name(0),
        "tf32_disabled": True,
    }


def _execute_frontend(
    panel: list[dict[str, Any]],
    dataset_root: Path,
    allowed_files: dict[str, Path],
    *,
    enforce: bool,
) -> dict[str, Any]:
    real_panel = [row for row in panel if row["source_dataset_read"]]
    allowed_keys = {_row_key(row) for row in real_panel}
    if len(allowed_keys) != len(real_panel):
        _fail("PANEL_CONTRACT_MISMATCH", "duplicate real rows")
    model = NativeSpectralA1(AUDIT_SEED).eval()
    before = {name: parameter.detach().clone() for name, parameter in model.named_parameters()}
    dtype_counts: Counter[str] = Counter()
    cuda_rows = {_row_key(row) for row in _cuda_panel(real_panel)} if torch.cuda.is_available() else set()
    retained_inputs: dict[tuple[str, int, str], torch.Tensor] = {}
    retained_outputs: dict[tuple[str, int, str], Any] = {}
    ordered = sorted(real_panel, key=lambda row: (row["window_count"], row["subject"], row["slot"]))
    dereferenced: set[tuple[str, int, str]] = set()

    for offset in range(0, len(ordered), 4):
        batch_rows = ordered[offset : offset + 4]
        tensors: list[torch.Tensor] = []
        individual: list[Any] = []
        for row in batch_rows:
            key = _row_key(row)
            if key in dereferenced:
                _fail("FORBIDDEN_CELL_DEREFERENCE", f"repeat {key!r}")
            tensor, source_dtype = _read_raw(row, dataset_root, allowed_files, allowed_keys)
            dereferenced.add(key)
            dtype_counts[source_dtype] += 1
            lengths = torch.tensor([row["raw_samples"]], dtype=torch.int64)
            with torch.inference_mode():
                first = model(tensor, lengths, **METADATA)
                second = model(tensor, lengths, **METADATA)
            if not _equal_output(first, second):
                _fail("CPU_REPEAT_MISMATCH", repr(key))
            _check_single_output(first, row["window_count"])
            tensors.append(tensor)
            individual.append(first)
            if key in cuda_rows:
                retained_inputs[key] = tensor.clone()
                retained_outputs[key] = type(first)(
                    first.window_embeddings.clone(), first.window_mask.clone(), first.pooled_embedding.clone()
                )

        maximum = max(row["raw_samples"] for row in batch_rows)
        zero = torch.zeros((len(batch_rows), 105, maximum), dtype=torch.float32)
        nan = torch.full((len(batch_rows), 105, maximum), float("nan"), dtype=torch.float32)
        lengths = torch.tensor([row["raw_samples"] for row in batch_rows], dtype=torch.int64)
        for index, (row, tensor) in enumerate(zip(batch_rows, tensors)):
            zero[index, :, : row["raw_samples"]] = tensor[0]
            nan[index, :, : row["raw_samples"]] = tensor[0]
        with torch.inference_mode():
            zero_output = model(zero, lengths, **METADATA)
            nan_output = model(nan, lengths, **METADATA)
        if not _equal_output(zero_output, nan_output):
            _fail("PADDING_ISOLATION_MISMATCH", f"batch offset={offset}")
        for index, (row, single) in enumerate(zip(batch_rows, individual)):
            windows = row["window_count"]
            try:
                torch.testing.assert_close(zero_output.window_embeddings[index, :windows], single.window_embeddings[0], rtol=2.0e-5, atol=2.0e-5)
                torch.testing.assert_close(zero_output.pooled_embedding[index], single.pooled_embedding[0], rtol=2.0e-5, atol=2.0e-5)
            except AssertionError as exc:
                _fail("BATCH_PARITY_MISMATCH", f"{_row_key(row)!r}:{type(exc).__name__}")
            if not zero_output.window_mask[index, :windows].all().item() or zero_output.window_mask[index, windows:].any().item():
                _fail("BATCH_PARITY_MISMATCH", f"mask {_row_key(row)!r}")
        del tensors, individual, zero, nan, zero_output, nan_output

    if dereferenced != allowed_keys:
        _fail("FORBIDDEN_CELL_DEREFERENCE", "real-panel coverage")
    for name, parameter in model.named_parameters():
        if not torch.equal(before[name], parameter) or parameter.grad is not None:
            _fail("PARAMETER_MUTATION", name)
    if model.training:
        _fail("PARAMETER_MUTATION", "model training mode")
    cuda = _validate_cuda(model, real_panel, retained_inputs, retained_outputs, enforce=enforce)
    return {
        "real_distinct_rows_read": len(dereferenced),
        "role_counts": dict(sorted(Counter(row["role"] for row in real_panel).items())),
        "subject_count": len({row["subject"] for row in real_panel}),
        "window_count": sum(row["window_count"] for row in real_panel),
        "source_dtype_counts": dict(sorted(dtype_counts.items())),
        "cpu_status": "PASS",
        "cpu_repeat": "PASS",
        "batch_parity": "PASS",
        "padding_isolation": "PASS",
        "parameter_immutability": "PASS",
        "cuda": cuda,
    }


def _jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(
        (json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n").encode("utf-8")
        for row in rows
    )


def _yaml_bytes(value: dict[str, Any]) -> bytes:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=False).encode("utf-8")


def _report_bytes(freeze: dict[str, Any]) -> bytes:
    counts = freeze["acceptance_counts"]
    execution = freeze["check_results"]
    cuda = execution["cuda"]
    lines = [
        "# RC-HSG A1 Bounded Real-Frontend Self-Check", "",
        "## Scope", "",
        "The frozen native A1 loader and frontend passed a bounded outer-train real-data self-check. This is not full admission, training, representation quality, performance, reference, leakage-audit, or Gate evidence.", "",
        "## Audit panel", "",
        f"- Ledger rows: {counts['ledger_rows']}",
        f"- Real arrays read: {counts['real_distinct_rows_read']} distinct rows across {counts['subject_count']} subjects",
        f"- Roles: train-fit {counts['real_role_counts']['train_fit']}, inner-val {counts['real_role_counts']['inner_val']}",
        f"- Full windows: {counts['panel_windows']}",
        f"- Short rows: {counts['short_no_read']} retained with no source-array dereference", "",
        "## Checks", "",
        f"- CPU canonical path: `{execution['cpu_status']}`",
        f"- CPU repeat / batch parity / padding isolation / parameter immutability: `{execution['cpu_repeat']}` / `{execution['batch_parity']}` / `{execution['padding_isolation']}` / `{execution['parameter_immutability']}`",
        f"- CUDA: `{cuda['status']}` ({cuda['rows']} rows, {cuda['windows']} windows)",
        f"- Source dtype schema: `{freeze['loader_contract']['actual_source_dtype_counts']}`", "",
        "## Downstream boundary", "",
        "Full outer-train admission is incomplete. The remaining 3,390 eligible outer-train arrays were not read. The next task is `S0_LEAKAGE_AUDIT`; test remains locked.", "",
        "No EEG value, tensor, token, embedding, waveform hash, output hash, amplitude/frequency summary, text, outcome, prediction, metric, checkpoint, or cache was emitted.", "",
    ]
    return "\n".join(lines).encode("utf-8")


def _atomic_write(outputs: dict[Path, bytes]) -> None:
    pending: list[tuple[Path, Path]] = []
    try:
        for destination, content in outputs.items():
            destination.parent.mkdir(parents=True, exist_ok=True)
            fd, name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
            temporary = Path(name)
            with os.fdopen(fd, "wb") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            pending.append((temporary, destination))
        for temporary, destination in pending:
            os.replace(temporary, destination)
    except OSError as exc:
        _fail("ATOMIC_OUTPUT_FAILURE", type(exc).__name__)
    finally:
        for temporary, _ in pending:
            temporary.unlink(missing_ok=True)


def validate_a1_frontend(
    project_root: Path,
    dataset_root: Path,
    output_root: Path,
    *,
    enforce_frozen_expectations: bool = True,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    paths, hashes = _verify_inputs(project_root, enforce_frozen_expectations)
    eligibility = _load_jsonl(paths["eligibility"], "eligibility")
    analysis = _load_jsonl(paths["analysis_view"], "analysis_view")
    panel = select_audit_panel(eligibility, analysis)
    outer = [row for row in eligibility if row.get("role") in OUTER_ROLES]
    counts = _panel_counts(panel, outer)
    if enforce_frozen_expectations:
        _assert_frozen_panel(counts, panel)

    targeted = _load_yaml(paths["targeted_manifest_v3"], "targeted_manifest_v3")
    osf = _load_yaml(paths["osf_file_metadata"], "osf_file_metadata")
    root, allowed_files, source_identities = _dataset_files(
        dataset_root, targeted, osf, enforce=enforce_frozen_expectations
    )
    real_files = {row["source_file"] for row in panel if row["source_dataset_read"]}
    if not real_files.issubset(allowed_files):
        _fail("SOURCE_IDENTITY_MISMATCH", "panel source files")
    with _strict_execution_kernels():
        execution = _execute_frontend(panel, root, allowed_files, enforce=enforce_frozen_expectations)

    panel_content = _jsonl_bytes(panel)
    panel_hash = hashlib.sha256(panel_content).hexdigest()
    validator_path = Path(__file__).resolve()
    freeze = {
        "schema_version": 1,
        "artifact": "RC_HSG_A1_REAL_FRONTEND_VALIDATION_V1",
        "spec_version": "v2.3",
        "baseline_commit": BASELINE_COMMIT,
        "task": "S0_A1_FRONTEND",
        "policy_id": POLICY_ID,
        "evidence_scope": EVIDENCE_SCOPE,
        "input_artifacts": {
            label: {"path": FIXED_INPUTS[label][0], "sha256": hashes[label]}
            for label in FIXED_INPUTS
        },
        "authorized_scope": {
            "roles": ["train_fit", "inner_val"],
            "source_field": "rawData",
            "real_panel_only": True,
            "real_distinct_rows": execution["real_distinct_rows_read"],
            "short_rows_source_dataset_read": 0,
            "calibration_rows_source_dataset_read": 0,
            "test_rows_source_dataset_read": 0,
        },
        "panel_contract": {
            "path": OUTPUTS["panel"], "sha256": panel_hash,
            "canonical_order": ["subject", "slot", "occurrence_id"],
            "selection": "SUBJECT_ROLE_WINDOW_STRATUM_MIN_KEY_PLUS_ROLE_MAX_STRESS_AND_ALL_OUTER_SHORT",
            "strata": {"W01_04": [1, 4], "W05_16": [5, 16], "W17_PLUS": [17, None]},
        },
        "source_identity_contract": {
            "summary_files_checked": len(source_identities),
            "relative_path_and_size": "PASS",
            "osf_sha256": "REUSED_VERIFIED_RUN005_NO_REHASH",
            "files": source_identities,
        },
        "loader_contract": {
            "hdf5_path": "sentenceData/rawData[slot-1,0]",
            "reference_scope": "SAME_FILE_OBJECT_REFERENCE_ONLY",
            "source_shape": "RAW_SAMPLES_BY_105",
            "source_dtypes": ["float32", "float64"],
            "actual_source_dtype_counts": execution["source_dtype_counts"],
            "cast": "CONTIGUOUS_NATIVE_FLOAT32_NO_SCALE",
            "transpose": "EXPLICIT_T_105_TO_1_105_T",
            "finite_before_and_after_cast": "PASS",
        },
        "execution_contract": {
            "model_mode": "EVAL_INFERENCE_MODE",
            "maximum_batch_rows": 4,
            "cpu_dtype": "float32",
            "individual_repeat": "EXACT",
            "attention_kernels": "MATH_ONLY_NO_FASTPATH",
            "torch_native_jit": False,
            "torch_native_triton_overrides": False,
            "batch_tolerance": {"rtol": 2.0e-5, "atol": 2.0e-5},
            "cuda_tolerance": {"rtol": 2.0e-4, "atol": 2.0e-4},
            "training": False,
            "backward": False,
            "optimizer": False,
        },
        "acceptance_counts": {
            "outer_train_rows": counts["outer_train"]["total"],
            "outer_train_eligible": counts["outer_train"]["eligible"],
            "outer_train_short": counts["outer_train"]["short"],
            "outer_train_windows": counts["outer_train"]["windows"],
            "ledger_rows": counts["panel"]["ledger_rows"],
            "real_distinct_rows_read": execution["real_distinct_rows_read"],
            "short_no_read": counts["panel"]["short_no_read"],
            "panel_windows": execution["window_count"],
            "subject_count": execution["subject_count"],
            "real_role_counts": execution["role_counts"],
        },
        "check_results": {
            "source_identity": "PASS",
            "hdf5_firewall": "PASS",
            "real_tensor_finite": "PASS",
            "window_mask_shape": "PASS",
            "cpu_status": execution["cpu_status"],
            "cpu_repeat": execution["cpu_repeat"],
            "batch_parity": execution["batch_parity"],
            "padding_isolation": execution["padding_isolation"],
            "parameter_immutability": execution["parameter_immutability"],
            "cuda": execution["cuda"],
        },
        "implementation": {
            "validator_path": "scripts/validate_a1_frontend.py",
            "validator_sha256": _sha256(validator_path),
            "python_version": platform.python_version(),
            "torch_version": str(torch.__version__),
            "numpy_version": str(np.__version__),
            "h5py_version": str(h5py.__version__),
            "audit_seed": AUDIT_SEED,
            "audit_seed_status": "AUDIT_ONLY_NOT_MAIN_EXPERIMENT_SEED",
            "cpu_status": execution["cpu_status"],
            "cuda_status": execution["cuda"]["status"],
        },
        "prohibited": [
            "NON_PANEL_EEG_READ", "SHORT_CAL_TEST_DEREFERENCE", "TEXT_OR_OUTCOME_READ",
            "TRAINING_OR_BACKWARD", "OUTPUT_OR_TENSOR_HASH", "VALUE_SUMMARY", "CACHE_WRITE",
            "UNIT_CONVERSION", "RESAMPLING", "REREFERENCE", "CHANNEL_INTERPOLATION",
        ],
        "safety": {
            "raw_or_tensor_emitted": False,
            "value_summary_emitted": False,
            "text_or_outcome_read": False,
            "training_or_parameter_update": False,
            "full_leakage_audit_run": False,
            "test_status": "LOCKED_UNTIL_ROUTE_LOCK",
        },
        "downstream_boundary": {
            "full_outer_train_admission_completed": False,
            "remaining_eligible_rows_not_read": 3390 if enforce_frozen_expectations else max(0, counts["outer_train"]["eligible"] - execution["real_distinct_rows_read"]),
            "next_task": "S0_LEAKAGE_AUDIT",
        },
    }
    freeze_content = _yaml_bytes(freeze)
    report_content = _report_bytes(freeze)
    destinations = _safe_output_paths(output_root)
    _atomic_write({
        destinations["panel"]: panel_content,
        destinations["freeze"]: freeze_content,
        destinations["report"]: report_content,
    })
    return {
        "output_hashes": {label: _sha256(path) for label, path in destinations.items()},
        "panel": panel,
        "freeze": freeze,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args(argv)
    try:
        result = validate_a1_frontend(
            PROJECT_ROOT,
            PRODUCTION_DATASET_ROOT,
            args.output_root,
            enforce_frozen_expectations=True,
        )
    except A1FrontendValidationError as exc:
        print(f"A1_FRONTEND_VALIDATION_BLOCKED: {exc}", file=sys.stderr)
        return 1
    for label, digest in result["output_hashes"].items():
        print(f"{label}={digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
