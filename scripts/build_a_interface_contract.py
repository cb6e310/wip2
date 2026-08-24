#!/usr/bin/env python3
"""Build the frozen native spectral A-interface metadata contract.

The builder reads committed metadata only. It never follows source locators or
opens EEG, stimulus, outcome, prediction, metric, or historical result files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import numpy
import torch
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from rc_hsg.backbones.native_spectral_a1 import (  # noqa: E402
    BANDS_HZ,
    CHANNEL_ORDER_HASH,
    EMBEDDING_DIM,
    FEATURE_EPSILON,
    HOP_SAMPLES,
    INPUT_CHANNELS,
    PROCESSED_REFERENCE,
    SAMPLING_HZ,
    TOKEN_DIM,
    UNIT_STATUS,
    WINDOW_SAMPLES,
    NativeSpectralA1,
)


BASELINE_COMMIT = "91997faa1de1616d1eb662cd36edc1547613206d"
POLICY_ID = "RC_HSG_NATIVE_SPECTRAL_A1_V1"
EVIDENCE_SCOPE = "SYNTHETIC_INTERFACE_AND_COMMITTED_METADATA_ONLY_NO_REAL_EEG_VALUES_NO_OUTCOMES"
INPUTS = {
    "a_policy": ("artifacts/backbone_a_policy.yaml", "034a523119f12f648266d94e0499179882fbe181584d10c1af17a3502a797425"),
    "analysis_view": ("artifacts/admission/zuco2_nr_analysis_view_v1.jsonl", "0751259f9f9455cba72bd7d027ffa1423e790e631ac0f5174c38da65d7cd12ff"),
    "split_regime_i": ("artifacts/split_regimeI.json", "e2c065e5b395053cd655670fede8a2b117f6eb9821af884ca31c6fed3842fbab"),
    "data_card": ("artifacts/data_card.yaml", "d9331bfe34937c264b7b8c667a2b831569c4440120e1d445011aeaf419c30f84"),
    "targeted_manifest_v3": ("artifacts/admission/zuco2_nr_targeted_manifest_v3.yaml", "50806a60937b28ae36207509c44d606af6f6b6b1be2a69c06081672f0931bfaf"),
    "requirements_lock": ("requirements-trust-align.lock.txt", "72a2a3274ef9516dba95a4f4022cacfba0e02d10445e1618da2a569f59381910"),
}
OUTPUTS = {
    "contract": "artifacts/backbone_a_contract.yaml",
    "eligibility": "artifacts/a_interface_eligibility_v1.jsonl",
    "report": "reports/a_interface_contract.md",
}
EXPECTED_FIELDS = {
    "subject", "session", "task", "block", "slot", "material_line",
    "occurrence_id", "stimulus_sha256", "raw_shape", "raw_samples",
    "raw_channels", "source_locator",
}
EXPECTED_COUNTS = {
    "train_fit": {"total_rows": 2832, "eligible": 2797, "forced_l0": 35, "full_windows": 29263},
    "inner_val": {"total_rows": 709, "eligible": 700, "forced_l0": 9, "full_windows": 6482},
    "cal": {"total_rows": 1171, "eligible": 1156, "forced_l0": 15, "full_windows": 11558},
    "test": {"total_rows": 1193, "eligible": 1179, "forced_l0": 14, "full_windows": 13219},
    "total": {"total_rows": 5905, "eligible": 5832, "forced_l0": 73, "full_windows": 60522},
}
EXPECTED_RESERVES = {
    "cal_select_reserve": {"eligible": 582, "forced_l0": 9},
    "cal_cert_reserve": {"eligible": 574, "forced_l0": 6},
}


class BuildError(RuntimeError):
    """Fail-closed builder error with a stable code prefix."""


def _fail(code: str, detail: str) -> None:
    raise BuildError(f"{code}: {detail}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_symlink_chain(path: Path, stop: Path, label: str) -> None:
    current = path
    while True:
        if current.exists() and current.is_symlink():
            _fail("PATH_SYMLINK", label)
        if current == stop or current.parent == current:
            return
        current = current.parent


def _input_path(root: Path, relative: str, label: str) -> Path:
    root = root.resolve()
    candidate = root / relative
    _reject_symlink_chain(candidate, root, label)
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        _fail("INPUT_PATH_ESCAPE", label)
    if not resolved.is_file():
        _fail("INPUT_NOT_FILE", label)
    return resolved


def _output_paths(output_root: Path) -> dict[str, Path]:
    unresolved_root = output_root.absolute()
    current = unresolved_root
    while True:
        if current.exists() and current.is_symlink():
            _fail("PATH_SYMLINK", "output_root")
        if current.parent == current:
            break
        current = current.parent
    output_root = unresolved_root.resolve()
    paths: dict[str, Path] = {}
    for label, relative in OUTPUTS.items():
        candidate = output_root / relative
        _reject_symlink_chain(candidate, output_root, label)
        parent = candidate.parent.resolve()
        try:
            parent.relative_to(output_root)
        except ValueError:
            _fail("OUTPUT_PATH_ESCAPE", label)
        paths[label] = parent / candidate.name
    return paths


def _load_yaml(path: Path, label: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        _fail("INPUT_PARSE_ERROR", f"{label}:{type(exc).__name__}")
    if not isinstance(value, dict):
        _fail("INPUT_SCHEMA_MISMATCH", label)
    return value


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail("INPUT_PARSE_ERROR", f"{label}:{type(exc).__name__}")
    if not isinstance(value, dict):
        _fail("INPUT_SCHEMA_MISMATCH", label)
    return value


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                value = json.loads(line)
                if not isinstance(value, dict):
                    _fail("INPUT_SCHEMA_MISMATCH", f"analysis_view:{line_number}")
                rows.append(value)
    except BuildError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail("INPUT_PARSE_ERROR", f"analysis_view:{type(exc).__name__}")
    return rows


def _jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(
        (json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n").encode("utf-8")
        for row in rows
    )


def _yaml_bytes(value: dict[str, Any]) -> bytes:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=False).encode("utf-8")


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
    finally:
        for temporary, _ in pending:
            temporary.unlink(missing_ok=True)


def _validate_fixed_metadata(policy: dict[str, Any], card: dict[str, Any], targeted: dict[str, Any]) -> None:
    selected = policy.get("selected", {})
    if policy.get("policy_id") != POLICY_ID or selected.get("input_channels") != INPUT_CHANNELS:
        _fail("POLICY_MISMATCH", "policy identity or channels")
    if (
        selected.get("sampling_hz") != SAMPLING_HZ
        or selected.get("input_unit") != "RELEASE_NATIVE_AMPLITUDE_UNRESOLVED"
        or selected.get("processed_reference") != PROCESSED_REFERENCE
        or selected.get("window_samples") != WINDOW_SAMPLES
        or selected.get("hop_samples") != HOP_SAMPLES
        or [tuple(item) for item in selected.get("bands_hz", [])] != list(BANDS_HZ)
        or selected.get("token_input_dim") != TOKEN_DIM
        or selected.get("projection_dim") != EMBEDDING_DIM
    ):
        _fail("POLICY_MISMATCH", "selected interface constants")
    signal = card.get("signal", {})
    units = card.get("unit_policy", {})
    if (
        signal.get("channels") != INPUT_CHANNELS
        or signal.get("sampling_hz") != SAMPLING_HZ
        or signal.get("processed_reference") != PROCESSED_REFERENCE
        or units.get("physical_unit_status") != "UNRESOLVED_RELEASE_NATIVE_AMPLITUDE"
        or units.get("unit_inference_performed") is not False
    ):
        _fail("DATA_CARD_MISMATCH", "signal or unit contract")
    physical = targeted.get("physical_schema", {})
    if (
        targeted.get("schema_version") != 3
        or targeted.get("counts", {}).get("rows") != 6282
        or physical.get("sampling_hz_values") != [SAMPLING_HZ]
        or physical.get("processed_reference_values") != [PROCESSED_REFERENCE]
        or physical.get("unit_values") != []
    ):
        _fail("TARGETED_MANIFEST_MISMATCH", "physical metadata")


def _eligibility_rows(view: list[dict[str, Any]], split: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if len(view) != 5905 or split.get("schema_version") != 1 or split.get("test_status") != "LOCKED_UNTIL_ROUTE_LOCK":
        _fail("COUNT_OR_SCHEMA_MISMATCH", "analysis view or split")
    if view != sorted(view, key=lambda row: (row.get("subject"), row.get("slot"), row.get("occurrence_id"))):
        _fail("INPUT_ORDER_MISMATCH", "analysis_view")
    assignments = split.get("row_assignments")
    if not isinstance(assignments, list) or len(assignments) != 5905:
        _fail("SPLIT_SCHEMA_MISMATCH", "row_assignments")
    by_key: dict[tuple[str, int, str], dict[str, Any]] = {}
    for assignment in assignments:
        key = (assignment.get("subject"), assignment.get("slot"), assignment.get("occurrence_id"))
        if key in by_key:
            _fail("SPLIT_KEY_DUPLICATE", repr(key))
        role = assignment.get("role")
        reserve = assignment.get("calibration_reserve")
        if role not in {"train_fit", "inner_val", "cal", "test"}:
            _fail("SPLIT_ROLE_MISMATCH", repr(key))
        if reserve not in {None, "cal_select_reserve", "cal_cert_reserve"} or (role != "cal" and reserve is not None):
            _fail("SPLIT_RESERVE_MISMATCH", repr(key))
        by_key[key] = assignment

    output: list[dict[str, Any]] = []
    role_counts: dict[str, Counter[str]] = {role: Counter() for role in ("train_fit", "inner_val", "cal", "test")}
    reserve_counts: dict[str, Counter[str]] = {name: Counter() for name in EXPECTED_RESERVES}
    seen: set[tuple[str, int, str]] = set()
    for row in view:
        if set(row) != EXPECTED_FIELDS:
            _fail("ANALYSIS_SCHEMA_MISMATCH", repr(sorted(set(row))))
        subject, slot, occurrence_id = row.get("subject"), row.get("slot"), row.get("occurrence_id")
        raw_samples, raw_channels, raw_shape = row.get("raw_samples"), row.get("raw_channels"), row.get("raw_shape")
        key = (subject, slot, occurrence_id)
        if key in seen or key not in by_key:
            _fail("ROW_MAPPING_MISMATCH", repr(key))
        seen.add(key)
        if (
            not isinstance(subject, str) or not isinstance(slot, int) or not isinstance(occurrence_id, str)
            or not isinstance(raw_samples, int) or raw_samples < 1
            or raw_channels != INPUT_CHANNELS or raw_shape != [raw_samples, INPUT_CHANNELS]
        ):
            _fail("ANALYSIS_ROW_MISMATCH", repr(key))
        assignment = by_key[key]
        role, reserve = assignment["role"], assignment["calibration_reserve"]
        if raw_samples < WINDOW_SAMPLES:
            windows, status, action = 0, "A_INTERFACE_SHORT_SEGMENT", "FORCED_L0_NO_FRONTEND"
            role_counts[role]["forced_l0"] += 1
            if reserve is not None:
                reserve_counts[reserve]["forced_l0"] += 1
        else:
            windows = 1 + (raw_samples - WINDOW_SAMPLES) // HOP_SAMPLES
            status, action = "ELIGIBLE", "RUN_FRONTEND"
            role_counts[role]["eligible"] += 1
            if reserve is not None:
                reserve_counts[reserve]["eligible"] += 1
        role_counts[role]["total_rows"] += 1
        role_counts[role]["full_windows"] += windows
        output.append({
            "occurrence_id": occurrence_id,
            "subject": subject,
            "slot": slot,
            "role": role,
            "calibration_reserve": reserve,
            "raw_samples": raw_samples,
            "window_count": windows,
            "a_interface_status": status,
            "action": action,
        })
    if seen != set(by_key):
        _fail("ROW_MAPPING_MISMATCH", "split contains unmatched rows")
    output.sort(key=lambda row: (row["subject"], row["slot"], row["occurrence_id"]))
    actual_roles = {role: dict(role_counts[role]) for role in role_counts}
    total = {name: sum(actual_roles[role].get(name, 0) for role in actual_roles) for name in ("total_rows", "eligible", "forced_l0", "full_windows")}
    actual_counts = {**actual_roles, "total": total}
    actual_reserves = {name: dict(reserve_counts[name]) for name in reserve_counts}
    if actual_counts != EXPECTED_COUNTS:
        _fail("ACCEPTANCE_COUNT_MISMATCH", repr(actual_counts))
    if actual_reserves != EXPECTED_RESERVES:
        _fail("RESERVE_COUNT_MISMATCH", repr(actual_reserves))
    return output, {"by_role": actual_counts, "calibration_reserves": actual_reserves}


def _contract(input_records: dict[str, dict[str, str]], counts: dict[str, Any], code_hash: str) -> dict[str, Any]:
    parameter_count = sum(parameter.numel() for parameter in NativeSpectralA1(0).parameters() if parameter.requires_grad)
    if parameter_count != 1_270_528:
        _fail("PARAMETER_COUNT_MISMATCH", str(parameter_count))
    return {
        "schema_version": 1,
        "artifact": "RC_HSG_NATIVE_SPECTRAL_A1_CONTRACT_V1",
        "policy_id": POLICY_ID,
        "spec_version": "v2.2",
        "baseline_commit": BASELINE_COMMIT,
        "input_artifacts": input_records,
        "input_contract": {
            "tensor": "FLOATING_B_105_T",
            "valid_samples": "INTEGER_B_INCLUSIVE_VALID_PREFIX",
            "channel_order_hash": CHANNEL_ORDER_HASH,
            "sampling_hz": SAMPLING_HZ,
            "unit_status": UNIT_STATUS,
            "processed_reference": PROCESSED_REFERENCE,
            "minimum_valid_samples": WINDOW_SAMPLES,
            "implicit_device_move": False,
        },
        "preprocessing_contract": {
            "scope": "PER_TRIAL_PER_CHANNEL_VALID_SLICE_ONLY",
            "center": "MEDIAN",
            "scale": "MAX_1.4826_MAD_CENTERED_RMS_1E-6",
            "clip": [-20.0, 20.0],
            "computation_dtype": "float32",
        },
        "spectral_contract": {
            "window_samples": WINDOW_SAMPLES,
            "hop_samples": HOP_SAMPLES,
            "window": "SYMMETRIC_HANN_PERIODIC_FALSE",
            "tail": "DROP_NO_PADDING",
            "fft": "RFFT_N500_NORM_BACKWARD",
            "denominator_bins": [1, 75],
            "denominator_interval": "HALF_OPEN",
            "bands_hz_half_open": [list(item) for item in BANDS_HZ],
            "band_bin_counts": [3, 4, 2, 3, 7, 10, 15, 20],
            "feature": "LOG_RELATIVE_BANDPOWER",
            "epsilon": FEATURE_EPSILON,
            "flatten_order": "CHANNEL_MAJOR_THEN_BAND_MAJOR",
            "token_dim": TOKEN_DIM,
        },
        "encoder_contract": {
            "projection": "LINEAR_840_256_BIAS",
            "activation": "GELU_APPROXIMATE_NONE",
            "projection_layer_norm_eps": 1.0e-5,
            "dropout": 0.10,
            "position": "STANDARD_PARAMETER_FREE_SINUSOIDAL",
            "transformer_layers": 2,
            "attention_heads": 4,
            "feedforward_dim": 512,
            "batch_first": True,
            "norm_first": True,
            "final_layer_norm_eps": 1.0e-5,
        },
        "output_contract": {
            "window_embeddings": "FLOAT_B_WMAX_256_MASKED_POSITIONS_ZERO",
            "window_mask": "BOOL_B_WMAX_TRUE_FOR_FULL_WINDOWS",
            "pooled_embedding": "FLOAT_B_256_ARITHMETIC_MASKED_MEAN",
        },
        "initialization_contract": {
            "constructor": "NativeSpectralA1(init_seed: int)",
            "device_at_construction": "CPU",
            "caller_rng_pollution": False,
            "matrix_weights": "XAVIER_UNIFORM_GAIN_1",
            "bias": "ZERO",
            "layer_norm_weight": "ONE",
            "layer_norm_bias": "ZERO",
            "main_experiment_seed_selected": False,
        },
        "eligibility_contract": {
            "population_rows": 5905,
            "short_threshold_samples": WINDOW_SAMPLES,
            "eligible_action": "RUN_FRONTEND",
            "short_status": "A_INTERFACE_SHORT_SEGMENT",
            "short_action": "FORCED_L0_NO_FRONTEND",
            "short_rows_remain_in_population": True,
            "padding_or_imputation": False,
        },
        "acceptance_counts": counts,
        "implementation": {
            "code_path": "src/rc_hsg/backbones/native_spectral_a1.py",
            "code_sha256": code_hash,
            "python_version": platform.python_version(),
            "torch_version": str(torch.__version__),
            "numpy_version": str(numpy.__version__),
            "trainable_parameter_count": parameter_count,
            "real_eeg_validated": False,
        },
        "prohibited_features": ["raw_samples", "window_count", "a_interface_status", "padding_amount"],
        "prohibited_actions": [
            "AUTO_TRANSPOSE", "PADDING", "IMPUTATION", "RESAMPLING", "UNIT_CONVERSION",
            "CHANNEL_INTERPOLATION", "EXTERNAL_CODE_OR_WEIGHT_IMPORT", "SHORT_ROW_REMOVAL",
        ],
        "evidence_scope": EVIDENCE_SCOPE,
    }


def _report_bytes(contract: dict[str, Any], eligibility_hash: str) -> bytes:
    counts = contract["acceptance_counts"]["by_role"]
    lines = [
        "# RC-HSG Native Spectral A1 Interface Contract", "",
        "## Scope", "",
        "The frozen clean-room A interface is implemented and synthetic-tested. Real EEG traversal, physical-data frontend admission, representation quality, training, performance, reference feasibility, and Gate evidence remain unvalidated.", "",
        "## Frozen interface", "",
        "- Input: floating `[B,105,T]`, explicit valid lengths, 500 Hz, common-average, release-native unresolved amplitude.",
        "- Tokenizer: per-trial/channel robust normalization; 500/250 symmetric-Hann full windows; eight fixed log-relative-bandpower bands.",
        "- Encoder: 840-to-256 projection and two pre-norm Transformer layers; 1,270,528 trainable parameters.",
        "- Short segments: no frontend call, padding, imputation, or removal; forced L0 while retained in the paired population.", "",
        "## Eligibility overlay", "",
        "| role | rows | eligible | forced L0 | full windows |",
        "|---|---:|---:|---:|---:|",
        *[
            f"| {role} | {counts[role]['total_rows']} | {counts[role]['eligible']} | {counts[role]['forced_l0']} | {counts[role]['full_windows']} |"
            for role in ("train_fit", "inner_val", "cal", "test", "total")
        ], "",
        f"Eligibility JSONL SHA256: `{eligibility_hash}`.", "",
        "## Evidence boundary", "",
        f"`{EVIDENCE_SCOPE}`", "",
        "No real EEG value, semantic/calibration/test outcome, prediction, metric, historical model result, external implementation, checkpoint, or downloaded weight was read or used.", "",
    ]
    return "\n".join(lines).encode("utf-8")


def build(*, project_root: Path = PROJECT_ROOT, output_root: Path | None = None) -> dict[str, str]:
    project_root = project_root.resolve()
    output_root = project_root if output_root is None else output_root
    paths = {label: _input_path(project_root, relative, label) for label, (relative, _) in INPUTS.items()}
    hashes = {label: _sha256(path) for label, path in paths.items()}
    for label, (_, expected) in INPUTS.items():
        if hashes[label] != expected:
            _fail("INPUT_HASH_MISMATCH", label)
    policy = _load_yaml(paths["a_policy"], "a_policy")
    card = _load_yaml(paths["data_card"], "data_card")
    targeted = _load_yaml(paths["targeted_manifest_v3"], "targeted_manifest_v3")
    split = _load_json(paths["split_regime_i"], "split_regime_i")
    view = _load_jsonl(paths["analysis_view"])
    _validate_fixed_metadata(policy, card, targeted)
    rows, counts = _eligibility_rows(view, split)

    code_path = _input_path(project_root, "src/rc_hsg/backbones/native_spectral_a1.py", "implementation")
    input_records = {
        label: {"path": INPUTS[label][0], "sha256": hashes[label]}
        for label in INPUTS
    }
    eligibility_content = _jsonl_bytes(rows)
    contract = _contract(input_records, counts, _sha256(code_path))
    contract_content = _yaml_bytes(contract)
    report_content = _report_bytes(contract, hashlib.sha256(eligibility_content).hexdigest())
    destinations = _output_paths(output_root)
    _atomic_write({
        destinations["contract"]: contract_content,
        destinations["eligibility"]: eligibility_content,
        destinations["report"]: report_content,
    })
    return {label: _sha256(path) for label, path in destinations.items()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args(argv)
    try:
        hashes = build(output_root=args.output_root)
    except BuildError as exc:
        print(exc, file=sys.stderr)
        return 1
    for label, digest in hashes.items():
        print(f"{label}={digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
