from __future__ import annotations

import argparse
import ast
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_a_path_leakage.py"
SPEC = importlib.util.spec_from_file_location("audit_a_path_leakage", SCRIPT)
assert SPEC and SPEC.loader
audit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)


class APathLeakageAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def _build(self, name: str = "out") -> tuple[Path, dict[str, str]]:
        output = self.base / name
        hashes = audit.audit_a_path_leakage(ROOT, output)
        return output, hashes

    def _synthetic_project(self) -> Path:
        project = self.base / "synthetic"
        contracts = {**audit.FIXED_INPUTS, **audit.ADDITIONAL_INPUTS}
        for label, (relative, _) in contracts.items():
            destination = project / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if label in audit.SOURCE_LABELS or label == "audit_code":
                destination.write_bytes((ROOT / relative).read_bytes())
            else:
                destination.write_text("synthetic\n", encoding="utf-8")

        rows = [
            {"subject": "S1", "slot": 1, "occurrence_id": "O1", "role": "train_fit", "raw_samples": 600, "window_count": 1, "a_interface_status": "ELIGIBLE", "action": "RUN_FRONTEND"},
            {"subject": "S1", "slot": 2, "occurrence_id": "O2", "role": "inner_val", "raw_samples": 700, "window_count": 1, "a_interface_status": "ELIGIBLE", "action": "RUN_FRONTEND"},
            {"subject": "S1", "slot": 3, "occurrence_id": "O3", "role": "train_fit", "raw_samples": 400, "window_count": 0, "a_interface_status": "A_INTERFACE_SHORT_SEGMENT", "action": "FORCED_L0_NO_FRONTEND"},
            {"subject": "S1", "slot": 4, "occurrence_id": "O4", "role": "cal", "raw_samples": 800, "window_count": 2, "a_interface_status": "ELIGIBLE", "action": "RUN_FRONTEND"},
        ]
        split = {"outer_train_roles": ["train_fit", "inner_val"], "test_status": "LOCKED_UNTIL_ROUTE_LOCK", "row_assignments": rows}
        (project / audit.FIXED_INPUTS["split_regime_i"][0]).write_text(json.dumps(split), encoding="utf-8")
        analysis = [{"subject": row["subject"], "slot": row["slot"], "occurrence_id": row["occurrence_id"], "raw_samples": row["raw_samples"]} for row in rows]
        eligibility = [dict(row) for row in rows]
        panel = [
            {**analysis[0], "role": "train_fit", "window_count": 1, "a_interface_status": "ELIGIBLE", "action": "RUN_FRONTEND", "source_dataset_read": True},
            {**analysis[1], "role": "inner_val", "window_count": 1, "a_interface_status": "ELIGIBLE", "action": "RUN_FRONTEND", "source_dataset_read": True},
            {**analysis[2], "role": "train_fit", "window_count": 0, "a_interface_status": "A_INTERFACE_SHORT_SEGMENT", "action": "FORCED_L0_NO_FRONTEND", "source_dataset_read": False},
        ]
        for label, content in (("analysis_view", analysis), ("eligibility", eligibility), ("frontend_panel", panel)):
            path = project / audit.FIXED_INPUTS[label][0]
            path.write_text("".join(json.dumps(row) + "\n" for row in content), encoding="utf-8")
        freeze = {
            "safety": {"test_status": "LOCKED_UNTIL_ROUTE_LOCK"},
            "downstream_boundary": {"full_outer_train_admission_completed": False, "remaining_eligible_rows_not_read": 3390, "next_task": "S0_LEAKAGE_AUDIT"},
        }
        (project / audit.FIXED_INPUTS["frontend_freeze"][0]).write_text(yaml.safe_dump(freeze), encoding="utf-8")
        return project

    def test_production_static_metadata_build(self) -> None:
        output, hashes = self._build()
        artifact_path = output / audit.OUTPUTS["assertions"]
        artifact = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        self.assertEqual(list(artifact), [
            "schema_version", "artifact", "spec_version", "baseline_commit", "task",
            "evidence_scope", "input_artifacts", "audited_components", "frozen_scope",
            "assertions", "mutation_tests", "prohibited", "safety", "downstream_boundary",
        ])
        self.assertEqual([item["id"] for item in artifact["assertions"]], list(audit.ASSERTION_IDS))
        self.assertTrue(all(item["status"] == "PASS" for item in artifact["assertions"]))
        self.assertEqual([item["id"] for item in artifact["mutation_tests"]], [item[0] for item in audit.MUTATIONS])
        self.assertTrue(all(item["status"] == "PASS_REJECTED" for item in artifact["mutation_tests"]))
        self.assertFalse(artifact["safety"]["production_hdf5_opened"])
        self.assertEqual(set(hashes), set(audit.OUTPUTS.values()))

    def test_two_builds_are_byte_identical(self) -> None:
        first, first_hashes = self._build("first")
        second, second_hashes = self._build("second")
        self.assertEqual(first_hashes, second_hashes)
        for relative in audit.OUTPUTS.values():
            self.assertEqual((first / relative).read_bytes(), (second / relative).read_bytes())

    def test_repository_external_synthetic_metadata_fixture(self) -> None:
        project = self._synthetic_project()
        hashes = audit.audit_a_path_leakage(project, self.base / "synthetic-out", enforce_frozen_expectations=False)
        self.assertEqual(set(hashes), set(audit.OUTPUTS.values()))

    def test_all_twelve_in_memory_mutations_are_rejected(self) -> None:
        output, _ = self._build()
        artifact = yaml.safe_load((output / audit.OUTPUTS["assertions"]).read_text(encoding="utf-8"))
        self.assertEqual(len(artifact["mutation_tests"]), 12)
        self.assertEqual({item["status"] for item in artifact["mutation_tests"]}, {"PASS_REJECTED"})

    def test_comments_and_docstrings_do_not_supply_ast_evidence(self) -> None:
        sources = {label: (ROOT / audit.FIXED_INPUTS[label][0]).read_text(encoding="utf-8") for label in audit.SOURCE_LABELS}
        sources["frontend_validator"] = sources["frontend_validator"].replace("torch.inference_mode()", "nullcontext()") + '\n"torch.inference_mode() .eval()"\n# torch.inference_mode()\n'
        paths = {label: audit._safe_input(ROOT, relative, label) for label, (relative, _) in {**audit.FIXED_INPUTS, **audit.ADDITIONAL_INPUTS}.items()}
        audit._CURRENT_PATHS = paths
        data = audit._metadata(paths, enforce=True)
        with self.assertRaisesRegex(audit.APathLeakageAuditError, "INFERENCE_ONLY_FIREWALL"):
            audit._evaluate("INFERENCE_ONLY_FIREWALL", sources, data)

    def test_malformed_python_is_rejected(self) -> None:
        with self.assertRaisesRegex(audit.APathLeakageAuditError, "MALFORMED_PYTHON"):
            audit._parse("def broken(:\n", "synthetic")

    def test_missing_function_is_rejected(self) -> None:
        tree = ast.parse("x = 1\n")
        with self.assertRaisesRegex(audit.APathLeakageAuditError, "function:_read_raw"):
            audit._function(tree, "_read_raw", "DEREFERENCE_SCOPE_FIREWALL")

    def test_duplicate_key_is_rejected(self) -> None:
        rows = [{"subject": "S", "slot": 1, "occurrence_id": "O"}] * 2
        with self.assertRaisesRegex(audit.APathLeakageAuditError, "duplicate"):
            audit._unique_rows(rows, "synthetic")

    def test_role_drift_is_rejected(self) -> None:
        project = self._synthetic_project()
        split_path = project / audit.FIXED_INPUTS["split_regime_i"][0]
        split = json.loads(split_path.read_text(encoding="utf-8"))
        split["row_assignments"][0]["role"] = "cal_select"
        split_path.write_text(json.dumps(split), encoding="utf-8")
        with self.assertRaisesRegex(audit.APathLeakageAuditError, "SPLIT_ROLE_FIREWALL"):
            audit.audit_a_path_leakage(project, self.base / "role-out", enforce_frozen_expectations=False)

    def test_frozen_count_drift_is_rejected(self) -> None:
        project = self._synthetic_project()
        with self.assertRaisesRegex(audit.APathLeakageAuditError, "frozen-count"):
            paths = {label: audit._safe_input(project, relative, label) for label, (relative, _) in {**audit.FIXED_INPUTS, **audit.ADDITIONAL_INPUTS}.items()}
            audit._metadata(paths, enforce=True)

    def test_fixed_hash_drift_is_rejected(self) -> None:
        project = self._synthetic_project()
        with self.assertRaisesRegex(audit.APathLeakageAuditError, "hash:spec_v23"):
            audit.audit_a_path_leakage(project, self.base / "hash-out")

    def test_panel_tamper_is_rejected(self) -> None:
        project = self._synthetic_project()
        panel_path = project / audit.FIXED_INPUTS["frontend_panel"][0]
        panel = [json.loads(line) for line in panel_path.read_text(encoding="utf-8").splitlines()]
        panel[0]["role"] = "test"
        panel_path.write_text("".join(json.dumps(row) + "\n" for row in panel), encoding="utf-8")
        with self.assertRaisesRegex(audit.APathLeakageAuditError, "SPLIT_ROLE_FIREWALL|ROW_KEY_FIREWALL"):
            audit.audit_a_path_leakage(project, self.base / "panel-out", enforce_frozen_expectations=False)

    def test_test_unlock_is_rejected(self) -> None:
        project = self._synthetic_project()
        freeze_path = project / audit.FIXED_INPUTS["frontend_freeze"][0]
        freeze = yaml.safe_load(freeze_path.read_text(encoding="utf-8"))
        freeze["safety"]["test_status"] = "UNLOCKED"
        freeze_path.write_text(yaml.safe_dump(freeze), encoding="utf-8")
        with self.assertRaisesRegex(audit.APathLeakageAuditError, "TEST_AND_DOWNSTREAM_LOCK"):
            audit.audit_a_path_leakage(project, self.base / "unlock-out", enforce_frozen_expectations=False)

    def test_input_symlink_is_rejected(self) -> None:
        project = self._synthetic_project()
        target = project / audit.FIXED_INPUTS["spec_v23"][0]
        original = self.base / "outside.md"
        original.write_text("outside", encoding="utf-8")
        target.unlink()
        try:
            target.symlink_to(original)
        except OSError:
            self.skipTest("symlink creation unavailable")
        with self.assertRaisesRegex(audit.APathLeakageAuditError, "symlink"):
            audit.audit_a_path_leakage(project, self.base / "link-out", enforce_frozen_expectations=False)

    def test_relative_path_escape_is_rejected(self) -> None:
        with self.assertRaisesRegex(audit.APathLeakageAuditError, "unsafe-path"):
            audit._safe_input(ROOT, "../outside", "escape")

    def test_forbidden_data_suffix_is_rejected_before_open(self) -> None:
        with self.assertRaisesRegex(audit.APathLeakageAuditError, "unsafe-path"):
            audit._safe_input(ROOT, "production.h5", "forbidden")

    def test_unknown_cli_argument_is_rejected(self) -> None:
        completed = subprocess.run([sys.executable, str(SCRIPT), "--dataset-root", "forbidden"], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 2)
        self.assertIn("unrecognized arguments", completed.stderr)

    def test_assertion_failure_preserves_existing_outputs(self) -> None:
        output = self.base / "preserve"
        destinations = [output / relative for relative in audit.OUTPUTS.values()]
        for destination in destinations:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(b"sentinel\n")
        project = self._synthetic_project()
        split_path = project / audit.FIXED_INPUTS["split_regime_i"][0]
        split = json.loads(split_path.read_text(encoding="utf-8"))
        split["outer_train_roles"] = ["train_fit", "inner_val", "cal"]
        split_path.write_text(json.dumps(split), encoding="utf-8")
        with self.assertRaises(audit.APathLeakageAuditError):
            audit.audit_a_path_leakage(project, output, enforce_frozen_expectations=False)
        self.assertTrue(all(path.read_bytes() == b"sentinel\n" for path in destinations))

    def test_output_failure_has_stable_prefix(self) -> None:
        with mock.patch.object(audit.os, "replace", side_effect=OSError("synthetic")):
            with self.assertRaisesRegex(audit.APathLeakageAuditError, "A_PATH_AUDIT_OUTPUT_FAILURE"):
                self._build("replace-failure")

    def test_audit_module_has_no_forbidden_import_or_subprocess_call(self) -> None:
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        imports = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        imports |= {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertFalse(imports & {"h5py", "numpy", "torch", "subprocess", "rc_hsg", "validate_a1_frontend"})
        self.assertFalse(any(audit._call_name(node).startswith("subprocess") for node in ast.walk(tree) if isinstance(node, ast.Call)))


if __name__ == "__main__":
    unittest.main()
