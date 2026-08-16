#!/usr/bin/env python3
"""Print the cold-start NC-HSG project snapshot and next valid task."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

from check_project_state import ready_tasks, validate


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    return value if isinstance(value, dict) else {}


def render(root: Path) -> str:
    root = root.resolve()
    state = _load(root / "PROJECT_STATE.yaml")
    tasks = _load(root / "TASKS.yaml")
    errors = validate(root)
    candidates = ready_tasks(tasks, state)
    recommended = state.get("recommended_next_task")

    project = state.get("project", {})
    execution = state.get("execution", {})
    route = state.get("route", {})
    locked = route.get("locked")
    route_text = "unlocked" if locked in (None, []) else str(locked)
    blockers = state.get("blockers", [])
    last_completed = state.get("last_completed_task")

    lines = [
        "PROJECT SNAPSHOT",
        "",
        f"Spec: {project.get('spec_version')} | {project.get('spec_path')}",
        f"Current stage: {execution.get('stage')} ({execution.get('status')})",
        (
            f"Current route: {route_text} | primary={route.get('primary')} "
            f"| backup={route.get('backup')}"
        ),
        f"Last completed: {last_completed or 'none'}",
        "Active blockers:",
    ]
    if isinstance(blockers, list) and blockers:
        for blocker in blockers:
            if isinstance(blocker, dict):
                lines.append(f"- {blocker.get('id')}: {blocker.get('reason')}")
    else:
        lines.append("- none")

    lines.extend(["", "Ready tasks:"])
    if candidates:
        for index, task_id in enumerate(candidates, 1):
            lines.append(f"{index}. {task_id}: {tasks[task_id].get('title')}")
    else:
        lines.append("1. none")

    lines.extend(["", "Recommended next task:"])
    if recommended in tasks and recommended in candidates:
        lines.append(f"{recommended}: {tasks[recommended].get('title')}")
        why = tasks[recommended].get("why_ready")
        if not why:
            acceptance = tasks[recommended].get("acceptance", [])
            why = acceptance[0] if acceptance else "It is the first eligible task."
    else:
        lines.append("none")
        why = "No task is READY with all prerequisites DONE and no active blocker."
    lines.extend(["Why:", str(why)])

    lines.extend(["", "Blocked downstream:"])
    blocked_tasks = [
        task_id
        for task_id, task in tasks.items()
        if isinstance(task, dict) and task.get("status") == "BLOCKED"
    ]
    if blocked_tasks:
        for task_id in sorted(blocked_tasks):
            lines.append(
                f"- {task_id}: {tasks[task_id].get('blocked_reason', 'blocked')}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "Do not do yet:"])
    do_not = state.get("do_not_do_yet", [])
    if isinstance(do_not, list) and do_not:
        lines.extend(f"- {item}" for item in do_not)
    else:
        lines.append("- none")

    if errors:
        lines.extend(["", "Validation errors:"])
        lines.extend(f"- {item}" for item in errors)
    return "\n".join(lines)


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
    print(render(root))
    return 1 if validate(root) else 0


if __name__ == "__main__":
    sys.exit(main())
