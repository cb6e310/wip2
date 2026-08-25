#!/usr/bin/env python3
"""Execute the cumulative RC-HSG v2.9.3 outcome-blind Gate R0 audit."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import resource
import struct
import sys
import tempfile
import time
import warnings
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import torch
import yaml
from scipy.stats import ks_2samp
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    roc_auc_score,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from rc_hsg.references.n1_joint_permutation import N1JointPermutationSampler  # noqa: E402
from rc_hsg.references.n2_common_phase import N2CommonPhaseSampler  # noqa: E402


BASELINE_COMMIT = "4fa6fadc8bdee0d163acc8bf9ee48aeac4d3095d"
POLICY_ID = "RC_HSG_GATE_R0_REFERENCE_INTEGRITY_V1"
DATASET_ROOT = Path("/home/song/projects/trust_align/01_data_protocol/datasets/zuco_2.0")
REPLICATES = (1, 2, 199)
NUMERICAL_THRESHOLD = 1.0e-6
CLASSIFIER_THRESHOLD = 0.65
NUISANCE_THRESHOLD = 0.05
AMPLITUDE_KS_THRESHOLD = 0.15
QUANTILE_SHIFT_THRESHOLD = 0.25
ENDPOINT_RATIO_MIN = 0.5
ENDPOINT_RATIO_MAX = 2.0
PAIR_PANEL = ((0, 1), (0, 52), (0, 104), (1, 2), (26, 78), (52, 104), (103, 104))
MATCHED_PANEL_PREFIX = b"RC_HSG_GATE_R0_MATCHED_PANEL_V1\0"
BOOTSTRAP_DOMAIN = b"NC_HSG_GATE_A_POPULATION_V1\0SUBJECT_BOOTSTRAP\0"
BOOTSTRAP_SHA256 = "e77ca92b29c414a17c1e66edf4075edd470c007dfe2019487c36758f5f99c86d"
SUPPORT_SHA256 = "3f2eb411e54c730453d1dd8a39c5bfeff0aa34ee278c545ac66d2f24b2af2246"
PANEL_SHA256 = "2cffa7699e7a29eee4996172a20707678ba1ec3529d35e32b2ca453ad79aa806"
SUBJECTS = (
    "YAC", "YAG", "YAK", "YDG", "YDR", "YFR", "YFS", "YHS", "YIS",
    "YLS", "YMD", "YMS", "YRH", "YRK", "YRP", "YSD", "YSL", "YTL",
)
EXPECTED = {
    "outer_rows": 3541,
    "eligible_rows": 3497,
    "short_rows": 44,
    "power_pass_rows": 3493,
    "insufficient_train_cell_rows": 4,
    "train_fit": 2797,
    "inner_val": 700,
    "subjects": 18,
    "source_files": 18,
    "minimum_samples": 513,
    "maximum_samples": 18436,
    "theoretical_role_cells": 216,
    "nonempty_role_cells": 192,
    "missing_role_cells": 24,
    "theoretical_nuisance_strata": 108,
    "matched_support": 88,
    "train_only": 16,
    "inner_only": 0,
    "absent_both": 4,
    "panel_rows": 176,
    "panel_train_fit": 88,
    "panel_inner_val": 88,
}
FIXED_INPUTS = {
    "spec_v28": ("guide/RC_HSG_Paper_Spec_v2_8_2026-08-24.md", "f718fc37875a6dac7c539260de054d9f9c52966905b1912cf193d573a0424f23"),
    "review_v28": ("artifacts/spec_review/rc_hsg_v28_n2_common_phase_sampler_review.md", "66edb1aca13e01f87d1a162b86254bbad87ce207ae208474f46a326e53948ea7"),
    "run019": ("runs/2026-08-24_019_n2_common_phase_sampler.md", "764778bae4f873e66e806beced6c0c7c336c750b7c30b6a510c3e6fe02526996"),
    "n2_module": ("src/rc_hsg/references/n2_common_phase.py", "65fc0c3215a2b289c498e989795db74002642388ca64caa2fea93d7780a5aa7e"),
    "n2_builder": ("scripts/build_n2_sampler_contract.py", "baebfa04bf2381075786d9375e78a741ded32f157ea21da37885bc4001530252"),
    "n2_contract": ("artifacts/nulls/n2_contract.yaml", "c2713dc4fbe989c1680e02e88c336541482bfcb9e828170b3a225d2466d1377d"),
    "n2_report": ("reports/n2_selfcheck.md", "042fc06f0627d4b29ead30075bb003800b0305ceb7d67387bc3f3e9d2f15f13c"),
    "eligibility": ("artifacts/a_interface_eligibility_v1.jsonl", "8eded8fb2786747e96b8388d4d91315e39db9f8a9eb25ea69056d219e1e8e1ad"),
    "admission": ("artifacts/a1_outer_train_admission_v1.jsonl", "b3c1b4e11855ef4c51c5bd0c2c0009f8a24e390c511d97118c48082fc7febfd5"),
    "admission_freeze": ("artifacts/a1_outer_train_admission_freeze.yaml", "e973fbbe841a47f027cbf0f8a8ad65e66d106d675e8ed838dd0daf4a08dcab12"),
    "n1_assignment": ("artifacts/nulls/n1_block_assignment_v1.jsonl", "d0acc5e5fe78bc36a69cb04b6f605983c675e49a764538ae1665f86a28acee04"),
    "n1_feasibility": ("artifacts/nulls/n1_block_feasibility.yaml", "90a6178100f507299e12223d15291699aad84e4b58bb52e29843dbf99ee6f771"),
    "n1_contract": ("artifacts/nulls/n1_contract.yaml", "4fee63f743936db06eea41164f85f67228785872d3fca2098e657b1dc0383729"),
    "n1_manifest": ("artifacts/nulls/n1_permutation_manifest_v1.jsonl", "b7e68368799be446af60dcec029458e4e769f6605c1c56c032b76fb069f38c06"),
    "split": ("artifacts/split_regimeI.json", "e2c065e5b395053cd655670fede8a2b117f6eb9821af884ca31c6fed3842fbab"),
    "population": ("artifacts/gate_a_population.yaml", "279e3edf1c41971b6967f74657ec531533977d90ea4dc3d48a5efd63dd295d60"),
    "a1_code": ("src/rc_hsg/backbones/native_spectral_a1.py", "71ae12d65cc0acc6fd5870434e141ee7d849eb8befa718a84fb99cb86ed533d9"),
    "reader": ("scripts/validate_a1_frontend.py", "ecc84a0363629e919409321cdc73327b6e3c7e779e224a18ab55a6b6ac6777cd"),
    "requirements": ("requirements-trust-align.lock.txt", "72a2a3274ef9516dba95a4f4022cacfba0e02d10445e1618da2a569f59381910"),
}
CONTROL_INPUTS = {
    "analysis": ("artifacts/admission/zuco2_nr_analysis_view_v1.jsonl", "0751259f9f9455cba72bd7d027ffa1423e790e631ac0f5174c38da65d7cd12ff"),
    "targeted": ("artifacts/admission/zuco2_nr_targeted_manifest_v3.yaml", "50806a60937b28ae36207509c44d606af6f6b6b1be2a69c06081672f0931bfaf"),
    "osf": ("artifacts/admission/zuco2_osf_file_metadata.yaml", "85a8c89eeb7a523c06fb7f38aa1c371e042413087e66dcc338c16833bd8bb721"),
    "spec_v29": ("guide/RC_HSG_Paper_Spec_v2_9_2026-08-24.md", "0c9498b440ddc883a490a3d5d8fa1f39d3fc49d9e1d593d07ea63d24b23fc1fd"),
    "review_v29": ("artifacts/spec_review/rc_hsg_v29_gate_r0_review.md", "31b8d6cfe8f8d0ea96f3c201217710f48fe83a4d4651376aef762a20d5cfdf51"),
    "addendum_v291": ("guide/RC_HSG_Paper_Spec_v2_9_1_GATE_R0_PANEL_ADDENDUM_2026-08-24.md", "f33911ec40030f212969b63b90218d6fcb1dc30e7edc83148d67df28fee3c603"),
    "review_v291": ("artifacts/spec_review/rc_hsg_v291_gate_r0_panel_conflict_resolution.md", "50393d3b4b7c8cd59ce674072f1bdfd3b506847284fe200f22214567ee2f8a93"),
    "active_spec_v291": ("guide/RC_HSG_Paper_Spec_v2_9_1_2026-08-24.md", "d37692f7ed64c33d53534b5ccdfefa600775c4e66874523a00254242d3205f40"),
    "addendum_v292": ("guide/RC_HSG_Paper_Spec_v2_9_2_MODEL_WARNING_ADDENDUM_2026-08-24.md", "49481783458da3a4d0020a914eed54559fb7e1006f8a4132014f9b5a166eff0c"),
    "review_v292": ("artifacts/spec_review/rc_hsg_v292_model_warning_conflict_resolution.md", "d60980875ad80652f8e55a6ea1935b737286f88089d4324af3b0b51c6e189b5a"),
    "active_spec_v292": ("guide/RC_HSG_Paper_Spec_v2_9_2_2026-08-24.md", "4a5138bcfe8199d7ab5c9cd90d6a2669c987b624953c63a419df41730858225c"),
    "addendum_v293": ("guide/RC_HSG_Paper_Spec_v2_9_3_FIT_CLASS_DOMAIN_ADDENDUM_2026-08-24.md", "48e5d7f5eeb2b705f125bc9e954c6ab644533a19f560de45cd9101c2f3113846"),
    "review_v293": ("artifacts/spec_review/rc_hsg_v293_fit_class_domain_conflict_resolution.md", "70b331a9ad125404dad74609cdab132a76f5e29ba01a14038c0546346c174c12"),
    "active_spec_v293": ("guide/RC_HSG_Paper_Spec_v2_9_3_2026-08-24.md", "8650a71144af074ecf6b0ca1e3c92dcc76a9283891c991de0672edfd124f3745"),
}
OUTPUTS = {
    "correction": "artifacts/governance/run019_postcommit_correction.yaml",
    "model_certificate": "artifacts/gates/gate_r0_logistic_api_equivalence_v1.yaml",
    "support": "artifacts/gates/gate_r0_matched_support_v1.jsonl",
    "panel": "artifacts/gates/gate_r0_panel_v1.jsonl",
    "coverage": "artifacts/gates/gate_r0_n2_coverage_v1.jsonl",
    "gate": "artifacts/gates/gate_r0.yaml",
    "report": "reports/gate_r0.md",
}

MODEL_PARAMETERS = {
    "l1_ratio": 0.0,
    "C": 1.0,
    "solver": "lbfgs",
    "tol": 1.0e-8,
    "max_iter": 2000,
    "fit_intercept": True,
    "class_weight": None,
    "warm_start": False,
}
FIT_DOMAINS = {
    "reference_detector": ("N2", "real"),
    "nuisance_subject": SUBJECTS,
    "nuisance_length": ("W01_04", "W05_16", "W17_PLUS"),
    "nuisance_power": ("P_HIGH", "P_LOW"),
}


class GateR0TechnicalAbort(RuntimeError):
    """Fail-closed technical abort with no scientific outcome."""


def _fail(code: str, detail: str) -> None:
    raise GateR0TechnicalAbort(f"{code}: {detail}")


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
            _fail("GATE_R0_PATH_MISMATCH", f"symlink:{label}")
        if current == stop or current.parent == current:
            return
        current = current.parent


def _safe_input(root: Path, relative: str, label: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts or rel.suffix.lower() in {".mat", ".h5", ".hdf5"}:
        _fail("GATE_R0_INPUT_MISMATCH", f"unsafe:{label}")
    unresolved = root.absolute()
    _reject_symlink_chain(unresolved, Path(unresolved.anchor), "project-root")
    candidate = unresolved / rel
    _reject_symlink_chain(candidate, unresolved, label)
    resolved_root = unresolved.resolve()
    resolved = candidate.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError:
        _fail("GATE_R0_INPUT_MISMATCH", f"escape:{label}")
    if not resolved.is_file():
        _fail("GATE_R0_INPUT_MISMATCH", f"missing:{label}")
    return resolved


def _verify_inputs(project_root: Path, enforce: bool) -> tuple[dict[str, Path], dict[str, str]]:
    expected = {**FIXED_INPUTS, **CONTROL_INPUTS}
    paths = {label: _safe_input(project_root, item[0], label) for label, item in expected.items()}
    hashes = {label: _sha256(path) for label, path in paths.items()}
    if enforce:
        for label, (_, digest) in expected.items():
            if hashes[label] != digest:
                _fail("GATE_R0_INPUT_MISMATCH", f"hash:{label}")
        versions = {
            "numpy": np.__version__,
            "scipy": __import__("scipy").__version__,
            "scikit-learn": __import__("sklearn").__version__,
            "torch": str(torch.__version__).split("+")[0],
        }
        required = {"numpy": "2.5.2", "scipy": "1.18.0", "scikit-learn": "1.9.0", "torch": "2.13.0"}
        if versions != required:
            _fail("GATE_R0_MODEL_MISMATCH", repr(versions))
        lock = paths["requirements"].read_text(encoding="utf-8").splitlines()
        if any(f"{name}=={version}" not in lock for name, version in required.items()):
            _fail("GATE_R0_INPUT_MISMATCH", "requirements-versions")
    return paths, hashes


def _load_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            value = json.loads(line)
            if not isinstance(value, dict):
                _fail("GATE_R0_INPUT_MISMATCH", f"schema:{label}:{number}")
            rows.append(value)
    except GateR0TechnicalAbort:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail("GATE_R0_INPUT_MISMATCH", f"jsonl:{label}:{type(exc).__name__}")
    return rows


def _load_yaml(path: Path, label: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        _fail("GATE_R0_INPUT_MISMATCH", f"yaml:{label}:{type(exc).__name__}")
    if not isinstance(value, dict):
        _fail("GATE_R0_INPUT_MISMATCH", f"schema:{label}")
    return value


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail("GATE_R0_INPUT_MISMATCH", f"json:{label}:{type(exc).__name__}")
    if not isinstance(value, dict):
        _fail("GATE_R0_INPUT_MISMATCH", f"schema:{label}")
    return value


def _load_reader(path: Path) -> Any:
    name = "rc_hsg_run020_frozen_reader"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        _fail("GATE_R0_READER_MISMATCH", "import-spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        _fail("GATE_R0_READER_MISMATCH", f"import:{type(exc).__name__}")
    required = {"_dataset_files", "_read_raw", "_row_key", "METADATA", "PRODUCTION_DATASET_ROOT", "NativeSpectralA1"}
    if any(not hasattr(module, name) for name in required):
        _fail("GATE_R0_READER_MISMATCH", "api")
    return module


def _key(row: dict[str, Any]) -> tuple[str, int, str]:
    result = (row.get("subject"), row.get("slot"), row.get("occurrence_id"))
    if not isinstance(result[0], str) or not isinstance(result[1], int) or not isinstance(result[2], str):
        _fail("GATE_R0_SCOPE_MISMATCH", "row-key")
    return result


def _row_key(row: dict[str, Any]) -> str:
    key = f"{row['subject']}\t{row['slot']:06d}\t{row['occurrence_id']}"
    try:
        key.encode("ascii")
    except UnicodeEncodeError:
        _fail("GATE_R0_SCOPE_MISMATCH", "row-key-ascii")
    return key


def _unique(rows: Iterable[dict[str, Any]], label: str) -> dict[tuple[str, int, str], dict[str, Any]]:
    result: dict[tuple[str, int, str], dict[str, Any]] = {}
    for row in rows:
        key = _key(row)
        if key in result:
            _fail("GATE_R0_SCOPE_MISMATCH", f"duplicate:{label}")
        result[key] = row
    return result


def _metadata_preflight(paths: dict[str, Path], enforce: bool) -> dict[str, Any]:
    admission = _load_jsonl(paths["admission"], "admission")
    eligibility = _load_jsonl(paths["eligibility"], "eligibility")
    analysis = _load_jsonl(paths["analysis"], "analysis")
    assignments = _load_jsonl(paths["n1_assignment"], "n1-assignment")
    split = _load_json(paths["split"], "split")
    population = _load_yaml(paths["population"], "population")
    by_admission = _unique(admission, "admission")
    by_eligibility = _unique(eligibility, "eligibility")
    by_analysis = _unique(analysis, "analysis")
    by_assignment = _unique(assignments, "assignment")
    if split.get("test_status") != "LOCKED_UNTIL_ROUTE_LOCK":
        _fail("GATE_R0_SCOPE_MISMATCH", "test-lock")
    if set(by_admission) != set(by_assignment) or not set(by_admission).issubset(by_eligibility):
        _fail("GATE_R0_SCOPE_MISMATCH", "ledger-keys")
    if set(by_eligibility) != set(by_analysis):
        _fail("GATE_R0_SCOPE_MISMATCH", "analysis-keys")
    subject_order = population.get("paired_subject_bootstrap", {}).get("subject_order")
    if tuple(subject_order or ()) != SUBJECTS:
        _fail("GATE_R0_SCOPE_MISMATCH", "subject-order")

    eligible: list[dict[str, Any]] = []
    short: list[dict[str, Any]] = []
    for key, admitted in by_admission.items():
        eligibility_row = by_eligibility[key]
        analysis_row = by_analysis[key]
        assignment = by_assignment[key]
        locator = analysis_row.get("source_locator")
        common = (
            admitted.get("role") in {"train_fit", "inner_val"}
            and eligibility_row.get("role") == admitted.get("role")
            and assignment.get("role") == admitted.get("role")
            and analysis_row.get("session") == assignment.get("session") == 1
            and analysis_row.get("task") == "NR"
            and isinstance(locator, dict)
            and locator.get("field") == admitted.get("source_field") == "rawData"
            and locator.get("slot") == admitted.get("slot")
            and locator.get("summary_file") == admitted.get("source_file") == assignment.get("source_file")
            and analysis_row.get("raw_samples") == admitted.get("raw_samples") == assignment.get("raw_samples")
        )
        if not common:
            _fail("GATE_R0_SCOPE_MISMATCH", f"join:{key!r}")
        row = {
            "subject": admitted["subject"], "session": 1, "slot": admitted["slot"],
            "occurrence_id": admitted["occurrence_id"], "role": admitted["role"],
            "raw_samples": admitted["raw_samples"], "window_count": admitted["window_count"],
            "a_interface_status": admitted["a_interface_status"], "action": admitted["action"],
            "source_file": admitted["source_file"], "source_field": "rawData",
            "length_bin": assignment.get("length_bin"), "power_bin": assignment.get("power_bin"),
            "power_edge_status": assignment.get("power_edge_status"),
            "source_dataset_read": admitted.get("a_interface_status") == "ELIGIBLE",
        }
        if row["source_dataset_read"]:
            if (
                row["action"] != "RUN_FRONTEND"
                or admitted.get("source_dataset_read_cumulative") is not True
                or admitted.get("frontend_status") != "PASS"
                or admitted.get("input_finite_status") != "PASS"
                or admitted.get("window_mask_status") != "PASS"
                or admitted.get("output_finite_status") != "PASS"
                or admitted.get("observed_window_count") != row["window_count"]
                or analysis_row.get("raw_shape") != [row["raw_samples"], 105]
                or row["length_bin"] not in {"W01_04", "W05_16", "W17_PLUS"}
                or row["power_edge_status"] not in {"PASS", "INSUFFICIENT_TRAIN_CELL"}
            ):
                _fail("GATE_R0_SCOPE_MISMATCH", f"eligible:{key!r}")
            eligible.append(row)
        else:
            if row["a_interface_status"] != "A_INTERFACE_SHORT_SEGMENT" or row["action"] != "FORCED_L0_NO_FRONTEND":
                _fail("GATE_R0_SCOPE_MISMATCH", f"short:{key!r}")
            short.append(row)

    eligible.sort(key=lambda row: (row["source_file"].encode("ascii"), row["slot"], row["subject"].encode("ascii"), row["occurrence_id"].encode("ascii")))
    short.sort(key=_row_key)
    actual = {
        "outer_rows": len(admission), "eligible_rows": len(eligible), "short_rows": len(short),
        "power_pass_rows": sum(row["power_edge_status"] == "PASS" for row in eligible),
        "insufficient_train_cell_rows": sum(row["power_edge_status"] == "INSUFFICIENT_TRAIN_CELL" for row in eligible),
        "train_fit": sum(row["role"] == "train_fit" for row in eligible),
        "inner_val": sum(row["role"] == "inner_val" for row in eligible),
        "subjects": len({row["subject"] for row in eligible}),
        "source_files": len({row["source_file"] for row in eligible}),
        "minimum_samples": min(row["raw_samples"] for row in eligible),
        "maximum_samples": max(row["raw_samples"] for row in eligible),
    }
    if enforce and actual != {key: EXPECTED[key] for key in actual}:
        _fail("GATE_R0_SCOPE_MISMATCH", f"counts:{actual!r}")
    if tuple(sorted({row["subject"] for row in eligible})) != SUBJECTS:
        _fail("GATE_R0_SCOPE_MISMATCH", "subjects")
    support, panel, support_bytes, panel_bytes, panel_counts = _build_support_panel(eligible)
    actual.update(panel_counts)
    if enforce:
        for label in (
            "theoretical_role_cells", "nonempty_role_cells", "missing_role_cells",
            "theoretical_nuisance_strata", "matched_support", "train_only", "inner_only",
            "absent_both", "panel_rows", "panel_train_fit", "panel_inner_val",
        ):
            if actual[label] != EXPECTED[label]:
                _fail("GATE_R0_SCOPE_MISMATCH", f"{label}:{actual[label]}")
        if hashlib.sha256(support_bytes).hexdigest() != SUPPORT_SHA256:
            _fail("GATE_R0_SCOPE_MISMATCH", "support-hash")
        if hashlib.sha256(panel_bytes).hexdigest() != PANEL_SHA256:
            _fail("GATE_R0_SCOPE_MISMATCH", "panel-hash")
    return {
        "eligible": eligible, "short": short, "eligible_keys": {_key(row) for row in eligible},
        "panel_keys": {_key(row) for row in panel}, "panel_rows": panel,
        "support_rows": support, "support_bytes": support_bytes, "panel_bytes": panel_bytes,
        "actual": actual,
    }


def _build_support_panel(
    eligible: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], bytes, bytes, dict[str, int]]:
    role_cells: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in eligible:
        if row["power_edge_status"] == "PASS":
            role_cells[(row["subject"], row["role"], row["length_bin"], row["power_bin"])].append(row)
    lengths = ("W01_04", "W05_16", "W17_PLUS")
    powers = ("P_LOW", "P_HIGH")
    roles = ("train_fit", "inner_val")
    support: list[dict[str, Any]] = []
    panel: list[dict[str, Any]] = []
    for subject in SUBJECTS:
        for length_bin in lengths:
            for power_bin in powers:
                candidates = {
                    role: role_cells.get((subject, role, length_bin, power_bin), [])
                    for role in roles
                }
                train_n, inner_n = (len(candidates[role]) for role in roles)
                if train_n and inner_n:
                    status = "MATCHED_SUPPORT"
                elif train_n:
                    status = "TRAIN_ONLY"
                elif inner_n:
                    status = "INNER_ONLY"
                else:
                    status = "ABSENT_BOTH"
                support.append({
                    "subject": subject, "length_bin": length_bin, "power_bin": power_bin,
                    "train_fit_n": train_n, "inner_val_n": inner_n, "support_status": status,
                })
                if status != "MATCHED_SUPPORT":
                    continue
                for role in roles:
                    ranked: list[tuple[str, int, str, dict[str, Any]]] = []
                    for row in candidates[role]:
                        canonical = {
                            "subject": row["subject"], "role": row["role"],
                            "length_bin": row["length_bin"], "power_bin": row["power_bin"],
                            "slot": row["slot"], "occurrence_id": row["occurrence_id"],
                        }
                        encoded = json.dumps(
                            canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
                        ).encode("utf-8")
                        selection = hashlib.sha256(MATCHED_PANEL_PREFIX + encoded).hexdigest()
                        ranked.append((selection, row["slot"], row["occurrence_id"], row))
                    selection, _, _, row = min(ranked)
                    panel.append({
                        "subject": row["subject"], "session": row["session"], "role": row["role"],
                        "length_bin": row["length_bin"], "power_bin": row["power_bin"],
                        "slot": row["slot"], "occurrence_id": row["occurrence_id"],
                        "raw_samples": row["raw_samples"], "window_count": row["window_count"],
                        "source_file": row["source_file"], "source_field": row["source_field"],
                        "selection_sha256": selection,
                    })
    panel.sort(key=lambda row: (
        row["subject"], lengths.index(row["length_bin"]), powers.index(row["power_bin"]),
        roles.index(row["role"]), row["slot"], row["occurrence_id"],
    ))
    if len({_key(row) for row in panel}) != len(panel):
        _fail("GATE_R0_SCOPE_MISMATCH", "panel-unique")
    status_counts = Counter(row["support_status"] for row in support)
    role_counts = Counter(row["role"] for row in panel)
    expected_subject_counts = {
        "YAC": 10, "YAG": 12, "YAK": 8, "YDG": 10, "YDR": 10, "YFR": 10,
        "YFS": 10, "YHS": 8, "YIS": 10, "YLS": 12, "YMD": 6, "YMS": 12,
        "YRH": 10, "YRK": 10, "YRP": 10, "YSD": 10, "YSL": 10, "YTL": 8,
    }
    if dict(sorted(Counter(row["subject"] for row in panel).items())) != expected_subject_counts:
        _fail("GATE_R0_SCOPE_MISMATCH", "panel-subject-counts")
    support_bytes = _jsonl_bytes(support)
    panel_bytes = _jsonl_bytes(panel)
    counts = {
        "theoretical_role_cells": 216,
        "nonempty_role_cells": len(role_cells),
        "missing_role_cells": 216 - len(role_cells),
        "theoretical_nuisance_strata": len(support),
        "matched_support": status_counts["MATCHED_SUPPORT"],
        "train_only": status_counts["TRAIN_ONLY"],
        "inner_only": status_counts["INNER_ONLY"],
        "absent_both": status_counts["ABSENT_BOTH"],
        "panel_rows": len(panel),
        "panel_train_fit": role_counts["train_fit"],
        "panel_inner_val": role_counts["inner_val"],
    }
    return support, panel, support_bytes, panel_bytes, counts


def _bootstrap_indices() -> np.ndarray:
    limit = ((1 << 64) // 18) * 18
    output = bytearray()
    for replicate in range(10_000):
        for draw in range(18):
            retry = 0
            while True:
                digest = hashlib.sha256(BOOTSTRAP_DOMAIN + struct.pack(">IHH", replicate, draw, retry)).digest()
                value = int.from_bytes(digest[:8], "big")
                if value < limit:
                    output.append(value % 18)
                    break
                retry += 1
                if retry > 0xFFFF:
                    _fail("GATE_R0_BOOTSTRAP_MISMATCH", "retry")
    if hashlib.sha256(output).hexdigest() != BOOTSTRAP_SHA256:
        _fail("GATE_R0_BOOTSTRAP_MISMATCH", "hash")
    return np.frombuffer(bytes(output), dtype=np.uint8).reshape(10_000, 18)


class _TokenizerOnly:
    def __init__(self) -> None:
        self.hann_window = torch.hann_window(500, periodic=False, dtype=torch.float32)


def _audit_vector(
    reader: Any, tokenizer: _TokenizerOnly, values: torch.Tensor, expected_windows: int,
) -> np.ndarray:
    if values.device.type != "cpu" or values.dtype != torch.float32 or values.ndim != 2 or values.shape[0] != 105 or not values.is_contiguous():
        _fail("GATE_R0_FEATURE_MISMATCH", "input")
    with torch.inference_mode():
        tokens = reader.NativeSpectralA1._spectral_tokens(tokenizer, values, int(values.shape[1]))
    if tokens.shape != (expected_windows, 840) or not bool(torch.isfinite(tokens).all()):
        _fail("GATE_R0_FEATURE_MISMATCH", "tokens")
    token64 = tokens.numpy().astype(np.float64, copy=False)
    token_features = np.concatenate((token64.mean(axis=0), token64.std(axis=0, ddof=0)))
    signal = values.numpy().astype(np.float64, copy=False)
    centered = signal - np.median(signal, axis=1, keepdims=True)
    mad = np.median(np.abs(centered), axis=1, keepdims=True)
    rms = np.sqrt(np.mean(centered * centered, axis=1, keepdims=True))
    scale = np.maximum(np.maximum(1.4826 * mad, rms), 1.0e-6)
    normalized = np.clip(centered / scale, -20.0, 20.0)
    quantiles = np.asarray((0.01, 0.10, 0.25, 0.50, 0.75, 0.90, 0.99), dtype=np.float64)
    amplitude = np.quantile(normalized, quantiles, axis=1).T.reshape(-1)
    jump = np.abs(normalized[:, 0] - normalized[:, -1])
    differences = np.diff(normalized, axis=1)
    slip = np.abs(differences[:, 0] - differences[:, -1])
    endpoints = np.concatenate((np.quantile(jump, quantiles), np.quantile(slip, quantiles)))
    result = np.concatenate((token_features, amplitude, endpoints)).astype(np.float64, copy=False)
    del tokens, token64, signal, centered, mad, rms, scale, normalized, differences
    if result.shape != (2429,) or not np.isfinite(result).all():
        _fail("GATE_R0_FEATURE_MISMATCH", f"vector:{result.shape}")
    return result


def _relative_norm(actual: np.ndarray, expected: np.ndarray, floor: float = 1.0e-12) -> float:
    return float(np.linalg.norm(actual - expected) / max(float(np.linalg.norm(expected)), floor))


def _numerical_metrics(original: torch.Tensor, surrogate: torch.Tensor) -> dict[str, float]:
    x = original.numpy().astype(np.float64, copy=False)
    y = surrogate.numpy().astype(np.float64, copy=False)
    xf = np.fft.rfft(x, axis=-1, norm="backward")
    yf = np.fft.rfft(y, axis=-1, norm="backward")
    mean_denominator = max(float(np.linalg.norm(x.mean(axis=-1))), float(np.sqrt(np.mean(x * x))), 1.0e-12)
    original_cross = np.asarray([np.conj(xf[left]) * xf[right] for left, right in PAIR_PANEL])
    output_cross = np.asarray([np.conj(yf[left]) * yf[right] for left, right in PAIR_PANEL])
    result = {
        "psd_relative_norm": _relative_norm(np.abs(yf) ** 2, np.abs(xf) ** 2),
        "covariance_relative_norm": _relative_norm(np.cov(y), np.cov(x)),
        "mean_relative_norm": float(np.linalg.norm(y.mean(axis=-1) - x.mean(axis=-1)) / mean_denominator),
        "cross_spectrum_relative_norm": _relative_norm(output_cross, original_cross),
    }
    if not all(np.isfinite(value) for value in result.values()):
        _fail("GATE_R0_NUMERICAL_MISMATCH", "nonfinite")
    return result


def _endpoint_diagnostics(values: np.ndarray) -> tuple[float, float]:
    centered = values - values.mean(axis=-1, keepdims=True)
    jump = float(np.sum((values[:, 0] - values[:, -1]) ** 2) / max(float(np.sum(centered * centered)), 1.0e-12))
    differences = np.diff(values, axis=-1)
    slip = float(np.sum((differences[:, 0] - differences[:, -1]) ** 2) / max(float(np.sum(differences * differences)), 1.0e-12))
    return jump, slip


def _amplitude_metrics(original: torch.Tensor, surrogate: torch.Tensor) -> dict[str, float]:
    x = original.numpy().astype(np.float64, copy=False)
    y = surrogate.numpy().astype(np.float64, copy=False)
    ks = np.asarray(ks_2samp(x, y, axis=1, method="asymp").statistic, dtype=np.float64)
    quantiles = (0.01, 0.10, 0.25, 0.50, 0.75, 0.90, 0.99)
    xq = np.quantile(x, quantiles, axis=1)
    yq = np.quantile(y, quantiles, axis=1)
    rms = np.maximum(np.sqrt(np.mean(x * x, axis=1)), 1.0e-12)
    jump_x, slip_x = _endpoint_diagnostics(x)
    jump_y, slip_y = _endpoint_diagnostics(y)
    result = {
        "amplitude_ks": float(np.max(ks)),
        "quantile_shift": float(np.max(np.abs(yq - xq) / rms[np.newaxis, :])),
        "jump_real": jump_x, "jump_surrogate": jump_y,
        "slip_real": slip_x, "slip_surrogate": slip_y,
    }
    if not all(np.isfinite(value) for value in result.values()):
        _fail("GATE_R0_AMPLITUDE_MISMATCH", "nonfinite")
    return result


def _production_model() -> LogisticRegression:
    return LogisticRegression(
        l1_ratio=0.0,
        C=1.0,
        solver="lbfgs",
        tol=1.0e-8,
        max_iter=2000,
        fit_intercept=True,
        class_weight=None,
        warm_start=False,
    )


def _validate_constructor(model: LogisticRegression) -> None:
    try:
        actual = model.get_params(deep=False)
        if any(actual.get(key) != value for key, value in MODEL_PARAMETERS.items()):
            raise AssertionError("constructor-parameters")
    except (AssertionError, AttributeError) as exc:
        _fail("GATE_R0_MODEL_FIT_INVALID", str(exc))


def _semantic_classes(
    fit_type: str,
    semantic_domain: Iterable[str],
    y_fit: np.ndarray,
) -> tuple[np.ndarray, int]:
    if fit_type not in FIT_DOMAINS:
        _fail("GATE_R0_MODEL_FIT_INVALID", f"unknown-fit-type:{fit_type}")
    observed_domain = tuple(sorted(set(semantic_domain)))
    required_domain = tuple(sorted(FIT_DOMAINS[fit_type]))
    if observed_domain != required_domain:
        _fail("GATE_R0_MODEL_FIT_INVALID", f"semantic-domain:{fit_type}")
    target = np.asarray(y_fit)
    if target.ndim != 1 or target.size == 0:
        _fail("GATE_R0_MODEL_FIT_INVALID", f"target-shape:{fit_type}")
    expected_classes = np.unique(target)
    cardinality = len(required_domain)
    if expected_classes.ndim != 1 or len(expected_classes) != cardinality:
        _fail("GATE_R0_MODEL_FIT_INVALID", f"target-cardinality:{fit_type}")
    try:
        if fit_type == "reference_detector":
            required = np.asarray([0, 1], dtype=target.dtype)
        else:
            required = np.asarray(required_domain, dtype=target.dtype)
    except (TypeError, ValueError):
        _fail("GATE_R0_MODEL_FIT_INVALID", f"target-encoding:{fit_type}")
    if expected_classes.dtype != required.dtype or not np.array_equal(expected_classes, required):
        _fail("GATE_R0_MODEL_FIT_INVALID", f"target-encoding:{fit_type}")
    return expected_classes, cardinality


def _validate_fitted_model(
    model: LogisticRegression,
    expected_classes: np.ndarray,
    cardinality: int,
    feature_width: int,
    evaluated: list[tuple[np.ndarray, np.ndarray, np.ndarray]],
) -> dict[str, Any]:
    try:
        if model.classes_.dtype != expected_classes.dtype:
            raise AssertionError("classes-dtype")
        np.testing.assert_array_equal(model.classes_, expected_classes)
        if model.classes_.ndim != 1 or len(model.classes_) != cardinality:
            raise AssertionError("classes-shape")
        if model.n_iter_.shape != (1,) or not 1 <= int(model.n_iter_[0]) < 2000:
            raise AssertionError("iterations")
        if int(model.n_features_in_) != feature_width:
            raise AssertionError("feature-width")
        expected_coef = (1, feature_width) if cardinality == 2 else (cardinality, feature_width)
        expected_intercept = (1,) if cardinality == 2 else (cardinality,)
        if model.coef_.shape != expected_coef or model.intercept_.shape != expected_intercept:
            raise AssertionError("parameter-shape")
        if not bool(np.isfinite(model.coef_).all() and np.isfinite(model.intercept_).all()):
            raise AssertionError("parameter-finite")
        for values, decision, probability in evaluated:
            expected_decision = (len(values),) if cardinality == 2 else (len(values), cardinality)
            if decision.shape != expected_decision or probability.shape != (len(values), cardinality):
                raise AssertionError("output-shape")
            if not bool(np.isfinite(decision).all() and np.isfinite(probability).all()):
                raise AssertionError("output-finite")
            if not bool(((probability >= 0.0) & (probability <= 1.0)).all()):
                raise AssertionError("probability-range")
            if not np.allclose(probability.sum(axis=1), 1.0, rtol=0.0, atol=1.0e-12):
                raise AssertionError("probability-sum")
    except (AssertionError, AttributeError) as exc:
        _fail("GATE_R0_MODEL_FIT_INVALID", str(exc))
    return {
        "class_dtype": str(model.classes_.dtype),
        "classes": model.classes_.tolist(),
        "class_count": cardinality,
        "feature_width": feature_width,
        "coef_shape": list(model.coef_.shape),
        "intercept_shape": list(model.intercept_.shape),
        "decision_shapes": [list(item[1].shape) for item in evaluated],
        "probability_shapes": [list(item[2].shape) for item in evaluated],
        "warning_count": 0,
        "n_iter": int(model.n_iter_[0]),
        "finite_probability_sum_pass": True,
    }


def _fit_logistic(
    x: np.ndarray,
    y: np.ndarray,
    fit_type: str,
    semantic_domain: Iterable[str],
    evaluation_arrays: Iterable[np.ndarray],
) -> tuple[list[np.ndarray], list[np.ndarray], dict[str, Any]]:
    expected_classes, cardinality = _semantic_classes(fit_type, semantic_domain, y)
    values_to_evaluate = (x, *tuple(evaluation_arrays))
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            model = _production_model()
            _validate_constructor(model)
            model.fit(x, y)
            evaluated = [
                (values, model.decision_function(values), model.predict_proba(values))
                for values in values_to_evaluate
            ]
            predictions = [model.predict(values) for values in values_to_evaluate]
    except Exception as exc:
        _fail("GATE_R0_MODEL_FIT_INVALID", f"fit:{fit_type}:{type(exc).__name__}")
    if caught:
        categories = ",".join(item.category.__name__ for item in caught)
        _fail("GATE_R0_MODEL_FIT_INVALID", f"warning:{fit_type}:{categories}")
    diagnostic = _validate_fitted_model(
        model, expected_classes, cardinality, int(x.shape[1]), evaluated
    )
    diagnostic["fit_type"] = fit_type
    return predictions[1:], [item[2] for item in evaluated[1:]], diagnostic


def _normalized_warning_message(value: Warning) -> str:
    return " ".join(str(value).replace("'", "").replace('"', "").split())


def _model_api_preflight() -> tuple[dict[str, Any], bytes]:
    import sklearn

    warning_filters_before = list(warnings.filters)
    if sklearn.__version__ != "1.9.0":
        _fail("GATE_R0_MODEL_API_EQUIVALENCE_MISMATCH", f"sklearn:{sklearn.__version__}")
    x = np.asarray([
        [-2.0, -1.0, 0.00], [-1.5, -0.5, 0.25], [-1.0, -1.5, -0.25], [-0.5, -2.0, 0.50],
        [0.5, 2.0, -0.50], [1.0, 1.5, 0.25], [1.5, 0.5, -0.25], [2.0, 1.0, 0.00],
    ], dtype=np.float64)
    y = np.asarray([0, 0, 0, 0, 1, 1, 1, 1], dtype=np.int64)
    common = {key: value for key, value in MODEL_PARAMETERS.items() if key != "l1_ratio"}
    try:
        with warnings.catch_warnings(record=True) as legacy_warnings:
            warnings.simplefilter("always")
            legacy = LogisticRegression(penalty="l2", **common)
            legacy.fit(x, y)
        with warnings.catch_warnings(record=True) as modern_warnings:
            warnings.simplefilter("always")
            modern = _production_model()
            _validate_constructor(modern)
            modern.fit(x, y)
    except Exception as exc:
        _fail("GATE_R0_MODEL_API_EQUIVALENCE_MISMATCH", f"fit:{type(exc).__name__}")
    message = _normalized_warning_message(legacy_warnings[0].message) if len(legacy_warnings) == 1 else ""
    if (
        len(legacy_warnings) != 1
        or legacy_warnings[0].category is not FutureWarning
        or "penalty was deprecated in version 1.8" not in message
        or "removed in 1.10" not in message
        or modern_warnings
        or not np.array_equal(legacy.classes_, modern.classes_)
        or not np.array_equal(legacy.n_iter_, modern.n_iter_)
    ):
        _fail("GATE_R0_MODEL_API_EQUIVALENCE_MISMATCH", "warning-or-metadata")
    comparisons = {
        "coef": (legacy.coef_, modern.coef_),
        "intercept": (legacy.intercept_, modern.intercept_),
        "decision": (legacy.decision_function(x), modern.decision_function(x)),
        "probability": (legacy.predict_proba(x), modern.predict_proba(x)),
    }
    maxima = {label: float(np.max(np.abs(left - right))) for label, (left, right) in comparisons.items()}
    if (
        not all(np.allclose(left, right, rtol=0.0, atol=1.0e-14) for left, right in comparisons.values())
        or not all(np.isfinite(left).all() and np.isfinite(right).all() for left, right in comparisons.values())
        or not all(1 <= int(model.n_iter_[0]) < 2000 for model in (legacy, modern))
    ):
        _fail("GATE_R0_MODEL_API_EQUIVALENCE_MISMATCH", "numerical")

    capabilities = []
    for cardinality in (2, 3, 18):
        rows = []
        labels = []
        for class_index in range(cardinality):
            for replicate in range(4):
                rows.append([
                    (class_index - (cardinality - 1) / 2) / max(cardinality - 1, 1),
                    (class_index % 3) - 1,
                    ((class_index % 5) - 2) / 2,
                    (replicate - 1.5) / 2,
                    (((class_index + replicate) % 7) - 3) / 3,
                    (((2 * class_index + replicate) % 11) - 5) / 5,
                ])
                labels.append(f"C{class_index:02d}")
        fixture = np.asarray(rows, dtype=np.float64)
        target = np.asarray(labels)
        try:
            with warnings.catch_warnings(record=True) as capability_warnings:
                warnings.simplefilter("always")
                model = _production_model()
                _validate_constructor(model)
                model.fit(fixture, target)
                evaluated = [(fixture, model.decision_function(fixture), model.predict_proba(fixture))]
        except Exception as exc:
            _fail("GATE_R0_MODEL_FIT_INVALID", f"capability:{cardinality}:{type(exc).__name__}")
        if capability_warnings:
            _fail("GATE_R0_MODEL_FIT_INVALID", f"capability-warning:{cardinality}")
        expected = np.asarray([f"C{index:02d}" for index in range(cardinality)], dtype=target.dtype)
        diagnostic = _validate_fitted_model(model, expected, cardinality, 6, evaluated)
        capabilities.append({"K": cardinality, **diagnostic})
    if warnings.filters != warning_filters_before:
        _fail("GATE_R0_MODEL_API_EQUIVALENCE_MISMATCH", "global-warning-filters")

    certificate = {
        "schema_version": 1,
        "artifact": "RC_HSG_GATE_R0_LOGISTIC_API_EQUIVALENCE_V1",
        "fit_type_contract_version": "RC_HSG_GATE_R0_FIT_CLASS_DOMAIN_V293",
        "sklearn_version": sklearn.__version__,
        "production_constructor": MODEL_PARAMETERS,
        "legacy_modern_binary": {
            "legacy_warning_count": 1,
            "legacy_warning_category": "FutureWarning",
            "legacy_warning_message_sha256": hashlib.sha256(message.encode("utf-8")).hexdigest(),
            "modern_warning_count": 0,
            "legacy_n_iter": int(legacy.n_iter_[0]),
            "modern_n_iter": int(modern.n_iter_[0]),
            "classes_equal": True,
            "n_iter_equal": True,
            "rtol": 0.0,
            "atol": 1.0e-14,
            "maximum_absolute_difference": maxima,
            "finite": True,
            "verdict": "PASS",
        },
        "multiclass_capability": capabilities,
        "fixture_or_model_values_persisted": False,
        "verdict": "PASS",
    }
    rendered = _yaml_bytes(certificate)
    return certificate, rendered


def _standardize(train: np.ndarray, *others: np.ndarray) -> tuple[np.ndarray, ...]:
    mean = train.mean(axis=0, dtype=np.float64)
    sd = train.std(axis=0, ddof=0, dtype=np.float64)
    keep = sd >= 1.0e-12
    if not bool(keep.any()):
        _fail("GATE_R0_MODEL_FAILURE", "zero-features")
    return tuple((values[:, keep] - mean[keep]) / sd[keep] for values in (train, *others))


def _classifier_audit(
    rows: list[dict[str, Any]], real: np.ndarray, surrogates: dict[int, np.ndarray], bootstrap: np.ndarray,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    train = np.asarray([row["role"] == "train_fit" for row in rows])
    valid = ~train
    subjects = np.asarray([row["subject"] for row in rows])
    output: dict[str, Any] = {}
    diagnostics: list[dict[str, Any]] = []
    for replicate in REPLICATES:
        train_x = np.concatenate((real[train], surrogates[replicate][train]), axis=0)
        train_y = np.concatenate((np.zeros(train.sum(), dtype=np.int8), np.ones(train.sum(), dtype=np.int8)))
        valid_x = np.concatenate((real[valid], surrogates[replicate][valid]), axis=0)
        valid_y = np.concatenate((np.zeros(valid.sum(), dtype=np.int8), np.ones(valid.sum(), dtype=np.int8)))
        train_z, valid_z = _standardize(train_x, valid_x)
        _, probabilities, diagnostic = _fit_logistic(
            train_z, train_y, "reference_detector", ("real", "N2"), (valid_z,)
        )
        diagnostics.append({"replicate": replicate, **diagnostic})
        probability = probabilities[0][:, 1]
        valid_subjects = np.concatenate((subjects[valid], subjects[valid]))
        subject_auc = []
        for subject in SUBJECTS:
            mask = valid_subjects == subject
            if set(valid_y[mask]) != {0, 1}:
                _fail("GATE_R0_MODEL_FAILURE", f"subject-classes:{subject}")
            subject_auc.append(float(roc_auc_score(valid_y[mask], probability[mask])))
        subject_auc_array = np.asarray(subject_auc, dtype=np.float64)
        point = float(subject_auc_array.mean())
        boot = subject_auc_array[bootstrap].mean(axis=1)
        upper = float(np.sort(boot)[9749])
        output[str(replicate)] = {
            "subject_auc": {subject: float(value).hex() for subject, value in zip(SUBJECTS, subject_auc, strict=True)},
            "subject_macro_auc": point.hex(),
            "bootstrap_upper_97_5": upper.hex(),
            "pooled_auc": float(roc_auc_score(valid_y, probability)).hex(),
            "pooled_auprc": float(average_precision_score(valid_y, probability)).hex(),
            "pooled_brier": float(brier_score_loss(valid_y, probability)).hex(),
            "point_pass": point <= CLASSIFIER_THRESHOLD,
            "upper_pass": upper <= CLASSIFIER_THRESHOLD,
        }
        del train_x, train_y, valid_x, valid_y, train_z, valid_z, probability, boot
    return output, diagnostics


def _macro_by_subject(target: np.ndarray, prediction: np.ndarray, subjects: np.ndarray) -> float:
    metrics = []
    for subject in SUBJECTS:
        mask = subjects == subject
        if not bool(mask.any()) or len(set(target[mask])) < 2:
            _fail("GATE_R0_MODEL_FAILURE", f"probe-subject:{subject}")
        metrics.append(float(balanced_accuracy_score(target[mask], prediction[mask])))
    return float(np.mean(metrics))


def _nuisance_audit(
    rows: list[dict[str, Any]], real: np.ndarray, surrogates: dict[int, np.ndarray],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    train = np.asarray([row["role"] == "train_fit" for row in rows])
    valid = ~train
    subjects = np.asarray([row["subject"] for row in rows])
    length = np.asarray([row["length_bin"] for row in rows])
    power = np.asarray([row["power_bin"] for row in rows])
    if any(row["power_bin"] not in {"P_LOW", "P_HIGH"} for row in rows):
        _fail("GATE_R0_MODEL_FIT_INVALID", "panel-power-domain")
    power_ok = np.ones(len(rows), dtype=bool)
    output: dict[str, Any] = {}
    diagnostics: list[dict[str, Any]] = []
    probes = (
        ("subject", subjects, np.ones(len(rows), dtype=bool), False),
        ("length", length, np.ones(len(rows), dtype=bool), True),
        ("power", power, power_ok, True),
    )
    for label, target, eligible, subject_macro in probes:
        train_mask = train & eligible
        valid_mask = valid & eligible
        standardized = _standardize(real[train_mask], real[valid_mask], *(surrogates[r][valid_mask] for r in REPLICATES))
        predictions, _, diagnostic = _fit_logistic(
            standardized[0], target[train_mask], f"nuisance_{label}",
            set(target[train_mask]), standardized[1:],
        )
        diagnostics.append(diagnostic)
        if subject_macro:
            metrics = [_macro_by_subject(target[valid_mask], prediction, subjects[valid_mask]) for prediction in predictions]
        else:
            metrics = [float(balanced_accuracy_score(target[valid_mask], prediction)) for prediction in predictions]
        real_metric = metrics[0]
        output[label] = {
            "real": real_metric.hex(),
            "surrogate": {str(rep): metrics[index + 1].hex() for index, rep in enumerate(REPLICATES)},
            "absolute_difference": {str(rep): abs(metrics[index + 1] - real_metric).hex() for index, rep in enumerate(REPLICATES)},
            "pass": {str(rep): abs(metrics[index + 1] - real_metric) <= NUISANCE_THRESHOLD for index, rep in enumerate(REPLICATES)},
        }
        del standardized, predictions
    output["session"] = {"constant": 1, "real_surrogate_exact_parity": True}
    return output, diagnostics


def _amplitude_audit(rows: list[dict[str, Any]], collected: dict[tuple[str, int], list[dict[str, float]]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for subject in SUBJECTS:
        output[subject] = {}
        for replicate in REPLICATES:
            values = collected.get((subject, replicate), [])
            expected = sum(row["subject"] == subject and row["role"] == "inner_val" for row in rows)
            if len(values) != expected or not values:
                _fail("GATE_R0_AMPLITUDE_MISMATCH", f"coverage:{subject}:{replicate}")
            medians = {label: float(np.median([item[label] for item in values])) for label in values[0]}
            jump_ratio = medians["jump_surrogate"] / max(medians["jump_real"], 1.0e-12)
            slip_ratio = medians["slip_surrogate"] / max(medians["slip_real"], 1.0e-12)
            output[subject][str(replicate)] = {
                "median_amplitude_ks": medians["amplitude_ks"].hex(),
                "median_quantile_shift": medians["quantile_shift"].hex(),
                "median_jump_real": medians["jump_real"].hex(),
                "median_jump_surrogate": medians["jump_surrogate"].hex(),
                "jump_ratio": jump_ratio.hex(),
                "median_slip_real": medians["slip_real"].hex(),
                "median_slip_surrogate": medians["slip_surrogate"].hex(),
                "slip_ratio": slip_ratio.hex(),
                "pass": (
                    medians["amplitude_ks"] <= AMPLITUDE_KS_THRESHOLD
                    and medians["quantile_shift"] <= QUANTILE_SHIFT_THRESHOLD
                    and ENDPOINT_RATIO_MIN <= jump_ratio <= ENDPOINT_RATIO_MAX
                    and ENDPOINT_RATIO_MIN <= slip_ratio <= ENDPOINT_RATIO_MAX
                ),
            }
    return output


def _numerical_summary(values: dict[tuple[int, str], list[float]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for replicate in REPLICATES:
        output[str(replicate)] = {}
        for metric in ("psd_relative_norm", "covariance_relative_norm", "mean_relative_norm", "cross_spectrum_relative_norm"):
            series = np.asarray(values[(replicate, metric)], dtype=np.float64)
            expected_count = EXPECTED["eligible_rows"] if replicate == 1 else EXPECTED["panel_rows"]
            if len(series) != expected_count:
                _fail("GATE_R0_NUMERICAL_MISMATCH", f"count:{replicate}:{metric}:{len(series)}")
            output[str(replicate)][metric] = {
                "count": int(len(series)),
                "maximum": float(series.max()).hex(),
                "median": float(np.median(series)).hex(),
                "q_0_95": float(np.quantile(series, 0.95)).hex(),
                "q_0_99": float(np.quantile(series, 0.99)).hex(),
                "all_rows_pass": bool(np.all(series <= NUMERICAL_THRESHOLD)),
            }
    return output


def _n1_audit(project_root: Path) -> dict[str, Any]:
    contract = _load_yaml(project_root / FIXED_INPUTS["n1_contract"][0], "n1-contract")
    expected = _load_jsonl(project_root / FIXED_INPUTS["n1_manifest"][0], "n1-manifest")
    by_replicate = {int(row["replicate_id"]): row for row in expected}
    if set(by_replicate) != set(range(1, 200)):
        _fail("GATE_R0_N1_MISMATCH", "manifest-replicates")
    sampler = N1JointPermutationSampler.from_frozen_assignment(project_root)
    hashes: list[str] = []
    fixed: list[int] = []
    for replicate in range(1, 200):
        batch = sampler.build(replicate)
        row = by_replicate[replicate]
        if batch.joint_mapping_sha256 != row.get("joint_mapping_sha256") or batch.fixed_points != row.get("fixed_points"):
            _fail("GATE_R0_N1_MISMATCH", f"parity:{replicate}")
        hashes.append(batch.joint_mapping_sha256)
        fixed.append(batch.fixed_points)
    parity = contract.get("parity", {})
    if len(set(hashes)) != 199 or sum(fixed) != 35529 or min(fixed) != 145 or max(fixed) != 214:
        _fail("GATE_R0_N1_MISMATCH", "summary")
    if parity.get("bijection_violations") != 0 or parity.get("cross_block_violations") != 0:
        _fail("GATE_R0_N1_MISMATCH", "contract")
    if not callable(getattr(sampler, "evaluate_real", None)) or not callable(getattr(sampler, "evaluate_pseudo_real", None)):
        _fail("GATE_R0_N1_MISMATCH", "selection-api")
    return {
        "structural_integrity": "PASS",
        "mechanism_robustness": "ADMITTED",
        "primary_fallback": "INELIGIBLE_DEGRADED_COVERAGE",
        "new_real_eeg_reads": 0,
        "replicates": 199,
        "unique_joint_mapping_hashes": 199,
        "fixed_points_total": 35529,
        "fixed_points_range": [145, 214],
        "selection_aware_callback_api": "PASS",
    }


def _scan(
    reader: Any,
    metadata: dict[str, Any],
    dataset_root: Path,
    allowed_files: dict[str, Path],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = metadata["eligible"]
    panel_keys = metadata["panel_keys"]
    panel_index = {_key(row): index for index, row in enumerate(metadata["panel_rows"])}
    n_rows = len(rows)
    panel_count = len(panel_index)
    real_features = np.empty((panel_count, 2429), dtype=np.float64)
    surrogate_features = {replicate: np.empty((panel_count, 2429), dtype=np.float64) for replicate in REPLICATES}
    sampler = N2CommonPhaseSampler()
    tokenizer = _TokenizerOnly()
    dereferenced: set[tuple[str, int, str]] = set()
    numerical: dict[tuple[int, str], list[float]] = defaultdict(list)
    amplitude: dict[tuple[str, int], list[dict[str, float]]] = defaultdict(list)
    coverage: list[dict[str, Any]] = []
    dtype_counts: Counter[str] = Counter()
    all_phase_hashes: set[str] = set()

    for index, row in enumerate(rows):
        key = _key(row)
        if key in dereferenced:
            _fail("GATE_R0_READ_MISMATCH", f"duplicate:{_row_key(row)}")
        try:
            batch, source_dtype = reader._read_raw(row, dataset_root, allowed_files, metadata["eligible_keys"])
        except Exception as exc:
            _fail("GATE_R0_READ_FAILURE", f"{_row_key(row)}:{str(exc).split(':', 1)[0]}")
        dereferenced.add(key)
        dtype_counts[source_dtype] += 1
        if batch.shape != (1, 105, row["raw_samples"]) or batch.dtype != torch.float32 or batch.device.type != "cpu" or not batch.is_contiguous():
            _fail("GATE_R0_READ_MISMATCH", f"tensor:{_row_key(row)}")
        real = batch[0].contiguous()
        before = real.clone()
        expected_windows = 1 + (row["raw_samples"] - 500) // 250
        row_mask = expected_windows == row["window_count"]
        if key in panel_keys:
            real_features[panel_index[key]] = _audit_vector(reader, tokenizer, real, expected_windows)
        phase_hashes: dict[str, str] = {}
        row_numeric_pass = True
        row_finite = True
        row_shape = True
        for replicate in REPLICATES:
            try:
                generated = sampler.generate_unpadded(real, _row_key(row), replicate)
            except Exception as exc:
                _fail("GATE_R0_N2_FAILURE", f"{_row_key(row)}:{replicate}:{type(exc).__name__}")
            surrogate = generated.values
            phase_hashes[str(replicate)] = generated.phase_seed_sha256
            if generated.phase_seed_sha256 in all_phase_hashes:
                _fail("GATE_R0_N2_FAILURE", f"duplicate-phase-hash:{_row_key(row)}:{replicate}")
            all_phase_hashes.add(generated.phase_seed_sha256)
            row_finite &= bool(torch.isfinite(surrogate).all())
            row_shape &= surrogate.shape == real.shape and surrogate.dtype == real.dtype
            if key in panel_keys:
                surrogate_features[replicate][panel_index[key]] = _audit_vector(
                    reader, tokenizer, surrogate, expected_windows
                )
            if replicate == 1 or key in panel_keys:
                metrics = _numerical_metrics(real, surrogate)
                for label, value in metrics.items():
                    numerical[(replicate, label)].append(value)
                    row_numeric_pass &= value <= NUMERICAL_THRESHOLD
            if key in panel_keys and replicate == 1:
                replay = sampler.generate_unpadded(real, _row_key(row), replicate)
                if not torch.equal(replay.values, surrogate) or replay.phase_seed_sha256 != generated.phase_seed_sha256:
                    _fail("GATE_R0_REPLAY_MISMATCH", _row_key(row))
                del replay
            if row["role"] == "inner_val":
                amplitude[(row["subject"], replicate)].append(_amplitude_metrics(real, surrogate))
            del surrogate, generated
        if not torch.equal(real, before):
            _fail("GATE_R0_N2_FAILURE", f"input-mutated:{_row_key(row)}")
        if len(set(phase_hashes.values())) != 3:
            _fail("GATE_R0_N2_FAILURE", f"phase-hash:{_row_key(row)}")
        coverage.append({
            "row_key": _row_key(row), "role": row["role"], "panel": key in panel_keys,
            "no_power_bin_full_only": row["power_edge_status"] == "INSUFFICIENT_TRAIN_CELL",
            "replicate_ids": list(REPLICATES),
            "phase_seed_sha256": [phase_hashes[str(replicate)] for replicate in REPLICATES],
            "read_count": 1, "finite_pass": bool(row_finite),
            "shape_dtype_pass": bool(row_shape), "mask_window_pass": bool(row_mask),
            "numerical_scope_pass": bool(row_numeric_pass),
        })
        del batch, real, before
        if index and index % 100 == 0:
            print(f"GATE_R0_PROGRESS rows={index}/{n_rows}", flush=True)

    if (
        dereferenced != metadata["eligible_keys"]
        or len(coverage) != n_rows
        or len(all_phase_hashes) != n_rows * len(REPLICATES)
    ):
        _fail("GATE_R0_READ_MISMATCH", "closure")
    summaries = {
        "features": (real_features, surrogate_features),
        "numerical": _numerical_summary(numerical),
        "amplitude": _amplitude_audit(rows, amplitude),
        "dtype_counts": dict(sorted(dtype_counts.items())),
    }
    return coverage, summaries


def _all_pass(gate: dict[str, Any]) -> tuple[str, list[str], list[str]]:
    failures: list[str] = []
    inconclusive: list[str] = []
    if not gate["coverage"]["eligible_all_replicates"]:
        failures.append("coverage:eligible-all-replicates")
    if gate["coverage"]["no_power_bin_full_audit_rows"] != 4 or gate["coverage"]["no_power_bin_panel_rows"] != 0:
        failures.append("coverage:no-power-bin-scope")
    for replicate, metrics in gate["numerical"].items():
        for label, summary in metrics.items():
            if not summary["all_rows_pass"]:
                failures.append(f"numerical:{replicate}:{label}")
    for replicate, result in gate["classifier"].items():
        if not result["point_pass"]:
            failures.append(f"classifier-point:{replicate}")
        elif not result["upper_pass"]:
            inconclusive.append(f"classifier-upper:{replicate}")
    for probe, result in gate["nuisance"].items():
        if probe != "session":
            failures.extend(f"nuisance:{probe}:{rep}" for rep, passed in result["pass"].items() if not passed)
    for subject, replicates in gate["amplitude_endpoint"].items():
        failures.extend(f"amplitude-endpoint:{subject}:{rep}" for rep, result in replicates.items() if not result["pass"])
    if failures or inconclusive:
        return "FAIL_NO_PRIMARY_REFERENCE", failures, inconclusive
    return "PASS_N2_PRIMARY_N1_MECHANISM_ONLY", failures, inconclusive


def _hex_thresholds() -> dict[str, Any]:
    return {
        "numerical_relative_norm_max": NUMERICAL_THRESHOLD.hex(),
        "classifier_subject_macro_auc_max": CLASSIFIER_THRESHOLD.hex(),
        "classifier_bootstrap_upper_max": CLASSIFIER_THRESHOLD.hex(),
        "nuisance_absolute_difference_max": NUISANCE_THRESHOLD.hex(),
        "subject_median_amplitude_ks_max": AMPLITUDE_KS_THRESHOLD.hex(),
        "subject_median_quantile_shift_max": QUANTILE_SHIFT_THRESHOLD.hex(),
        "endpoint_ratio_min": ENDPOINT_RATIO_MIN.hex(),
        "endpoint_ratio_max": ENDPOINT_RATIO_MAX.hex(),
    }


def _correction() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "artifact": "RC_HSG_RUN019_POSTCOMMIT_CORRECTION_V1",
        "created_by_run": "2026-08-24_020_gate_r0_reference_integrity",
        "historical_run": "runs/2026-08-24_019_n2_common_phase_sampler.md",
        "original_commit": "f8dce4168ac123c51b5cb1db474734f83bd60799",
        "original_run_sha256": "77d9469e5d9cf5dcf75e38b2272c965128802938e5c65f8f213d3cc0c31851a2",
        "original_repository_status": "RC_HSG_V28_N2_COMMON_PHASE_SAMPLER_IMPLEMENTED_GATE_R0_PENDING",
        "corrected_commit": BASELINE_COMMIT,
        "corrected_run_sha256": FIXED_INPUTS["run019"][1],
        "corrected_repository_status": "RC_HSG_V28_N2_COMMON_PHASE_SAMPLER_IMPLEMENTED_GATE_R0_AUDIT_PENDING",
        "field": "repository_status",
        "scientific_state_changed": False,
        "historical_run_modified_by_run020": False,
    }


def _jsonl_bytes(rows: list[dict[str, Any]]) -> bytes:
    return b"".join((json.dumps(row, sort_keys=False, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii") for row in rows)


def _yaml_bytes(value: dict[str, Any]) -> bytes:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=False, width=120).encode("utf-8")


def _report_bytes(gate: dict[str, Any]) -> bytes:
    lines = [
        "# RC-HSG v2.9.3 Gate R0 Reference Integrity Audit", "",
        "## Outcome", "",
        f"Decision: `{gate['decision']}`.",
        "This outcome-blind audit decides reference admissibility only. It is not semantic performance, calibration, or mechanism evidence.", "",
        "## Scope", "",
        f"Eligible outer-train arrays read once: {gate['read_counters']['eligible_outer_train_arrays']}.",
        "Short, calibration, test, text, outcome, and test-identity reads: 0.",
        "N1 used frozen metadata only and remains mechanism/robustness-only.", "",
        "## Frozen checks", "",
        "The 216 theoretical role-cells are structural coverage only: 192 are non-empty and 24 are missing.",
        "Matched nuisance support is 88/16/0/4 across MATCHED/TRAIN_ONLY/INNER_ONLY/ABSENT_BOTH; the panel has 176 rows (88/88 by role).",
        f"Support ledger SHA256: `{gate['support']['ledger_sha256']}`; panel SHA256: `{gate['panel']['sha256']}`.",
        f"N2 eligible coverage: `{gate['coverage']['eligible_conditional']}`; system population coverage: `{gate['coverage']['system_population']}`.",
        f"Classifier threshold and bootstrap upper threshold: `{gate['thresholds']['classifier_subject_macro_auc_max']}`.",
        f"Numerical relative-norm threshold: `{gate['thresholds']['numerical_relative_norm_max']}`.",
        f"Scientific failures: {gate['scientific_failures']}; inconclusive checks: {gate['inconclusive_checks']}.", "",
        "## Boundary", "",
        "Route remains unlocked and test remains `LOCKED_UNTIL_ROUTE_LOCK`.",
        "Run 020 stops before semantic schema, candidates, reference scores, reliability, calibration, later Gates, route lock, or test unlock.", "",
    ]
    return "\n".join(lines).encode("utf-8")


def _safe_output_root(root: Path, project_root: Path, label: str, external: bool) -> Path:
    unresolved = root.absolute()
    _reject_symlink_chain(unresolved, Path(unresolved.anchor), label)
    if unresolved.exists() and not unresolved.is_dir():
        _fail("GATE_R0_OUTPUT_FAILURE", f"root-type:{label}")
    resolved = unresolved.resolve(strict=False)
    inside = True
    try:
        resolved.relative_to(project_root.resolve())
    except ValueError:
        inside = False
    if external == inside:
        _fail("GATE_R0_OUTPUT_FAILURE", f"boundary:{label}")
    return resolved


def _atomic_write(root: Path, rendered: dict[str, bytes]) -> None:
    pending: list[tuple[Path, Path]] = []
    try:
        for label, relative in OUTPUTS.items():
            destination = root / relative
            _reject_symlink_chain(destination, root, label)
            destination.parent.mkdir(parents=True, exist_ok=True)
            descriptor, name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
            temporary = Path(name)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(rendered[label])
                handle.flush()
                os.fsync(handle.fileno())
            pending.append((temporary, destination))
        for temporary, destination in pending:
            os.replace(temporary, destination)
    except GateR0TechnicalAbort:
        raise
    except Exception as exc:
        for temporary, _ in pending:
            temporary.unlink(missing_ok=True)
        _fail("GATE_R0_OUTPUT_FAILURE", type(exc).__name__)


def audit_gate_r0(
    project_root: Path,
    dataset_root: Path,
    canonical_output_root: Path,
    verification_output_roots: tuple[Path, Path],
    *,
    enforce_frozen_expectations: bool = True,
) -> dict[str, str]:
    started = time.perf_counter()
    project = Path(project_root).absolute()
    if not isinstance(verification_output_roots, tuple) or len(verification_output_roots) != 2:
        _fail("GATE_R0_OUTPUT_FAILURE", "verification-root-count")
    canonical = _safe_output_root(Path(canonical_output_root), project, "canonical", external=False)
    verify_a = _safe_output_root(Path(verification_output_roots[0]), project, "verification-a", external=True)
    verify_b = _safe_output_root(Path(verification_output_roots[1]), project, "verification-b", external=True)
    if len({canonical, verify_a, verify_b}) != 3:
        _fail("GATE_R0_OUTPUT_FAILURE", "duplicate-roots")
    paths, hashes = _verify_inputs(project, enforce_frozen_expectations)
    metadata = _metadata_preflight(paths, enforce_frozen_expectations)
    bootstrap = _bootstrap_indices()
    n1 = _n1_audit(project)
    model_certificate, model_certificate_bytes = _model_api_preflight()
    reader = _load_reader(paths["reader"])
    targeted = _load_yaml(paths["targeted"], "targeted")
    osf = _load_yaml(paths["osf"], "osf")
    try:
        resolved_dataset, allowed_files, identities = reader._dataset_files(
            dataset_root, targeted, osf, enforce=enforce_frozen_expectations
        )
    except Exception as exc:
        _fail("GATE_R0_READER_MISMATCH", f"identity:{type(exc).__name__}")
    if enforce_frozen_expectations and resolved_dataset != DATASET_ROOT:
        _fail("GATE_R0_READER_MISMATCH", "dataset-root")
    if len(allowed_files) != 18 or len(identities) != 18 or not {row["source_file"] for row in metadata["eligible"]}.issubset(allowed_files):
        _fail("GATE_R0_READER_MISMATCH", "source-files")

    coverage_rows, scan = _scan(reader, metadata, resolved_dataset, allowed_files)
    real_features, surrogate_features = scan.pop("features")
    classifier, classifier_diagnostics = _classifier_audit(
        metadata["panel_rows"], real_features, surrogate_features, bootstrap
    )
    nuisance, nuisance_diagnostics = _nuisance_audit(
        metadata["panel_rows"], real_features, surrogate_features
    )
    del real_features, surrogate_features, bootstrap
    read_counters = {
        "eligible_outer_train_arrays": len(coverage_rows),
        "train_fit_arrays": EXPECTED["train_fit"],
        "inner_val_arrays": EXPECTED["inner_val"],
        "full_audit_arrays": EXPECTED["eligible_rows"],
        "matched_panel_arrays": EXPECTED["panel_rows"],
        "matched_panel_train_fit": EXPECTED["panel_train_fit"],
        "matched_panel_inner_val": EXPECTED["panel_inner_val"],
        "eligible_outside_panel": EXPECTED["eligible_rows"] - EXPECTED["panel_rows"],
        "short_arrays": 0,
        "calibration_arrays": 0,
        "test_arrays": 0,
        "text_reads": 0,
        "outcome_reads": 0,
        "test_identity_reads": 0,
        "n1_real_eeg_reads": 0,
    }
    if read_counters["eligible_outer_train_arrays"] != EXPECTED["eligible_rows"]:
        _fail("GATE_R0_READ_MISMATCH", "count")
    gate = {
        "schema_version": 1,
        "artifact": POLICY_ID,
        "spec_version": "v2.9.3",
        "baseline_commit": BASELINE_COMMIT,
        "task": "GATE_R0",
        "evidence_scope": "OUTCOME_BLIND_OUTER_TRAIN_REFERENCE_INTEGRITY_NO_TEXT_NO_OUTCOME_NO_CAL_TEST",
        "input_artifacts": {label: {"path": ({**FIXED_INPUTS, **CONTROL_INPUTS})[label][0], "sha256": digest} for label, digest in hashes.items()},
        "population": metadata["actual"],
        "replicates": list(REPLICATES),
        "support": {
            "theoretical_role_cells": 216,
            "nonempty_role_cells": 192,
            "missing_role_cells": 24,
            "theoretical_nuisance_strata": 108,
            "matched_support": 88,
            "train_only": 16,
            "inner_only": 0,
            "absent_both": 4,
            "ledger_sha256": SUPPORT_SHA256,
        },
        "panel": {
            "law": "RC_HSG_GATE_R0_MATCHED_PANEL_V1",
            "rows": len(metadata["panel_keys"]),
            "train_fit": 88,
            "inner_val": 88,
            "subjects": 18,
            "sha256": PANEL_SHA256,
            "direct_192_role_cell_union": False,
            "borrowing_duplication_replacement": False,
        },
        "thresholds": _hex_thresholds(),
        "coverage": {
            "eligible_conditional": float(3497 / 3497).hex(),
            "system_population": float(3497 / 3541).hex(),
            "eligible_all_replicates": all(row["finite_pass"] and row["shape_dtype_pass"] and row["mask_window_pass"] for row in coverage_rows),
            "no_power_bin_full_audit_rows": sum(row["no_power_bin_full_only"] for row in coverage_rows),
            "no_power_bin_panel_rows": sum(row["no_power_bin_full_only"] and row["panel"] for row in coverage_rows),
        },
        "numerical": scan["numerical"],
        "classifier": classifier,
        "nuisance": nuisance,
        "model_api_certificate_sha256": hashlib.sha256(model_certificate_bytes).hexdigest(),
        "model_fit_diagnostics": {
            "reference_detector": classifier_diagnostics,
            "nuisance": nuisance_diagnostics,
            "all_production_warning_counts_zero": True,
        },
        "amplitude_endpoint": scan["amplitude"],
        "n1": n1,
        "read_counters": read_counters,
        "source_dtype_counts": scan["dtype_counts"],
        "persistence": {
            "waveform_surrogate_token_feature_fft_phase_written": False,
            "classifier_coefficients_probabilities_written": False,
            "binary_model_or_cache_written": False,
        },
        "test_status": "LOCKED_UNTIL_ROUTE_LOCK",
        "route_locked": False,
    }
    decision, failures, inconclusive = _all_pass(gate)
    gate["decision"] = decision
    gate["scientific_failures"] = failures
    gate["inconclusive_checks"] = inconclusive
    gate["n2_primary"] = "ADMITTED" if decision == "PASS_N2_PRIMARY_N1_MECHANISM_ONLY" else "NOT_ADMITTED"
    gate["elapsed_seconds"] = float(time.perf_counter() - started).hex()
    gate["peak_rss_bytes"] = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
    rendered = {
        "correction": _yaml_bytes(_correction()),
        "model_certificate": model_certificate_bytes,
        "support": metadata["support_bytes"],
        "panel": metadata["panel_bytes"],
        "coverage": _jsonl_bytes(coverage_rows),
        "gate": _yaml_bytes(gate),
        "report": _report_bytes(gate),
    }
    if sum(len(value) for value in rendered.values()) > 2 * 1024 * 1024:
        _fail("GATE_R0_OUTPUT_FAILURE", "size-limit")
    for root in (verify_a, verify_b, canonical):
        _atomic_write(root, rendered)
    hashes_out: dict[str, str] = {}
    for label, relative in OUTPUTS.items():
        content = rendered[label]
        if any((root / relative).read_bytes() != content for root in (verify_a, verify_b, canonical)):
            _fail("GATE_R0_OUTPUT_FAILURE", f"byte-identity:{label}")
        hashes_out[relative] = hashlib.sha256(content).hexdigest()
    return hashes_out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--verification-root-a", type=Path, required=True)
    parser.add_argument("--verification-root-b", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        hashes = audit_gate_r0(
            PROJECT_ROOT,
            DATASET_ROOT,
            args.output_root,
            (args.verification_root_a, args.verification_root_b),
        )
    except GateR0TechnicalAbort as exc:
        print(f"TECHNICAL_ABORT_NO_OUTCOME: {exc}", file=sys.stderr)
        return 2
    for path, digest in hashes.items():
        print(f"{path} {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
