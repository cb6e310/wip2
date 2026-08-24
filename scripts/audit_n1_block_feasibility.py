#!/usr/bin/env python3
"""Audit the frozen outcome-blind N1 block-feasibility contract."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import struct
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASELINE_COMMIT = "1c432a02f50cacda99359f630f14cfbfdfb439a1"
POLICY_ID = "RC_HSG_N1_BLOCK_FEASIBILITY_V1"
PROXY_POLICY_ID = "RC_HSG_N1_A1_LOG_RELATIVE_BANDPOWER_MEDIAN_V1"
PROBE_POLICY_ID = "RC_HSG_N1_JOINT_PERMUTATION_PROBE_V1"
EVIDENCE_SCOPE = "OUTCOME_BLIND_OUTER_TRAIN_N1_BLOCK_FEASIBILITY_SHARED_A1_SPECTRAL_PROXY_NO_TEXT_NO_OUTCOMES_NO_SAMPLER"
MIN_TRAIN_ROWS_PER_POWER_EDGE = 4
PERMUTATION_REPLICATES = 199
POPULATION_COVERAGE_THRESHOLD = 0.90
OUTER_ROLES = {"train_fit", "inner_val"}

FIXED_INPUTS = {
    "spec_v25": ("guide/RC_HSG_Paper_Spec_v2_5_2026-08-24.md", "b225a1528a05d2c0b83b31114347cd045ccc5b9a746df1ae6f06241d976b55ae"),
    "a_policy": ("artifacts/backbone_a_policy.yaml", "034a523119f12f648266d94e0499179882fbe181584d10c1af17a3502a797425"),
    "a_contract": ("artifacts/backbone_a_contract.yaml", "4c9ccddf4d5c208870422c7e5ceee65ee184d812fce662bb885998b0dad65cac"),
    "eligibility": ("artifacts/a_interface_eligibility_v1.jsonl", "8eded8fb2786747e96b8388d4d91315e39db9f8a9eb25ea69056d219e1e8e1ad"),
    "a_code": ("src/rc_hsg/backbones/native_spectral_a1.py", "71ae12d65cc0acc6fd5870434e141ee7d849eb8befa718a84fb99cb86ed533d9"),
    "analysis_view": ("artifacts/admission/zuco2_nr_analysis_view_v1.jsonl", "0751259f9f9455cba72bd7d027ffa1423e790e631ac0f5174c38da65d7cd12ff"),
    "split_regime_i": ("artifacts/split_regimeI.json", "e2c065e5b395053cd655670fede8a2b117f6eb9821af884ca31c6fed3842fbab"),
    "targeted_manifest_v3": ("artifacts/admission/zuco2_nr_targeted_manifest_v3.yaml", "50806a60937b28ae36207509c44d606af6f6b6b1be2a69c06081672f0931bfaf"),
    "osf_file_metadata": ("artifacts/admission/zuco2_osf_file_metadata.yaml", "85a8c89eeb7a523c06fb7f38aa1c371e042413087e66dcc338c16833bd8bb721"),
    "requirements_lock": ("requirements-trust-align.lock.txt", "72a2a3274ef9516dba95a4f4022cacfba0e02d10445e1618da2a569f59381910"),
    "frontend_validator": ("scripts/validate_a1_frontend.py", "ecc84a0363629e919409321cdc73327b6e3c7e779e224a18ab55a6b6ac6777cd"),
    "admission_ledger": ("artifacts/a1_outer_train_admission_v1.jsonl", "b3c1b4e11855ef4c51c5bd0c2c0009f8a24e390c511d97118c48082fc7febfd5"),
    "admission_freeze": ("artifacts/a1_outer_train_admission_freeze.yaml", "e973fbbe841a47f027cbf0f8a8ad65e66d106d675e8ed838dd0daf4a08dcab12"),
    "admission_report": ("reports/a1_admission.md", "c2dc97d886d31fdc93e82778981fdf3a2dc1fd382c850d4035fdba3487513eac"),
    "run016": ("runs/2026-08-24_016_a1_full_outer_train_admission.md", "42a0030551fbff4a9c8dd256d786987f620147712556034d2edb6108f5af96dc"),
    "a_path_assertions": ("artifacts/a_path_leakage_assertions.yaml", "eb60565b40991f19856673acc030ec7a7dcab6c520c6af5c1b1c39167f864f70"),
    "spec_v26": ("guide/RC_HSG_Paper_Spec_v2_6_2026-08-24.md", None),
    "feasibility_code": ("scripts/audit_n1_block_feasibility.py", None),
}
OUTPUTS = {
    "ledger": "artifacts/nulls/n1_block_assignment_v1.jsonl",
    "freeze": "artifacts/nulls/n1_block_feasibility.yaml",
    "report": "reports/n1_block_feasibility.md",
}
LEDGER_FIELDS = (
    "subject", "session", "slot", "occurrence_id", "role", "raw_samples", "window_count",
    "a_interface_status", "action", "length_bin", "power_bin", "power_edge_cell_id",
    "power_edge_status", "block_id", "block_size", "n1_evaluable", "n1_status",
    "source_file", "source_field", "source_dataset_read_run017",
)
EXPECTED = {
    "outer_rows": 3541,
    "eligible_rows": 3497,
    "short_rows": 44,
    "outer_windows": 35745,
    "subjects": 18,
    "source_files": 18,
}


class N1BlockFeasibilityError(RuntimeError):
    """Fail-closed N1 block-feasibility error."""


def _fail(code: str, detail: str) -> None:
    raise N1BlockFeasibilityError(f"{code}: {detail}")


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
        _fail("N1_FEASIBILITY_INPUT_MISMATCH", f"unsafe:{label}")
    unresolved = root.absolute()
    _reject_symlink_chain(unresolved, Path(unresolved.anchor), "N1_FEASIBILITY_INPUT_MISMATCH", "project_root")
    candidate = unresolved / rel
    _reject_symlink_chain(candidate, unresolved, "N1_FEASIBILITY_INPUT_MISMATCH", label)
    resolved_root = unresolved.resolve()
    resolved = candidate.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError:
        _fail("N1_FEASIBILITY_INPUT_MISMATCH", f"escape:{label}")
    if not resolved.is_file():
        _fail("N1_FEASIBILITY_INPUT_MISMATCH", f"missing:{label}")
    return resolved


def _verify_inputs(project_root: Path, enforce: bool) -> tuple[dict[str, Path], dict[str, str]]:
    paths = {label: _safe_input(project_root, relative, label) for label, (relative, _) in FIXED_INPUTS.items()}
    hashes = {label: _sha256(path) for label, path in paths.items()}
    if enforce:
        for label, (_, expected) in FIXED_INPUTS.items():
            if expected is not None and hashes[label] != expected:
                _fail("N1_FEASIBILITY_INPUT_MISMATCH", f"hash:{label}")
    else:
        for label in ("frontend_validator", "a_code"):
            if hashes[label] != FIXED_INPUTS[label][1]:
                _fail("N1_FEASIBILITY_INPUT_MISMATCH", f"audited-code:{label}")
    return paths, hashes


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail("N1_FEASIBILITY_INPUT_MISMATCH", f"json:{label}:{type(exc).__name__}")
    if not isinstance(value, dict):
        _fail("N1_FEASIBILITY_INPUT_MISMATCH", f"schema:{label}")
    return value


def _load_yaml(path: Path, label: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        _fail("N1_FEASIBILITY_INPUT_MISMATCH", f"yaml:{label}:{type(exc).__name__}")
    if not isinstance(value, dict):
        _fail("N1_FEASIBILITY_INPUT_MISMATCH", f"schema:{label}")
    return value


def _load_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            value = json.loads(line)
            if not isinstance(value, dict):
                _fail("N1_FEASIBILITY_INPUT_MISMATCH", f"schema:{label}:{number}")
            rows.append(value)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail("N1_FEASIBILITY_INPUT_MISMATCH", f"jsonl:{label}:{type(exc).__name__}")
    return rows


def _load_validator(path: Path) -> Any:
    name = "rc_hsg_run017_frozen_frontend_validator"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        _fail("N1_FEASIBILITY_INPUT_MISMATCH", "validator-import-spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        _fail("N1_FEASIBILITY_INPUT_MISMATCH", f"validator-import:{type(exc).__name__}")
    required = {
        "_dataset_files", "_read_raw", "_row_key", "METADATA", "PRODUCTION_DATASET_ROOT",
        "NativeSpectralA1",
    }
    if any(not hasattr(module, item) for item in required):
        _fail("N1_FEASIBILITY_INPUT_MISMATCH", "validator-api")
    return module


def _row_key(row: dict[str, Any]) -> tuple[str, int, str]:
    key = (row.get("subject"), row.get("slot"), row.get("occurrence_id"))
    if not isinstance(key[0], str) or not isinstance(key[1], int) or not isinstance(key[2], str):
        _fail("N1_FEASIBILITY_SCOPE_MISMATCH", "invalid-key")
    return key


def _unique(rows: list[dict[str, Any]], label: str) -> dict[tuple[str, int, str], dict[str, Any]]:
    result: dict[tuple[str, int, str], dict[str, Any]] = {}
    for row in rows:
        key = _row_key(row)
        if key in result:
            _fail("N1_FEASIBILITY_SCOPE_MISMATCH", f"duplicate:{label}")
        result[key] = row
    return result


def _length_bin(window_count: int) -> str:
    if 1 <= window_count <= 4:
        return "W01_04"
    if 5 <= window_count <= 16:
        return "W05_16"
    if window_count >= 17:
        return "W17_PLUS"
    _fail("N1_FEASIBILITY_SCOPE_MISMATCH", "length-bin")


def _power_cell_id(subject: str, session: int, length_bin: str) -> str:
    payload = b"RC_HSG_N1_POWER_CELL_V1\0" + f"{subject}\t{session}\t{length_bin}".encode("ascii")
    return "n1pc_v1_" + hashlib.sha256(payload).hexdigest()


def _block_id(role: str, subject: str, session: int, length_bin: str, power_bin: str) -> str:
    payload = b"RC_HSG_N1_BLOCK_V1\0" + f"{role}\t{subject}\t{session}\t{length_bin}\t{power_bin}".encode("ascii")
    return "n1b_v1_" + hashlib.sha256(payload).hexdigest()


def _canonical_row_key(row: dict[str, Any]) -> str:
    return f"{row['subject']}\t{row['slot']:06d}\t{row['occurrence_id']}"


def _median_float64(values: list[float]) -> float:
    if not values:
        _fail("N1_FEASIBILITY_PROXY_BLOCKED", "empty-median")
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[middle])
    return math.fsum([float(ordered[middle - 1]), float(ordered[middle])]) / 2.0


def _token_proxy(torch: Any, tokens: Any) -> float:
    if tokens.ndim != 2 or tokens.shape[1] != 840 or tokens.dtype != torch.float32:
        _fail("N1_FEASIBILITY_PROXY_BLOCKED", "token-shape-dtype")
    if not torch.isfinite(tokens).all().item():
        _fail("N1_FEASIBILITY_PROXY_BLOCKED", "token-nonfinite")
    flattened = tokens.reshape(-1)
    count = int(flattened.numel())
    if count == 0 or count % 2:
        _fail("N1_FEASIBILITY_PROXY_BLOCKED", "token-count")
    lower = float(torch.kthvalue(flattened, count // 2).values.item())
    upper = float(torch.kthvalue(flattened, count // 2 + 1).values.item())
    value = math.fsum([lower, upper]) / 2.0
    if not math.isfinite(value):
        _fail("N1_FEASIBILITY_PROXY_BLOCKED", "proxy-nonfinite")
    return value


def _safe_output_root(root: Path, project_root: Path, label: str, *, external: bool) -> Path:
    unresolved = root.absolute()
    _reject_symlink_chain(unresolved, Path(unresolved.anchor), "N1_FEASIBILITY_OUTPUT_FAILURE", label)
    if unresolved.exists() and not unresolved.is_dir():
        _fail("N1_FEASIBILITY_OUTPUT_FAILURE", f"root-type:{label}")
    resolved = unresolved.resolve(strict=False)
    if external:
        try:
            resolved.relative_to(project_root.resolve())
        except ValueError:
            pass
        else:
            _fail("N1_FEASIBILITY_OUTPUT_FAILURE", f"not-external:{label}")
    return resolved


def _output_paths(root: Path, label: str) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for output_label, relative in OUTPUTS.items():
        candidate = root / relative
        _reject_symlink_chain(candidate, root, "N1_FEASIBILITY_OUTPUT_FAILURE", f"{label}:{output_label}")
        resolved = candidate.resolve(strict=False)
        try:
            resolved.relative_to(root)
        except ValueError:
            _fail("N1_FEASIBILITY_OUTPUT_FAILURE", f"escape:{label}:{output_label}")
        if resolved.exists() and (resolved.is_symlink() or not resolved.is_file()):
            _fail("N1_FEASIBILITY_OUTPUT_FAILURE", f"target-type:{label}:{output_label}")
        paths[output_label] = resolved
    return paths


def _prepare_output_roots(
    project_root: Path,
    canonical: Path,
    verification: tuple[Path, Path],
) -> dict[str, dict[str, Path]]:
    roots = {
        "verification_a": _safe_output_root(verification[0], project_root, "verification_a", external=True),
        "verification_b": _safe_output_root(verification[1], project_root, "verification_b", external=True),
        "canonical": _safe_output_root(canonical, project_root, "canonical", external=False),
    }
    if len(set(roots.values())) != 3:
        _fail("N1_FEASIBILITY_OUTPUT_FAILURE", "duplicate-roots")
    return {label: _output_paths(root, label) for label, root in roots.items()}


def _metadata_preflight(paths: dict[str, Path], enforce: bool) -> dict[str, Any]:
    admission = _load_jsonl(paths["admission_ledger"], "admission_ledger")
    eligibility = _load_jsonl(paths["eligibility"], "eligibility")
    analysis = _load_jsonl(paths["analysis_view"], "analysis_view")
    split = _load_json(paths["split_regime_i"], "split_regime_i")
    by_admission = _unique(admission, "admission")
    by_eligibility = _unique(eligibility, "eligibility")
    by_analysis = _unique(analysis, "analysis")
    if not set(by_admission).issubset(by_eligibility) or set(by_eligibility) != set(by_analysis):
        _fail("N1_FEASIBILITY_SCOPE_MISMATCH", "key-joins")
    if split.get("test_status") != "LOCKED_UNTIL_ROUTE_LOCK":
        _fail("N1_FEASIBILITY_SCOPE_MISMATCH", "test-lock")

    eligible: list[dict[str, Any]] = []
    short: list[dict[str, Any]] = []
    for key, admitted in by_admission.items():
        eligibility_row = by_eligibility[key]
        analysis_row = by_analysis[key]
        locator = analysis_row.get("source_locator")
        if (
            admitted.get("role") not in OUTER_ROLES
            or eligibility_row.get("role") != admitted.get("role")
            or analysis_row.get("session") != 1
            or analysis_row.get("task") != "NR"
            or not isinstance(locator, dict)
            or locator.get("field") != "rawData"
            or locator.get("slot") != admitted.get("slot")
            or locator.get("summary_file") != admitted.get("source_file")
            or analysis_row.get("raw_samples") != admitted.get("raw_samples")
        ):
            _fail("N1_FEASIBILITY_SCOPE_MISMATCH", "row-contract")
        base = {
            "subject": admitted["subject"], "session": 1, "slot": admitted["slot"],
            "occurrence_id": admitted["occurrence_id"], "role": admitted["role"],
            "raw_samples": admitted["raw_samples"], "window_count": admitted["window_count"],
            "a_interface_status": admitted["a_interface_status"], "action": admitted["action"],
            "source_file": admitted["source_file"], "source_field": "rawData",
        }
        if admitted.get("a_interface_status") == "ELIGIBLE":
            if (
                admitted.get("action") != "RUN_FRONTEND"
                or admitted.get("source_dataset_read_cumulative") is not True
                or admitted.get("source_shape_status") != "PASS"
                or admitted.get("input_finite_status") != "PASS"
                or admitted.get("frontend_status") != "PASS"
                or admitted.get("window_mask_status") != "PASS"
                or admitted.get("output_finite_status") != "PASS"
                or admitted.get("observed_window_count") != admitted.get("window_count")
                or analysis_row.get("raw_shape") != [admitted.get("raw_samples"), 105]
            ):
                _fail("N1_FEASIBILITY_SCOPE_MISMATCH", "eligible-admission")
            base["length_bin"] = _length_bin(base["window_count"])
            base["source_dataset_read"] = True
            eligible.append(base)
        elif admitted.get("a_interface_status") == "A_INTERFACE_SHORT_SEGMENT":
            if (
                admitted.get("action") != "FORCED_L0_NO_FRONTEND"
                or admitted.get("window_count") != 0
                or admitted.get("source_dataset_read_cumulative") is not False
            ):
                _fail("N1_FEASIBILITY_SCOPE_MISMATCH", "short-contract")
            base["source_dataset_read"] = False
            short.append(base)
        else:
            _fail("N1_FEASIBILITY_SCOPE_MISMATCH", "admission-class")

    eligible_keys = {_row_key(row) for row in eligible}
    short_keys = {_row_key(row) for row in short}
    if eligible_keys & short_keys or eligible_keys | short_keys != set(by_admission):
        _fail("N1_FEASIBILITY_SCOPE_MISMATCH", "partition")
    eligible.sort(key=lambda row: (row["subject"], row["session"], row["length_bin"], row["role"], row["slot"], row["occurrence_id"]))
    short.sort(key=lambda row: (row["subject"], row["slot"], row["occurrence_id"]))
    actual = {
        "outer_rows": len(admission),
        "eligible_rows": len(eligible),
        "short_rows": len(short),
        "outer_windows": sum(row["window_count"] for row in eligible),
        "subjects": len({row["subject"] for row in admission}),
        "source_files": len({row["source_file"] for row in admission}),
    }
    if enforce and actual != EXPECTED:
        _fail("N1_FEASIBILITY_SCOPE_MISMATCH", "frozen-counts")
    return {
        "admission": admission, "eligible": eligible, "short": short,
        "eligible_keys": eligible_keys, "actual": actual,
    }


def _stable_key(row: dict[str, Any]) -> str:
    return f"{row['subject']}:{row['slot']}:{row['occurrence_id']}"


def _scan_proxies(
    validator: Any,
    eligible: list[dict[str, Any]],
    eligible_keys: set[tuple[str, int, str]],
    dataset_root: Path,
    allowed_files: dict[str, Path],
) -> tuple[dict[tuple[str, int, str], float], dict[str, int]]:
    torch = validator.torch
    try:
        model = validator.NativeSpectralA1(20260824).eval()
    except Exception as exc:
        _fail("N1_FEASIBILITY_PROXY_BLOCKED", f"model-init:{type(exc).__name__}")
    if next(model.parameters()).device.type != "cpu" or model.training:
        _fail("N1_FEASIBILITY_PROXY_BLOCKED", "cpu-eval")
    proxies: dict[tuple[str, int, str], float] = {}
    dereferenced: set[tuple[str, int, str]] = set()
    dtype_counts: Counter[str] = Counter()
    for row in eligible:
        key = _row_key(row)
        if key in dereferenced:
            _fail("N1_FEASIBILITY_SCOPE_MISMATCH", f"repeat:{_stable_key(row)}")
        try:
            trial, source_dtype = validator._read_raw(row, dataset_root, allowed_files, eligible_keys)
        except Exception as exc:
            code = str(exc).split(":", 1)[0]
            _fail("N1_FEASIBILITY_SOURCE_BLOCKED", f"{_stable_key(row)}:{code}")
        dereferenced.add(key)
        dtype_counts[source_dtype] += 1
        try:
            lengths = model._validate(
                trial,
                torch.tensor([row["raw_samples"]], dtype=torch.int64),
                **validator.METADATA,
            )
            if lengths != [row["raw_samples"]]:
                _fail("N1_FEASIBILITY_PROXY_BLOCKED", f"{_stable_key(row)}:valid-length")
            with torch.inference_mode():
                tokens = model._spectral_tokens(trial[0], row["raw_samples"])
            if tuple(tokens.shape) != (row["window_count"], 840):
                _fail("N1_FEASIBILITY_PROXY_BLOCKED", f"{_stable_key(row)}:window-count")
            proxies[key] = _token_proxy(torch, tokens)
        except N1BlockFeasibilityError:
            raise
        except Exception as exc:
            _fail("N1_FEASIBILITY_PROXY_BLOCKED", f"{_stable_key(row)}:{type(exc).__name__}")
        del trial, tokens
    if dereferenced != eligible_keys or set(proxies) != eligible_keys:
        _fail("N1_FEASIBILITY_SCOPE_MISMATCH", "dereference-closure")
    if model.training or any(parameter.grad is not None for parameter in model.parameters()):
        _fail("N1_FEASIBILITY_PROXY_BLOCKED", "model-state")
    return proxies, dict(sorted(dtype_counts.items()))


def _edge_and_assignments(
    metadata: dict[str, Any],
    proxies: dict[tuple[str, int, str], float],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    eligible = metadata["eligible"]
    cells: dict[tuple[str, int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in eligible:
        cells[(row["subject"], row["session"], row["length_bin"])].append(row)
    edges: list[dict[str, Any]] = []
    edge_lookup: dict[tuple[str, int, str], tuple[str, float | None]] = {}
    for cell_key in sorted(cells):
        subject, session, length_bin = cell_key
        train = [row for row in cells[cell_key] if row["role"] == "train_fit"]
        cell_id = _power_cell_id(subject, session, length_bin)
        if len(train) < MIN_TRAIN_ROWS_PER_POWER_EDGE:
            status = "INSUFFICIENT_TRAIN_CELL"
            edge = None
            low = high = ties = 0
        else:
            status = "PASS"
            edge = _median_float64([proxies[_row_key(row)] for row in train])
            low = sum(proxies[_row_key(row)] <= edge for row in train)
            high = sum(proxies[_row_key(row)] > edge for row in train)
            ties = sum(proxies[_row_key(row)] == edge for row in train)
        edge_lookup[cell_key] = (status, edge)
        edges.append({
            "power_edge_cell_id": cell_id, "subject": subject, "session": session,
            "length_bin": length_bin, "status": status, "train_rows": len(train),
            "edge_float64_hex": None if edge is None else edge.hex(),
            "train_low_rows": low, "train_high_rows": high, "train_tie_rows": ties,
        })

    assigned: list[dict[str, Any]] = []
    block_members: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for source in eligible:
        row = dict(source)
        cell_key = (row["subject"], row["session"], row["length_bin"])
        status, edge = edge_lookup[cell_key]
        row["power_edge_cell_id"] = _power_cell_id(*cell_key)
        row["power_edge_status"] = status
        if edge is None:
            row["power_bin"] = None
            row["block_id"] = None
        else:
            row["power_bin"] = "P_LOW" if proxies[_row_key(row)] <= edge else "P_HIGH"
            row["block_id"] = _block_id(row["role"], row["subject"], row["session"], row["length_bin"], row["power_bin"])
            block_members[row["block_id"]].append(row)
        assigned.append(row)

    for row in assigned:
        if row["power_edge_status"] != "PASS":
            row["block_size"] = 0
            row["n1_evaluable"] = False
            row["n1_status"] = "N1_NOT_EVALUABLE_POWER_EDGE_UNAVAILABLE"
            continue
        size = len(block_members[row["block_id"]])
        row["block_size"] = size
        row["n1_evaluable"] = size >= 2
        row["n1_status"] = "N1_EVALUABLE" if size >= 2 else "N1_NOT_EVALUABLE_SINGLETON"
    return edges, assigned, dict(block_members)


def _ledger_rows(metadata: dict[str, Any], assigned: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in assigned:
        rows.append({
            "subject": source["subject"], "session": source["session"], "slot": source["slot"],
            "occurrence_id": source["occurrence_id"], "role": source["role"],
            "raw_samples": source["raw_samples"], "window_count": source["window_count"],
            "a_interface_status": source["a_interface_status"], "action": source["action"],
            "length_bin": source["length_bin"], "power_bin": source["power_bin"],
            "power_edge_cell_id": source["power_edge_cell_id"],
            "power_edge_status": source["power_edge_status"], "block_id": source["block_id"],
            "block_size": source["block_size"], "n1_evaluable": source["n1_evaluable"],
            "n1_status": source["n1_status"], "source_file": source["source_file"],
            "source_field": "rawData", "source_dataset_read_run017": True,
        })
    for source in metadata["short"]:
        rows.append({
            "subject": source["subject"], "session": source["session"], "slot": source["slot"],
            "occurrence_id": source["occurrence_id"], "role": source["role"],
            "raw_samples": source["raw_samples"], "window_count": 0,
            "a_interface_status": "A_INTERFACE_SHORT_SEGMENT", "action": "FORCED_L0_NO_FRONTEND",
            "length_bin": "NOT_APPLICABLE_SHORT", "power_bin": None,
            "power_edge_cell_id": None, "power_edge_status": "NOT_APPLICABLE_SHORT",
            "block_id": None, "block_size": 0, "n1_evaluable": False,
            "n1_status": "N1_NOT_EVALUABLE_SHORT_FORCED_L0", "source_file": source["source_file"],
            "source_field": "rawData", "source_dataset_read_run017": False,
        })
    rows.sort(key=lambda row: (row["subject"], row["slot"], row["occurrence_id"]))
    if any(tuple(row) != LEDGER_FIELDS for row in rows):
        _fail("N1_FEASIBILITY_OUTPUT_FAILURE", "ledger-fields")
    return rows


def _ratio(numerator: int, denominator: int) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


def _coverage(ledger: list[dict[str, Any]]) -> dict[str, Any]:
    eligible = [row for row in ledger if row["a_interface_status"] == "ELIGIBLE"]
    evaluable = [row for row in eligible if row["n1_evaluable"]]
    by_role = []
    for role in sorted(OUTER_ROLES):
        population = [row for row in ledger if row["role"] == role]
        role_eligible = [row for row in eligible if row["role"] == role]
        role_evaluable = [row for row in evaluable if row["role"] == role]
        by_role.append({
            "role": role, "population_rows": len(population), "eligible_rows": len(role_eligible),
            "evaluable_rows": len(role_evaluable),
            "eligible_conditional_coverage": _ratio(len(role_evaluable), len(role_eligible)),
            "population_coverage": _ratio(len(role_evaluable), len(population)),
        })
    subject_roles = []
    for subject, role in sorted({(row["subject"], row["role"]) for row in ledger}):
        population = [row for row in ledger if row["subject"] == subject and row["role"] == role]
        cell_eligible = [row for row in eligible if row["subject"] == subject and row["role"] == role]
        cell_evaluable = [row for row in evaluable if row["subject"] == subject and row["role"] == role]
        subject_roles.append({
            "subject": subject, "role": role, "population_rows": len(population),
            "eligible_rows": len(cell_eligible), "evaluable_rows": len(cell_evaluable),
            "eligible_conditional_coverage": _ratio(len(cell_evaluable), len(cell_eligible)),
            "population_coverage": _ratio(len(cell_evaluable), len(population)),
        })
    length_power = []
    pairs = sorted({(row["length_bin"], row["power_bin"]) for row in eligible if row["power_bin"] is not None})
    for length_bin, power_bin in pairs:
        rows = [row for row in eligible if row["length_bin"] == length_bin and row["power_bin"] == power_bin]
        length_power.append({
            "length_bin": length_bin, "power_bin": power_bin, "rows": len(rows),
            "evaluable_rows": sum(row["n1_evaluable"] for row in rows),
        })
    exclusions = Counter(row["n1_status"] for row in ledger if not row["n1_evaluable"])
    return {
        "overall": {
            "population_rows": len(ledger), "eligible_rows": len(eligible), "evaluable_rows": len(evaluable),
            "eligible_conditional_coverage": _ratio(len(evaluable), len(eligible)),
            "population_coverage": _ratio(len(evaluable), len(ledger)),
        },
        "by_role": by_role,
        "by_subject_role": subject_roles,
        "by_length_power": length_power,
        "exclusion_reason_counts": dict(sorted(exclusions.items())),
        "minimum_subject_role_population_coverage": min((item["population_coverage"] for item in subject_roles), default=0.0),
    }


def _block_distribution(block_members: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    sizes = sorted(len(rows) for rows in block_members.values())
    counts = Counter(sizes)
    return {
        "blocks": len(sizes),
        "evaluable_blocks": sum(size >= 2 for size in sizes),
        "singleton_blocks": sum(size == 1 for size in sizes),
        "singleton_rows": sum(size for size in sizes if size == 1),
        "size_counts": {str(size): counts[size] for size in sorted(counts)},
        "minimum": min(sizes, default=0),
        "median": _median_float64([float(size) for size in sizes]) if sizes else 0.0,
        "maximum": max(sizes, default=0),
    }


def _permutation_probe(block_members: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    evaluable_blocks = {
        block_id: sorted(rows, key=_canonical_row_key)
        for block_id, rows in block_members.items() if len(rows) >= 2
    }
    evaluable_rows = sum(len(rows) for rows in evaluable_blocks.values())
    replicates = []
    distinct_donors: dict[str, set[str]] = defaultdict(set)
    fixed_by_role: Counter[str] = Counter()
    total_by_role: Counter[str] = Counter()
    fixed_by_subject: Counter[str] = Counter()
    total_by_subject: Counter[str] = Counter()
    violations = Counter()
    for replicate in range(1, PERMUTATION_REPLICATES + 1):
        lines: list[bytes] = []
        fixed_points = 0
        for block_id in sorted(evaluable_blocks):
            recipients = evaluable_blocks[block_id]
            donors = sorted(
                recipients,
                key=lambda row: (
                    hashlib.sha256(
                        b"RC_HSG_N1_FEASIBILITY_V1\0PERM\0"
                        + struct.pack(">H", replicate) + b"\0" + block_id.encode("ascii")
                        + b"\0" + _canonical_row_key(row).encode("ascii")
                    ).digest(),
                    _canonical_row_key(row),
                ),
            )
            if sorted(_canonical_row_key(row) for row in donors) != sorted(_canonical_row_key(row) for row in recipients):
                violations["bijection"] += 1
            for recipient, donor in zip(recipients, donors):
                recipient_key = _canonical_row_key(recipient)
                donor_key = _canonical_row_key(donor)
                if any(recipient[field] != donor[field] for field in ("role", "subject", "session", "length_bin", "power_bin")):
                    violations["cross_block"] += 1
                distinct_donors[recipient_key].add(donor_key)
                total_by_role[recipient["role"]] += 1
                total_by_subject[recipient["subject"]] += 1
                if recipient_key == donor_key:
                    fixed_points += 1
                    fixed_by_role[recipient["role"]] += 1
                    fixed_by_subject[recipient["subject"]] += 1
                lines.append(f"{replicate}\t{block_id}\t{recipient_key}\t{donor_key}\n".encode("ascii"))
        joint_hash = hashlib.sha256(b"".join(sorted(lines))).hexdigest()
        replicates.append({
            "replicate_id": replicate, "joint_mapping_sha256": joint_hash,
            "evaluable_rows": evaluable_rows, "fixed_points": fixed_points,
        })
    hashes = [item["joint_mapping_sha256"] for item in replicates]
    fixed_total = sum(item["fixed_points"] for item in replicates)
    denominator = evaluable_rows * PERMUTATION_REPLICATES
    donor_distribution = Counter(len(values) for values in distinct_donors.values())
    return {
        "replicates": replicates,
        "joint_mapping_unique_count": len(set(hashes)),
        "joint_mapping_unique_rate": _ratio(len(set(hashes)), PERMUTATION_REPLICATES),
        "fixed_points_total": fixed_total,
        "fixed_point_rate": _ratio(fixed_total, denominator),
        "fixed_points_by_role": [
            {"role": role, "fixed_points": fixed_by_role[role], "assignments": total_by_role[role], "rate": _ratio(fixed_by_role[role], total_by_role[role])}
            for role in sorted(total_by_role)
        ],
        "fixed_points_by_subject": [
            {"subject": subject, "fixed_points": fixed_by_subject[subject], "assignments": total_by_subject[subject], "rate": _ratio(fixed_by_subject[subject], total_by_subject[subject])}
            for subject in sorted(total_by_subject)
        ],
        "distinct_donor_count_distribution": {str(key): donor_distribution[key] for key in sorted(donor_distribution)},
        "bijection_violations": violations["bijection"],
        "cross_block_violations": violations["cross_block"],
    }


def _decision(coverage: dict[str, Any], probe: dict[str, Any], ledger: list[dict[str, Any]]) -> dict[str, Any]:
    subject_roles = coverage["by_subject_role"]
    structural = (
        all(any(row["n1_evaluable"] for row in ledger if row["subject"] == item["subject"] and row["role"] == item["role"]) for item in subject_roles)
        and probe["bijection_violations"] == 0
        and probe["cross_block_violations"] == 0
        and probe["joint_mapping_unique_count"] == PERMUTATION_REPLICATES
    )
    minimum = coverage["minimum_subject_role_population_coverage"]
    if structural and minimum >= POPULATION_COVERAGE_THRESHOLD:
        return {
            "structural_status": "PASS", "decision": "PASS",
            "evidence_label": "N1_OUTER_TRAIN_BLOCK_FEASIBILITY_PASS",
            "primary_fallback_status": "PENDING_CAL_COVERAGE_AND_GATE_R0",
            "next_task": "S0_N1_SAMPLER",
        }
    if structural:
        return {
            "structural_status": "PASS", "decision": "DEGRADED_COVERAGE",
            "evidence_label": "N1_OUTER_TRAIN_BLOCK_FEASIBILITY_DEGRADED_COVERAGE",
            "primary_fallback_status": "INELIGIBLE_DUE_TO_OUTER_TRAIN_COVERAGE_BELOW_0_90",
            "next_task": "S0_N1_SAMPLER",
        }
    return {
        "structural_status": "FAIL", "decision": "FAIL",
        "evidence_label": "N1_OUTER_TRAIN_BLOCK_FEASIBILITY_FAIL",
        "primary_fallback_status": "N1_FAMILY_REJECTED",
        "next_task": "S0_N2_SAMPLER",
    }


def _freeze(
    hashes: dict[str, str],
    counts: dict[str, Any],
    dtype_counts: dict[str, int],
    edges: list[dict[str, Any]],
    coverage: dict[str, Any],
    blocks: dict[str, Any],
    probe: dict[str, Any],
    decision: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "artifact": "RC_HSG_N1_BLOCK_FEASIBILITY_V1",
        "spec_version": "v2.6",
        "baseline_commit": BASELINE_COMMIT,
        "task": "S0_N1_BLOCK_FEASIBILITY",
        "policy_id": POLICY_ID,
        "evidence_scope": EVIDENCE_SCOPE,
        "input_artifacts": {
            label: {"path": FIXED_INPUTS[label][0], "sha256": hashes[label]}
            for label in FIXED_INPUTS
        },
        "authorized_scope": {
            "roles": ["train_fit", "inner_val"], "session": 1, "task": "NR",
            "eligible_arrays": counts["eligible_rows"], "short_no_read": counts["short_rows"],
            "calibration_arrays_read": 0, "test_arrays_read": 0,
        },
        "power_proxy_contract": {
            "policy_id": PROXY_POLICY_ID, "device": "CPU_ONLY",
            "reader": "AUDITED_VALIDATE_A1_FRONTEND__READ_RAW_ONLY",
            "tokenizer": "NativeSpectralA1(20260824).eval()._spectral_tokens_ONLY",
            "shape": "WINDOWS_BY_840_FLOAT32_FINITE", "median": "TWO_MIDDLE_KTHVALUE_MATH_FSUM_DIV_2",
            "row_proxy_persisted": False, "full_encoder_executed": False,
        },
        "length_bin_contract": {
            "source": "FROZEN_WINDOW_COUNT", "bins": {"W01_04": [1, 4], "W05_16": [5, 16], "W17_PLUS": [17, None]},
        },
        "power_bin_contract": {
            "edge_key": ["subject", "session", "length_bin"], "fit_role": "train_fit",
            "minimum_train_rows": MIN_TRAIN_ROWS_PER_POWER_EDGE, "low_rule": "proxy<=edge",
            "high_rule": "proxy>edge", "borrowing": False, "edge_serialization": "float.hex",
        },
        "block_contract": {
            "scientific_key": ["subject", "session", "length_bin", "power_bin"],
            "permutation_key": ["role", "subject", "session", "length_bin", "power_bin"],
            "source_experimental_block_in_key": False, "minimum_evaluable_size": 2,
            "fixed_points_allowed": True, "adjacent_borrowing": False,
        },
        "permutation_probe_contract": {
            "policy_id": PROBE_POLICY_ID, "replicates": PERMUTATION_REPLICATES,
            "algorithm": "SHA256_HASH_SORT_WITHIN_BLOCK_BIJECTION", "index_only": True,
            "donor_eeg_read": False, "donor_mapping_persisted": False,
        },
        "acceptance_thresholds": {
            "coverage_denominator": "ALL_OUTER_TRAIN_ROWS_BY_SUBJECT_ROLE",
            "minimum_subject_role_population_coverage": POPULATION_COVERAGE_THRESHOLD,
            "unique_joint_mapping_hashes": PERMUTATION_REPLICATES,
        },
        "acceptance_counts": {
            "outer_train_rows": counts["outer_rows"], "eligible_rows_read": counts["eligible_rows"],
            "short_rows_no_read": counts["short_rows"], "full_windows": counts["outer_windows"],
            "subjects": counts["subjects"], "source_files": counts["source_files"],
            "source_dtype_counts": dtype_counts,
        },
        "power_edges": edges,
        "coverage": coverage,
        "block_size_distribution": blocks,
        "permutation_probe": probe,
        "decision": decision,
        "implementation": {
            "path": FIXED_INPUTS["feasibility_code"][0], "sha256": hashes["feasibility_code"],
            "direct_hdf5_import": False, "alternate_reader": False, "alternate_spectral_transform": False,
        },
        "prohibited": [
            "SHORT_CAL_TEST_DEREFERENCE", "FULL_ENCODER", "ROW_PROXY_TOKEN_EMBEDDING_PERSISTENCE",
            "DONOR_EEG_OR_MAPPING", "TEXT_OR_OUTCOME_READ", "VALUE_CACHE", "TRAINING_OR_UPDATE",
            "N1_N2_SAMPLER", "GATE_EXECUTION", "TEST_UNLOCK",
        ],
        "safety": {
            "production_scan_attempts": 1, "eligible_arrays_read": counts["eligible_rows"],
            "short_arrays_read": 0, "calibration_arrays_read": 0, "test_arrays_read": 0,
            "cpu_tokenizer_only": True, "full_encoder_executed": False,
            "row_proxy_persisted": False, "donor_eeg_read": False, "donor_map_persisted": False,
            "text_or_outcome_read": False, "training_or_parameter_update": False,
            "test_status": "LOCKED_UNTIL_ROUTE_LOCK",
        },
        "downstream_boundary": {
            "n1_block_feasibility_completed": True, "n1_sampler_implemented": False,
            "n2_sampler_implemented": False, "gate_r0_executed": False,
            "route_locked": False, "next_task": decision["next_task"],
        },
    }


def _jsonl_bytes(rows: list[dict[str, Any]]) -> bytes:
    return b"".join((json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n").encode("utf-8") for row in rows)


def _yaml_bytes(value: dict[str, Any]) -> bytes:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=False, width=120).encode("utf-8")


def _report_bytes(freeze: dict[str, Any]) -> bytes:
    decision = freeze["decision"]
    coverage = freeze["coverage"]
    probe = freeze["permutation_probe"]
    blocks = freeze["block_size_distribution"]
    lines = [
        "# RC-HSG v2.6 N1 Block Feasibility", "",
        "## Decision", "",
        f"The outcome-blind outer-train decision is `{decision['decision']}` with evidence label `{decision['evidence_label']}`.",
        f"The minimum subject-by-role population coverage is {coverage['minimum_subject_role_population_coverage']:.12f}; the frozen threshold is 0.90.", "",
        "## Population denominator", "",
        f"The complete ledger contains {freeze['acceptance_counts']['outer_train_rows']:,} rows. The primary denominator includes eligible, short forced-L0, unavailable-edge, and singleton rows; it does not remove difficult rows to increase coverage.",
        f"Exactly {freeze['acceptance_counts']['eligible_rows_read']:,} eligible arrays were read once. All {freeze['acceptance_counts']['short_rows_no_read']} short arrays and all calibration/test arrays were not read.", "",
        "## Blocks and index-only probe", "",
        f"The frozen train-fit edges produced {blocks['blocks']} populated role-scoped blocks, including {blocks['singleton_blocks']} singleton blocks. Only blocks of size at least two were evaluable.",
        f"All {PERMUTATION_REPLICATES} index-only replicates were evaluated; {probe['joint_mapping_unique_count']}/{PERMUTATION_REPLICATES} joint mapping hashes were unique.",
        "Fixed points are retained and reported because forcing derangements would change the frozen randomization law. No recipient-donor mapping or donor EEG was persisted or read.", "",
        "## Evidence boundary", "",
        "Power edges use train-fit only and are serialized as float.hex strings. Row proxies, spectral tokens, waveforms, embeddings, and value hashes are absent from every output.",
        "This outer-train feasibility decision does not validate calibration/test coverage, implement an N1 sampler, admit N1 as the primary fallback, execute Gate R0, establish semantic/reference utility, or unlock test.", "",
        "## Stop", "",
        f"The mechanical next task is `{decision['next_task']}`, owner `CHATGPT_OR_AUTHOR`, under a new exact contract. Run 017 stops before that task.", "",
    ]
    return "\n".join(lines).encode("utf-8")


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
        _fail("N1_FEASIBILITY_OUTPUT_FAILURE", type(exc).__name__)
    finally:
        for temporary, _ in pending:
            temporary.unlink(missing_ok=True)


def _write_three(output_paths: dict[str, dict[str, Path]], rendered: dict[str, bytes]) -> None:
    for root_label in ("verification_a", "verification_b"):
        _atomic_write(output_paths[root_label], rendered)
        if any(output_paths[root_label][label].read_bytes() != rendered[label] for label in OUTPUTS):
            _fail("N1_FEASIBILITY_OUTPUT_FAILURE", f"identity:{root_label}")
    for label in OUTPUTS:
        if output_paths["verification_a"][label].read_bytes() != output_paths["verification_b"][label].read_bytes():
            _fail("N1_FEASIBILITY_OUTPUT_FAILURE", f"verification-mismatch:{label}")
    _atomic_write(output_paths["canonical"], rendered)
    if any(output_paths["canonical"][label].read_bytes() != rendered[label] for label in OUTPUTS):
        _fail("N1_FEASIBILITY_OUTPUT_FAILURE", "canonical-identity")


def audit_n1_block_feasibility(
    project_root: Path,
    dataset_root: Path,
    canonical_output_root: Path,
    verification_output_roots: tuple[Path, Path],
    *,
    enforce_frozen_expectations: bool = True,
) -> dict[str, str]:
    project_root = project_root.absolute()
    paths, hashes = _verify_inputs(project_root, enforce_frozen_expectations)
    output_paths = _prepare_output_roots(project_root, canonical_output_root, verification_output_roots)
    metadata = _metadata_preflight(paths, enforce_frozen_expectations)
    validator = _load_validator(paths["frontend_validator"])
    targeted = _load_yaml(paths["targeted_manifest_v3"], "targeted_manifest_v3")
    osf = _load_yaml(paths["osf_file_metadata"], "osf_file_metadata")
    try:
        resolved_dataset, allowed_files, _ = validator._dataset_files(
            dataset_root, targeted, osf, enforce=enforce_frozen_expectations
        )
    except Exception as exc:
        _fail("N1_FEASIBILITY_SOURCE_BLOCKED", f"identity:{type(exc).__name__}")
    if not {row["source_file"] for row in metadata["eligible"]}.issubset(allowed_files):
        _fail("N1_FEASIBILITY_SCOPE_MISMATCH", "source-files")

    proxies, dtype_counts = _scan_proxies(
        validator, metadata["eligible"], metadata["eligible_keys"], resolved_dataset, allowed_files
    )
    edges, assigned, block_members = _edge_and_assignments(metadata, proxies)
    ledger = _ledger_rows(metadata, assigned)
    coverage = _coverage(ledger)
    blocks = _block_distribution(block_members)
    probe = _permutation_probe(block_members)
    decision = _decision(coverage, probe, ledger)
    freeze = _freeze(hashes, metadata["actual"], dtype_counts, edges, coverage, blocks, probe, decision)
    rendered = {
        "ledger": _jsonl_bytes(ledger),
        "freeze": _yaml_bytes(freeze),
        "report": _report_bytes(freeze),
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
        hashes = audit_n1_block_feasibility(
            PROJECT_ROOT,
            Path("/home/song/projects/trust_align/01_data_protocol/datasets/zuco_2.0"),
            args.output_root,
            (args.verification_root_a, args.verification_root_b),
        )
    except N1BlockFeasibilityError as exc:
        print(f"N1_BLOCK_FEASIBILITY_BLOCKED: {exc}", file=sys.stderr)
        return 2
    for path, digest in hashes.items():
        print(f"{path} {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
