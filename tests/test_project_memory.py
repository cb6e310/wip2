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
            content = f"# fixture {self.state['project']['spec_version']}\n" if field == "spec_path" else f"fixture {field}\n"
            path.write_text(content, encoding="utf-8")
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
        (self.root / "CODEX_NEXT_TASK.md").write_text(
            "NO_READY_TASK\n" if self.state.get("recommended_next_task") is None else str(self.state["recommended_next_task"]),
            encoding="utf-8",
        )
        for relative in CHECKER.SNAPSHOT_PATHS:
            source = yaml.safe_load((PROJECT_ROOT / relative).read_text(encoding="utf-8"))
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(yaml.safe_dump(source, sort_keys=False), encoding="utf-8")
        for relative in (
            "artifacts/backbone_a_policy.yaml",
            *CHECKER.FROZEN_RUN_011_HASHES,
            *CHECKER.V22_OUTPUT_HASHES,
            *CHECKER.V23_OUTPUT_HASHES,
            *CHECKER.V24_OUTPUT_HASHES,
            *CHECKER.V25_FIXED_INPUT_HASHES,
            *CHECKER.V25_OUTPUT_HASHES,
            *CHECKER.V26_FIXED_INPUT_HASHES,
            *CHECKER.V26_OUTPUT_HASHES,
            *CHECKER.V27_FIXED_INPUT_HASHES,
            *CHECKER.V27_IMPLEMENTATION_HASHES,
            *CHECKER.V27_OUTPUT_HASHES,
            *CHECKER.V28_FIXED_INPUT_HASHES,
            *CHECKER.V28_IMPLEMENTATION_HASHES,
            *CHECKER.V28_OUTPUT_HASHES,
            *CHECKER.V293_FIXED_HASHES,
            "src/rc_hsg/backbones/native_spectral_a1.py",
            "scripts/validate_a1_frontend.py",
            "scripts/audit_a_path_leakage.py",
            "scripts/admit_a1_outer_train.py",
            "scripts/audit_n1_block_feasibility.py",
            "tests/test_audit_n1_block_feasibility.py",
            "tests/test_admit_a1_outer_train.py",
            "tests/test_validate_a1_frontend.py",
        ):
            source = PROJECT_ROOT / relative
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        entry = (
            f"Active SPEC: `{self.state['project']['spec_path']}` "
            f"(version `{self.state['project']['spec_version']}`).\n"
        )
        for name in ("AGENTS.md", "AI_START_HERE.md", "HANDOFF.md", "PACKAGE_README.md"):
            (self.root / name).write_text(entry, encoding="utf-8")

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

    def test_active_spec_entrypoints_agree(self) -> None:
        self.assertFalse(any(e.startswith("ENTRYPOINT_SPEC_MISMATCH:") for e in self._errors()))

    def test_agents_wrong_spec_path_fails(self) -> None:
        (self.root / "AGENTS.md").write_text("v1.2 guide/old_spec.md\n", encoding="utf-8")
        self._assert_code(self._errors(), "ENTRYPOINT_SPEC_MISMATCH")

    def test_ai_start_wrong_version_fails(self) -> None:
        path = self.state["project"]["spec_path"]
        (self.root / "AI_START_HERE.md").write_text(f"{path} version v1.2\n", encoding="utf-8")
        self._assert_code(self._errors(), "ENTRYPOINT_SPEC_MISMATCH")

    def test_package_readme_wrong_spec_fails(self) -> None:
        (self.root / "PACKAGE_README.md").write_text(
            "Active SPEC: `guide/old.md` (version `v1.8`).\n", encoding="utf-8"
        )
        self._assert_code(self._errors(), "ENTRYPOINT_SPEC_MISMATCH")

    def test_missing_agents_fails(self) -> None:
        (self.root / "AGENTS.md").unlink()
        self._assert_code(self._errors(), "FILE_MISSING")

    def _complete_for_order_test(self, task_id: str) -> None:
        task = self.tasks[task_id]
        task["status"] = "DONE"
        task["completed_by_run"] = "fixture_order"
        task["acceptance_evidence"] = ["fixture_order_evidence.txt"]
        run = self.root / "runs" / "fixture_order.md"
        run.parent.mkdir(parents=True, exist_ok=True)
        run.write_text("fixture\n", encoding="utf-8")
        (self.root / "fixture_order_evidence.txt").write_text("fixture\n", encoding="utf-8")
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
        self.state["blockers"][0]["blocks"].append("S0_SEMANTIC_ITEM")
        self._assert_code(self._errors(), "READY_BLOCKED")

    def test_blocked_without_reason_fails(self) -> None:
        self.tasks["S0_METHOD_LEAKAGE_AUDIT"].pop("blocked_reason", None)
        self._assert_code(self._errors(), "BLOCKED_REASON_MISSING")

    def test_recommendation_must_be_ready(self) -> None:
        self.state["recommended_next_task"] = "S0_DATA_CARD"
        self._assert_code(self._errors(), "RECOMMENDATION_NOT_READY")

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

    def test_gate_r0_order_fails(self) -> None:
        self._complete_for_order_test("GATE_R0")
        self.tasks["S0_N2_SAMPLER"]["status"] = "BLOCKED"
        self.tasks["S0_N2_SAMPLER"]["blocked_reason"] = "fixture"
        self.state["gates"]["gate_r0"].update(status="DONE", outcome="PASS")
        self._assert_code(self._errors(), "GATE_R0_ORDER")

    def test_gate_r_order_fails(self) -> None:
        self._complete_for_order_test("GATE_R")
        self.state["gates"]["gate_r"].update(status="DONE", outcome="PASS")
        self._assert_code(self._errors(), "GATE_R_ORDER")

    def test_gate_c_order_fails(self) -> None:
        self._complete_for_order_test("GATE_C")
        self.state["gates"]["gate_c"].update(status="DONE", outcome="PASS")
        self._assert_code(self._errors(), "GATE_C_ORDER")

    def test_gate_h_order_fails(self) -> None:
        self._complete_for_order_test("GATE_H")
        self.state["gates"]["gate_h"].update(status="DONE", outcome="PASS")
        self._assert_code(self._errors(), "GATE_H_ORDER")

    def test_mechanism_a_order_fails(self) -> None:
        self._complete_for_order_test("MECHANISM_A")
        self.state["gates"]["mechanism_a"].update(status="DONE", outcome="PASS")
        self._assert_code(self._errors(), "MECHANISM_A_ORDER")

    def test_route_lock_order_fails(self) -> None:
        self._complete_for_order_test("ROUTE_LOCK")
        self._assert_code(self._errors(), "ROUTE_LOCK_ORDER")

    def test_main_experiment_order_fails(self) -> None:
        self._complete_for_order_test("MAIN_EXPERIMENT")
        self._assert_code(self._errors(), "MAIN_EXPERIMENT_ORDER")

    def test_dual_route_lock_fails(self) -> None:
        self.state["route"]["locked"] = ["RC_HSG", "FLAT_RC"]
        self.state["route"]["locked_by_run"] = "fixture"
        self._assert_code(self._errors(), "MULTIPLE_ROUTES_LOCKED")

    def test_v293_current_spec_passes(self) -> None:
        self.assertEqual(self._errors(), [])

    def test_v293_task_counts_and_ready_set(self) -> None:
        self.assertEqual(len(self.tasks), 79)
        self.assertEqual(
            sum(task["status"] == "DONE" for task in self.tasks.values()), 48
        )
        self.assertEqual(
            [task_id for task_id, task in self.tasks.items() if task["status"] == "READY"],
            ["S0_SEMANTIC_ITEM"],
        )

    def test_v21_superseded_tasks_are_locked(self) -> None:
        for task_id in CHECKER.V21_SUPERSEDED_TASKS:
            task = self.tasks[task_id]
            self.assertEqual(task["status"], "SKIPPED")
            self.assertFalse(task["critical_path"])
            self.assertEqual(task["skip_reason"], "SUPERSEDED_BY_RC_HSG_V21")

    def test_v28_dependency_rewrite_is_exact(self) -> None:
        for task_id, expected in CHECKER.V23_DEPENDENCIES.items():
            self.assertEqual(set(self.tasks[task_id]["prerequisites"]), expected)

    def test_v21_active_gate_set_is_exact(self) -> None:
        self.assertEqual(set(self.state["gates"]), set(CHECKER.V21_ACTIVE_GATES))
        self.assertEqual(self.state["gates"]["gate_r0"], {"status": "DONE", "outcome": "FAIL_NO_PRIMARY_REFERENCE"})
        self.assertTrue(all(
            item["status"] == "BLOCKED" and item["outcome"] is None
            for key, item in self.state["gates"].items() if key != "gate_r0"
        ))

    def test_v28_a_policy_tamper_fails(self) -> None:
        policy_path = self.root / "artifacts/backbone_a_policy.yaml"
        policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
        policy["selected"]["sampling_hz"] = 200
        policy_path.write_text(
            yaml.safe_dump(policy, sort_keys=False), encoding="utf-8"
        )
        self._assert_code(CHECKER.validate(self.root), "V293_ARTIFACT_HASH_MISMATCH")

    def test_v28_frozen_split_tamper_fails(self) -> None:
        path = self.root / "artifacts/split_manifest.yaml"
        path.write_text(
            path.read_text(encoding="utf-8") + "# tamper\n", encoding="utf-8"
        )
        self._assert_code(CHECKER.validate(self.root), "V293_ARTIFACT_HASH_MISMATCH")

    def test_v28_a_contract_tamper_fails(self) -> None:
        path = self.root / "artifacts/backbone_a_contract.yaml"
        path.write_bytes(path.read_bytes() + b"\n# tamper\n")
        self._assert_code(CHECKER.validate(self.root), "V293_ARTIFACT_HASH_MISMATCH")

    def test_v293_b9_and_b4_are_closed_and_b3_does_not_block_resolver(self) -> None:
        b9 = next(item for item in self.state["superseded_blockers"] if item["id"] == "B_V9_A_FULL_OUTER_TRAIN_ADMISSION_PENDING")
        b4 = next(item for item in self.state["superseded_blockers"] if item["id"] == "B_V4_NULL_CONTRACT_UNVERIFIED")
        b3 = next(item for item in self.state["blockers"] if item["id"] == "B_V3_SCHEMA_UNFROZEN")
        self.assertEqual(b9["closed_by"], "S0_A1_ADMISSION")
        self.assertEqual(b4["closed_by"], "GATE_R0")
        self.assertNotIn("S0_SEMANTIC_ITEM", b3["blocks"])

    def test_v28_feasibility_artifact_tamper_fails(self) -> None:
        path = self.root / "artifacts/nulls/n1_block_feasibility.yaml"
        artifact = yaml.safe_load(path.read_text(encoding="utf-8"))
        artifact["decision"]["decision"] = "PASS"
        path.write_text(yaml.safe_dump(artifact, sort_keys=False), encoding="utf-8")
        self._assert_code(CHECKER.validate(self.root), "V293_ARTIFACT_HASH_MISMATCH")

    def test_v28_ledger_tamper_fails(self) -> None:
        path = self.root / "artifacts/nulls/n1_block_assignment_v1.jsonl"
        path.write_bytes(path.read_bytes() + b"\n")
        self._assert_code(CHECKER.validate(self.root), "V293_ARTIFACT_HASH_MISMATCH")

    def test_v28_n1_contract_tamper_fails(self) -> None:
        path = self.root / "artifacts/nulls/n1_contract.yaml"
        contract = yaml.safe_load(path.read_text(encoding="utf-8"))
        contract["parity"]["fixed_points_total"] = 35528
        path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
        self._assert_code(CHECKER.validate(self.root), "V293_ARTIFACT_HASH_MISMATCH")

    def test_v28_manifest_tamper_fails(self) -> None:
        path = self.root / "artifacts/nulls/n1_permutation_manifest_v1.jsonl"
        path.write_bytes(path.read_bytes() + b"\n")
        self._assert_code(CHECKER.validate(self.root), "V293_ARTIFACT_HASH_MISMATCH")

    def test_v28_n2_contract_tamper_fails(self) -> None:
        path = self.root / "artifacts/nulls/n2_contract.yaml"
        contract = yaml.safe_load(path.read_text(encoding="utf-8"))
        contract["downstream_boundary"]["n2_primary_admitted"] = True
        path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
        self._assert_code(CHECKER.validate(self.root), "V293_ARTIFACT_HASH_MISMATCH")

    def test_v28_provenance_correction_tamper_fails(self) -> None:
        path = self.root / "artifacts/governance/run018_provenance_correction.yaml"
        correction = yaml.safe_load(path.read_text(encoding="utf-8"))
        correction["scientific_state_changed"] = True
        path.write_text(yaml.safe_dump(correction, sort_keys=False), encoding="utf-8")
        self._assert_code(CHECKER.validate(self.root), "V293_ARTIFACT_HASH_MISMATCH")

    def test_v293_branch_owner_tamper_fails(self) -> None:
        self.tasks["S0_SEMANTIC_ITEM"]["owner"] = "CODEX"
        self._assert_code(self._errors(), "V293_READY_SET_MISMATCH")

    def test_v293_branch_status_tamper_fails(self) -> None:
        self.tasks["S0_SEMANTIC_ITEM"]["status"] = "BLOCKED"
        self.tasks["S0_SEMANTIC_ITEM"]["blocked_reason"] = "fixture"
        self._assert_code(self._errors(), "V293_TASK_STATE_MISMATCH")

    def test_v28_frontend_validator_tamper_fails(self) -> None:
        path = self.root / "scripts/validate_a1_frontend.py"
        path.write_bytes(path.read_bytes() + b"\n# tamper\n")
        self._assert_code(CHECKER.validate(self.root), "V293_ARTIFACT_HASH_MISMATCH")

    def test_v28_leakage_artifact_tamper_fails(self) -> None:
        path = self.root / "artifacts/a_path_leakage_assertions.yaml"
        path.write_bytes(path.read_bytes() + b"\n# tamper\n")
        self._assert_code(CHECKER.validate(self.root), "V293_ARTIFACT_HASH_MISMATCH")

    def test_v28_admission_ledger_tamper_fails(self) -> None:
        path = self.root / "artifacts/a1_outer_train_admission_v1.jsonl"
        path.write_bytes(path.read_bytes() + b"\n")
        self._assert_code(CHECKER.validate(self.root), "V293_ARTIFACT_HASH_MISMATCH")

    def test_v28_admission_freeze_tamper_fails(self) -> None:
        path = self.root / "artifacts/a1_outer_train_admission_freeze.yaml"
        freeze = yaml.safe_load(path.read_text(encoding="utf-8"))
        freeze["safety"]["run014_panel_arrays_reread"] = 1
        path.write_text(yaml.safe_dump(freeze, sort_keys=False), encoding="utf-8")
        errors = CHECKER.validate(self.root)
        self._assert_code(errors, "V293_ARTIFACT_HASH_MISMATCH")

    def test_v28_b9_active_again_fails(self) -> None:
        b9 = next(item for item in self.state["superseded_blockers"] if item["id"] == "B_V9_A_FULL_OUTER_TRAIN_ADMISSION_PENDING")
        self.state["blockers"].append({
            "id": b9["id"],
            "reason": "fixture",
            "blocks": ["S0_N1_BLOCK_FEASIBILITY"],
            "resolution": "fixture",
        })
        self._assert_code(self._errors(), "V293_B9_CLOSURE_MISMATCH")

    def test_spec_filename_mismatch_fails(self) -> None:
        self.state["project"]["spec_path"] = "guide/NC_HSG_Paper_Spec_v1_2_fixture.md"
        self._assert_code(self._errors(), "SPEC_VERSION_MISMATCH")

    def test_spec_header_mismatch_fails(self) -> None:
        path = self.root / self.state["project"]["spec_path"]
        path.write_text("# fixture v9.9\n", encoding="utf-8")
        self._save()
        self._assert_code(CHECKER.validate(self.root), "SPEC_VERSION_MISMATCH")

    def test_route_done_requires_locked_value(self) -> None:
        self._complete_for_order_test("ROUTE_LOCK")
        self.state["route"]["locked"] = None
        self.state["route"]["locked_by_run"] = "fixture_order"
        self._assert_code(self._errors(), "ROUTE_LOCK_REQUIRED")

    def test_route_lock_run_must_exist(self) -> None:
        self._complete_for_order_test("ROUTE_LOCK")
        self.state["route"]["locked"] = "RC_HSG"
        self.state["route"]["locked_by_run"] = "missing_lock_run"
        self._assert_code(self._errors(), "ROUTE_LOCK_RUN_MISSING")

    def test_route_cannot_be_premature(self) -> None:
        self.state["route"]["locked"] = "RC_HSG"
        self._assert_code(self._errors(), "ROUTE_LOCK_PREMATURE")

    def test_done_acceptance_evidence_required(self) -> None:
        self.tasks["S0_ENVIRONMENT_SYNC"].pop("acceptance_evidence")
        self._assert_code(self._errors(), "DONE_ACCEPTANCE_EVIDENCE_MISSING")

    def test_done_acceptance_evidence_invalid_path_fails(self) -> None:
        self.tasks["S0_ENVIRONMENT_SYNC"]["acceptance_evidence"] = ["../outside"]
        self._assert_code(self._errors(), "DONE_ACCEPTANCE_EVIDENCE_PATH_INVALID")

    def test_done_acceptance_evidence_missing_path_fails(self) -> None:
        self.tasks["S0_ENVIRONMENT_SYNC"]["acceptance_evidence"] = ["missing.txt"]
        self._assert_code(self._errors(), "DONE_ACCEPTANCE_EVIDENCE_MISSING_PATH")

    def test_updated_by_run_must_match_last_run(self) -> None:
        self.state["updated_by_run"] = "wrong_run"
        self._assert_code(self._errors(), "UPDATED_BY_RUN_MISMATCH")

    def test_snapshot_updated_run_required(self) -> None:
        relative = CHECKER.SNAPSHOT_PATHS[0]
        snapshot = yaml.safe_load((self.root / relative).read_text(encoding="utf-8"))
        snapshot.pop("updated_by_run")
        (self.root / relative).write_text(yaml.safe_dump(snapshot), encoding="utf-8")
        self._save()
        self._assert_code(CHECKER.validate(self.root), "SNAPSHOT_PROVENANCE_RUN_MISSING")

    def test_snapshot_commit_required(self) -> None:
        relative = CHECKER.SNAPSHOT_PATHS[0]
        snapshot = yaml.safe_load((self.root / relative).read_text(encoding="utf-8"))
        snapshot["evidence_as_of_commit"] = "bad"
        (self.root / relative).write_text(yaml.safe_dump(snapshot), encoding="utf-8")
        self._save()
        self._assert_code(CHECKER.validate(self.root), "SNAPSHOT_PROVENANCE_COMMIT_INVALID")

    def test_snapshot_run_must_exist(self) -> None:
        relative = CHECKER.SNAPSHOT_PATHS[0]
        snapshot = yaml.safe_load((self.root / relative).read_text(encoding="utf-8"))
        snapshot["updated_by_run"] = "missing_snapshot_run"
        (self.root / relative).write_text(yaml.safe_dump(snapshot), encoding="utf-8")
        self._save()
        self._assert_code(CHECKER.validate(self.root), "SNAPSHOT_PROVENANCE_RUN_MISSING")

    def test_stale_next_task_fails(self) -> None:
        (self.root / "CODEX_NEXT_TASK.md").write_text("bootstrap again\n", encoding="utf-8")
        self._save()
        self._assert_code(CHECKER.validate(self.root), "NEXT_TASK_STALE")

    def test_semantic_item_requires_author_owner(self) -> None:
        self.tasks["S0_SEMANTIC_ITEM"]["owner"] = "CODEX"
        self._assert_code(self._errors(), "V293_READY_SET_MISMATCH")

    def test_discovery_is_first_after_hardening(self) -> None:
        task = self.tasks["S0_INPUT_DISCOVERY_AUDIT"]
        task["status"] = "READY"
        task.pop("completed_by_run", None)
        task.pop("acceptance_evidence", None)
        self.assertEqual(CHECKER.ready_tasks(self.tasks, self.state)[0], "S0_INPUT_DISCOVERY_AUDIT")

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
