#!/usr/bin/env python3
"""Admit the remaining Regime-I outer-train rows through the frozen A1 frontend."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASELINE_COMMIT = "07c37b3bb77c3cf396116078b64687dcebb9ee03"
POLICY_ID = "RC_HSG_NATIVE_SPECTRAL_A1_V1"
EVIDENCE_SCOPE = "FULL_REGIME_I_OUTER_TRAIN_A1_FRONTEND_ADMISSION_REUSING_RUN014_PANEL_NO_OUTCOMES_NO_TRAINING"
FIXED_INPUTS = {
    "spec_v24": ("guide/RC_HSG_Paper_Spec_v2_4_2026-08-24.md", "5878fa84db5abb380c71e6257a4a7c30e0587ab8d505ba0d9446c110d47426b5"),
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
    "frontend_validator": ("scripts/validate_a1_frontend.py", "ecc84a0363629e919409321cdc73327b6e3c7e779e224a18ab55a6b6ac6777cd"),
    "frontend_panel": ("artifacts/a1_frontend_audit_panel_v1.jsonl", "95db4e18501ae25f559bb6446621b6c062a7f36936ca0f4eec3236dc57ca43ed"),
    "frontend_freeze": ("artifacts/a1_frontend_freeze.yaml", "817b1be11d3545f1279e87fd40d391b71dd3347d0eed57c174abdfc6bf760d66"),
    "frontend_report": ("reports/a1_frontend_selfcheck.md", "703e999bc9903183dd019df853e92558a81ba8526945e32a24ae926d95af4503"),
    "a_path_audit_code": ("scripts/audit_a_path_leakage.py", "797618af0113a2f8f357ea8c91f53de7b9375afcbb3860baf437ebc1bfbe5e24"),
    "a_path_assertions": ("artifacts/a_path_leakage_assertions.yaml", "eb60565b40991f19856673acc030ec7a7dcab6c520c6af5c1b1c39167f864f70"),
    "a_path_report": ("reports/a_path_leakage_audit.md", "491986e4caed53623069b26918b9be232aff74416c8e4ef973955a6810b7fd27"),
    "run015": ("runs/2026-08-24_015_a_path_leakage_audit.md", "52ff87aad5c260d6bb3ef34367839cbb6f1251ff6f4f1282075db9d4af1b22f6"),
    "spec_v25": ("guide/RC_HSG_Paper_Spec_v2_5_2026-08-24.md", "b225a1528a05d2c0b83b31114347cd045ccc5b9a746df1ae6f06241d976b55ae"),
    "admission_code": ("scripts/admit_a1_outer_train.py", None),
}
OUTPUTS = {
    "ledger": "artifacts/a1_outer_train_admission_v1.jsonl",
    "freeze": "artifacts/a1_outer_train_admission_freeze.yaml",
    "report": "reports/a1_admission.md",
}
LEDGER_FIELDS = (
    "subject", "slot", "occurrence_id", "role", "raw_samples", "window_count",
    "a_interface_status", "action", "evidence_source", "source_file", "source_field",
    "source_dataset_read_run016", "source_dataset_read_cumulative",
    "source_dtype", "source_shape_status", "input_finite_status",
    "frontend_status", "observed_window_count", "window_mask_status",
    "output_finite_status",
)
OUTER_ROLES = {"train_fit", "inner_val"}
EXPECTED = {
    "outer_rows": 3541,
    "eligible_rows": 3497,
    "short_rows": 44,
    "outer_windows": 35745,
    "panel_rows": 107,
    "panel_windows": 1452,
    "remaining_rows": 3390,
    "remaining_windows": 34293,
    "remaining_role_rows": {"train_fit": 2742, "inner_val": 648},
    "remaining_role_windows": {"train_fit": 28411, "inner_val": 5882},
    "subjects": 18,
    "source_files": 18,
    "minimum_samples": 513,
    "maximum_samples": 18436,
    "maximum_windows": 72,
}


class A1AdmissionError(RuntimeError):
    """Fail-closed full outer-train admission error."""


def _fail(code: str, detail: str) -> None:
    raise A1AdmissionError(f"{code}: {detail}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_symlink_chain(path: Path, stop: Path, code: str, label: str) -> None:
    current = path.absolute()
    stop = stop.absolute()
    while True:
        if current.is_symlink():
            _fail(code, f"symlink:{label}")
        if current == stop or current.parent == current:
            return
        current = current.parent


def _safe_input(root: Path, relative: str, label: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts or rel.suffix.lower() in {".mat", ".h5", ".hdf5"}:
        _fail("A1_ADMISSION_INPUT_MISMATCH", f"unsafe:{label}")
    unresolved = root.absolute()
    _reject_symlink_chain(unresolved, Path(unresolved.anchor), "A1_ADMISSION_INPUT_MISMATCH", "project_root")
    candidate = unresolved / rel
    _reject_symlink_chain(candidate, unresolved, "A1_ADMISSION_INPUT_MISMATCH", label)
    resolved_root = unresolved.resolve()
    resolved = candidate.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError:
        _fail("A1_ADMISSION_INPUT_MISMATCH", f"escape:{label}")
    if not resolved.is_file():
        _fail("A1_ADMISSION_INPUT_MISMATCH", f"missing:{label}")
    return resolved


def _verify_inputs(project_root: Path, enforce: bool) -> tuple[dict[str, Path], dict[str, str]]:
    paths = {label: _safe_input(project_root, relative, label) for label, (relative, _) in FIXED_INPUTS.items()}
    hashes = {label: _sha256(path) for label, path in paths.items()}
    if enforce:
        for label, (_, expected) in FIXED_INPUTS.items():
            if expected is not None and hashes[label] != expected:
                _fail("A1_ADMISSION_INPUT_MISMATCH", f"hash:{label}")
    else:
        for label in ("frontend_validator", "a_code"):
            if hashes[label] != FIXED_INPUTS[label][1]:
                _fail("A1_ADMISSION_INPUT_MISMATCH", f"audited-code:{label}")
    return paths, hashes


def _load_yaml(path: Path, label: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        _fail("A1_ADMISSION_INPUT_MISMATCH", f"yaml:{label}:{type(exc).__name__}")
    if not isinstance(value, dict):
        _fail("A1_ADMISSION_INPUT_MISMATCH", f"schema:{label}")
    return value


def _load_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            value = json.loads(line)
            if not isinstance(value, dict):
                _fail("A1_ADMISSION_INPUT_MISMATCH", f"schema:{label}:{number}")
            rows.append(value)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail("A1_ADMISSION_INPUT_MISMATCH", f"jsonl:{label}:{type(exc).__name__}")
    return rows


def _load_validator(path: Path) -> Any:
    name = "rc_hsg_run016_frozen_frontend_validator"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        _fail("A1_ADMISSION_INPUT_MISMATCH", "validator-import-spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        _fail("A1_ADMISSION_INPUT_MISMATCH", f"validator-import:{type(exc).__name__}")
    required = {
        "_dataset_files", "_read_raw", "_strict_execution_kernels", "select_audit_panel",
        "_row_key", "METADATA", "AUDIT_SEED", "PRODUCTION_DATASET_ROOT", "NativeSpectralA1",
    }
    if any(not hasattr(module, item) for item in required):
        _fail("A1_ADMISSION_INPUT_MISMATCH", "validator-api")
    return module


def _row_key(row: dict[str, Any]) -> tuple[str, int, str]:
    key = (row.get("subject"), row.get("slot"), row.get("occurrence_id"))
    if not isinstance(key[0], str) or not isinstance(key[1], int) or not isinstance(key[2], str):
        _fail("A1_ADMISSION_SCOPE_MISMATCH", "invalid-key")
    return key


def _unique(rows: list[dict[str, Any]], label: str) -> dict[tuple[str, int, str], dict[str, Any]]:
    result: dict[tuple[str, int, str], dict[str, Any]] = {}
    for row in rows:
        key = _row_key(row)
        if key in result:
            _fail("A1_ADMISSION_SCOPE_MISMATCH", f"duplicate:{label}")
        result[key] = row
    return result


def _safe_output_root(root: Path, project_root: Path, label: str, *, external: bool) -> Path:
    unresolved = root.absolute()
    _reject_symlink_chain(unresolved, Path(unresolved.anchor), "A1_ADMISSION_OUTPUT_FAILURE", label)
    if unresolved.exists() and not unresolved.is_dir():
        _fail("A1_ADMISSION_OUTPUT_FAILURE", f"root-type:{label}")
    resolved = unresolved.resolve(strict=False)
    if external:
        try:
            resolved.relative_to(project_root.resolve())
        except ValueError:
            pass
        else:
            _fail("A1_ADMISSION_OUTPUT_FAILURE", f"not-external:{label}")
    return resolved


def _output_paths(root: Path, label: str) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for output_label, relative in OUTPUTS.items():
        candidate = root / relative
        _reject_symlink_chain(candidate, root, "A1_ADMISSION_OUTPUT_FAILURE", f"{label}:{output_label}")
        resolved = candidate.resolve(strict=False)
        try:
            resolved.relative_to(root)
        except ValueError:
            _fail("A1_ADMISSION_OUTPUT_FAILURE", f"escape:{label}:{output_label}")
        if resolved.exists() and (resolved.is_symlink() or not resolved.is_file()):
            _fail("A1_ADMISSION_OUTPUT_FAILURE", f"target-type:{label}:{output_label}")
        paths[output_label] = resolved
    return paths


def _prepare_output_roots(
    project_root: Path,
    canonical: Path,
    verification: tuple[Path, Path],
) -> tuple[dict[str, Path], dict[str, dict[str, Path]]]:
    roots = {
        "verification_a": _safe_output_root(verification[0], project_root, "verification_a", external=True),
        "verification_b": _safe_output_root(verification[1], project_root, "verification_b", external=True),
        "canonical": _safe_output_root(canonical, project_root, "canonical", external=False),
    }
    if len(set(roots.values())) != 3:
        _fail("A1_ADMISSION_OUTPUT_FAILURE", "duplicate-roots")
    return roots, {label: _output_paths(root, label) for label, root in roots.items()}


def _metadata_preflight(paths: dict[str, Path], validator: Any, enforce: bool) -> dict[str, Any]:
    eligibility = _load_jsonl(paths["eligibility"], "eligibility")
    analysis = _load_jsonl(paths["analysis_view"], "analysis_view")
    committed_panel = _load_jsonl(paths["frontend_panel"], "frontend_panel")
    by_eligibility = _unique(eligibility, "eligibility")
    by_analysis = _unique(analysis, "analysis")
    if set(by_eligibility) != set(by_analysis):
        _fail("A1_ADMISSION_SCOPE_MISMATCH", "analysis-eligibility-keys")
    selected_panel = validator.select_audit_panel(eligibility, analysis)
    if selected_panel != committed_panel:
        _fail("A1_ADMISSION_SCOPE_MISMATCH", "panel-evidence")
    panel = [row for row in committed_panel if row.get("source_dataset_read") is True]
    short_panel = [row for row in committed_panel if row.get("source_dataset_read") is False]
    outer = [row for row in eligibility if row.get("role") in OUTER_ROLES]
    eligible = [row for row in outer if row.get("a_interface_status") == "ELIGIBLE"]
    short = [row for row in outer if row.get("a_interface_status") == "A_INTERFACE_SHORT_SEGMENT"]
    panel_keys = {_row_key(row) for row in panel}
    eligible_keys = {_row_key(row) for row in eligible}
    short_keys = {_row_key(row) for row in short}
    remaining_keys = eligible_keys - panel_keys
    if panel_keys & short_keys or remaining_keys & short_keys or panel_keys & remaining_keys or panel_keys | remaining_keys != eligible_keys:
        _fail("A1_ADMISSION_SCOPE_MISMATCH", "partition")
    if {_row_key(row) for row in short_panel} != short_keys:
        _fail("A1_ADMISSION_SCOPE_MISMATCH", "short-panel")

    remaining: list[dict[str, Any]] = []
    for key in remaining_keys:
        row = by_eligibility[key]
        analysis_row = by_analysis[key]
        locator = analysis_row.get("source_locator")
        if (
            row.get("role") not in OUTER_ROLES
            or row.get("action") != "RUN_FRONTEND"
            or not isinstance(locator, dict)
            or locator.get("field") != "rawData"
            or locator.get("slot") != row.get("slot")
            or not isinstance(locator.get("summary_file"), str)
            or analysis_row.get("raw_samples") != row.get("raw_samples")
            or analysis_row.get("raw_shape") != [row.get("raw_samples"), 105]
        ):
            _fail("A1_ADMISSION_SCOPE_MISMATCH", "remaining-row")
        remaining.append({
            "subject": row["subject"], "slot": row["slot"], "occurrence_id": row["occurrence_id"],
            "role": row["role"], "raw_samples": row["raw_samples"], "window_count": row["window_count"],
            "a_interface_status": row["a_interface_status"], "action": row["action"],
            "source_file": locator["summary_file"], "source_field": "rawData", "source_dataset_read": True,
        })
    remaining.sort(key=lambda row: (row["window_count"], row["raw_samples"], row["subject"], row["slot"], row["occurrence_id"]))

    role_rows = Counter(row["role"] for row in remaining)
    role_windows = Counter()
    for row in remaining:
        role_windows[row["role"]] += row["window_count"]
    actual = {
        "outer_rows": len(outer), "eligible_rows": len(eligible), "short_rows": len(short),
        "outer_windows": sum(row["window_count"] for row in eligible),
        "panel_rows": len(panel), "panel_windows": sum(row["window_count"] for row in panel),
        "remaining_rows": len(remaining), "remaining_windows": sum(row["window_count"] for row in remaining),
        "remaining_role_rows": dict(role_rows), "remaining_role_windows": dict(role_windows),
        "subjects": len({row["subject"] for row in eligible}),
        "source_files": len({row["source_file"] for row in remaining} | {row["source_file"] for row in panel}),
        "minimum_samples": min((row["raw_samples"] for row in eligible), default=0),
        "maximum_samples": max((row["raw_samples"] for row in eligible), default=0),
        "maximum_windows": max((row["window_count"] for row in eligible), default=0),
    }
    if enforce and actual != EXPECTED:
        _fail("A1_ADMISSION_SCOPE_MISMATCH", "frozen-counts")
    return {
        "eligibility": eligibility, "analysis": analysis, "panel": panel, "short": short,
        "remaining": remaining, "remaining_keys": remaining_keys, "actual": actual,
    }


def _stable_key(row: dict[str, Any]) -> str:
    return f"{row['subject']}:{row['slot']}:{row['occurrence_id']}"


def _scan(
    validator: Any,
    remaining: list[dict[str, Any]],
    remaining_keys: set[tuple[str, int, str]],
    dataset_root: Path,
    allowed_files: dict[str, Path],
    device: Any,
) -> tuple[dict[tuple[str, int, str], dict[str, Any]], dict[str, int]]:
    torch = validator.torch
    try:
        model = validator.NativeSpectralA1(validator.AUDIT_SEED).eval()
        model = model.to(device)
        before = {name: parameter.detach().clone() for name, parameter in model.named_parameters()}
    except Exception as exc:
        _fail("A1_ADMISSION_FRONTEND_BLOCKED", f"device-init:{type(exc).__name__}")
    if model.training or any(parameter.grad is not None for parameter in model.parameters()):
        _fail("A1_ADMISSION_FRONTEND_BLOCKED", "initial-model-state")

    dereferenced: set[tuple[str, int, str]] = set()
    evidence: dict[tuple[str, int, str], dict[str, Any]] = {}
    dtype_counts: Counter[str] = Counter()
    try:
        with validator._strict_execution_kernels():
            for offset in range(0, len(remaining), 4):
                batch_rows = remaining[offset : offset + 4]
                tensors: list[Any] = []
                source_dtypes: list[str] = []
                for row in batch_rows:
                    key = _row_key(row)
                    if key in dereferenced:
                        _fail("A1_ADMISSION_SCOPE_MISMATCH", f"repeat:{_stable_key(row)}")
                    try:
                        tensor, source_dtype = validator._read_raw(row, dataset_root, allowed_files, remaining_keys)
                    except Exception as exc:
                        code = str(exc).split(":", 1)[0]
                        _fail("A1_ADMISSION_SOURCE_BLOCKED", f"{_stable_key(row)}:{code}")
                    dereferenced.add(key)
                    dtype_counts[source_dtype] += 1
                    tensors.append(tensor)
                    source_dtypes.append(source_dtype)

                maximum = max(row["raw_samples"] for row in batch_rows)
                padded = torch.zeros((len(batch_rows), 105, maximum), dtype=torch.float32)
                lengths = torch.tensor([row["raw_samples"] for row in batch_rows], dtype=torch.int64)
                for index, (row, tensor) in enumerate(zip(batch_rows, tensors)):
                    padded[index, :, : row["raw_samples"]] = tensor[0]
                try:
                    padded = padded.to(device)
                    lengths = lengths.to(device)
                    with torch.inference_mode():
                        output = model(padded, lengths, **validator.METADATA)
                except Exception as exc:
                    _fail("A1_ADMISSION_FRONTEND_BLOCKED", f"batch:{offset}:{type(exc).__name__}")

                expected_pooled = output.window_embeddings.sum(dim=1) / output.window_mask.sum(
                    dim=1, keepdim=True
                ).to(output.window_embeddings.dtype)
                if not torch.equal(output.pooled_embedding, expected_pooled):
                    _fail("A1_ADMISSION_TENSOR_BLOCKED", f"batch:{offset}:pooled")

                for index, row in enumerate(batch_rows):
                    windows = row["window_count"]
                    key = _row_key(row)
                    try:
                        if (
                            output.window_embeddings.shape[0] != len(batch_rows)
                            or output.window_embeddings.shape[2] != 256
                            or output.window_mask.shape[:1] != (len(batch_rows),)
                            or output.pooled_embedding.shape != (len(batch_rows), 256)
                            or output.window_mask.dtype != torch.bool
                            or output.window_embeddings.shape[1] < windows
                            or output.window_mask.shape[1] != output.window_embeddings.shape[1]
                            or not output.window_mask[index, :windows].all().item()
                            or output.window_mask[index, windows:].any().item()
                        ):
                            _fail("A1_ADMISSION_TENSOR_BLOCKED", f"{_stable_key(row)}:shape-mask")
                        if not torch.isfinite(output.window_embeddings[index]).all().item() or not torch.isfinite(output.pooled_embedding[index]).all().item():
                            _fail("A1_ADMISSION_TENSOR_BLOCKED", f"{_stable_key(row)}:nonfinite")
                    except A1AdmissionError:
                        raise
                    except Exception as exc:
                        _fail("A1_ADMISSION_TENSOR_BLOCKED", f"{_stable_key(row)}:{type(exc).__name__}")
                    evidence[key] = {"source_dtype": source_dtypes[index]}
                if model.training or any(parameter.grad is not None for parameter in model.parameters()):
                    _fail("A1_ADMISSION_FRONTEND_BLOCKED", f"batch:{offset}:model-state")
                del tensors, source_dtypes, padded, lengths, output
    except A1AdmissionError:
        raise
    except Exception as exc:
        _fail("A1_ADMISSION_FRONTEND_BLOCKED", f"scan:{type(exc).__name__}")

    if dereferenced != remaining_keys or len(evidence) != len(remaining_keys):
        _fail("A1_ADMISSION_SCOPE_MISMATCH", "dereference-closure")
    for name, parameter in model.named_parameters():
        if not torch.equal(before[name], parameter) or parameter.grad is not None:
            _fail("A1_ADMISSION_FRONTEND_BLOCKED", f"parameter:{name}")
    if model.training:
        _fail("A1_ADMISSION_FRONTEND_BLOCKED", "final-model-state")
    return evidence, dict(sorted(dtype_counts.items()))


def _ledger_rows(metadata: dict[str, Any], scan: dict[tuple[str, int, str], dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in metadata["panel"]:
        rows.append({
            "subject": row["subject"], "slot": row["slot"], "occurrence_id": row["occurrence_id"],
            "role": row["role"], "raw_samples": row["raw_samples"], "window_count": row["window_count"],
            "a_interface_status": row["a_interface_status"], "action": row["action"],
            "evidence_source": "RUN014_BOUNDED_PANEL_REUSED", "source_file": row["source_file"],
            "source_field": "rawData", "source_dataset_read_run016": False,
            "source_dataset_read_cumulative": True, "source_dtype": "float64",
            "source_shape_status": "PASS", "input_finite_status": "PASS", "frontend_status": "PASS",
            "observed_window_count": row["window_count"], "window_mask_status": "PASS", "output_finite_status": "PASS",
        })
    remaining_by_key = {_row_key(row): row for row in metadata["remaining"]}
    for key, evidence in scan.items():
        row = remaining_by_key[key]
        rows.append({
            "subject": row["subject"], "slot": row["slot"], "occurrence_id": row["occurrence_id"],
            "role": row["role"], "raw_samples": row["raw_samples"], "window_count": row["window_count"],
            "a_interface_status": row["a_interface_status"], "action": row["action"],
            "evidence_source": "RUN016_STREAMING_FRONTEND_PASS", "source_file": row["source_file"],
            "source_field": "rawData", "source_dataset_read_run016": True,
            "source_dataset_read_cumulative": True, "source_dtype": evidence["source_dtype"],
            "source_shape_status": "PASS", "input_finite_status": "PASS", "frontend_status": "PASS",
            "observed_window_count": row["window_count"], "window_mask_status": "PASS", "output_finite_status": "PASS",
        })
    analysis_by_key = _unique(metadata["analysis"], "analysis-ledger")
    for row in metadata["short"]:
        locator = analysis_by_key[_row_key(row)].get("source_locator", {})
        rows.append({
            "subject": row["subject"], "slot": row["slot"], "occurrence_id": row["occurrence_id"],
            "role": row["role"], "raw_samples": row["raw_samples"], "window_count": 0,
            "a_interface_status": "A_INTERFACE_SHORT_SEGMENT", "action": "FORCED_L0_NO_FRONTEND",
            "evidence_source": "SHORT_FORCED_L0_NO_READ", "source_file": locator.get("summary_file"),
            "source_field": "rawData", "source_dataset_read_run016": False,
            "source_dataset_read_cumulative": False, "source_dtype": "NOT_READ",
            "source_shape_status": "NOT_APPLICABLE", "input_finite_status": "NOT_APPLICABLE",
            "frontend_status": "NOT_APPLICABLE_FORCED_L0", "observed_window_count": 0,
            "window_mask_status": "NOT_APPLICABLE", "output_finite_status": "NOT_APPLICABLE",
        })
    rows.sort(key=lambda row: (row["subject"], row["slot"], row["occurrence_id"]))
    if any(tuple(row) != LEDGER_FIELDS for row in rows):
        _fail("A1_ADMISSION_OUTPUT_FAILURE", "ledger-fields")
    return rows


def _jsonl_bytes(rows: list[dict[str, Any]]) -> bytes:
    return b"".join((json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n").encode("utf-8") for row in rows)


def _yaml_bytes(value: dict[str, Any]) -> bytes:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=False, width=120).encode("utf-8")


def _report_bytes(device_status: str, dtype_counts: dict[str, int]) -> bytes:
    dtype_text = ", ".join(f"{key}={value}" for key, value in dtype_counts.items())
    lines = [
        "# RC-HSG v2.5 Full Outer-Train A1 Admission", "",
        "## Cumulative admission", "",
        "The Regime-I outer-train ledger contains 3,541 rows: 3,497 eligible rows with 35,745 windows and 44 short rows retained as forced L0 without dereference.", "",
        "Run 014 evidence is reused for 107 eligible rows and 1,452 windows without rereading those arrays. Run 016 performed one streaming scan of the remaining 3,390 distinct eligible rows and 34,293 windows through the frozen A1 frontend.", "",
        "## Execution evidence", "",
        f"Selected device policy status: `{device_status}`.",
        f"Audited-loader source dtype counts for run 016: {dtype_text}.",
        "Every run-016 row passed source identity, shape, finite input, expected windows, mask, finite output, exact masked mean, eval mode, null-gradient, and parameter-immutability checks.", "",
        "The same serialized ledger, freeze, and report bytes were atomically written to two repository-external verification roots and the canonical root after the single scan.", "",
        "## Evidence reuse and limits", "",
        "The run-014 repeat, padding, batch-parity, and CPU/CUDA-parity evidence remains frozen and was not regenerated. Physical units remain unresolved release-native amplitude; no unit inference, scaling, rereference, resampling, or interpolation was performed.", "",
        "This admission is not training, representation-quality evidence, N1/N2 feasibility, semantic/reference/reliability/calibration evidence, a Gate result, method leakage completion, or test unlock.", "",
        "## Stop boundary", "",
        "`S0_N1_BLOCK_FEASIBILITY` requires a new ChatGPT/author-frozen contract and is not authorized by run 016.", "",
    ]
    return "\n".join(lines).encode("utf-8")


def _freeze(
    hashes: dict[str, str],
    counts: dict[str, Any],
    dtype_counts: dict[str, int],
    device_status: str,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "artifact": "RC_HSG_A1_FULL_OUTER_TRAIN_ADMISSION_V1",
        "spec_version": "v2.5",
        "baseline_commit": BASELINE_COMMIT,
        "task": "S0_A1_ADMISSION",
        "policy_id": POLICY_ID,
        "evidence_scope": EVIDENCE_SCOPE,
        "input_artifacts": {
            label: {"path": FIXED_INPUTS[label][0], "sha256": hashes[label]}
            for label in FIXED_INPUTS
        },
        "population_contract": {
            "roles": ["train_fit", "inner_val"], "join_key": ["subject", "slot", "occurrence_id"],
            "outer_train_rows": counts["outer_rows"], "eligible_rows": counts["eligible_rows"],
            "short_rows": counts["short_rows"], "full_windows": counts["outer_windows"],
            "subjects": counts["subjects"], "source_files": counts["source_files"], "source_field": "rawData",
        },
        "reuse_contract": {
            "panel_path": FIXED_INPUTS["frontend_panel"][0], "panel_sha256": FIXED_INPUTS["frontend_panel"][1],
            "eligible_rows": counts["panel_rows"], "windows": counts["panel_windows"], "panel_reread": False,
        },
        "loader_contract": {
            "validator_path": FIXED_INPUTS["frontend_validator"][0], "validator_sha256": FIXED_INPUTS["frontend_validator"][1],
            "reader": "AUDITED_VALIDATE_A1_FRONTEND__READ_RAW_ONLY", "alternate_loader": False,
            "hdf5_path": "sentenceData/rawData[slot-1,0]", "reference_scope": "SAME_FILE_OBJECT_REFERENCE_ONLY",
            "source_shape": "RAW_SAMPLES_BY_105", "source_dtypes": ["float32", "float64"],
            "cast": "CONTIGUOUS_NATIVE_FLOAT32_NO_SCALE", "transpose": "EXPLICIT_T_105_TO_1_105_T",
        },
        "execution_contract": {
            "production_scan_attempts": 1,
            "scan_order": ["window_count", "raw_samples", "subject", "slot", "occurrence_id"],
            "maximum_batch_rows": 4, "device_policy_status": device_status,
            "model": "NativeSpectralA1(20260824).eval()", "inference_only": True, "representation_cache": False,
            "run014_repeat_padding_batch_and_parity_evidence_reused": True,
        },
        "acceptance_counts": {
            "outer_train_rows": counts["outer_rows"], "eligible_cumulative": counts["eligible_rows"],
            "short_no_read": counts["short_rows"], "full_windows_cumulative": counts["outer_windows"],
            "run014_panel_reused": counts["panel_rows"], "run014_panel_windows": counts["panel_windows"],
            "run016_remaining_distinct_arrays_read": counts["remaining_rows"], "run016_windows": counts["remaining_windows"],
            "run016_role_rows": counts["remaining_role_rows"], "run016_role_windows": counts["remaining_role_windows"],
            "subjects": counts["subjects"], "source_files": counts["source_files"],
            "minimum_eligible_samples": counts["minimum_samples"], "maximum_eligible_samples": counts["maximum_samples"],
            "maximum_windows": counts["maximum_windows"], "run016_source_dtype_counts": dtype_counts,
        },
        "check_results": {
            "input_hashes": "PASS", "key_partition": "PASS", "scope": "PASS", "source_identity": "PASS",
            "source_shape_and_finite": "PASS", "frontend_windows": "PASS", "window_masks": "PASS",
            "output_finite_and_pool": "PASS", "parameter_immutability": "PASS", "triple_render": "PASS",
        },
        "implementation": {
            "admission_path": FIXED_INPUTS["admission_code"][0], "admission_sha256": hashes["admission_code"],
            "audited_validator_only": True, "direct_hdf5_import": False,
        },
        "prohibited": [
            "PANEL_REREAD", "SHORT_CAL_TEST_DEREFERENCE", "TEXT_OR_OUTCOME_READ", "TRAINING_OR_BACKWARD",
            "REPRESENTATION_OR_VALUE_CACHE", "AMPLITUDE_POWER_FREQUENCY_SUMMARY", "UNIT_INFERENCE",
            "N1_N2_EXECUTION", "GATE_EXECUTION", "TEST_UNLOCK",
        ],
        "safety": {
            "production_scan_attempts": 1, "run014_panel_arrays_reread": 0,
            "run016_remaining_distinct_arrays_read": counts["remaining_rows"], "short_arrays_read": 0,
            "calibration_arrays_read": 0, "test_arrays_read": 0, "text_or_outcome_read": False,
            "training_or_parameter_update": False, "representation_or_value_cache_written": False,
            "test_status": "LOCKED_UNTIL_ROUTE_LOCK",
        },
        "blocker_resolution": {
            "blocker": "B_V9_A_FULL_OUTER_TRAIN_ADMISSION_PENDING", "status": "CLOSED",
            "closed_by": "S0_A1_ADMISSION",
            "retained_limitation": "OUTER_TRAIN_ONLY_SHORT_FORCED_L0_PHYSICAL_UNIT_UNRESOLVED_CAL_TEST_UNREAD_NO_PERFORMANCE_EVIDENCE",
        },
        "downstream_boundary": {
            "full_outer_train_admission_completed": True, "n1_block_feasibility_completed": False,
            "n1_sampler_implemented": False, "n2_sampler_implemented": False,
            "method_leakage_audit_completed": False, "route_locked": False,
            "next_task": "S0_N1_BLOCK_FEASIBILITY",
        },
    }


def _atomic_write(paths: dict[str, Path], rendered: dict[str, bytes]) -> None:
    pending: list[tuple[Path, Path]] = []
    replaced: list[tuple[Path, bytes | None]] = []
    try:
        for label in OUTPUTS:
            destination = paths[label]
            destination.parent.mkdir(parents=True, exist_ok=True)
            descriptor, name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
            temporary = Path(name)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(rendered[label])
                handle.flush()
                os.fsync(handle.fileno())
            pending.append((temporary, destination))
        for temporary, destination in pending:
            previous = destination.read_bytes() if destination.exists() else None
            os.replace(temporary, destination)
            replaced.append((destination, previous))
    except OSError as exc:
        for destination, previous in reversed(replaced):
            try:
                if previous is None:
                    destination.unlink(missing_ok=True)
                else:
                    destination.write_bytes(previous)
            except OSError:
                pass
        _fail("A1_ADMISSION_OUTPUT_FAILURE", type(exc).__name__)
    finally:
        for temporary, _ in pending:
            temporary.unlink(missing_ok=True)


def _write_three(
    output_paths: dict[str, dict[str, Path]],
    rendered: dict[str, bytes],
) -> None:
    for root_label in ("verification_a", "verification_b"):
        _atomic_write(output_paths[root_label], rendered)
        if any(output_paths[root_label][label].read_bytes() != rendered[label] for label in OUTPUTS):
            _fail("A1_ADMISSION_OUTPUT_FAILURE", f"identity:{root_label}")
    for label in OUTPUTS:
        if output_paths["verification_a"][label].read_bytes() != output_paths["verification_b"][label].read_bytes():
            _fail("A1_ADMISSION_OUTPUT_FAILURE", f"verification-mismatch:{label}")
    _atomic_write(output_paths["canonical"], rendered)
    if any(output_paths["canonical"][label].read_bytes() != rendered[label] for label in OUTPUTS):
        _fail("A1_ADMISSION_OUTPUT_FAILURE", "canonical-identity")


def admit_a1_outer_train(
    project_root: Path,
    dataset_root: Path,
    canonical_output_root: Path,
    verification_output_roots: tuple[Path, Path],
    *,
    enforce_frozen_expectations: bool = True,
) -> dict[str, str]:
    project_root = project_root.absolute()
    paths, hashes = _verify_inputs(project_root, enforce_frozen_expectations)
    roots, output_paths = _prepare_output_roots(project_root, canonical_output_root, verification_output_roots)
    validator = _load_validator(paths["frontend_validator"])
    metadata = _metadata_preflight(paths, validator, enforce_frozen_expectations)
    targeted = _load_yaml(paths["targeted_manifest_v3"], "targeted_manifest_v3")
    osf = _load_yaml(paths["osf_file_metadata"], "osf_file_metadata")
    try:
        resolved_dataset, allowed_files, _ = validator._dataset_files(
            dataset_root, targeted, osf, enforce=enforce_frozen_expectations
        )
    except Exception as exc:
        _fail("A1_ADMISSION_SOURCE_BLOCKED", f"identity:{type(exc).__name__}")
    real_files = {row["source_file"] for row in metadata["remaining"]}
    if not real_files.issubset(allowed_files):
        _fail("A1_ADMISSION_SCOPE_MISMATCH", "source-files")

    torch = validator.torch
    cuda_available = bool(torch.cuda.is_available())
    device = torch.device("cuda:0" if cuda_available else "cpu")
    device_status = "CUDA_0_SELECTED" if cuda_available else "CPU_SELECTED_CUDA_UNAVAILABLE"

    scan, dtype_counts = _scan(
        validator, metadata["remaining"], metadata["remaining_keys"], resolved_dataset,
        allowed_files, device,
    )
    if enforce_frozen_expectations and sum(dtype_counts.values()) != EXPECTED["remaining_rows"]:
        _fail("A1_ADMISSION_SCOPE_MISMATCH", "dtype-counts")
    rows = _ledger_rows(metadata, scan)
    if enforce_frozen_expectations and len(rows) != EXPECTED["outer_rows"]:
        _fail("A1_ADMISSION_OUTPUT_FAILURE", "ledger-count")
    freeze = _freeze(hashes, metadata["actual"], dtype_counts, device_status)
    rendered = {
        "ledger": _jsonl_bytes(rows),
        "freeze": _yaml_bytes(freeze),
        "report": _report_bytes(device_status, dtype_counts),
    }
    _write_three(output_paths, rendered)
    return {OUTPUTS[label]: hashlib.sha256(rendered[label]).hexdigest() for label in OUTPUTS}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--verification-root-a", type=Path, required=True)
    parser.add_argument("--verification-root-b", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        hashes = admit_a1_outer_train(
            PROJECT_ROOT,
            Path("/home/song/projects/trust_align/01_data_protocol/datasets/zuco_2.0"),
            args.output_root,
            (args.verification_root_a, args.verification_root_b),
        )
    except A1AdmissionError as exc:
        print(f"A1_FULL_ADMISSION_BLOCKED: {exc}", file=sys.stderr)
        return 2
    for path, digest in hashes.items():
        print(f"{path} {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
