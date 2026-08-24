#!/usr/bin/env python3
"""Validate the RC-HSG file-based project memory system.

The validator deliberately fails closed: a task cannot claim readiness or
completion without its declared prerequisites, evidence, run record, and gate
ordering.  Scientific unknowns remain blockers rather than inferred facts.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment failure
    raise SystemExit("DEPENDENCY_MISSING: PyYAML>=6,<7 is required") from exc


ALLOWED_STATUSES = {
    "TODO",
    "READY",
    "IN_PROGRESS",
    "DONE",
    "BLOCKED",
    "FAILED",
    "SKIPPED",
    "TERMINATED",
}
ALLOWED_GATE_OUTCOMES = {None, "PASS", "FAIL", "DEGRADED", "TOPIC_ONLY"}
ALLOWED_LOCKED_ROUTES = {
    "RC_HSG",
    "ORDINARY_HIERARCHICAL_SELECTIVE_GENERATION",
    "FLAT_RC",
    "RELIABILITY_REFERENCE_STUDY",
    "EMPIRICAL_RISK_AWARE",
}
REQUIRED_TASK_FIELDS = {
    "title",
    "stage",
    "status",
    "prerequisites",
    "produces",
    "acceptance",
}
REQUIRED_TASK_IDS = {
    "SPEC_V21_REVIEW",
    "S0_SCIENTIFIC_REDESIGN_FREEZE",
    "SPEC_V20_REVIEW",
    "SPEC_V19_REVIEW",
    "SPEC_V18_REVIEW",
    "S0_STIMULUS_SOURCE_BINDING",
    "S0_STIMULUS_SIMILARITY_DIAGNOSTIC",
    "S0_STIMULUS_GROUP_POLICY_REVIEW",
    "SPEC_V17_REVIEW",
    "S0_DATA_ADMISSION_POLICY_REPAIR",
    "SPEC_V16_REVIEW",
    "S0_ZUCO2_NR_SEGMENT_CORRESPONDENCE",
    "SPEC_V15_REVIEW",
    "S0_ZUCO2_NR_ADMISSION_REPAIR",
    "SPEC_V14_REVIEW",
    "S0_ACTIVE_SPEC_GUARD",
    "S0_ZUCO2_NR_TARGETED_ADMISSION",
    "SPEC_V13_REVIEW",
    "S0_GOVERNANCE_HARDENING",
    "S0_INPUT_DISCOVERY_AUDIT",
    "SPEC_V12_REVIEW",
    "S0_GOVERNANCE_BOOTSTRAP",
    "S0_REPOSITORY_AUDIT",
    "S0_DATA_CARD",
    "S0_SEMANTIC_ITEM",
    "S0_H_DEFINITION",
    "S0_JOINT_SPLIT",
    "S0_LEAKAGE_AUDIT",
    "S0_A_INTERFACE",
    "S0_A1_FRONTEND",
    "S0_A1_ADMISSION",
    "S0_A3_CONTAMINATION_CHECK",
    "S0_N1_BLOCK_FEASIBILITY",
    "S0_N1_SAMPLER",
    "S0_N2_SAMPLER",
    "GATE_A1",
    "S0_SCHEMA_AUDIT",
    "S0_GATE_A_POPULATION_E5",
    "S0_A_POLICY_REVIEW",
    "STAGE1_PROBES",
    "SHAM_VALIDATION",
    "GATE_A",
    "S0_CALIBRATION_CONTRACT",
    "S0_DIRECT_C",
    "S0_PMI_BASELINE",
    "S0_NC_HSG_CORE",
    "S0_ANMA_ORIG",
    "S0_ALIGN_UNIT_COST",
    "GATE_B",
    "ROUTE_LOCK",
    "MAIN_EXPERIMENT",
    "GATE_R0",
    "S0_REFERENCE_FEATURES",
    "S0_RELIABILITY_MODELS",
    "S0_CALIBRATION_FEASIBILITY_REVIEW",
    "S0_ABSOLUTE_HSG",
    "S0_RC_HSG_CORE",
    "S0_FLAT_RC",
    "GATE_R",
    "GATE_C",
    "GATE_H",
    "MECHANISM_A",
}
V21_ACTIVE_GATES = {
    "gate_r0": "GATE_R0",
    "gate_r": "GATE_R",
    "gate_c": "GATE_C",
    "gate_h": "GATE_H",
    "mechanism_a": "MECHANISM_A",
}
V21_SUPERSEDED_TASKS = {
    "GATE_A1",
    "GATE_A",
    "GATE_B",
    "S0_NC_HSG_CORE",
    "S0_DIRECT_C",
    "STAGE1_PROBES",
    "SHAM_VALIDATION",
}
V21_DEPENDENCIES = {
    "S0_A_INTERFACE": {
        "S0_REPOSITORY_AUDIT",
        "S0_DATA_CARD",
        "S0_A_POLICY_REVIEW",
        "S0_JOINT_SPLIT",
    },
    "S0_SEMANTIC_ITEM": {
        "S0_A_INTERFACE",
        "S0_DATA_CARD",
        "S0_JOINT_SPLIT",
        "S0_LEAKAGE_AUDIT",
    },
    "S0_H_DEFINITION": {"S0_SEMANTIC_ITEM", "S0_JOINT_SPLIT"},
    "S0_SCHEMA_AUDIT": {"S0_SEMANTIC_ITEM", "S0_H_DEFINITION"},
    "GATE_R0": {
        "S0_LEAKAGE_AUDIT",
        "S0_A1_ADMISSION",
        "S0_N1_SAMPLER",
        "S0_N2_SAMPLER",
    },
    "S0_CALIBRATION_CONTRACT": {
        "S0_CALIBRATION_FEASIBILITY_REVIEW",
        "S0_RELIABILITY_MODELS",
        "S0_GATE_A_POPULATION_E5",
    },
    "S0_PMI_BASELINE": {
        "S0_A_INTERFACE",
        "S0_H_DEFINITION",
        "S0_RELIABILITY_MODELS",
        "S0_CALIBRATION_CONTRACT",
    },
    "ROUTE_LOCK": {
        "S0_ABSOLUTE_HSG",
        "S0_RC_HSG_CORE",
        "S0_FLAT_RC",
        "S0_PMI_BASELINE",
        "S0_CALIBRATION_CONTRACT",
        "S0_LEAKAGE_AUDIT",
        "S0_ALIGN_UNIT_COST",
    },
    "GATE_R": {"ROUTE_LOCK", "S0_ABSOLUTE_HSG", "S0_RC_HSG_CORE"},
    "GATE_C": {"ROUTE_LOCK", "S0_RC_HSG_CORE", "S0_CALIBRATION_CONTRACT"},
    "GATE_H": {"ROUTE_LOCK", "S0_RC_HSG_CORE", "S0_FLAT_RC"},
    "MECHANISM_A": {
        "ROUTE_LOCK",
        "GATE_R0",
        "S0_REFERENCE_FEATURES",
        "S0_GATE_A_POPULATION_E5",
    },
    "MAIN_EXPERIMENT": {
        "ROUTE_LOCK",
        "GATE_R",
        "GATE_C",
        "GATE_H",
        "MECHANISM_A",
        "S0_LEAKAGE_AUDIT",
        "S0_ALIGN_UNIT_COST",
    },
}
FROZEN_RUN_011_HASHES = {
    "artifacts/split_regimeI.json": "e2c065e5b395053cd655670fede8a2b117f6eb9821af884ca31c6fed3842fbab",
    "artifacts/split_regimeII.json": "9643dd5abe953e863e7535989f2f65d0f013a1c775c167e49f7d107545016393",
    "artifacts/split_manifest.yaml": "56ccf23881c4e5dee2f3f00704a8af4847636d116783a9da8c2526fdb5c2549f",
    "artifacts/gate_a_population.yaml": "279e3edf1c41971b6967f74657ec531533977d90ea4dc3d48a5efd63dd295d60",
    "reports/joint_split_population.md": "13755eac6198352b9c4dd6605f95a31b6e859db395bb5e6539a715427f742d09",
}
SNAPSHOT_PATHS = (
    "artifacts/governance/repository_inventory.yaml",
    "artifacts/governance/environment_snapshot.yaml",
    "artifacts/governance/spec_implementation_matrix.yaml",
)
SPEC_VERSION_RE = re.compile(r"^v[0-9]+\.[0-9]+(?:\.[0-9]+)?$")
ACTIVE_SPEC_DECL_RE = re.compile(
    r"Active SPEC:\s*`?([^`\s]+)`?\s*\(version\s*`?(v[0-9]+\.[0-9]+(?:\.[0-9]+)?)`?\)",
    re.IGNORECASE,
)
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
FOREIGN_PROJECT_MARKERS = {
    "EQ-ANMA",
    "CSPE",
    "711340d",
    "STRUCTURAL_NO_GO_N50",
}


def _error(errors: list[str], code: str, detail: str) -> None:
    errors.append(f"{code}: {detail}")


def _load_yaml(path: Path, errors: list[str], label: str) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = yaml.safe_load(handle)
    except FileNotFoundError:
        _error(errors, "FILE_MISSING", f"{label} not found: {path}")
        return None
    except yaml.YAMLError as exc:
        _error(errors, "YAML_INVALID", f"{label}: {exc}")
        return None
    if value is None:
        _error(errors, "YAML_EMPTY", label)
    return value


def _safe_relative_path(root: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None
    return resolved


def _check_active_spec_entrypoints(root: Path, project: dict[str, Any], errors: list[str]) -> None:
    """Fail closed when any live recovery entry point names another SPEC."""
    expected_path = project.get("spec_path")
    expected_version = project.get("spec_version")
    for relative in ("AGENTS.md", "AI_START_HERE.md", "HANDOFF.md", "PACKAGE_README.md"):
        path = root / relative
        try:
            content = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            _error(errors, "FILE_MISSING", f"active SPEC entry point not found: {path}")
            continue
        except OSError as exc:
            _error(errors, "FILE_UNREADABLE", f"{relative}: {type(exc).__name__}")
            continue
        declaration = ACTIVE_SPEC_DECL_RE.search(content)
        if declaration is None:
            _error(errors, "ENTRYPOINT_SPEC_MISMATCH", f"{relative}: Active SPEC declaration missing")
            continue
        declared_path, declared_version = declaration.groups()
        if declared_path != expected_path:
            _error(errors, "ENTRYPOINT_SPEC_MISMATCH", f"{relative}: path {declared_path!r} != {expected_path!r}")
        if declared_version != expected_version:
            _error(errors, "ENTRYPOINT_SPEC_MISMATCH", f"{relative}: version {declared_version!r} != {expected_version!r}")


def _prerequisites_done(task: dict[str, Any], tasks: dict[str, Any]) -> bool:
    prerequisites = task.get("prerequisites")
    if not isinstance(prerequisites, list):
        return False
    return all(
        isinstance(tasks.get(task_id), dict)
        and tasks[task_id].get("status") == "DONE"
        for task_id in prerequisites
    )


def active_blocked_task_ids(state: dict[str, Any]) -> set[str]:
    blocked: set[str] = set()
    blockers = state.get("blockers", [])
    if not isinstance(blockers, list):
        return blocked
    for blocker in blockers:
        if not isinstance(blocker, dict):
            continue
        blocks = blocker.get("blocks", [])
        if isinstance(blocks, list):
            blocked.update(item for item in blocks if isinstance(item, str))
    return blocked


def ready_tasks(tasks: dict[str, Any], state: dict[str, Any]) -> list[str]:
    """Return valid READY tasks in the mandated deterministic order."""

    blocked = active_blocked_task_ids(state)
    candidates = [
        task_id
        for task_id, task in tasks.items()
        if isinstance(task, dict)
        and task.get("status") == "READY"
        and task_id not in blocked
        and _prerequisites_done(task, tasks)
    ]

    def rank(task_id: str) -> tuple[int, int, str]:
        task = tasks[task_id]
        priority = task.get("priority", 1_000_000)
        try:
            numeric_priority = int(priority)
        except (TypeError, ValueError):
            numeric_priority = 1_000_000
        return (
            0 if task.get("critical_path") is True else 1,
            numeric_priority,
            task_id,
        )

    return sorted(candidates, key=rank)


def _check_cycles(tasks: dict[str, Any], errors: list[str]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str, trail: list[str]) -> None:
        if task_id in visiting:
            _error(
                errors,
                "DEPENDENCY_CYCLE",
                " -> ".join(trail + [task_id]),
            )
            return
        if task_id in visited:
            return
        visiting.add(task_id)
        task = tasks.get(task_id)
        if isinstance(task, dict):
            prerequisites = task.get("prerequisites", [])
            if isinstance(prerequisites, list):
                for prerequisite in prerequisites:
                    if prerequisite in tasks:
                        visit(prerequisite, trail + [task_id])
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in tasks:
        visit(task_id, [])


def _run_record_path(root: Path, completed_by_run: Any) -> Path | None:
    if not isinstance(completed_by_run, str) or not completed_by_run.strip():
        return None
    value = completed_by_run.strip()
    relative = value if value.startswith("runs/") else f"runs/{value}.md"
    return _safe_relative_path(root, relative)


def _require_done(
    tasks: dict[str, Any], required: Iterable[str], errors: list[str], code: str
) -> None:
    missing = [
        task_id
        for task_id in required
        if not isinstance(tasks.get(task_id), dict)
        or tasks[task_id].get("status") != "DONE"
    ]
    if missing:
        _error(errors, code, "required DONE tasks: " + ", ".join(missing))


def _check_gate_order(tasks: dict[str, Any], errors: list[str]) -> None:
    if tasks.get("GATE_R0", {}).get("status") == "DONE":
        _require_done(
            tasks,
            ("S0_LEAKAGE_AUDIT", "S0_A1_ADMISSION", "S0_N1_SAMPLER", "S0_N2_SAMPLER"),
            errors,
            "GATE_R0_ORDER",
        )

    if tasks.get("ROUTE_LOCK", {}).get("status") == "DONE":
        _require_done(
            tasks,
            (
                "S0_ABSOLUTE_HSG",
                "S0_RC_HSG_CORE",
                "S0_FLAT_RC",
                "S0_PMI_BASELINE",
                "S0_CALIBRATION_CONTRACT",
                "S0_LEAKAGE_AUDIT",
                "S0_ALIGN_UNIT_COST",
            ),
            errors,
            "ROUTE_LOCK_ORDER",
        )

    if tasks.get("GATE_R", {}).get("status") == "DONE":
        _require_done(
            tasks,
            ("ROUTE_LOCK", "S0_ABSOLUTE_HSG", "S0_RC_HSG_CORE"),
            errors,
            "GATE_R_ORDER",
        )

    if tasks.get("GATE_C", {}).get("status") == "DONE":
        _require_done(
            tasks,
            ("ROUTE_LOCK", "S0_RC_HSG_CORE", "S0_CALIBRATION_CONTRACT"),
            errors,
            "GATE_C_ORDER",
        )

    if tasks.get("GATE_H", {}).get("status") == "DONE":
        _require_done(
            tasks,
            ("ROUTE_LOCK", "S0_RC_HSG_CORE", "S0_FLAT_RC"),
            errors,
            "GATE_H_ORDER",
        )

    if tasks.get("MECHANISM_A", {}).get("status") == "DONE":
        _require_done(
            tasks,
            ("ROUTE_LOCK", "GATE_R0", "S0_REFERENCE_FEATURES", "S0_GATE_A_POPULATION_E5"),
            errors,
            "MECHANISM_A_ORDER",
        )

    if tasks.get("MAIN_EXPERIMENT", {}).get("status") == "DONE":
        _require_done(
            tasks,
            (
                "ROUTE_LOCK",
                "GATE_R",
                "GATE_C",
                "GATE_H",
                "MECHANISM_A",
                "S0_LEAKAGE_AUDIT",
                "S0_ALIGN_UNIT_COST",
            ),
            errors,
            "MAIN_EXPERIMENT_ORDER",
        )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _check_v21_contract(root: Path, state: dict[str, Any], tasks: dict[str, Any], errors: list[str]) -> None:
    project = state.get("project", {})
    if project.get("spec_version") != "v2.1":
        return

    if len(tasks) != 67:
        _error(errors, "V21_TASK_COUNT_MISMATCH", f"expected 67, got {len(tasks)}")
    done = sum(isinstance(task, dict) and task.get("status") == "DONE" for task in tasks.values())
    if done != 29:
        _error(errors, "V21_DONE_COUNT_MISMATCH", f"expected 29, got {done}")
    ready = [task_id for task_id, task in tasks.items() if isinstance(task, dict) and task.get("status") == "READY"]
    if ready != ["S0_A_INTERFACE"]:
        _error(errors, "V21_READY_SET_MISMATCH", repr(ready))
    if tasks.get("S0_A_INTERFACE", {}).get("owner") != "CODEX":
        _error(errors, "V21_A_INTERFACE_OWNER_MISMATCH", repr(tasks.get("S0_A_INTERFACE", {}).get("owner")))

    for task_id in V21_SUPERSEDED_TASKS:
        task = tasks.get(task_id, {})
        if task.get("status") != "SKIPPED" or task.get("critical_path") is not False or task.get("skip_reason") != "SUPERSEDED_BY_RC_HSG_V21":
            _error(errors, "V21_SUPERSEDED_TASK_MISMATCH", task_id)

    for task_id, expected in V21_DEPENDENCIES.items():
        actual = tasks.get(task_id, {}).get("prerequisites")
        if not isinstance(actual, list) or set(actual) != expected or len(actual) != len(expected):
            _error(errors, "V21_DEPENDENCY_MISMATCH", f"{task_id}: {actual!r}")

    gates = state.get("gates")
    if not isinstance(gates, dict) or set(gates) != set(V21_ACTIVE_GATES):
        _error(errors, "V21_ACTIVE_GATE_SET_MISMATCH", repr(sorted(gates) if isinstance(gates, dict) else gates))

    policy = _load_yaml(root / "artifacts/backbone_a_policy.yaml", errors, "backbone A policy")
    if isinstance(policy, dict):
        expected_selected = {
            "implementation": "PROJECT_NATIVE_CLEAN_ROOM",
            "external_source_code_copied": False,
            "pretrained_checkpoint": None,
            "weight_download_required": False,
            "input_channels": 105,
            "sampling_hz": 500,
            "input_unit": "RELEASE_NATIVE_AMPLITUDE_UNRESOLVED",
            "physical_unit_conversion": "NONE",
            "channel_interpolation": False,
            "processed_reference": "common-average",
            "per_trial_transform": {
                "center": "channel_median",
                "scale": "max(1.4826_times_MAD,centered_RMS,1e-6)",
                "clip": [-20.0, 20.0],
            },
            "window_samples": 500,
            "hop_samples": 250,
            "window_function": "HANN",
            "bands_hz": [[1, 4], [4, 8], [8, 10], [10, 13], [13, 20], [20, 30], [30, 45], [55, 75]],
            "feature": "LOG_RELATIVE_BANDPOWER",
            "feature_epsilon": 1.0e-12,
            "token_input_dim": 840,
            "projection_dim": 256,
            "temporal_encoder_layers": 2,
            "attention_heads": 4,
            "feedforward_dim": 512,
            "dropout": 0.10,
            "position": "SINUSOIDAL",
            "output_contract": {"window_embeddings": "L_BY_256", "mask": "L", "pooled_embedding": 256},
            "initialization": "DETERMINISTIC_PROJECT_OWNED_RANDOM_INIT_PER_FROZEN_MAIN_SEED",
            "trainability": "TRAIN_FROM_SCRATCH_ALL_METHODS_SHARED",
            "peft": False,
            "test_fitted_scaling": False,
        }
        if policy.get("schema_version") != 1 or policy.get("artifact") != "RC_HSG_BACKBONE_A_POLICY_V1" or policy.get("policy_id") != "RC_HSG_NATIVE_SPECTRAL_A1_V1" or policy.get("decision_basis") != "OUTCOME_BLIND_AUTHOR_POLICY":
            _error(errors, "V21_A_POLICY_IDENTITY_MISMATCH", "schema/artifact/policy/decision basis")
        if policy.get("selected") != expected_selected:
            _error(errors, "V21_A_POLICY_SELECTED_MISMATCH", "selected interface differs from frozen policy")
        expected_rejections = {
            "TRUST_ALIGN_A1_SPECTRAL": "REJECT_PRIMARY_EXTERNAL_SOURCE_LICENSE_NOT_FOUND_NO_CODE_COPY",
            "TRUST_ALIGN_LABRAM_A3": "REJECT_PRIMARY_UNIT_CHANNEL_FILTER_CHECKPOINT_INTERFACE_UNRESOLVED",
            "OFFICIAL_NEUROLM_B_VQ": "REJECT_PRIMARY_MICROVOLT_CHANNEL_ADAPTER_AND_UNDOWNLOADED_WEIGHT_GAPS",
        }
        ledger = policy.get("candidate_ledger", {})
        actual_rejections = {key: value.get("primary_decision") for key, value in ledger.items()} if isinstance(ledger, dict) else {}
        if actual_rejections != expected_rejections:
            _error(errors, "V21_A_POLICY_REJECTION_MISMATCH", repr(actual_rejections))

    for relative, expected in FROZEN_RUN_011_HASHES.items():
        path = root / relative
        if not path.is_file():
            _error(errors, "V21_FROZEN_ARTIFACT_MISSING", relative)
        elif _sha256(path) != expected:
            _error(errors, "V21_FROZEN_ARTIFACT_HASH_MISMATCH", relative)

    split = _load_yaml(root / "artifacts/split_manifest.yaml", errors, "split manifest")
    if isinstance(split, dict) and split.get("assertions", {}).get("test_status") != "LOCKED_UNTIL_ROUTE_LOCK":
        _error(errors, "V21_TEST_LOCK_MISMATCH", repr(split.get("assertions", {}).get("test_status")))


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    state_path = root / "PROJECT_STATE.yaml"
    tasks_path = root / "TASKS.yaml"
    state = _load_yaml(state_path, errors, "PROJECT_STATE.yaml")
    tasks = _load_yaml(tasks_path, errors, "TASKS.yaml")
    if not isinstance(state, dict) or not isinstance(tasks, dict):
        return errors

    missing_ids = sorted(REQUIRED_TASK_IDS - set(tasks))
    if missing_ids:
        _error(errors, "REQUIRED_TASK_MISSING", ", ".join(missing_ids))

    blockers = state.get("blockers", [])
    if not isinstance(blockers, list):
        _error(errors, "BLOCKERS_NOT_LIST", "PROJECT_STATE.blockers")
        blockers = []
    blocked_ids: set[str] = set()
    for index, blocker in enumerate(blockers):
        if not isinstance(blocker, dict):
            _error(errors, "BLOCKER_INVALID", f"index {index} is not a mapping")
            continue
        for field in ("id", "reason", "blocks", "resolution"):
            value = blocker.get(field)
            if value is None or value == "" or value == []:
                _error(
                    errors,
                    "BLOCKER_FIELD_MISSING",
                    f"blocker {blocker.get('id', index)!r}: {field}",
                )
        blocks = blocker.get("blocks", [])
        if not isinstance(blocks, list):
            _error(errors, "BLOCKER_BLOCKS_NOT_LIST", str(blocker.get("id", index)))
            continue
        for task_id in blocks:
            if task_id not in tasks:
                _error(
                    errors,
                    "BLOCKER_UNKNOWN_TASK",
                    f"{blocker.get('id')}: {task_id}",
                )
            elif isinstance(task_id, str):
                blocked_ids.add(task_id)

    for task_id, task in tasks.items():
        if not isinstance(task, dict):
            _error(errors, "TASK_NOT_MAPPING", task_id)
            continue
        missing_fields = sorted(REQUIRED_TASK_FIELDS - set(task))
        if missing_fields:
            _error(
                errors,
                "TASK_FIELD_MISSING",
                f"{task_id}: {', '.join(missing_fields)}",
            )
        status = task.get("status")
        if status not in ALLOWED_STATUSES:
            _error(errors, "ILLEGAL_STATUS", f"{task_id}: {status!r}")
        for field in ("prerequisites", "produces", "acceptance"):
            if field in task and not isinstance(task[field], list):
                _error(errors, "TASK_FIELD_NOT_LIST", f"{task_id}.{field}")
        prerequisites = task.get("prerequisites", [])
        if isinstance(prerequisites, list):
            for prerequisite in prerequisites:
                if prerequisite not in tasks:
                    _error(
                        errors,
                        "UNKNOWN_PREREQUISITE",
                        f"{task_id}: {prerequisite}",
                    )

        prerequisites_done = _prerequisites_done(task, tasks)
        if status == "READY":
            if not prerequisites_done:
                _error(errors, "READY_PREREQUISITE_NOT_DONE", task_id)
            if task_id in blocked_ids:
                _error(errors, "READY_BLOCKED", task_id)
            if task_id == "S0_A_INTERFACE" and task.get("owner") != "CODEX":
                _error(errors, "A_INTERFACE_OWNER_MISMATCH", task_id)
        elif status == "DONE":
            if not prerequisites_done:
                _error(errors, "DONE_PREREQUISITE_NOT_DONE", task_id)
            completed_by_run = task.get("completed_by_run")
            run_path = _run_record_path(root, completed_by_run)
            if run_path is None:
                _error(errors, "DONE_RUN_MISSING", f"{task_id}: completed_by_run")
            elif not run_path.is_file():
                _error(errors, "DONE_RUN_MISSING", f"{task_id}: {run_path}")
            produces = task.get("produces", [])
            if isinstance(produces, list):
                for artifact in produces:
                    artifact_path = _safe_relative_path(root, artifact)
                    if artifact_path is None:
                        _error(errors, "ARTIFACT_PATH_INVALID", f"{task_id}: {artifact!r}")
                    elif not artifact_path.exists():
                        _error(errors, "DONE_ARTIFACT_MISSING", f"{task_id}: {artifact}")
            evidence = task.get("acceptance_evidence")
            if not isinstance(evidence, list) or not evidence:
                _error(errors, "DONE_ACCEPTANCE_EVIDENCE_MISSING", task_id)
            else:
                valid_evidence: list[str] = []
                for item in evidence:
                    evidence_path = _safe_relative_path(root, item)
                    if evidence_path is None:
                        _error(
                            errors,
                            "DONE_ACCEPTANCE_EVIDENCE_PATH_INVALID",
                            f"{task_id}: {item!r}",
                        )
                    elif not evidence_path.exists():
                        _error(
                            errors,
                            "DONE_ACCEPTANCE_EVIDENCE_MISSING_PATH",
                            f"{task_id}: {item}",
                        )
                    else:
                        valid_evidence.append(str(item))
                non_run = [item for item in valid_evidence if not item.startswith("runs/")]
                if not non_run and any(not str(item).startswith("runs/") for item in produces):
                    _error(errors, "DONE_ACCEPTANCE_EVIDENCE_MISSING", f"{task_id}: run-only evidence")
        elif status == "BLOCKED":
            if not isinstance(task.get("blocked_reason"), str) or not task.get(
                "blocked_reason", ""
            ).strip():
                _error(errors, "BLOCKED_REASON_MISSING", task_id)
            if prerequisites_done and task_id not in blocked_ids:
                _error(
                    errors,
                    "BLOCKED_WITHOUT_CAUSE",
                    f"{task_id}: prerequisites are DONE and no active blocker names it",
                )

    _check_cycles(tasks, errors)
    _check_gate_order(tasks, errors)
    _check_v21_contract(root, state, tasks, errors)

    project = state.get("project")
    if not isinstance(project, dict):
        _error(errors, "PROJECT_SECTION_INVALID", "project must be a mapping")
        project = {}
    _check_active_spec_entrypoints(root, project, errors)
    for field, code in (
        ("spec_path", "SPEC_PATH_INVALID"),
        ("management_contract_path", "MANAGEMENT_CONTRACT_PATH_INVALID"),
    ):
        path = _safe_relative_path(root, project.get(field))
        if path is None or not path.is_file():
            _error(errors, code, repr(project.get(field)))
    spec_version = project.get("spec_version")
    spec_path_value = project.get("spec_path", "")
    spec_path = _safe_relative_path(root, spec_path_value)
    spec_header = ""
    if spec_path is not None and spec_path.is_file():
        try:
            with spec_path.open("r", encoding="utf-8") as handle:
                spec_header = "".join(handle.readline() for _ in range(5))
        except OSError:
            pass
    version_token = spec_version.replace(".", "_") if isinstance(spec_version, str) else ""
    if (
        not isinstance(spec_version, str)
        or SPEC_VERSION_RE.fullmatch(spec_version) is None
        or version_token not in Path(str(spec_path_value)).name
        or spec_version not in spec_header
    ):
        _error(
            errors,
            "SPEC_VERSION_MISMATCH",
            f"version={spec_version!r}, path={spec_path_value!r}",
        )
    if COMMIT_RE.fullmatch(str(project.get("reviewed_commit", ""))) is None:
        _error(errors, "REVIEWED_COMMIT_INVALID", repr(project.get("reviewed_commit")))

    execution = state.get("execution", {})
    if not isinstance(execution, dict) or execution.get("status") not in ALLOWED_STATUSES:
        _error(
            errors,
            "EXECUTION_STATUS_INVALID",
            repr(execution.get("status") if isinstance(execution, dict) else execution),
        )

    gates = state.get("gates", {})
    if not isinstance(gates, dict):
        _error(errors, "GATES_SECTION_INVALID", "gates must be a mapping")
        gates = {}
    for key, task_id in V21_ACTIVE_GATES.items():
        gate = gates.get(key, {})
        if not isinstance(gate, dict):
            _error(errors, "GATE_INVALID", key)
            continue
        if gate.get("status") not in ALLOWED_STATUSES:
            _error(errors, "GATE_STATUS_INVALID", f"{key}: {gate.get('status')!r}")
        if gate.get("outcome") not in ALLOWED_GATE_OUTCOMES:
            _error(errors, "GATE_OUTCOME_INVALID", f"{key}: {gate.get('outcome')!r}")
        task_status = tasks.get(task_id, {}).get("status")
        if gate.get("status") != task_status:
            _error(
                errors,
                "GATE_TASK_STATUS_MISMATCH",
                f"{key}={gate.get('status')!r}, {task_id}={task_status!r}",
            )
        if task_status == "DONE" and gate.get("outcome") is None:
            _error(errors, "GATE_OUTCOME_REQUIRED", task_id)
        if task_status != "DONE" and gate.get("outcome") is not None:
            _error(errors, "PREMATURE_GATE_OUTCOME", task_id)

    route = state.get("route", {})
    if not isinstance(route, dict):
        _error(errors, "ROUTE_SECTION_INVALID", "route must be a mapping")
        route = {}
    locked = route.get("locked")
    route_lock_done = tasks.get("ROUTE_LOCK", {}).get("status") == "DONE"
    if isinstance(locked, list):
        if len(locked) > 1:
            _error(errors, "MULTIPLE_ROUTES_LOCKED", repr(locked))
        locked_values = set(locked)
    elif locked is None:
        locked_values = set()
    elif isinstance(locked, str):
        locked_values = {locked} if locked else set()
    else:
        _error(errors, "ROUTE_LOCK_INVALID", repr(locked))
        locked_values = set()
    illegal_routes = locked_values - ALLOWED_LOCKED_ROUTES
    if illegal_routes:
        _error(errors, "ROUTE_VALUE_INVALID", repr(sorted(illegal_routes)))
    locked_by_run = route.get("locked_by_run")
    if route_lock_done:
        if not isinstance(locked, str) or not locked:
            _error(errors, "ROUTE_LOCK_REQUIRED", repr(locked))
        if not isinstance(locked_by_run, str) or not locked_by_run.strip():
            _error(errors, "ROUTE_LOCK_RUN_MISSING", repr(locked_by_run))
        else:
            lock_run_path = _run_record_path(root, locked_by_run)
            if lock_run_path is None or not lock_run_path.is_file():
                _error(errors, "ROUTE_LOCK_RUN_MISSING", repr(locked_by_run))
    else:
        if locked_values:
            _error(errors, "ROUTE_LOCK_PREMATURE", repr(sorted(locked_values)))
        if locked_by_run not in (None, ""):
            _error(errors, "ROUTE_LOCK_PREMATURE", f"locked_by_run={locked_by_run!r}")

    last_completed = state.get("last_completed_task")
    if last_completed is not None and tasks.get(last_completed, {}).get("status") != "DONE":
        _error(errors, "LAST_COMPLETED_NOT_DONE", repr(last_completed))
    last_run = _safe_relative_path(root, state.get("last_run"))
    if last_run is None or not last_run.is_file():
        _error(errors, "LAST_RUN_MISSING", repr(state.get("last_run")))
    else:
        expected_run_id = last_run.stem
        if state.get("updated_by_run") != expected_run_id:
            _error(
                errors,
                "UPDATED_BY_RUN_MISMATCH",
                f"expected {expected_run_id!r}, got {state.get('updated_by_run')!r}",
            )
        if isinstance(last_completed, str):
            completed_by = tasks.get(last_completed, {}).get("completed_by_run")
            completed_path = _run_record_path(root, completed_by)
            if completed_path is None or completed_path.resolve() != last_run.resolve():
                _error(
                    errors,
                    "LAST_COMPLETED_RUN_MISMATCH",
                    f"{last_completed}: {completed_by!r}",
                )

    candidates = ready_tasks(tasks, state)
    recommended = state.get("recommended_next_task")
    if candidates:
        if recommended not in tasks:
            _error(errors, "RECOMMENDATION_UNKNOWN", repr(recommended))
        elif tasks[recommended].get("status") != "READY":
            _error(errors, "RECOMMENDATION_NOT_READY", repr(recommended))
        elif recommended in blocked_ids or not _prerequisites_done(tasks[recommended], tasks):
            _error(errors, "RECOMMENDATION_INELIGIBLE", repr(recommended))
        if recommended != candidates[0]:
            _error(
                errors,
                "RECOMMENDATION_MISMATCH",
                f"expected {candidates[0]!r}, got {recommended!r}",
            )
    elif recommended is not None:
        _error(
            errors,
            "RECOMMENDATION_WITHOUT_READY_TASK",
            repr(recommended),
        )

    next_task_path = root / "CODEX_NEXT_TASK.md"
    try:
        next_task_text = next_task_path.read_text(encoding="utf-8")
    except OSError:
        _error(errors, "NEXT_TASK_STALE", "CODEX_NEXT_TASK.md missing or unreadable")
    else:
        if recommended is not None and str(recommended) not in next_task_text:
            _error(errors, "NEXT_TASK_STALE", f"missing recommended task {recommended}")
        if recommended is None and "NO_READY_TASK" not in next_task_text:
            _error(errors, "NEXT_TASK_STALE", "missing NO_READY_TASK")

    for relative in SNAPSHOT_PATHS:
        snapshot = _load_yaml(root / relative, errors, relative)
        if not isinstance(snapshot, dict):
            continue
        for field in ("generated_by_run", "updated_by_run"):
            run_id = snapshot.get(field)
            run_path = _run_record_path(root, run_id)
            if not isinstance(run_id, str) or not run_id.strip() or run_path is None or not run_path.is_file():
                _error(errors, "SNAPSHOT_PROVENANCE_RUN_MISSING", f"{relative}.{field}={run_id!r}")
        commit = snapshot.get("evidence_as_of_commit")
        if COMMIT_RE.fullmatch(str(commit or "")) is None:
            _error(errors, "SNAPSHOT_PROVENANCE_COMMIT_INVALID", f"{relative}: {commit!r}")

    try:
        state_text = state_path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover - already caught during YAML load
        _error(errors, "STATE_READ_FAILED", str(exc))
    else:
        for marker in sorted(FOREIGN_PROJECT_MARKERS):
            if marker in state_text:
                _error(errors, "FOREIGN_PROJECT_STATE", marker)

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="project root; defaults to the parent of scripts/",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    errors = validate(root)
    if errors:
        print("PROJECT STATE INVALID")
        for item in errors:
            print(item)
        return 1
    tasks = _load_yaml(root / "TASKS.yaml", [], "TASKS.yaml")
    done = sum(
        isinstance(task, dict) and task.get("status") == "DONE"
        for task in tasks.values()
    )
    print(f"PROJECT STATE VALID | tasks={len(tasks)} | done={done}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
