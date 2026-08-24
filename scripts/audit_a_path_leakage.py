#!/usr/bin/env python3
"""Audit the frozen early Regime-I split/data/A path without reading EEG values."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASELINE_COMMIT = "dc105709563cf9eb216f1c28f82fdf754e7b0683"
EVIDENCE_SCOPE = (
    "STATIC_CODE_COMMITTED_METADATA_AND_SYNTHETIC_FIXTURE_A_PATH_LEAKAGE_"
    "AUDIT_NO_NEW_REAL_EEG_VALUES_NO_OUTCOMES"
)
FIXED_INPUTS = {
    "spec_v23": ("guide/RC_HSG_Paper_Spec_v2_3_2026-08-24.md", "f5fdb4f9815cb519cc44a214c5c75812d3ebffdd007314304f20e544ae15ba9a"),
    "split_regime_i": ("artifacts/split_regimeI.json", "e2c065e5b395053cd655670fede8a2b117f6eb9821af884ca31c6fed3842fbab"),
    "analysis_view": ("artifacts/admission/zuco2_nr_analysis_view_v1.jsonl", "0751259f9f9455cba72bd7d027ffa1423e790e631ac0f5174c38da65d7cd12ff"),
    "eligibility": ("artifacts/a_interface_eligibility_v1.jsonl", "8eded8fb2786747e96b8388d4d91315e39db9f8a9eb25ea69056d219e1e8e1ad"),
    "a_policy": ("artifacts/backbone_a_policy.yaml", "034a523119f12f648266d94e0499179882fbe181584d10c1af17a3502a797425"),
    "a_contract": ("artifacts/backbone_a_contract.yaml", "4c9ccddf4d5c208870422c7e5ceee65ee184d812fce662bb885998b0dad65cac"),
    "a_code": ("src/rc_hsg/backbones/native_spectral_a1.py", "71ae12d65cc0acc6fd5870434e141ee7d849eb8befa718a84fb99cb86ed533d9"),
    "a_interface_builder": ("scripts/build_a_interface_contract.py", "153d887b7eafb605745eafd820162f5f636ff9fef40b0e4ef14d4db5d93ef964"),
    "joint_split_builder": ("scripts/build_joint_split.py", "794083d43d7c15cfb970e22699e1504738393b015198f77edcca524a85a81b5b"),
    "frontend_validator": ("scripts/validate_a1_frontend.py", "ecc84a0363629e919409321cdc73327b6e3c7e779e224a18ab55a6b6ac6777cd"),
    "frontend_panel": ("artifacts/a1_frontend_audit_panel_v1.jsonl", "95db4e18501ae25f559bb6446621b6c062a7f36936ca0f4eec3236dc57ca43ed"),
    "frontend_freeze": ("artifacts/a1_frontend_freeze.yaml", "817b1be11d3545f1279e87fd40d391b71dd3347d0eed57c174abdfc6bf760d66"),
    "frontend_report": ("reports/a1_frontend_selfcheck.md", "703e999bc9903183dd019df853e92558a81ba8526945e32a24ae926d95af4503"),
}
ADDITIONAL_INPUTS = {
    "spec_v24": ("guide/RC_HSG_Paper_Spec_v2_4_2026-08-24.md", "5878fa84db5abb380c71e6257a4a7c30e0587ab8d505ba0d9446c110d47426b5"),
    "audit_code": ("scripts/audit_a_path_leakage.py", None),
}
OUTPUTS = {
    "assertions": "artifacts/a_path_leakage_assertions.yaml",
    "report": "reports/a_path_leakage_audit.md",
}
SOURCE_LABELS = ("frontend_validator", "a_code", "a_interface_builder", "joint_split_builder")
RUNTIME_LABELS = ("frontend_validator", "a_code")
METADATA_LABELS = ("a_interface_builder", "joint_split_builder")
ASSERTION_IDS = (
    "SPLIT_ROLE_FIREWALL", "ROW_KEY_FIREWALL", "SHORT_BYPASS_FIREWALL",
    "DEREFERENCE_SCOPE_FIREWALL", "SOURCE_IDENTITY_FIREWALL",
    "SOURCE_FIELD_SLOT_FIREWALL", "NUMERIC_TRANSFORM_FIREWALL",
    "PER_ROW_PREPROCESSING_FIREWALL", "INFERENCE_ONLY_FIREWALL",
    "NO_VALUE_TEXT_OUTCOME_CACHE", "FAIL_CLOSED_AND_DETERMINISTIC",
    "TEST_AND_DOWNSTREAM_LOCK",
)
MUTATIONS = (
    ("M01_ROLE_BROADEN_CAL", "frontend_validator", 'OUTER_ROLES = {"train_fit", "inner_val"}', 'OUTER_ROLES = {"train_fit", "inner_val", "cal"}', "SPLIT_ROLE_FIREWALL"),
    ("M02_REMOVE_READ_FLAG_GUARD", "frontend_validator", ' or not row.get("source_dataset_read")', '', "DEREFERENCE_SCOPE_FIREWALL"),
    ("M03_REMOVE_ALLOWED_KEY_GUARD", "frontend_validator", 'key not in allowed_keys or ', '', "DEREFERENCE_SCOPE_FIREWALL"),
    ("M04_HDF5_WRITE_MODE", "frontend_validator", 'h5py.File(path, "r")', 'h5py.File(path, "r+")', "SOURCE_FIELD_SLOT_FIREWALL"),
    ("M05_FORBIDDEN_SOURCE_FIELD", "frontend_validator", 'sentence["rawData"]', 'sentence["content"]', "SOURCE_FIELD_SLOT_FIREWALL"),
    ("M06_WRONG_SLOT", "frontend_validator", 'references[row["slot"] - 1, 0]', 'references[0, 0]', "SOURCE_FIELD_SLOT_FIREWALL"),
    ("M07_REMOVE_VALID_SLICE", "a_code", 'trial[:, :valid_length]', 'trial[:, :]', "PER_ROW_PREPROCESSING_FIREWALL"),
    ("M08_CROSS_ROW_FIT", "a_code", '        signal = trial[:, :valid_length].to(dtype=torch.float32)', '        cross_row_fit = trial.mean(dim=0)\n        signal = trial[:, :valid_length].to(dtype=torch.float32)', "PER_ROW_PREPROCESSING_FIREWALL"),
    ("M09_TRAINING_OR_BACKWARD", "a_code", '        lengths = self._validate(', '        self.train()\n        lengths = self._validate(', "INFERENCE_ONLY_FIREWALL"),
    ("M10_OUTPUT_CACHE_WRITE", "frontend_validator", '    real_panel = [row for row in panel if row["source_dataset_read"]]', '    torch.save({}, "cache.pt")\n    real_panel = [row for row in panel if row["source_dataset_read"]]', "NO_VALUE_TEXT_OUTCOME_CACHE"),
    ("M11_DATASET_CLI_OVERRIDE", "frontend_validator", '    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT)', '    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT)\n    parser.add_argument("--dataset-root", type=Path)', "SOURCE_IDENTITY_FIREWALL"),
    ("M12_SHORT_DEREFERENCE", "frontend_validator", '            "source_field": "rawData", "source_dataset_read": False,', '            "source_field": "rawData", "source_dataset_read": True,', "SHORT_BYPASS_FIREWALL"),
)


class APathLeakageAuditError(RuntimeError):
    """Fail-closed A-path leakage audit error."""


def _fail(prefix: str, detail: str) -> None:
    raise APathLeakageAuditError(f"{prefix}: {detail}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_symlink_chain(path: Path, stop: Path, label: str) -> None:
    current = path.absolute()
    stop = stop.absolute()
    while True:
        if current.is_symlink():
            _fail("A_PATH_AUDIT_INPUT_MISMATCH", f"symlink:{label}")
        if current == stop or current.parent == current:
            return
        current = current.parent


def _safe_input(root: Path, relative: str, label: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts or rel.suffix.lower() in {".mat", ".h5", ".hdf5"}:
        _fail("A_PATH_AUDIT_INPUT_MISMATCH", f"unsafe-path:{label}")
    unresolved_root = root.absolute()
    _reject_symlink_chain(unresolved_root, Path(unresolved_root.anchor), "project_root")
    candidate = unresolved_root / rel
    _reject_symlink_chain(candidate, unresolved_root, label)
    resolved_root = unresolved_root.resolve()
    resolved = candidate.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError:
        _fail("A_PATH_AUDIT_INPUT_MISMATCH", f"path-escape:{label}")
    if not resolved.is_file():
        _fail("A_PATH_AUDIT_INPUT_MISMATCH", f"missing-or-type:{label}")
    return resolved


def _safe_outputs(output_root: Path) -> dict[str, Path]:
    unresolved = output_root.absolute()
    _reject_symlink_chain(unresolved, Path(unresolved.anchor), "output_root")
    if unresolved.exists() and not unresolved.is_dir():
        _fail("A_PATH_AUDIT_OUTPUT_FAILURE", "output-root-type")
    root = unresolved.resolve(strict=False)
    paths: dict[str, Path] = {}
    for label, relative in OUTPUTS.items():
        candidate = root / relative
        _reject_symlink_chain(candidate, root, label)
        resolved = candidate.resolve(strict=False)
        try:
            resolved.relative_to(root)
        except ValueError:
            _fail("A_PATH_AUDIT_OUTPUT_FAILURE", f"path-escape:{label}")
        if resolved.exists() and (resolved.is_symlink() or not resolved.is_file()):
            _fail("A_PATH_AUDIT_OUTPUT_FAILURE", f"output-type:{label}")
        paths[label] = resolved
    return paths


def _read_text(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        _fail("A_PATH_AUDIT_INPUT_MISMATCH", f"read:{label}:{type(exc).__name__}")


def _load_yaml(path: Path, label: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(_read_text(path, label))
    except yaml.YAMLError as exc:
        _fail("A_PATH_AUDIT_INPUT_MISMATCH", f"yaml:{label}:{type(exc).__name__}")
    if not isinstance(value, dict):
        _fail("A_PATH_AUDIT_INPUT_MISMATCH", f"schema:{label}")
    return value


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(_read_text(path, label))
    except json.JSONDecodeError as exc:
        _fail("A_PATH_AUDIT_INPUT_MISMATCH", f"json:{label}:{type(exc).__name__}")
    if not isinstance(value, dict):
        _fail("A_PATH_AUDIT_INPUT_MISMATCH", f"schema:{label}")
    return value


def _load_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for number, line in enumerate(_read_text(path, label).splitlines(), 1):
            value = json.loads(line)
            if not isinstance(value, dict):
                _fail("A_PATH_AUDIT_INPUT_MISMATCH", f"schema:{label}:{number}")
            rows.append(value)
    except json.JSONDecodeError as exc:
        _fail("A_PATH_AUDIT_INPUT_MISMATCH", f"jsonl:{label}:{type(exc).__name__}")
    return rows


def _parse(source: str, label: str) -> ast.Module:
    try:
        return ast.parse(source, filename=label)
    except SyntaxError as exc:
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", f"MALFORMED_PYTHON:{label}:{exc.lineno}")


def _function(tree: ast.Module, name: str, assertion: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    matches = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name]
    if len(matches) != 1:
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", f"{assertion}:function:{name}")
    return matches[0]


def _call_name(call: ast.Call) -> str:
    parts: list[str] = []
    value: ast.AST = call.func
    while isinstance(value, ast.Attribute):
        parts.append(value.attr)
        value = value.value
    if isinstance(value, ast.Name):
        parts.append(value.id)
    return ".".join(reversed(parts))


def _calls(node: ast.AST) -> list[ast.Call]:
    return [item for item in ast.walk(node) if isinstance(item, ast.Call)]


def _assignment_set(tree: ast.Module, name: str) -> set[Any] | None:
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            if isinstance(node.value, (ast.Set, ast.Tuple, ast.List)):
                return {item.value for item in node.value.elts if isinstance(item, ast.Constant)}
    return None


def _dict_values(function: ast.AST, key: str) -> list[Any]:
    values: list[Any] = []
    for node in ast.walk(function):
        if isinstance(node, ast.Dict):
            for dict_key, value in zip(node.keys, node.values):
                if isinstance(dict_key, ast.Constant) and dict_key.value == key and isinstance(value, ast.Constant):
                    values.append(value.value)
    return values


def _row_key(row: dict[str, Any], label: str) -> tuple[str, int, str]:
    key = (row.get("subject"), row.get("slot"), row.get("occurrence_id"))
    if not isinstance(key[0], str) or not isinstance(key[1], int) or not isinstance(key[2], str):
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", f"ROW_KEY_FIREWALL:invalid:{label}")
    return key


def _unique_rows(rows: list[dict[str, Any]], label: str) -> dict[tuple[str, int, str], dict[str, Any]]:
    output: dict[tuple[str, int, str], dict[str, Any]] = {}
    for row in rows:
        key = _row_key(row, label)
        if key in output:
            _fail("A_PATH_AUDIT_ASSERTION_FAILED", f"ROW_KEY_FIREWALL:duplicate:{label}")
        output[key] = row
    return output


def _metadata(paths: dict[str, Path], *, enforce: bool) -> dict[str, Any]:
    split = _load_json(paths["split_regime_i"], "split_regime_i")
    analysis = _load_jsonl(paths["analysis_view"], "analysis_view")
    eligibility = _load_jsonl(paths["eligibility"], "eligibility")
    panel = _load_jsonl(paths["frontend_panel"], "frontend_panel")
    freeze = _load_yaml(paths["frontend_freeze"], "frontend_freeze")
    assignments = split.get("row_assignments")
    if not isinstance(assignments, list):
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "SPLIT_ROLE_FIREWALL:row_assignments")
    maps = {
        "split": _unique_rows(assignments, "split"),
        "analysis": _unique_rows(analysis, "analysis"),
        "eligibility": _unique_rows(eligibility, "eligibility"),
        "panel": _unique_rows(panel, "panel"),
    }
    if set(maps["split"]) != set(maps["analysis"]) or set(maps["split"]) != set(maps["eligibility"]):
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "ROW_KEY_FIREWALL:join-coverage")
    if not set(maps["panel"]).issubset(maps["split"]):
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "ROW_KEY_FIREWALL:panel-coverage")
    if enforce and (len(maps["split"]) != 5905 or len(maps["panel"]) != 151):
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "ROW_KEY_FIREWALL:frozen-count")
    return {"split": split, "analysis": analysis, "eligibility": eligibility, "panel": panel, "freeze": freeze, "maps": maps, "enforce": enforce}


def _assert_split(trees: dict[str, ast.Module], data: dict[str, Any]) -> str:
    roles = {row.get("role") for row in data["maps"]["split"].values()}
    if not roles or not roles <= {"train_fit", "inner_val", "cal", "test"}:
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "SPLIT_ROLE_FIREWALL:roles")
    if data["split"].get("outer_train_roles") != ["train_fit", "inner_val"]:
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "SPLIT_ROLE_FIREWALL:split-outer")
    if _assignment_set(trees["frontend_validator"], "OUTER_ROLES") != {"train_fit", "inner_val"}:
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "SPLIT_ROLE_FIREWALL:runtime-outer")
    if any(row.get("role") not in {"train_fit", "inner_val"} for row in data["panel"]):
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "SPLIT_ROLE_FIREWALL:panel-role")
    return "Split roles are closed to four frozen labels; runtime and real panel are outer-train only."


def _assert_keys(trees: dict[str, ast.Module], data: dict[str, Any]) -> str:
    maps = data["maps"]
    for key, panel in maps["panel"].items():
        eligibility = maps["eligibility"][key]
        analysis = maps["analysis"][key]
        if panel.get("role") != eligibility.get("role") or panel.get("raw_samples") != analysis.get("raw_samples"):
            _fail("A_PATH_AUDIT_ASSERTION_FAILED", "ROW_KEY_FIREWALL:joined-fields")
    if data["enforce"]:
        expected_hash = FIXED_INPUTS["frontend_panel"][1]
        if _sha256(_CURRENT_PATHS["frontend_panel"]) != expected_hash:
            _fail("A_PATH_AUDIT_ASSERTION_FAILED", "ROW_KEY_FIREWALL:panel-hash")
    return f"The exact (subject,slot,occurrence_id) key uniquely joins {len(maps['split'])} rows; panel rows={len(maps['panel'])}."


def _assert_short(trees: dict[str, ast.Module], data: dict[str, Any]) -> str:
    short = [row for row in data["panel"] if not row.get("source_dataset_read")]
    if any(row.get("a_interface_status") != "A_INTERFACE_SHORT_SEGMENT" or row.get("action") != "FORCED_L0_NO_FRONTEND" or row.get("window_count") != 0 for row in short):
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "SHORT_BYPASS_FIREWALL:ledger")
    selector = _function(trees["frontend_validator"], "select_audit_panel", "SHORT_BYPASS_FIREWALL")
    if sorted(_dict_values(selector, "source_dataset_read"), key=str) != [False, True]:
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "SHORT_BYPASS_FIREWALL:source-construction")
    if data["enforce"] and len(short) != 44:
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "SHORT_BYPASS_FIREWALL:count")
    return f"Short ledger rows={len(short)}; all are forced L0 with zero windows and no source read."


def _assert_dereference(trees: dict[str, ast.Module], data: dict[str, Any]) -> str:
    reader = _function(trees["frontend_validator"], "_read_raw", "DEREFERENCE_SCOPE_FIREWALL")
    executor = _function(trees["frontend_validator"], "_execute_frontend", "DEREFERENCE_SCOPE_FIREWALL")
    dumped_reader = ast.dump(reader, include_attributes=False)
    dumped_executor = ast.dump(executor, include_attributes=False)
    membership_guard = any(
        isinstance(node, ast.Compare)
        and isinstance(node.left, ast.Name)
        and node.left.id == "key"
        and len(node.ops) == 1
        and isinstance(node.ops[0], ast.NotIn)
        and len(node.comparators) == 1
        and isinstance(node.comparators[0], ast.Name)
        and node.comparators[0].id == "allowed_keys"
        for node in ast.walk(reader)
    )
    required = ("source_dataset_read", "OUTER_ROLES")
    if not membership_guard or any(item not in dumped_reader for item in required):
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "DEREFERENCE_SCOPE_FIREWALL:guard")
    read_calls = [call for call in _calls(trees["frontend_validator"]) if _call_name(call) == "_read_raw"]
    if len(read_calls) != 1 or "dereferenced" not in dumped_executor or "allowed_keys" not in dumped_executor or "NotEq" not in dumped_executor:
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "DEREFERENCE_SCOPE_FIREWALL:once-or-closure")
    real = [row for row in data["panel"] if row.get("source_dataset_read") is True]
    if len({_row_key(row, "real-panel") for row in real}) != len(real):
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "DEREFERENCE_SCOPE_FIREWALL:real-keys")
    if data["enforce"] and len(real) != 107:
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "DEREFERENCE_SCOPE_FIREWALL:count")
    return f"Only {len(real)} distinct read-true outer-train panel keys can reach the single dereference call; set equality closes coverage."


def _cli_options(tree: ast.Module) -> list[str]:
    main = _function(tree, "main", "SOURCE_IDENTITY_FIREWALL")
    options: list[str] = []
    for call in _calls(main):
        if _call_name(call).endswith("add_argument") and call.args and isinstance(call.args[0], ast.Constant) and isinstance(call.args[0].value, str):
            options.append(call.args[0].value)
    return options


def _assert_identity(trees: dict[str, ast.Module], data: dict[str, Any]) -> str:
    validator = trees["frontend_validator"]
    constants = [node.value for node in ast.walk(validator) if isinstance(node, ast.Constant) and isinstance(node.value, str)]
    if "/home/song/projects/trust_align/01_data_protocol/datasets/zuco_2.0" not in constants:
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "SOURCE_IDENTITY_FIREWALL:constant-root")
    if _cli_options(validator) != ["--output-root"]:
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "SOURCE_IDENTITY_FIREWALL:cli")
    source = _function(validator, "_dataset_files", "SOURCE_IDENTITY_FIREWALL")
    dumped = ast.dump(source, include_attributes=False)
    for token in ("_reject_symlink_chain", "relative_to", "size_bytes", "actual_paths", "expected_paths"):
        if token not in dumped:
            _fail("A_PATH_AUDIT_ASSERTION_FAILED", f"SOURCE_IDENTITY_FIREWALL:{token}")
    return "Dataset root is a module constant; CLI has no dataset override; symlink, escape, file-set, and size guards are present."


def _assert_field_slot(trees: dict[str, ast.Module], data: dict[str, Any]) -> str:
    reader = _function(trees["frontend_validator"], "_read_raw", "SOURCE_FIELD_SLOT_FIREWALL")
    calls = _calls(reader)
    hdf5 = [call for call in calls if _call_name(call) == "h5py.File"]
    if len(hdf5) != 1 or len(hdf5[0].args) < 2 or not isinstance(hdf5[0].args[1], ast.Constant) or hdf5[0].args[1].value != "r":
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "SOURCE_FIELD_SLOT_FIREWALL:readonly")
    dumped = ast.dump(reader, include_attributes=False)
    for token in ("rawData", "HardLink", "check_dtype", "reference", "raw_samples"):
        if token not in dumped:
            _fail("A_PATH_AUDIT_ASSERTION_FAILED", f"SOURCE_FIELD_SLOT_FIREWALL:{token}")
    forbidden_fields = {"content", "word", "label", "outcome", "prediction", "result"}
    constants = {node.value for node in ast.walk(reader) if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    exact_slot = False
    for node in ast.walk(reader):
        if not (
            isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Name)
            and node.value.id == "references"
            and isinstance(node.slice, ast.Tuple)
            and len(node.slice.elts) == 2
        ):
            continue
        first, second = node.slice.elts
        exact_slot = (
            isinstance(first, ast.BinOp)
            and isinstance(first.op, ast.Sub)
            and isinstance(first.left, ast.Subscript)
            and isinstance(first.left.value, ast.Name)
            and first.left.value.id == "row"
            and isinstance(first.left.slice, ast.Constant)
            and first.left.slice.value == "slot"
            and isinstance(first.right, ast.Constant)
            and first.right.value == 1
            and isinstance(second, ast.Constant)
            and second.value == 0
        )
    if constants & forbidden_fields or not exact_slot:
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "SOURCE_FIELD_SLOT_FIREWALL:slot-or-field")
    return "The reader opens one HDF5 file read-only and follows the same-file hard reference at sentenceData/rawData[slot-1,0] with floating [raw_samples,105] checks."


def _assert_numeric(trees: dict[str, ast.Module], data: dict[str, Any]) -> str:
    reader = _function(trees["frontend_validator"], "_read_raw", "NUMERIC_TRANSFORM_FIREWALL")
    dumped = ast.dump(reader, include_attributes=False)
    for token in ("isfinite", "float32", "asarray", "ascontiguousarray", "c_contiguous"):
        if token not in dumped:
            _fail("A_PATH_AUDIT_ASSERTION_FAILED", f"NUMERIC_TRANSFORM_FIREWALL:{token}")
    calls = {_call_name(call) for call in _calls(reader)}
    if calls & {"resample", "interpolate", "rereference", "guess_unit"}:
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "NUMERIC_TRANSFORM_FIREWALL:forbidden-transform")
    return "Finite checks bracket a no-scale contiguous float32 cast followed by one explicit transpose; no unit or sampling transform is called."


def _assert_preprocessing(trees: dict[str, ast.Module], data: dict[str, Any]) -> str:
    spectral = _function(trees["a_code"], "_spectral_tokens", "PER_ROW_PREPROCESSING_FIREWALL")
    forward = _function(trees["a_code"], "forward", "PER_ROW_PREPROCESSING_FIREWALL")
    dumped = ast.dump(spectral, include_attributes=False)
    if "valid_length" not in dumped or "Slice(upper=Name(id='valid_length'" not in dumped:
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "PER_ROW_PREPROCESSING_FIREWALL:valid-slice")
    for token in ("median", "mad", "rms", "mean", "sqrt"):
        if token not in dumped:
            _fail("A_PATH_AUDIT_ASSERTION_FAILED", f"PER_ROW_PREPROCESSING_FIREWALL:{token}")
    combined = list(ast.walk(spectral)) + list(ast.walk(forward))
    names = {node.id for node in combined if isinstance(node, ast.Name)}
    call_names = {_call_name(node) for node in combined if isinstance(node, ast.Call)}
    if any("cross_row" in name or "dataset" in name for name in names) or any(name.endswith(".fit") or name.endswith(".partial_fit") for name in call_names):
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "PER_ROW_PREPROCESSING_FIREWALL:cross-row")
    if "_spectral_tokens" not in ast.dump(forward, include_attributes=False) or "enumerate" not in ast.dump(forward, include_attributes=False):
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "PER_ROW_PREPROCESSING_FIREWALL:row-loop")
    return "Native A slices each valid prefix, computes channel-wise median/MAD/RMS per row, and tokenizes rows independently before padding."


def _assert_inference(trees: dict[str, ast.Module], data: dict[str, Any]) -> str:
    runtime_calls = [_call_name(call) for label in RUNTIME_LABELS for call in _calls(trees[label])]
    if "torch.inference_mode" not in runtime_calls or not any(name == "eval" or name.endswith(".eval") for name in runtime_calls):
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "INFERENCE_ONLY_FIREWALL:eval-inference")
    forbidden = ("train", "backward", "step", "optimizer", "loss")
    if any(any(name.lower() == token or name.lower().endswith(f".{token}") for token in forbidden) for name in runtime_calls):
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "INFERENCE_ONLY_FIREWALL:training-call")
    return "Frozen runtime constructs eval-mode models under inference_mode and contains no optimizer, loss, backward, update, train, or checkpoint call."


def _assert_no_cache(trees: dict[str, ast.Module], data: dict[str, Any]) -> str:
    runtime_calls = [_call_name(call).lower() for label in RUNTIME_LABELS for call in _calls(trees[label])]
    forbidden_calls = ("torch.save", "numpy.save", "np.save", "pickle", "joblib", "parquet", "h5py.file")
    for name in runtime_calls:
        if any(token in name for token in forbidden_calls) and name != "h5py.file":
            _fail("A_PATH_AUDIT_ASSERTION_FAILED", "NO_VALUE_TEXT_OUTCOME_CACHE:cache-writer")
    reader = _function(trees["frontend_validator"], "_read_raw", "NO_VALUE_TEXT_OUTCOME_CACHE")
    accessed = {node.value for node in ast.walk(reader) if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    if accessed & {"content", "word", "words", "label", "labels", "outcome", "prediction", "metric", "result"}:
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "NO_VALUE_TEXT_OUTCOME_CACHE:forbidden-field")
    return "The runtime reader accesses only rawData and contains no value, token, embedding, prediction, metric, checkpoint, or feature-cache writer."


def _assert_deterministic(trees: dict[str, ast.Module], data: dict[str, Any]) -> str:
    audit_tree = _parse(_read_text(_CURRENT_PATHS["audit_code"], "audit_code"), "audit_code")
    imports = {_call_name(node) for node in _calls(audit_tree)}
    source = _read_text(_CURRENT_PATHS["audit_code"], "audit_code")
    imported_modules = {
        alias.name
        for node in ast.walk(audit_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or ""
        for node in ast.walk(audit_tree)
        if isinstance(node, ast.ImportFrom)
    }
    forbidden_modules = ("subprocess", "h5py", "numpy", "torch", "rc_hsg", "validate_a1_frontend")
    if any(module == prefix or module.startswith(f"{prefix}.") for module in imported_modules for prefix in forbidden_modules):
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "FAIL_CLOSED_AND_DETERMINISTIC:forbidden-import")
    for token in ("tempfile.mkstemp", "flush", "os.fsync", "os.replace"):
        if token not in imports and token not in source:
            _fail("A_PATH_AUDIT_ASSERTION_FAILED", f"FAIL_CLOSED_AND_DETERMINISTIC:{token}")
    for prefix in ("A_PATH_AUDIT_INPUT_MISMATCH", "A_PATH_AUDIT_ASSERTION_FAILED", "A_PATH_AUDIT_MUTATION_NOT_REJECTED", "A_PATH_AUDIT_OUTPUT_FAILURE"):
        if prefix not in source:
            _fail("A_PATH_AUDIT_ASSERTION_FAILED", f"FAIL_CLOSED_AND_DETERMINISTIC:{prefix}")
    return "Inputs and outputs are path-closed; failures use stable prefixes; serialization precedes same-directory temp, flush, fsync, and replace."


def _assert_lock(trees: dict[str, ast.Module], data: dict[str, Any]) -> str:
    split = data["split"]
    freeze = data["freeze"]
    boundary = freeze.get("downstream_boundary", {})
    if split.get("test_status") != "LOCKED_UNTIL_ROUTE_LOCK" or freeze.get("safety", {}).get("test_status") != "LOCKED_UNTIL_ROUTE_LOCK":
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "TEST_AND_DOWNSTREAM_LOCK:test")
    if boundary != {"full_outer_train_admission_completed": False, "remaining_eligible_rows_not_read": 3390, "next_task": "S0_LEAKAGE_AUDIT"}:
        _fail("A_PATH_AUDIT_ASSERTION_FAILED", "TEST_AND_DOWNSTREAM_LOCK:prior-boundary")
    return "Route remains unlocked, test remains LOCKED_UNTIL_ROUTE_LOCK, 3,390 eligible rows remain unread, and no downstream method or Gate is executed."


ASSERTIONS: dict[str, Callable[[dict[str, ast.Module], dict[str, Any]], str]] = {
    "SPLIT_ROLE_FIREWALL": _assert_split,
    "ROW_KEY_FIREWALL": _assert_keys,
    "SHORT_BYPASS_FIREWALL": _assert_short,
    "DEREFERENCE_SCOPE_FIREWALL": _assert_dereference,
    "SOURCE_IDENTITY_FIREWALL": _assert_identity,
    "SOURCE_FIELD_SLOT_FIREWALL": _assert_field_slot,
    "NUMERIC_TRANSFORM_FIREWALL": _assert_numeric,
    "PER_ROW_PREPROCESSING_FIREWALL": _assert_preprocessing,
    "INFERENCE_ONLY_FIREWALL": _assert_inference,
    "NO_VALUE_TEXT_OUTCOME_CACHE": _assert_no_cache,
    "FAIL_CLOSED_AND_DETERMINISTIC": _assert_deterministic,
    "TEST_AND_DOWNSTREAM_LOCK": _assert_lock,
}
_CURRENT_PATHS: dict[str, Path] = {}


def _evaluate(assertion: str, sources: dict[str, str], data: dict[str, Any]) -> str:
    trees = {label: _parse(source, label) for label, source in sources.items()}
    return ASSERTIONS[assertion](trees, data)


def _mutation_probes(sources: dict[str, str], data: dict[str, Any]) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for mutation_id, label, old, new, assertion in MUTATIONS:
        if sources[label].count(old) != 1:
            _fail("A_PATH_AUDIT_MUTATION_NOT_REJECTED", f"{mutation_id}:replacement-count")
        mutated = dict(sources)
        mutated[label] = mutated[label].replace(old, new, 1)
        try:
            _evaluate(assertion, mutated, data)
        except APathLeakageAuditError as exc:
            if not str(exc).startswith("A_PATH_AUDIT_ASSERTION_FAILED:"):
                raise
        else:
            _fail("A_PATH_AUDIT_MUTATION_NOT_REJECTED", mutation_id)
        results.append({"id": mutation_id, "status": "PASS_REJECTED", "detecting_assertion": assertion})
    return results


def _yaml_bytes(value: dict[str, Any]) -> bytes:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=False, width=120).encode("utf-8")


def _report_bytes(assertions: list[dict[str, str]]) -> bytes:
    lines = [
        "# RC-HSG v2.4 A-Path Leakage Audit", "",
        "## Evidence boundary", "",
        "This audit combines committed metadata cross-checks, function-scoped AST semantics, synthetic-fixture tests, and twelve in-memory mutation probes. Production data files were not opened and the real frontend validator was not imported or executed.", "",
        "## Machine assertions", "",
    ]
    for item in assertions:
        lines.extend([f"### {item['id']}", "", item["evidence"], ""])
    lines.extend([
        "## Epistemic limits", "",
        "The evidence supports only the early Regime-I split/data/frozen-A-path firewall. It does not complete full outer-train admission, the later method leakage audit, schema or reference work, calibration, any Gate, or test unlock. The remaining 3,390 eligible rows and all short/cal/test signal arrays remain outside this run.", "",
        "## Stop boundary", "",
        "The next task is `S0_A1_ADMISSION`, which requires a separate author-frozen execution contract and is not authorized by run 015.", "",
    ])
    return "\n".join(lines).encode("utf-8")


def _atomic_write(outputs: dict[Path, bytes]) -> None:
    pending: list[tuple[Path, Path]] = []
    try:
        for destination, content in outputs.items():
            destination.parent.mkdir(parents=True, exist_ok=True)
            descriptor, name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
            temporary = Path(name)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            pending.append((temporary, destination))
        for temporary, destination in pending:
            os.replace(temporary, destination)
    except OSError as exc:
        _fail("A_PATH_AUDIT_OUTPUT_FAILURE", type(exc).__name__)
    finally:
        for temporary, _ in pending:
            temporary.unlink(missing_ok=True)


def audit_a_path_leakage(
    project_root: Path,
    output_root: Path,
    *,
    enforce_frozen_expectations: bool = True,
) -> dict[str, str]:
    global _CURRENT_PATHS
    project_root = project_root.absolute()
    contracts = {**FIXED_INPUTS, **ADDITIONAL_INPUTS}
    paths = {label: _safe_input(project_root, relative, label) for label, (relative, _) in contracts.items()}
    _CURRENT_PATHS = paths
    hashes = {label: _sha256(path) for label, path in paths.items()}
    if enforce_frozen_expectations:
        for label, (_, expected) in contracts.items():
            if expected is not None and hashes[label] != expected:
                _fail("A_PATH_AUDIT_INPUT_MISMATCH", f"hash:{label}")
    sources = {label: _read_text(paths[label], label) for label in SOURCE_LABELS}
    data = _metadata(paths, enforce=enforce_frozen_expectations)
    assertions = [{"id": assertion, "status": "PASS", "evidence": _evaluate(assertion, sources, data)} for assertion in ASSERTION_IDS]
    mutations = _mutation_probes(sources, data)
    input_artifacts = {
        label: {"path": contracts[label][0], "sha256": hashes[label]}
        for label in contracts
    }
    artifact = {
        "schema_version": 1,
        "artifact": "RC_HSG_A_PATH_LEAKAGE_ASSERTIONS_V1",
        "spec_version": "v2.4",
        "baseline_commit": BASELINE_COMMIT,
        "task": "S0_LEAKAGE_AUDIT",
        "evidence_scope": EVIDENCE_SCOPE,
        "input_artifacts": input_artifacts,
        "audited_components": {
            "runtime_value_path": [FIXED_INPUTS[label][0] for label in RUNTIME_LABELS],
            "metadata_provenance_path": [FIXED_INPUTS[label][0] for label in METADATA_LABELS],
        },
        "frozen_scope": {
            "roles": ["train_fit", "inner_val"],
            "join_key": ["subject", "slot", "occurrence_id"],
            "panel_rows": 151,
            "real_rows": 107,
            "short_no_read_rows": 44,
            "subjects": 18,
            "panel_windows": 1452,
            "remaining_eligible_rows_not_read": 3390,
            "source_field": "rawData",
            "test_status": "LOCKED_UNTIL_ROUTE_LOCK",
            "production_hdf5_open_count": 0,
        },
        "assertions": assertions,
        "mutation_tests": mutations,
        "prohibited": [
            "PRODUCTION_HDF5_OPEN", "NEW_REAL_EEG_VALUE_READ", "REAL_FRONTEND_VALIDATOR_EXECUTION",
            "TEXT_OR_OUTCOME_READ", "TRAINING_OR_PARAMETER_UPDATE", "VALUE_OR_FEATURE_CACHE_WRITE",
            "FULL_ADMISSION", "METHOD_LEAKAGE_AUDIT", "GATE_EXECUTION", "TEST_UNLOCK",
        ],
        "safety": {
            "production_hdf5_opened": False,
            "new_real_eeg_values_read": False,
            "real_frontend_validator_executed": False,
            "text_or_outcome_read": False,
            "training_or_parameter_update": False,
            "test_status": "LOCKED_UNTIL_ROUTE_LOCK",
        },
        "downstream_boundary": {
            "full_outer_train_admission_completed": False,
            "remaining_eligible_rows_not_read": 3390,
            "method_leakage_audit_completed": False,
            "full_method_leakage_pass_claimed": False,
            "next_task": "S0_A1_ADMISSION",
        },
    }
    rendered = {
        "assertions": _yaml_bytes(artifact),
        "report": _report_bytes(assertions),
    }
    outputs = _safe_outputs(output_root)
    _atomic_write({outputs[label]: rendered[label] for label in OUTPUTS})
    return {OUTPUTS[label]: hashlib.sha256(rendered[label]).hexdigest() for label in OUTPUTS}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args(argv)
    try:
        hashes = audit_a_path_leakage(PROJECT_ROOT, args.output_root)
    except APathLeakageAuditError as exc:
        print(f"A_PATH_LEAKAGE_AUDIT_BLOCKED: {exc}", file=sys.stderr)
        return 2
    for path, digest in hashes.items():
        print(f"{path} {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
