from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_joint_split", ROOT / "scripts/build_joint_split.py")
assert SPEC and SPEC.loader
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class BuildJointSplitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._class_temp = tempfile.TemporaryDirectory()
        cls.output_root = Path(cls._class_temp.name) / "first"
        cls.result = BUILDER.build(project_root=ROOT, output_root=cls.output_root)
        cls.regime_i = json.loads((cls.output_root / BUILDER.OUTPUTS["regime_i"]).read_text())
        cls.regime_ii = json.loads((cls.output_root / BUILDER.OUTPUTS["regime_ii"]).read_text())
        cls.manifest = yaml.safe_load((cls.output_root / BUILDER.OUTPUTS["manifest"]).read_text())
        cls.population = yaml.safe_load((cls.output_root / BUILDER.OUTPUTS["population"]).read_text())

    @classmethod
    def tearDownClass(cls) -> None:
        cls._class_temp.cleanup()

    def _fixture_root(self) -> Path:
        root = Path(tempfile.mkdtemp(dir=self._class_temp.name))
        for relative, _ in BUILDER.INPUTS.values():
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
        return root

    @staticmethod
    def _hashes(root: Path) -> dict[str, str]:
        return {label: BUILDER.sha256_file(root / contract[0]) for label, contract in BUILDER.INPUTS.items()}

    def test_fixed_input_hashes_and_output_paths(self) -> None:
        for _, (relative, expected) in BUILDER.INPUTS.items():
            self.assertEqual(BUILDER.sha256_file(ROOT / relative), expected)
        self.assertEqual(set(BUILDER.OUTPUTS), {"regime_i", "regime_ii", "manifest", "population", "report"})

    def test_primary_and_calibration_assignment_contracts(self) -> None:
        primary = self.result["primary"]
        reserve = self.result["reserve"]
        self.assertEqual(primary.iterations, 25)
        self.assertEqual(primary.objective, BUILDER.EXPECTED_PRIMARY_OBJECTIVE)
        self.assertEqual(primary.ledger_sha256, BUILDER.EXPECTED_PRIMARY_LEDGER)
        self.assertEqual(reserve.iterations, 6)
        self.assertEqual(reserve.objective, BUILDER.EXPECTED_CAL_OBJECTIVE)
        self.assertEqual(reserve.ledger_sha256, BUILDER.EXPECTED_CAL_LEDGER)
        self.assertEqual(Counter(primary.assignments.values()), Counter(dict(zip(BUILDER.PRIMARY_ROLES, BUILDER.PRIMARY_CAPACITIES))))
        self.assertEqual(Counter(reserve.assignments.values()), Counter(dict(zip(BUILDER.CAL_ROLES, BUILDER.CAL_CAPACITIES))))

    def test_regime_i_full_coverage_order_and_allowlist(self) -> None:
        groups = self.regime_i["group_assignments"]
        rows = self.regime_i["row_assignments"]
        self.assertEqual(len(groups), 342)
        self.assertEqual([row["stimulus_group_id"] for row in groups], sorted(row["stimulus_group_id"] for row in groups))
        self.assertEqual(sum(len(row["member_exact_stimulus_ids"]) for row in groups), 344)
        self.assertEqual(sorted(slot for row in groups for slot in row["member_slots"]), list(range(1, 350)))
        self.assertEqual(len(rows), 5905)
        self.assertEqual(len({(row["subject"], row["slot"]) for row in rows}), 5905)
        self.assertEqual(len({row["occurrence_id"] for row in rows}), 349)
        self.assertTrue(all(set(row) == BUILDER.REGIME_I_ROW_FIELDS for row in rows))
        self.assertEqual(rows, sorted(rows, key=lambda row: (row["subject"], row["slot"], row["occurrence_id"])))
        self.assertTrue(all(row["calibration_reserve"] is None for row in rows if row["role"] != "cal"))
        self.assertEqual(self.regime_i["test_status"], "LOCKED_UNTIL_ROUTE_LOCK")

    def test_fixed_summaries_and_subject_population(self) -> None:
        for role, expected in BUILDER.EXPECTED_ROLE_SUMMARY.items():
            row = self.manifest["role_summary"][role]
            self.assertEqual((row["groups"], row["occurrences"], row["analysis_rows"], row["block_occurrences"], row["per_subject_row_min"], row["per_subject_row_max"]), expected)
        for role, expected in BUILDER.EXPECTED_CAL_SUMMARY.items():
            row = self.manifest["calibration_reserve_summary"][role]
            self.assertEqual((row["groups"], row["occurrences"], row["analysis_rows"], row["block_occurrences"], row["per_subject_row_min"], row["per_subject_row_max"]), expected)
        self.assertEqual(self.population["regime_i_confirmatory_population"]["test_rows_by_subject"], BUILDER.EXPECTED_TEST_ROWS)

    def test_regime_ii_folds_reconstruct_without_leakage(self) -> None:
        self.assertEqual(self.regime_ii["fold_count"], 18)
        self.assertEqual([fold["held_out_subject"] for fold in self.regime_ii["folds"]], list(BUILDER.SUBJECTS))
        roles = {row["stimulus_group_id"]: row["role"] for row in self.regime_i["group_assignments"]}
        canonical_rows = self.regime_i["row_assignments"]
        for fold in self.regime_ii["folds"]:
            held_out = fold["held_out_subject"]
            counts = Counter()
            ledger = bytearray()
            test_ids = []
            for row in canonical_rows:
                status = BUILDER._fold_status(row["subject"], roles[row["stimulus_group_id"]], held_out)
                counts[status] += 1
                ledger.extend(f"{fold['fold_id']}\t{row['occurrence_id']}\t{status}\n".encode())
                if status == "test":
                    self.assertEqual(row["subject"], held_out)
                    self.assertEqual(roles[row["stimulus_group_id"]], "test")
                    test_ids.append(row["occurrence_id"])
                if status in ("train_fit", "inner_val", "cal"):
                    self.assertNotEqual(row["subject"], held_out)
                    self.assertNotEqual(roles[row["stimulus_group_id"]], "test")
            self.assertEqual(dict(counts), fold["counts"])
            self.assertEqual(hashlib.sha256(ledger).hexdigest(), fold["canonical_membership_ledger_sha256"])
            self.assertEqual(sorted(test_ids), fold["test_occurrence_ids"])
            self.assertEqual(sum(counts.values()), 5905)

    def test_population_aggregation_and_bootstrap(self) -> None:
        contract = self.population["aggregation_contract"]
        self.assertEqual(contract["independent_cluster_allowlist"], ["subject"])
        self.assertFalse(contract["zero_fill"])
        self.assertFalse(contract["silent_subject_deletion"])
        self.assertEqual(contract["missing_frozen_subject_action"], "CONFIRMATORY_GATE_NOT_EVALUABLE")
        digest, retries = BUILDER.bootstrap_index_hash()
        self.assertEqual(digest, BUILDER.EXPECTED_BOOTSTRAP)
        self.assertEqual(self.population["paired_subject_bootstrap"]["index_bytes_sha256"], digest)
        self.assertEqual(self.population["paired_subject_bootstrap"]["total_retries"], retries)
        self.assertFalse(self.population["paired_subject_bootstrap"]["binary_indices_committed"])

    def test_integer_objective_hash_order_and_tie_determinism(self) -> None:
        features = {
            "sg_v1_" + character * 64: tuple([index % 3] * 18 + [index % 2] * 7 + [1])
            for index, character in enumerate("1234", 1)
        }
        first = BUILDER.balance_assignment(features, ("left", "right"), (2, 2), b"fixture\0")
        second = BUILDER.balance_assignment(features, ("left", "right"), (2, 2), b"fixture\0")
        self.assertEqual(first, second)
        self.assertTrue(all(isinstance(value, int) for value in first.objective))
        self.assertEqual(first.ledger_sha256, hashlib.sha256(BUILDER._canonical_assignment_ledger(first.assignments)).hexdigest())

    def test_forbidden_fields_are_not_emitted(self) -> None:
        forbidden = {"material_line", "raw_channels", "raw_samples", "raw_shape", "source_locator", "stimulus_sha256"}

        def keys(value):
            found = set()
            if isinstance(value, dict):
                found.update(value)
                for child in value.values():
                    found.update(keys(child))
            elif isinstance(value, list):
                for child in value:
                    found.update(keys(child))
            return found

        for artifact in (self.regime_i, self.regime_ii, self.manifest, self.population):
            self.assertFalse(keys(artifact) & forbidden)
        produced = {path.relative_to(self.output_root).as_posix() for path in self.output_root.rglob("*") if path.is_file()}
        self.assertEqual(produced, {path.as_posix() for path in BUILDER.OUTPUTS.values()})

    def test_each_input_hash_tamper_fails_closed(self) -> None:
        for label, (relative, _) in BUILDER.INPUTS.items():
            root = self._fixture_root()
            with (root / relative).open("ab") as handle:
                handle.write(b"\n")
            with self.assertRaisesRegex(BUILDER.JointSplitError, "JOINT_SPLIT_INPUT_HASH_MISMATCH"):
                BUILDER.build(project_root=root, output_root=root / "out")

    def test_missing_extra_and_unknown_analysis_fields_fail_closed(self) -> None:
        for operation in ("missing_row", "extra_row", "unknown_field"):
            root = self._fixture_root()
            path = root / BUILDER.INPUTS["analysis_view"][0]
            lines = path.read_text().splitlines()
            if operation == "missing_row":
                lines.pop()
            elif operation == "extra_row":
                lines.append(lines[-1])
            else:
                row = json.loads(lines[0])
                row["unknown"] = 1
                lines[0] = json.dumps(row, sort_keys=True)
            path.write_text("\n".join(lines) + "\n")
            with self.assertRaises(BUILDER.JointSplitError):
                BUILDER.build(project_root=root, output_root=root / "out", expected_hashes=self._hashes(root))

    def test_path_escape_symlink_and_unknown_cli_fail_closed(self) -> None:
        with self.assertRaisesRegex(BUILDER.JointSplitError, "OUTPUT_PATH_ESCAPE"):
            BUILDER.build(project_root=ROOT, output_root=Path(".."))
        root = self._fixture_root()
        input_path = root / BUILDER.INPUTS["stimulus_identity"][0]
        outside = root / "outside.yaml"
        shutil.copyfile(input_path, outside)
        input_path.unlink()
        try:
            input_path.symlink_to(outside)
            with self.assertRaisesRegex(BUILDER.JointSplitError, "INPUT_SYMLINK"):
                BUILDER.build(project_root=root, output_root=root / "out")
        except OSError:
            with mock.patch.object(Path, "is_symlink", autospec=True, side_effect=lambda path: path == input_path):
                with self.assertRaisesRegex(BUILDER.JointSplitError, "INPUT_SYMLINK"):
                    BUILDER.build(project_root=root, output_root=root / "out")
        finally:
            input_path.unlink(missing_ok=True)
            shutil.copyfile(outside, input_path)
        for args in (["--seed", "1"], ["--capacity", "1"], ["--objective", "x"], ["extra"]):
            with self.assertRaises(SystemExit):
                BUILDER.main(args)

    def test_failed_validation_preserves_existing_outputs(self) -> None:
        root = self._fixture_root()
        output_root = root / "out"
        for relative in BUILDER.OUTPUTS.values():
            path = output_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"sentinel")
        with (root / BUILDER.INPUTS["data_card"][0]).open("ab") as handle:
            handle.write(b"\n")
        with self.assertRaises(BUILDER.JointSplitError):
            BUILDER.build(project_root=root, output_root=output_root)
        self.assertTrue(all((output_root / relative).read_bytes() == b"sentinel" for relative in BUILDER.OUTPUTS.values()))

    def test_two_complete_builds_are_byte_identical(self) -> None:
        second_root = Path(self._class_temp.name) / "second"
        second = BUILDER.build(project_root=ROOT, output_root=second_root)
        self.assertEqual(self.result["output_sha256"], second["output_sha256"])
        for relative in BUILDER.OUTPUTS.values():
            self.assertEqual((self.output_root / relative).read_bytes(), (second_root / relative).read_bytes())


if __name__ == "__main__":
    unittest.main()
