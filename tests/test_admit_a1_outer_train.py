from __future__ import annotations

import ast
import importlib.util
import json
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
SCRIPT = ROOT / "scripts" / "admit_a1_outer_train.py"
VALIDATOR_PATH = ROOT / "scripts" / "validate_a1_frontend.py"


def _import(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


admission = _import("admit_a1_outer_train", SCRIPT)
validator = _import("admit_a1_outer_train_test_validator", VALIDATOR_PATH)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")


class AdmissionFixture:
    def __init__(self, root: Path, *, fault: str | None = None):
        self.project = root / "project"
        self.dataset = root / "dataset"
        self.canonical = root / "canonical"
        self.verify_a = root / "verify-a"
        self.verify_b = root / "verify-b"
        self.project.mkdir()
        self.dataset.mkdir()
        self.rows = [
            ("S1", 1, "a1", "train_fit", 500, 1, "ELIGIBLE", "RUN_FRONTEND"),
            ("S1", 2, "a2", "train_fit", 750, 2, "ELIGIBLE", "RUN_FRONTEND"),
            ("S1", 3, "a3", "train_fit", 1000, 3, "ELIGIBLE", "RUN_FRONTEND"),
            ("S1", 4, "a4", "train_fit", 100, 0, "A_INTERFACE_SHORT_SEGMENT", "FORCED_L0_NO_FRONTEND"),
            ("S1", 5, "a5", "cal", 500, 1, "ELIGIBLE", "RUN_FRONTEND"),
            ("S1", 6, "a6", "test", 500, 1, "ELIGIBLE", "RUN_FRONTEND"),
            ("S2", 1, "b1", "train_fit", 1250, 4, "ELIGIBLE", "RUN_FRONTEND"),
            ("S2", 3, "b3", "inner_val", 500, 1, "ELIGIBLE", "RUN_FRONTEND"),
            ("S2", 4, "b4", "inner_val", 750, 2, "ELIGIBLE", "RUN_FRONTEND"),
        ]
        self._write_project_metadata()
        self.panel = validator.select_audit_panel(self.eligibility, self.analysis)
        _write_jsonl(self.project / admission.FIXED_INPUTS["frontend_panel"][0], self.panel)
        panel_keys = {validator._row_key(row) for row in self.panel if row["source_dataset_read"]}
        self.remaining_keys = {
            validator._row_key(row) for row in self.eligibility
            if row["role"] in validator.OUTER_ROLES and row["a_interface_status"] == "ELIGIBLE"
        } - panel_keys
        self._write_hdf5(fault)
        self._write_source_metadata()

    def _relative(self, subject: str) -> str:
        return f"task1 - NR/Matlab files/results{subject}_NR.mat"

    def _write_project_metadata(self) -> None:
        self.eligibility = []
        self.analysis = []
        for subject, slot, occurrence, role, samples, windows, status, action in self.rows:
            self.eligibility.append({
                "occurrence_id": occurrence, "subject": subject, "slot": slot, "role": role,
                "calibration_reserve": "cal_select_reserve" if role == "cal" else None,
                "raw_samples": samples, "window_count": windows,
                "a_interface_status": status, "action": action,
            })
            self.analysis.append({
                "block": 1, "material_line": slot, "occurrence_id": occurrence,
                "raw_channels": 105, "raw_samples": samples, "raw_shape": [samples, 105],
                "session": 1, "slot": slot,
                "source_locator": {"field": "rawData", "slot": slot, "summary_file": self._relative(subject)},
                "stimulus_sha256": "0" * 64, "subject": subject, "task": "NR",
            })
        self.eligibility.sort(key=lambda row: (row["subject"], row["slot"], row["occurrence_id"]))
        self.analysis.sort(key=lambda row: (row["subject"], row["slot"], row["occurrence_id"]))
        _write_jsonl(self.project / admission.FIXED_INPUTS["eligibility"][0], self.eligibility)
        _write_jsonl(self.project / admission.FIXED_INPUTS["analysis_view"][0], self.analysis)
        for label, (relative, _) in admission.FIXED_INPUTS.items():
            destination = self.project / relative
            if destination.exists() or label in {"eligibility", "analysis_view", "frontend_panel"}:
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            if label in {"frontend_validator", "a_code"}:
                shutil.copy2(ROOT / relative, destination)
            elif label == "admission_code":
                shutil.copy2(SCRIPT, destination)
            else:
                destination.write_text(f"fixture: {label}\n", encoding="utf-8")

    def _write_hdf5(self, fault: str | None) -> None:
        for subject in ("S1", "S2"):
            path = self.dataset / self._relative(subject)
            path.parent.mkdir(parents=True, exist_ok=True)
            with h5py.File(path, "w") as handle:
                sentence = handle.create_group("sentenceData")
                references = sentence.create_dataset("rawData", (349, 1), dtype=h5py.ref_dtype)
                refs = handle.create_group("refs")
                for row in self.eligibility:
                    key = validator._row_key(row)
                    if row["subject"] != subject or key not in self.remaining_keys:
                        continue
                    shape = (row["raw_samples"], 105)
                    dtype = np.float32 if row["slot"] == 2 else np.float64
                    if fault == "wrong_shape" and key == sorted(self.remaining_keys)[0]:
                        shape = (105, row["raw_samples"])
                    values = np.arange(np.prod(shape), dtype=np.float64).reshape(shape) % 31
                    if fault == "nonfinite" and key == sorted(self.remaining_keys)[0]:
                        values[0, 0] = np.nan
                    target = refs.create_dataset(f"raw_{row['slot']}", data=values.astype(dtype))
                    references[row["slot"] - 1, 0] = target.ref
                sentence.create_dataset("content", data=np.zeros((349, 1), dtype=np.uint8))

    def _write_source_metadata(self) -> None:
        summary = [{"subject": subject, "path": self._relative(subject)} for subject in ("S1", "S2")]
        targeted = {"schema_version": 3, "authorized_dataset_root_recorded": str(self.dataset.resolve()), "summary_schema": summary}
        targeted_path = self.project / admission.FIXED_INPUTS["targeted_manifest_v3"][0]
        targeted_path.write_text(yaml.safe_dump(targeted, sort_keys=False), encoding="utf-8")
        files = [
            {"path": self._relative(subject), "size_bytes": (self.dataset / self._relative(subject)).stat().st_size, "sha256": "1" * 64}
            for subject in ("S1", "S2")
        ]
        osf_path = self.project / admission.FIXED_INPUTS["osf_file_metadata"][0]
        osf_path.write_text(yaml.safe_dump({"schema_version": 1, "files": files}, sort_keys=False), encoding="utf-8")

    def run(self) -> dict[str, str]:
        with mock.patch.object(validator.torch.cuda, "is_available", return_value=False), mock.patch.object(admission, "_load_validator", return_value=validator):
            return admission.admit_a1_outer_train(
                self.project, self.dataset, self.canonical, (self.verify_a, self.verify_b),
                enforce_frozen_expectations=False,
            )


class AdmitA1OuterTrainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_single_scan_reuses_panel_and_writes_three_identical_renders(self) -> None:
        fixture = AdmissionFixture(self.root)
        reads: list[tuple[str, int, str]] = []
        original = validator._read_raw

        def tracked(row, *args, **kwargs):
            reads.append(validator._row_key(row))
            return original(row, *args, **kwargs)

        with mock.patch.object(validator, "_read_raw", side_effect=tracked), mock.patch.object(validator.torch.cuda, "is_available", return_value=False), mock.patch.object(admission, "_load_validator", return_value=validator):
            hashes = admission.admit_a1_outer_train(fixture.project, fixture.dataset, fixture.canonical, (fixture.verify_a, fixture.verify_b), enforce_frozen_expectations=False)
        self.assertEqual(set(reads), fixture.remaining_keys)
        self.assertEqual(len(reads), len(set(reads)))
        self.assertEqual(set(hashes), set(admission.OUTPUTS.values()))
        for relative in admission.OUTPUTS.values():
            self.assertEqual((fixture.verify_a / relative).read_bytes(), (fixture.verify_b / relative).read_bytes())
            self.assertEqual((fixture.verify_a / relative).read_bytes(), (fixture.canonical / relative).read_bytes())

    def test_ledger_classes_field_order_and_no_forbidden_reads(self) -> None:
        fixture = AdmissionFixture(self.root)
        fixture.run()
        rows = [json.loads(line) for line in (fixture.canonical / admission.OUTPUTS["ledger"]).read_text(encoding="utf-8").splitlines()]
        self.assertTrue(all(tuple(row) == admission.LEDGER_FIELDS for row in rows))
        classes = {row["evidence_source"] for row in rows}
        self.assertEqual(classes, {"RUN014_BOUNDED_PANEL_REUSED", "RUN016_STREAMING_FRONTEND_PASS", "SHORT_FORCED_L0_NO_READ"})
        run016 = [row for row in rows if row["evidence_source"] == "RUN016_STREAMING_FRONTEND_PASS"]
        self.assertEqual({_key(row) for row in run016}, fixture.remaining_keys)
        self.assertTrue(all(row["source_dataset_read_run016"] for row in run016))
        self.assertTrue(all(not row["source_dataset_read_run016"] for row in rows if row not in run016))

    def test_scan_order_is_frozen_and_batch_is_at_most_four(self) -> None:
        fixture = AdmissionFixture(self.root)
        reads: list[tuple[int, int, str, int, str]] = []
        original = validator._read_raw

        def tracked(row, *args, **kwargs):
            reads.append((row["window_count"], row["raw_samples"], row["subject"], row["slot"], row["occurrence_id"]))
            return original(row, *args, **kwargs)

        with mock.patch.object(validator, "_read_raw", side_effect=tracked), mock.patch.object(validator.torch.cuda, "is_available", return_value=False), mock.patch.object(admission, "_load_validator", return_value=validator):
            admission.admit_a1_outer_train(fixture.project, fixture.dataset, fixture.canonical, (fixture.verify_a, fixture.verify_b), enforce_frozen_expectations=False)
        self.assertEqual(reads, sorted(reads))
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("range(0, len(remaining), 4)", source)

    def test_dtype_shape_nonfinite_cast_transpose_and_frontend_pass(self) -> None:
        fixture = AdmissionFixture(self.root)
        fixture.run()
        freeze = yaml.safe_load((fixture.canonical / admission.OUTPUTS["freeze"]).read_text(encoding="utf-8"))
        self.assertEqual(sum(freeze["acceptance_counts"]["run016_source_dtype_counts"].values()), len(fixture.remaining_keys))
        for fault, code in (("wrong_shape", "A1_ADMISSION_SOURCE_BLOCKED"), ("nonfinite", "A1_ADMISSION_SOURCE_BLOCKED")):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as name:
                broken = AdmissionFixture(Path(name), fault=fault)
                with self.assertRaisesRegex(admission.A1AdmissionError, code):
                    broken.run()

    def test_duplicate_missing_overlap_and_panel_tamper_fail_before_read(self) -> None:
        for fault in ("duplicate", "missing", "panel"):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as name:
                fixture = AdmissionFixture(Path(name))
                path = fixture.project / admission.FIXED_INPUTS["eligibility"][0]
                rows = path.read_text(encoding="utf-8").splitlines()
                if fault == "duplicate":
                    rows.append(rows[0])
                    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
                elif fault == "missing":
                    path.write_text("\n".join(rows[1:]) + "\n", encoding="utf-8")
                else:
                    panel_path = fixture.project / admission.FIXED_INPUTS["frontend_panel"][0]
                    panel_rows = [json.loads(line) for line in panel_path.read_text(encoding="utf-8").splitlines()]
                    panel_rows[0]["source_dataset_read"] = not panel_rows[0]["source_dataset_read"]
                    _write_jsonl(panel_path, panel_rows)
                with mock.patch.object(validator, "_read_raw", side_effect=AssertionError("must not read")), mock.patch.object(admission, "_load_validator", return_value=validator):
                    with self.assertRaisesRegex(admission.A1AdmissionError, "A1_ADMISSION_SCOPE_MISMATCH"):
                        admission.admit_a1_outer_train(fixture.project, fixture.dataset, fixture.canonical, (fixture.verify_a, fixture.verify_b), enforce_frozen_expectations=False)

    def test_parameter_mutation_is_rejected(self) -> None:
        fixture = AdmissionFixture(self.root)
        original_class = validator.NativeSpectralA1

        class MutatingModel(original_class):
            def forward(self, *args, **kwargs):
                result = super().forward(*args, **kwargs)
                with validator.torch.no_grad():
                    next(self.parameters()).add_(1.0)
                return result

        with mock.patch.object(validator, "NativeSpectralA1", MutatingModel), mock.patch.object(validator.torch.cuda, "is_available", return_value=False), mock.patch.object(admission, "_load_validator", return_value=validator):
            with self.assertRaisesRegex(admission.A1AdmissionError, "A1_ADMISSION_FRONTEND_BLOCKED"):
                admission.admit_a1_outer_train(fixture.project, fixture.dataset, fixture.canonical, (fixture.verify_a, fixture.verify_b), enforce_frozen_expectations=False)

    def test_cuda_available_init_failure_never_falls_back_or_reads(self) -> None:
        fixture = AdmissionFixture(self.root)
        original_class = validator.NativeSpectralA1

        class FailedCudaModel(original_class):
            def to(self, device):
                raise RuntimeError("synthetic CUDA failure")

        with mock.patch.object(validator, "NativeSpectralA1", FailedCudaModel), mock.patch.object(validator.torch.cuda, "is_available", return_value=True), mock.patch.object(validator, "_read_raw", side_effect=AssertionError("must not read")), mock.patch.object(admission, "_load_validator", return_value=validator):
            with self.assertRaisesRegex(admission.A1AdmissionError, "A1_ADMISSION_FRONTEND_BLOCKED"):
                admission.admit_a1_outer_train(fixture.project, fixture.dataset, fixture.canonical, (fixture.verify_a, fixture.verify_b), enforce_frozen_expectations=False)

    def test_ast_uses_only_lazy_audited_loader(self) -> None:
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        imported = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        imported |= {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertNotIn("h5py", imported)
        calls = [admission._call_name(node) if hasattr(admission, "_call_name") else "" for node in ast.walk(tree) if isinstance(node, ast.Call)]
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("validate_a1_frontend(", source)
        self.assertNotIn("h5py.File", source)
        self.assertEqual(source.count("validator._read_raw("), 1)

    def test_outputs_contain_no_value_text_cache_or_device_name(self) -> None:
        fixture = AdmissionFixture(self.root)
        fixture.run()
        combined = b"".join((fixture.canonical / relative).read_bytes() for relative in admission.OUTPUTS.values()).lower()
        for forbidden in (b"waveform_hash", b"tensor_hash", b"embedding_hash", b"amplitude_mean", b"power_mean", b"device_name", b"stimulus_sha256"):
            self.assertNotIn(forbidden, combined)

    def test_atomic_output_failure_preserves_canonical(self) -> None:
        fixture = AdmissionFixture(self.root)
        for relative in admission.OUTPUTS.values():
            path = fixture.canonical / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"sentinel\n")
        original = admission.os.replace
        calls = 0

        def fail_canonical(source, destination):
            nonlocal calls
            calls += 1
            if str(destination).startswith(str(fixture.canonical)):
                raise OSError("synthetic")
            return original(source, destination)

        with mock.patch.object(admission.os, "replace", side_effect=fail_canonical):
            with self.assertRaisesRegex(admission.A1AdmissionError, "A1_ADMISSION_OUTPUT_FAILURE"):
                fixture.run()
        self.assertTrue(all((fixture.canonical / relative).read_bytes() == b"sentinel\n" for relative in admission.OUTPUTS.values()))
        self.assertGreater(calls, 0)

    def test_fixed_hash_tamper_fails_before_source_read(self) -> None:
        fixture = AdmissionFixture(self.root)
        policy = fixture.project / admission.FIXED_INPUTS["frontend_validator"][0]
        policy.write_bytes(policy.read_bytes() + b"# tamper\n")
        with mock.patch.object(admission, "_load_validator", side_effect=AssertionError("must not import")):
            with self.assertRaisesRegex(admission.A1AdmissionError, "A1_ADMISSION_INPUT_MISMATCH"):
                admission.admit_a1_outer_train(fixture.project, fixture.dataset, fixture.canonical, (fixture.verify_a, fixture.verify_b), enforce_frozen_expectations=False)

    def test_output_root_symlink_and_path_escape_are_rejected(self) -> None:
        fixture = AdmissionFixture(self.root)
        target = self.root / "target"
        target.mkdir()
        link = self.root / "link"
        link.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(admission.A1AdmissionError, "A1_ADMISSION_OUTPUT_FAILURE"):
            admission.admit_a1_outer_train(fixture.project, fixture.dataset, fixture.canonical, (link, fixture.verify_b), enforce_frozen_expectations=False)
        with self.assertRaisesRegex(admission.A1AdmissionError, "A1_ADMISSION_INPUT_MISMATCH"):
            admission._safe_input(fixture.project, "../escape", "escape")

    def test_unknown_cli_parameters_are_rejected(self) -> None:
        for args in (("--dataset-root", "x"), ("--device", "cpu"), ("--batch", "8"), ("--resume", "x")):
            completed = subprocess.run([
                sys.executable, str(SCRIPT),
                "--verification-root-a", "/tmp/a", "--verification-root-b", "/tmp/b",
                *args,
            ], cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(completed.returncode, 2)
            self.assertIn("unrecognized arguments", completed.stderr)


def _key(row: dict) -> tuple[str, int, str]:
    return row["subject"], row["slot"], row["occurrence_id"]


if __name__ == "__main__":
    unittest.main()
