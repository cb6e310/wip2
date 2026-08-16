#!/usr/bin/env python3
"""Validate the NC-HSG file-based project memory system.

The validator deliberately fails closed: a task cannot claim readiness or
completion without its declared prerequisites, evidence, run record, and gate
ordering.  Scientific unknowns remain blockers rather than inferred facts.
"""

from __future__ import annotations

import argparse
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
    "FULL_NC_HSG",
    "TOPIC_LEVEL",
    "FLAT_NULL_GATED",
    "PRIOR_CORRECTION",
    "NEGATIVE_AUDIT",
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
}
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
    if tasks.get("GATE_A1", {}).get("status") == "DONE":
        _require_done(
            tasks,
            ("S0_LEAKAGE_AUDIT", "S0_N1_SAMPLER", "S0_N2_SAMPLER"),
            errors,
            "GATE_A1_ORDER",
        )

    if tasks.get("GATE_A1", {}).get("status") != "DONE":
        forbidden_done = [
            task_id
            for task_id in ("S0_SEMANTIC_ITEM", "STAGE1_PROBES", "SHAM_VALIDATION")
            if tasks.get(task_id, {}).get("status") == "DONE"
        ]
        if forbidden_done:
            _error(
                errors,
                "SEMANTIC_BEFORE_GATE_A1",
                "DONE before GATE_A1: " + ", ".join(forbidden_done),
            )

    if tasks.get("GATE_A", {}).get("status") == "DONE":
        _require_done(
            tasks,
            (
                "GATE_A1",
                "STAGE1_PROBES",
                "SHAM_VALIDATION",
                "S0_SCHEMA_AUDIT",
                "S0_GATE_A_POPULATION_E5",
            ),
            errors,
            "GATE_A_ORDER",
        )

    if tasks.get("GATE_B", {}).get("status") == "DONE":
        _require_done(
            tasks,
            (
                "GATE_A",
                "S0_NC_HSG_CORE",
                "S0_DIRECT_C",
                "S0_PMI_BASELINE",
                "S0_ALIGN_UNIT_COST",
            ),
            errors,
            "GATE_B_ORDER",
        )

    if tasks.get("ROUTE_LOCK", {}).get("status") == "DONE":
        _require_done(
            tasks,
            ("GATE_A", "GATE_B", "S0_CALIBRATION_CONTRACT"),
            errors,
            "ROUTE_LOCK_ORDER",
        )

    if tasks.get("MAIN_EXPERIMENT", {}).get("status") == "DONE":
        _require_done(
            tasks,
            ("ROUTE_LOCK", "S0_LEAKAGE_AUDIT", "S0_ALIGN_UNIT_COST"),
            errors,
            "MAIN_EXPERIMENT_ORDER",
        )


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

    project = state.get("project")
    if not isinstance(project, dict):
        _error(errors, "PROJECT_SECTION_INVALID", "project must be a mapping")
        project = {}
    for field, code in (
        ("spec_path", "SPEC_PATH_INVALID"),
        ("management_contract_path", "MANAGEMENT_CONTRACT_PATH_INVALID"),
    ):
        path = _safe_relative_path(root, project.get(field))
        if path is None or not path.is_file():
            _error(errors, code, repr(project.get(field)))
    spec_version = project.get("spec_version")
    spec_path_value = project.get("spec_path", "")
    if spec_version != "v1.2" or "v1_2" not in str(spec_path_value):
        _error(
            errors,
            "SPEC_VERSION_MISMATCH",
            f"version={spec_version!r}, path={spec_path_value!r}",
        )

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
    for key, task_id in (("gate_a1", "GATE_A1"), ("gate_a", "GATE_A"), ("gate_b", "GATE_B")):
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
    if isinstance(locked, list):
        if len(locked) > 1:
            _error(errors, "MULTIPLE_ROUTES_LOCKED", repr(locked))
        locked_values = set(locked)
    elif locked is None:
        locked_values = set()
    elif isinstance(locked, str):
        locked_values = {locked}
    else:
        _error(errors, "ROUTE_LOCK_INVALID", repr(locked))
        locked_values = set()
    illegal_routes = locked_values - ALLOWED_LOCKED_ROUTES
    if illegal_routes:
        _error(errors, "ROUTE_VALUE_INVALID", repr(sorted(illegal_routes)))
    if locked_values:
        if tasks.get("ROUTE_LOCK", {}).get("status") != "DONE":
            _error(errors, "ROUTE_LOCK_PREMATURE", repr(sorted(locked_values)))
        if not route.get("locked_by_run"):
            _error(errors, "ROUTE_LOCK_RUN_MISSING", repr(sorted(locked_values)))

    last_completed = state.get("last_completed_task")
    if last_completed is not None and tasks.get(last_completed, {}).get("status") != "DONE":
        _error(errors, "LAST_COMPLETED_NOT_DONE", repr(last_completed))
    last_run = _safe_relative_path(root, state.get("last_run"))
    if last_run is None or not last_run.is_file():
        _error(errors, "LAST_RUN_MISSING", repr(state.get("last_run")))

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
