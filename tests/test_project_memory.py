from __future__ import annotations

import copy
import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = PROJECT_ROOT / "scripts" / "check_project_state.py"
STATUS_PATH = PROJECT_ROOT / "scripts" / "project_status.py"


def _import(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CHECKER = _import("check_project_state", CHECKER_PATH)
STATUS = _import("project_status", STATUS_PATH)


class ProjectMemoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.state = yaml.safe_load(
            (PROJECT_ROOT / "PROJECT_STATE.yaml").read_text(encoding="utf-8")
        )
        self.tasks = yaml.safe_load(
            (PROJECT_ROOT / "TASKS.yaml").read_text(encoding="utf-8")
        )
        self._materialize()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _materialize(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "PROJECT_STATE.yaml").write_text(
            yaml.safe_dump(self.state, sort_keys=False), encoding="utf-8"
        )
        (self.root / "TASKS.yaml").write_text(
            yaml.safe_dump(self.tasks, sort_keys=False), encoding="utf-8"
        )
        for field in ("spec_path", "management_contract_path"):
            path = self.root / self.state["project"][field]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"fixture {field}\n", encoding="utf-8")
        last_run = self.root / self.state["last_run"]
        last_run.parent.mkdir(parents=True, exist_ok=True)
        last_run.write_text("fixture last run\n", encoding="utf-8")
        for task in self.tasks.values():
            if not isinstance(task, dict) or task.get("status") != "DONE":
                continue
            completed_by_run = task.get("completed_by_run")
            if completed_by_run:
                relative = (
                    completed_by_run
                    if str(completed_by_run).startswith("runs/")
                    else f"runs/{completed_by_run}.md"
                )
                run = self.root / relative
                run.parent.mkdir(parents=True, exist_ok=True)
                run.write_text("fixture completed run\n", encoding="utf-8")
            for artifact in task.get("produces", []):
                path = self.root / artifact
                if path.name in {"PROJECT_STATE.yaml", "TASKS.yaml"}:
                    continue
                path.parent.mkdir(parents=True, exist_ok=True)
                if path.suffix:
                    path.write_text("fixture artifact\n", encoding="utf-8")
                else:
                    path.mkdir(parents=True, exist_ok=True)

    def _save(self) -> None:
        (self.root / "PROJECT_STATE.yaml").write_text(
            yaml.safe_dump(self.state, sort_keys=False), encoding="utf-8"
        )
        (self.root / "TASKS.yaml").write_text(
            yaml.safe_dump(self.tasks, sort_keys=False), encoding="utf-8"
        )

    def _errors(self) -> list[str]:
        self._save()
        return CHECKER.validate(self.root)

    def _assert_code(self, errors: list[str], code: str) -> None:
        self.assertTrue(
            any(item.startswith(f"{code}:") for item in errors),
            f"missing {code}; errors={errors}",
        )

    def _complete_for_order_test(self, task_id: str) -> None:
        task = self.tasks[task_id]
        task["status"] = "DONE"
        task["completed_by_run"] = "fixture_order"
        run = self.root / "runs" / "fixture_order.md"
        run.parent.mkdir(parents=True, exist_ok=True)
        run.write_text("fixture\n", encoding="utf-8")
        for artifact in task.get("produces", []):
            path = self.root / artifact
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture\n", encoding="utf-8")

    def test_current_bootstrap_state_passes(self) -> None:
        self.assertEqual(self._errors(), [])

    def test_illegal_status_fails(self) -> None:
        self.tasks["S0_DATA_CARD"]["status"] = "almost done"
        self._assert_code(self._errors(), "ILLEGAL_STATUS")

    def test_unknown_prerequisite_fails(self) -> None:
        self.tasks["S0_DATA_CARD"]["prerequisites"] = ["DOES_NOT_EXIST"]
        self._assert_code(self._errors(), "UNKNOWN_PREREQUISITE")

    def test_dependency_cycle_fails(self) -> None:
        self.tasks["SPEC_V12_REVIEW"]["prerequisites"] = [
            "S0_GOVERNANCE_BOOTSTRAP"
        ]
        self._assert_code(self._errors(), "DEPENDENCY_CYCLE")

    def test_done_missing_artifact_fails(self) -> None:
        missing = "artifacts/governance/missing_fixture.yaml"
        self.tasks["S0_REPOSITORY_AUDIT"]["produces"].append(missing)
        self._assert_code(self._errors(), "DONE_ARTIFACT_MISSING")

    def test_done_missing_run_fails(self) -> None:
        self.tasks["S0_REPOSITORY_AUDIT"]["completed_by_run"] = "missing_run"
        self._assert_code(self._errors(), "DONE_RUN_MISSING")

    def test_done_with_unfinished_prerequisite_fails(self) -> None:
        self.tasks["S0_GOVERNANCE_BOOTSTRAP"]["status"] = "BLOCKED"
        self.tasks["S0_GOVERNANCE_BOOTSTRAP"]["blocked_reason"] = "fixture"
        self._assert_code(self._errors(), "DONE_PREREQUISITE_NOT_DONE")

    def test_ready_named_by_blocker_fails(self) -> None:
        self.tasks["S0_DATA_CARD"]["status"] = "READY"
        self.tasks["S0_DATA_CARD"].pop("blocked_reason", None)
        self._assert_code(self._errors(), "READY_BLOCKED")

    def test_blocked_without_reason_fails(self) -> None:
        self.tasks["S0_DATA_CARD"].pop("blocked_reason", None)
        self._assert_code(self._errors(), "BLOCKED_REASON_MISSING")

    def test_recommendation_must_be_ready(self) -> None:
        self.state["recommended_next_task"] = "S0_DATA_CARD"
        self._assert_code(self._errors(), "RECOMMENDATION_WITHOUT_READY_TASK")

    def test_recommendation_must_be_first_ranked(self) -> None:
        template = {
            "title": "fixture",
            "stage": "fixture",
            "status": "READY",
            "critical_path": False,
            "priority": 50,
            "prerequisites": [],
            "produces": [],
            "acceptance": ["fixture"],
        }
        self.tasks["ZZ_SECOND"] = copy.deepcopy(template)
        self.tasks["AA_FIRST"] = copy.deepcopy(template)
        self.tasks["AA_FIRST"]["critical_path"] = True
        self.tasks["AA_FIRST"]["priority"] = 1
        self.state["recommended_next_task"] = "ZZ_SECOND"
        self._assert_code(self._errors(), "RECOMMENDATION_MISMATCH")

    def test_gate_a1_order_fails(self) -> None:
        self._complete_for_order_test("GATE_A1")
        self.state["gates"]["gate_a1"].update(status="DONE", outcome="PASS")
        self._assert_code(self._errors(), "GATE_A1_ORDER")

    def test_gate_a_order_fails(self) -> None:
        self._complete_for_order_test("GATE_A")
        self.state["gates"]["gate_a"].update(status="DONE", outcome="PASS")
        self._assert_code(self._errors(), "GATE_A_ORDER")

    def test_gate_b_order_fails(self) -> None:
        self._complete_for_order_test("GATE_B")
        self.state["gates"]["gate_b"].update(status="DONE", outcome="PASS")
        self._assert_code(self._errors(), "GATE_B_ORDER")

    def test_route_lock_order_fails(self) -> None:
        self._complete_for_order_test("ROUTE_LOCK")
        self._assert_code(self._errors(), "ROUTE_LOCK_ORDER")

    def test_main_experiment_order_fails(self) -> None:
        self._complete_for_order_test("MAIN_EXPERIMENT")
        self._assert_code(self._errors(), "MAIN_EXPERIMENT_ORDER")

    def test_dual_route_lock_fails(self) -> None:
        self.state["route"]["locked"] = ["FULL_NC_HSG", "TOPIC_LEVEL"]
        self.state["route"]["locked_by_run"] = "fixture"
        self._assert_code(self._errors(), "MULTIPLE_ROUTES_LOCKED")

    def test_foreign_project_state_fails(self) -> None:
        self.state["notes"] = "foreign marker 711340d"
        self._assert_code(self._errors(), "FOREIGN_PROJECT_STATE")

    def test_status_fields_and_sort_are_deterministic(self) -> None:
        template = {
            "title": "fixture",
            "stage": "fixture",
            "status": "READY",
            "critical_path": True,
            "priority": 10,
            "prerequisites": [],
            "produces": [],
            "acceptance": ["fixture"],
        }
        self.tasks["READY_B"] = copy.deepcopy(template)
        self.tasks["READY_A"] = copy.deepcopy(template)
        self.state["recommended_next_task"] = "READY_A"
        self._save()
        output_one = STATUS.render(self.root)
        output_two = STATUS.render(self.root)
        self.assertEqual(output_one, output_two)
        for label in (
            "PROJECT SNAPSHOT",
            "Spec:",
            "Current stage:",
            "Current route:",
            "Last completed:",
            "Active blockers:",
            "Ready tasks:",
            "Recommended next task:",
            "Why:",
            "Blocked downstream:",
            "Do not do yet:",
        ):
            self.assertIn(label, output_one)
        self.assertLess(output_one.index("READY_A"), output_one.index("READY_B"))


if __name__ == "__main__":
    unittest.main()
