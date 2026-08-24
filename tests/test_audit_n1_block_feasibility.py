from __future__ import annotations

import ast
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import h5py
import numpy as np
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_n1_block_feasibility.py"
VALIDATOR_PATH = ROOT / "scripts" / "validate_a1_frontend.py"


def _import(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


n1 = _import("audit_n1_block_feasibility", SCRIPT)
validator = _import("audit_n1_block_feasibility_test_validator", VALIDATOR_PATH)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")


def _key(row: dict) -> tuple[str, int, str]:
    return row["subject"], row["slot"], row["occurrence_id"]


class N1Fixture:
    def __init__(self, root: Path, *, fault: str | None = None):
        self.project = root / "project"
        self.dataset = root / "dataset"
        self.canonical = root / "canonical"
        self.verify_a = root / "verify-a"
        self.verify_b = root / "verify-b"
        self.project.mkdir()
        self.dataset.mkdir()
        self.rows: list[tuple[str, int, str, str, int, int, str, str]] = []
        for subject in ("S1", "S2"):
            for slot in range(1, 5):
                self.rows.append((subject, slot, f"{subject}t{slot}", "train_fit", 500, 1, "ELIGIBLE", "RUN_FRONTEND"))
            for slot in range(5, 7):
                self.rows.append((subject, slot, f"{subject}v{slot}", "inner_val", 500, 1, "ELIGIBLE", "RUN_FRONTEND"))
            self.rows.append((subject, 7, f"{subject}s7", "train_fit", 100, 0, "A_INTERFACE_SHORT_SEGMENT", "FORCED_L0_NO_FRONTEND"))
            self.rows.append((subject, 8, f"{subject}s8", "inner_val", 100, 0, "A_INTERFACE_SHORT_SEGMENT", "FORCED_L0_NO_FRONTEND"))
            self.rows.append((subject, 9, f"{subject}c9", "cal", 500, 1, "ELIGIBLE", "RUN_FRONTEND"))
            self.rows.append((subject, 10, f"{subject}e10", "test", 500, 1, "ELIGIBLE", "RUN_FRONTEND"))
        self._write_metadata(fault)
        self._write_hdf5(fault)
        self._write_source_metadata()

    @staticmethod
    def _relative(subject: str) -> str:
        return f"task1 - NR/Matlab files/results{subject}_NR.mat"

    def _write_metadata(self, fault: str | None) -> None:
        eligibility = []
        analysis = []
        admission = []
        for subject, slot, occurrence, role, samples, windows, status, action in self.rows:
            eligibility.append({
                "occurrence_id": occurrence, "subject": subject, "slot": slot, "role": role,
                "calibration_reserve": "cal_select_reserve" if role == "cal" else None,
                "raw_samples": samples, "window_count": windows,
                "a_interface_status": status, "action": action,
            })
            analysis.append({
                "block": 1, "material_line": slot, "occurrence_id": occurrence,
                "raw_channels": 105, "raw_samples": samples, "raw_shape": [samples, 105],
                "session": 1, "slot": slot,
                "source_locator": {"field": "rawData", "slot": slot, "summary_file": self._relative(subject)},
                "stimulus_sha256": "0" * 64, "subject": subject, "task": "NR",
            })
            if role not in n1.OUTER_ROLES:
                continue
            eligible = status == "ELIGIBLE"
            admission.append({
                "subject": subject, "slot": slot, "occurrence_id": occurrence, "role": role,
                "raw_samples": samples, "window_count": windows, "a_interface_status": status,
                "action": action, "evidence_source": "RUN016_STREAMING_FRONTEND_PASS" if eligible else "SHORT_FORCED_L0_NO_READ",
                "source_file": self._relative(subject), "source_field": "rawData",
                "source_dataset_read_run016": eligible, "source_dataset_read_cumulative": eligible,
                "source_dtype": "float64" if eligible else "NOT_READ",
                "source_shape_status": "PASS" if eligible else "NOT_APPLICABLE",
                "input_finite_status": "PASS" if eligible else "NOT_APPLICABLE",
                "frontend_status": "PASS" if eligible else "NOT_APPLICABLE_FORCED_L0",
                "observed_window_count": windows, "window_mask_status": "PASS" if eligible else "NOT_APPLICABLE",
                "output_finite_status": "PASS" if eligible else "NOT_APPLICABLE",
            })
        eligibility.sort(key=_key)
        analysis.sort(key=_key)
        admission.sort(key=_key)
        if fault == "duplicate":
            admission.append(dict(admission[0]))
        if fault == "test_unlock":
            test_status = "UNLOCKED"
        else:
            test_status = "LOCKED_UNTIL_ROUTE_LOCK"
        _write_jsonl(self.project / n1.FIXED_INPUTS["eligibility"][0], eligibility)
        _write_jsonl(self.project / n1.FIXED_INPUTS["analysis_view"][0], analysis)
        _write_jsonl(self.project / n1.FIXED_INPUTS["admission_ledger"][0], admission)
        split_path = self.project / n1.FIXED_INPUTS["split_regime_i"][0]
        split_path.parent.mkdir(parents=True, exist_ok=True)
        split_path.write_text(json.dumps({"test_status": test_status}) + "\n", encoding="utf-8")
        for label, (relative, _) in n1.FIXED_INPUTS.items():
            destination = self.project / relative
            if destination.exists():
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            if label in {"frontend_validator", "a_code"}:
                shutil.copy2(ROOT / relative, destination)
            elif label == "feasibility_code":
                shutil.copy2(SCRIPT, destination)
            else:
                destination.write_text(f"fixture: {label}\n", encoding="utf-8")

    def _write_hdf5(self, fault: str | None) -> None:
        frequencies = (3.0, 3.0, 15.0, 15.0, 3.0, 15.0)
        for subject in ("S1", "S2"):
            path = self.dataset / self._relative(subject)
            path.parent.mkdir(parents=True, exist_ok=True)
            with h5py.File(path, "w") as handle:
                sentence = handle.create_group("sentenceData")
                references = sentence.create_dataset("rawData", (349, 1), dtype=h5py.ref_dtype)
                refs = handle.create_group("refs")
                for row in [item for item in self.rows if item[0] == subject and item[3] in n1.OUTER_ROLES and item[6] == "ELIGIBLE"]:
                    _, slot, _, _, samples, _, _, _ = row
                    time = np.arange(samples, dtype=np.float64) / 500.0
                    frequency = frequencies[slot - 1]
                    channels = np.arange(105, dtype=np.float64)[:, None]
                    values = np.sin(2.0 * np.pi * frequency * time[None, :] + channels * 0.01).T
                    if fault == "nonfinite" and subject == "S1" and slot == 1:
                        values[0, 0] = np.nan
                    target = refs.create_dataset(f"raw_{slot}", data=values)
                    references[slot - 1, 0] = target.ref
                sentence.create_dataset("content", data=np.zeros((349, 1), dtype=np.uint8))

    def _write_source_metadata(self) -> None:
        subjects = ("S1", "S2")
        targeted = {
            "schema_version": 3,
            "authorized_dataset_root_recorded": str(self.dataset.resolve()),
            "summary_schema": [{"subject": subject, "path": self._relative(subject)} for subject in subjects],
        }
        path = self.project / n1.FIXED_INPUTS["targeted_manifest_v3"][0]
        path.write_text(yaml.safe_dump(targeted, sort_keys=False), encoding="utf-8")
        files = [
            {"path": self._relative(subject), "size_bytes": (self.dataset / self._relative(subject)).stat().st_size, "sha256": "1" * 64}
            for subject in subjects
        ]
        path = self.project / n1.FIXED_INPUTS["osf_file_metadata"][0]
        path.write_text(yaml.safe_dump({"schema_version": 1, "files": files}, sort_keys=False), encoding="utf-8")

    def run(self) -> dict[str, str]:
        with mock.patch.object(n1, "_load_validator", return_value=validator):
            return n1.audit_n1_block_feasibility(
                self.project, self.dataset, self.canonical, (self.verify_a, self.verify_b),
                enforce_frozen_expectations=False,
            )


def _assigned_row(subject: str, role: str, slot: int, power_bin: str, *, evaluable: bool = True) -> dict:
    return {
        "subject": subject, "session": 1, "slot": slot, "occurrence_id": f"o{slot}",
        "role": role, "raw_samples": 500, "window_count": 1, "a_interface_status": "ELIGIBLE",
        "action": "RUN_FRONTEND", "length_bin": "W01_04", "power_bin": power_bin,
        "power_edge_cell_id": n1._power_cell_id(subject, 1, "W01_04"), "power_edge_status": "PASS",
        "block_id": n1._block_id(role, subject, 1, "W01_04", power_bin),
        "block_size": 2 if evaluable else 1, "n1_evaluable": evaluable,
        "n1_status": "N1_EVALUABLE" if evaluable else "N1_NOT_EVALUABLE_SINGLETON",
        "source_file": f"results{subject}.mat", "source_field": "rawData",
        "source_dataset_read_run017": True,
    }


class N1BlockFeasibilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_one_scan_exact_once_and_three_identical_renders(self) -> None:
        fixture = N1Fixture(self.root)
        reads = []
        original = validator._read_raw

        def tracked(row, *args, **kwargs):
            reads.append(_key(row))
            return original(row, *args, **kwargs)

        with mock.patch.object(validator, "_read_raw", side_effect=tracked), mock.patch.object(n1, "_load_validator", return_value=validator):
            hashes = n1.audit_n1_block_feasibility(
                fixture.project, fixture.dataset, fixture.canonical, (fixture.verify_a, fixture.verify_b),
                enforce_frozen_expectations=False,
            )
        expected = {_key(row) for row in json.loads("[" + ",".join((fixture.project / n1.FIXED_INPUTS["admission_ledger"][0]).read_text().splitlines()) + "]") if row["a_interface_status"] == "ELIGIBLE"}
        self.assertEqual(set(reads), expected)
        self.assertEqual(len(reads), len(set(reads)))
        self.assertEqual(set(hashes), set(n1.OUTPUTS.values()))
        for relative in n1.OUTPUTS.values():
            self.assertEqual((fixture.verify_a / relative).read_bytes(), (fixture.verify_b / relative).read_bytes())
            self.assertEqual((fixture.verify_a / relative).read_bytes(), (fixture.canonical / relative).read_bytes())

    def test_ledger_schema_short_no_read_and_no_forbidden_output(self) -> None:
        fixture = N1Fixture(self.root)
        fixture.run()
        ledger_path = fixture.canonical / n1.OUTPUTS["ledger"]
        rows = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines()]
        self.assertTrue(all(tuple(row) == n1.LEDGER_FIELDS for row in rows))
        short = [row for row in rows if row["a_interface_status"] == "A_INTERFACE_SHORT_SEGMENT"]
        self.assertTrue(short and all(not row["source_dataset_read_run017"] for row in short))
        combined = b"".join((fixture.canonical / relative).read_bytes() for relative in n1.OUTPUTS.values()).lower()
        for forbidden in (b"row_proxy_value", b"recipient_row_key", b"donor_row_key", b'"donor_mapping":', b"stimulus_sha256", b"waveform_hash", b"embedding_hash", b"token_values"):
            self.assertNotIn(forbidden, combined)

    def test_full_forward_is_never_called_and_scan_order_is_exact(self) -> None:
        fixture = N1Fixture(self.root)
        reads = []
        original_read = validator._read_raw
        original_class = validator.NativeSpectralA1

        class NoForward(original_class):
            def forward(self, *args, **kwargs):
                raise AssertionError("full forward is forbidden")

        def tracked(row, *args, **kwargs):
            reads.append((row["subject"], row["session"], row["length_bin"], row["role"], row["slot"], row["occurrence_id"]))
            return original_read(row, *args, **kwargs)

        with mock.patch.object(validator, "NativeSpectralA1", NoForward), mock.patch.object(validator, "_read_raw", side_effect=tracked), mock.patch.object(n1, "_load_validator", return_value=validator):
            n1.audit_n1_block_feasibility(fixture.project, fixture.dataset, fixture.canonical, (fixture.verify_a, fixture.verify_b), enforce_frozen_expectations=False)
        self.assertEqual(reads, sorted(reads))

    def test_ast_is_audited_loader_and_tokenizer_only(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        imports |= {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertNotIn("h5py", imports)
        self.assertEqual(source.count("validator._read_raw("), 1)
        self.assertEqual(source.count("model._spectral_tokens("), 1)
        self.assertNotIn("model(", source)
        self.assertNotIn("torch.fft", source)

    def test_length_boundaries_are_exact(self) -> None:
        expected = {1: "W01_04", 4: "W01_04", 5: "W05_16", 16: "W05_16", 17: "W17_PLUS"}
        self.assertEqual({value: n1._length_bin(value) for value in expected}, expected)
        with self.assertRaisesRegex(n1.N1BlockFeasibilityError, "N1_FEASIBILITY_SCOPE_MISMATCH"):
            n1._length_bin(0)

    def test_proxy_two_middle_statistics_and_scale_invariance(self) -> None:
        torch = validator.torch
        values = torch.arange(1, 9, dtype=torch.float32).reshape(1, 8).repeat(1, 105)
        self.assertEqual(n1._token_proxy(torch, values), 4.5)
        model = validator.NativeSpectralA1(20260824).eval()
        time = torch.arange(500, dtype=torch.float32) / 500.0
        trial = torch.sin(2.0 * math.pi * 8.0 * time).repeat(105, 1)
        with torch.inference_mode():
            one = n1._token_proxy(torch, model._spectral_tokens(trial, 500))
            scaled = n1._token_proxy(torch, model._spectral_tokens(trial * 7.0, 500))
        self.assertLess(abs(one - scaled), 1.0e-4)

    def test_edge_n3_n4_hex_and_tie_rule(self) -> None:
        rows = []
        proxies = {}
        for slot, value in enumerate((1.0, 2.0, 3.0, 4.0), start=1):
            row = {"subject": "S", "session": 1, "slot": slot, "occurrence_id": f"o{slot}", "role": "train_fit", "raw_samples": 500, "window_count": 1, "a_interface_status": "ELIGIBLE", "action": "RUN_FRONTEND", "source_file": "x", "source_field": "rawData", "length_bin": "W01_04"}
            rows.append(row)
            proxies[_key(row)] = value
        metadata = {"eligible": rows[:3]}
        edges, assigned, _ = n1._edge_and_assignments(metadata, {key: value for key, value in proxies.items() if key[1] <= 3})
        self.assertEqual(edges[0]["status"], "INSUFFICIENT_TRAIN_CELL")
        metadata = {"eligible": rows}
        edges, assigned, _ = n1._edge_and_assignments(metadata, proxies)
        self.assertEqual(float.fromhex(edges[0]["edge_float64_hex"]), 2.5)
        self.assertEqual([row["power_bin"] for row in assigned], ["P_LOW", "P_LOW", "P_HIGH", "P_HIGH"])
        proxies[_key(rows[1])] = 2.5
        proxies[_key(rows[2])] = 2.5
        _, assigned, _ = n1._edge_and_assignments(metadata, proxies)
        self.assertEqual(assigned[2]["power_bin"], "P_LOW")

    def test_inner_val_and_other_cells_never_rescue_sparse_train_cell(self) -> None:
        rows = []
        proxies = {}
        for slot in range(1, 9):
            role = "train_fit" if slot <= 3 else "inner_val"
            row = {"subject": "S", "session": 1, "slot": slot, "occurrence_id": f"o{slot}", "role": role, "raw_samples": 500, "window_count": 1, "a_interface_status": "ELIGIBLE", "action": "RUN_FRONTEND", "source_file": "x", "source_field": "rawData", "length_bin": "W01_04"}
            rows.append(row)
            proxies[_key(row)] = float(slot)
        edges, assigned, _ = n1._edge_and_assignments({"eligible": rows}, proxies)
        self.assertEqual(edges[0]["status"], "INSUFFICIENT_TRAIN_CELL")
        self.assertTrue(all(row["n1_status"] == "N1_NOT_EVALUABLE_POWER_EDGE_UNAVAILABLE" for row in assigned))

    def test_singletons_remain_in_population_denominator(self) -> None:
        rows = [_assigned_row("S", "train_fit", slot, "P_LOW", evaluable=slot < 10) for slot in range(1, 11)]
        coverage = n1._coverage(rows)
        self.assertEqual(coverage["overall"]["population_rows"], 10)
        self.assertEqual(coverage["overall"]["evaluable_rows"], 9)
        self.assertEqual(coverage["minimum_subject_role_population_coverage"], 0.9)

    def test_decision_threshold_pass_degraded_and_fail(self) -> None:
        probe = {"bijection_violations": 0, "cross_block_violations": 0, "joint_mapping_unique_count": 199}
        ledger = [_assigned_row("S", "train_fit", slot, "P_LOW") for slot in range(1, 3)]
        coverage = {"by_subject_role": [{"subject": "S", "role": "train_fit"}], "minimum_subject_role_population_coverage": 0.90}
        self.assertEqual(n1._decision(coverage, probe, ledger)["decision"], "PASS")
        coverage["minimum_subject_role_population_coverage"] = 0.899
        self.assertEqual(n1._decision(coverage, probe, ledger)["decision"], "DEGRADED_COVERAGE")
        probe["joint_mapping_unique_count"] = 198
        self.assertEqual(n1._decision(coverage, probe, ledger)["decision"], "FAIL")

    def test_199_hash_sort_bijections_unique_and_fixed_points_retained(self) -> None:
        rows = [_assigned_row("S", "train_fit", slot, "P_LOW") for slot in range(1, 6)]
        probe = n1._permutation_probe({rows[0]["block_id"]: rows})
        self.assertEqual(len(probe["replicates"]), 199)
        self.assertEqual(probe["joint_mapping_unique_count"], 199)
        self.assertEqual(probe["bijection_violations"], 0)
        self.assertEqual(probe["cross_block_violations"], 0)
        self.assertGreater(probe["fixed_points_total"], 0)
        self.assertTrue(all(set(item) == {"replicate_id", "joint_mapping_sha256", "evaluable_rows", "fixed_points"} for item in probe["replicates"]))

    def test_tampered_role_inside_block_is_rejected_structurally(self) -> None:
        rows = [_assigned_row("S", "train_fit", 1, "P_LOW"), _assigned_row("S", "inner_val", 2, "P_LOW")]
        probe = n1._permutation_probe({rows[0]["block_id"]: rows})
        self.assertGreater(probe["cross_block_violations"], 0)

    def test_duplicate_and_test_unlock_fail_before_read(self) -> None:
        for fault in ("duplicate", "test_unlock"):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as name:
                fixture = N1Fixture(Path(name), fault=fault)
                with mock.patch.object(validator, "_read_raw", side_effect=AssertionError("must not read")), mock.patch.object(n1, "_load_validator", return_value=validator):
                    with self.assertRaisesRegex(n1.N1BlockFeasibilityError, "N1_FEASIBILITY_SCOPE_MISMATCH"):
                        n1.audit_n1_block_feasibility(fixture.project, fixture.dataset, fixture.canonical, (fixture.verify_a, fixture.verify_b), enforce_frozen_expectations=False)

    def test_source_nonfinite_blocks_without_output(self) -> None:
        fixture = N1Fixture(self.root, fault="nonfinite")
        with self.assertRaisesRegex(n1.N1BlockFeasibilityError, "N1_FEASIBILITY_SOURCE_BLOCKED"):
            fixture.run()
        self.assertFalse(any((fixture.canonical / relative).exists() for relative in n1.OUTPUTS.values()))

    def test_fixed_audited_code_hash_tamper_fails_before_import(self) -> None:
        fixture = N1Fixture(self.root)
        path = fixture.project / n1.FIXED_INPUTS["frontend_validator"][0]
        path.write_bytes(path.read_bytes() + b"# tamper\n")
        with mock.patch.object(n1, "_load_validator", side_effect=AssertionError("must not import")):
            with self.assertRaisesRegex(n1.N1BlockFeasibilityError, "N1_FEASIBILITY_INPUT_MISMATCH"):
                n1.audit_n1_block_feasibility(fixture.project, fixture.dataset, fixture.canonical, (fixture.verify_a, fixture.verify_b), enforce_frozen_expectations=False)

    def test_atomic_failure_preserves_existing_canonical(self) -> None:
        fixture = N1Fixture(self.root)
        for relative in n1.OUTPUTS.values():
            path = fixture.canonical / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"sentinel\n")
        original = n1.os.replace

        def failed(source, destination):
            if str(destination).startswith(str(fixture.canonical)):
                raise OSError("synthetic")
            return original(source, destination)

        with mock.patch.object(n1.os, "replace", side_effect=failed):
            with self.assertRaisesRegex(n1.N1BlockFeasibilityError, "N1_FEASIBILITY_OUTPUT_FAILURE"):
                fixture.run()
        self.assertTrue(all((fixture.canonical / relative).read_bytes() == b"sentinel\n" for relative in n1.OUTPUTS.values()))

    def test_symlink_path_escape_and_unknown_cli_are_rejected(self) -> None:
        fixture = N1Fixture(self.root)
        target = self.root / "target"
        target.mkdir()
        link = self.root / "link"
        link.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(n1.N1BlockFeasibilityError, "N1_FEASIBILITY_OUTPUT_FAILURE"):
            n1.audit_n1_block_feasibility(fixture.project, fixture.dataset, fixture.canonical, (link, fixture.verify_b), enforce_frozen_expectations=False)
        with self.assertRaisesRegex(n1.N1BlockFeasibilityError, "N1_FEASIBILITY_INPUT_MISMATCH"):
            n1._safe_input(fixture.project, "../escape", "escape")
        for args in (("--dataset-root", "x"), ("--threshold", "0.5"), ("--replicates", "2"), ("--device", "cuda")):
            completed = subprocess.run([
                sys.executable, str(SCRIPT), "--verification-root-a", "/tmp/a",
                "--verification-root-b", "/tmp/b", *args,
            ], cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(completed.returncode, 2)
            self.assertIn("unrecognized arguments", completed.stderr)


if __name__ == "__main__":
    unittest.main()
