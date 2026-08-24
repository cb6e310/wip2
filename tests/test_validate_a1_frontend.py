from __future__ import annotations

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


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = PROJECT_ROOT / "scripts" / "validate_a1_frontend.py"


def _import_validator():
    spec = importlib.util.spec_from_file_location("validate_a1_frontend", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


VALIDATOR = _import_validator()


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, separators=(",", ":"), ensure_ascii=True) + "\n" for row in rows),
        encoding="utf-8",
    )


class FrontendFixture:
    def __init__(self, root: Path, *, fault: str | None = None):
        self.project = root / "project"
        self.dataset = root / "dataset"
        self.output = root / "output"
        self.project.mkdir()
        self.dataset.mkdir()
        self.rows = [
            ("S1", 1, "a1", "train_fit", 500, 1, "ELIGIBLE", "RUN_FRONTEND"),
            ("S1", 2, "a2", "train_fit", 750, 2, "ELIGIBLE", "RUN_FRONTEND"),
            ("S1", 3, "a3", "inner_val", 1000, 3, "ELIGIBLE", "RUN_FRONTEND"),
            ("S1", 4, "a4", "train_fit", 100, 0, "A_INTERFACE_SHORT_SEGMENT", "FORCED_L0_NO_FRONTEND"),
            ("S1", 5, "a5", "cal", 500, 1, "ELIGIBLE", "RUN_FRONTEND"),
            ("S1", 6, "a6", "test", 500, 1, "ELIGIBLE", "RUN_FRONTEND"),
            ("S2", 1, "b1", "train_fit", 1250, 4, "ELIGIBLE", "RUN_FRONTEND"),
            ("S2", 2, "b2", "inner_val", 500, 1, "ELIGIBLE", "RUN_FRONTEND"),
        ]
        self.selected = {("S1", 1), ("S1", 3), ("S2", 1), ("S2", 2)}
        self._write_hdf5(fault)
        self._write_metadata(fault)

    def _relative(self, subject: str) -> str:
        return f"task1 - NR/Matlab files/results{subject}_NR.mat"

    def _write_hdf5(self, fault: str | None) -> None:
        for subject in ("S1", "S2"):
            path = self.dataset / self._relative(subject)
            path.parent.mkdir(parents=True, exist_ok=True)
            with h5py.File(path, "w") as handle:
                sentence = handle.create_group("sentenceData")
                references = sentence.create_dataset("rawData", (349, 1), dtype=h5py.ref_dtype)
                refs = handle.create_group("refs")
                for row in self.rows:
                    row_subject, slot, _, _, samples, _, _, _ = row
                    if row_subject != subject or (subject, slot) not in self.selected:
                        continue
                    shape = (samples, 105)
                    dtype = np.float32 if (subject, slot) == ("S2", 2) else np.float64
                    if fault == "wrong_shape" and (subject, slot) == ("S1", 1):
                        shape = (105, samples)
                    if fault == "integer_dtype" and (subject, slot) == ("S1", 1):
                        dtype = np.int16
                    values = np.arange(np.prod(shape), dtype=np.float64).reshape(shape) % 97
                    if fault == "nonfinite" and (subject, slot) == ("S1", 1):
                        values[0, 0] = np.nan
                    target = refs.create_dataset(f"raw_{slot}", data=values.astype(dtype))
                    references[slot - 1, 0] = target.ref
                sentence.create_dataset("content", data=np.zeros((349, 1), dtype=np.uint8))
            if fault == "external_link" and subject == "S1":
                external = path.parent / "external.h5"
                with h5py.File(external, "w") as other:
                    other.create_dataset("rawData", data=np.zeros((349, 1)))
                with h5py.File(path, "a") as handle:
                    del handle["sentenceData/rawData"]
                    handle["sentenceData/rawData"] = h5py.ExternalLink(external.name, "/rawData")

    def _write_metadata(self, fault: str | None) -> None:
        eligibility: list[dict] = []
        analysis: list[dict] = []
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
        eligibility.sort(key=lambda row: (row["subject"], row["slot"], row["occurrence_id"]))
        analysis.sort(key=lambda row: (row["subject"], row["slot"], row["occurrence_id"]))
        _write_jsonl(self.project / VALIDATOR.FIXED_INPUTS["eligibility"][0], eligibility)
        _write_jsonl(self.project / VALIDATOR.FIXED_INPUTS["analysis_view"][0], analysis)

        summary = [
            {"subject": subject, "path": self._relative(subject)}
            for subject in ("S1", "S2")
        ]
        targeted = {
            "schema_version": 3,
            "authorized_dataset_root_recorded": str(self.dataset.resolve()),
            "summary_schema": summary,
        }
        targeted_path = self.project / VALIDATOR.FIXED_INPUTS["targeted_manifest_v3"][0]
        targeted_path.parent.mkdir(parents=True, exist_ok=True)
        targeted_path.write_text(yaml.safe_dump(targeted, sort_keys=False), encoding="utf-8")
        files = []
        for subject in ("S1", "S2"):
            path = self.dataset / self._relative(subject)
            size = path.stat().st_size
            if fault == "size_drift" and subject == "S1":
                size += 1
            files.append({"path": self._relative(subject), "size_bytes": size, "sha256": "1" * 64})
        osf = {"schema_version": 1, "metadata_only": True, "files": files}
        osf_path = self.project / VALIDATOR.FIXED_INPUTS["osf_file_metadata"][0]
        osf_path.parent.mkdir(parents=True, exist_ok=True)
        osf_path.write_text(yaml.safe_dump(osf, sort_keys=False), encoding="utf-8")

        placeholders = {
            "spec_v22": "# v2.2 fixture\n",
            "a_policy": "policy_id: RC_HSG_NATIVE_SPECTRAL_A1_V1\n",
            "a_contract": "artifact: RC_HSG_NATIVE_SPECTRAL_A1_CONTRACT_V1\n",
            "split_regime_i": "{}\n",
            "data_card": "schema_version: 1\n",
            "requirements_lock": "fixture==1\n",
        }
        for label, content in placeholders.items():
            path = self.project / VALIDATOR.FIXED_INPUTS[label][0]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        code_path = self.project / VALIDATOR.FIXED_INPUTS["a_code"][0]
        code_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PROJECT_ROOT / VALIDATOR.FIXED_INPUTS["a_code"][0], code_path)


class ValidateA1FrontendTests(unittest.TestCase):
    def test_frozen_repository_panel_selection_is_exact(self) -> None:
        eligibility = VALIDATOR._load_jsonl(PROJECT_ROOT / VALIDATOR.FIXED_INPUTS["eligibility"][0], "eligibility")
        analysis = VALIDATOR._load_jsonl(PROJECT_ROOT / VALIDATOR.FIXED_INPUTS["analysis_view"][0], "analysis")
        panel = VALIDATOR.select_audit_panel(eligibility, analysis)
        counts = VALIDATOR._panel_counts(panel, [row for row in eligibility if row["role"] in VALIDATOR.OUTER_ROLES])
        VALIDATOR._assert_frozen_panel(counts, panel)
        self.assertEqual(panel, sorted(panel, key=lambda row: (row["subject"], row["slot"], row["occurrence_id"])))
        self.assertEqual(sum(row["source_dataset_read"] for row in panel), 107)
        self.assertEqual(sum(not row["source_dataset_read"] for row in panel), 44)

    def test_fixture_validates_only_selected_refs_and_emits_canonical_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            fixture = FrontendFixture(Path(name))
            with mock.patch.object(VALIDATOR.torch.cuda, "is_available", return_value=False):
                result = VALIDATOR.validate_a1_frontend(
                    fixture.project, fixture.dataset, fixture.output,
                    enforce_frozen_expectations=False,
                )
            freeze = result["freeze"]
            self.assertEqual(freeze["check_results"]["cpu_status"], "PASS")
            self.assertEqual(freeze["acceptance_counts"]["real_distinct_rows_read"], 4)
            self.assertEqual(freeze["acceptance_counts"]["short_no_read"], 1)
            self.assertEqual(freeze["loader_contract"]["actual_source_dtype_counts"], {"float32": 1, "float64": 3})
            self.assertEqual(list(freeze), [
                "schema_version", "artifact", "spec_version", "baseline_commit", "task", "policy_id",
                "evidence_scope", "input_artifacts", "authorized_scope", "panel_contract",
                "source_identity_contract", "loader_contract", "execution_contract", "acceptance_counts",
                "check_results", "implementation", "prohibited", "safety", "downstream_boundary",
            ])
            panel_lines = (fixture.output / VALIDATOR.OUTPUTS["panel"]).read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(panel_lines), 5)
            self.assertTrue(all(list(json.loads(line)) == list(VALIDATOR.PANEL_FIELDS) for line in panel_lines))

    def test_two_fixture_builds_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            fixture = FrontendFixture(root)
            first, second = root / "first", root / "second"
            with mock.patch.object(VALIDATOR.torch.cuda, "is_available", return_value=False):
                VALIDATOR.validate_a1_frontend(fixture.project, fixture.dataset, first, enforce_frozen_expectations=False)
                VALIDATOR.validate_a1_frontend(fixture.project, fixture.dataset, second, enforce_frozen_expectations=False)
            for relative in VALIDATOR.OUTPUTS.values():
                self.assertEqual((first / relative).read_bytes(), (second / relative).read_bytes(), relative)

    @unittest.skipUnless(VALIDATOR.torch.cuda.is_available(), "CUDA unavailable")
    def test_fixture_cuda_available_branch(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            fixture = FrontendFixture(Path(name))
            result = VALIDATOR.validate_a1_frontend(
                fixture.project, fixture.dataset, fixture.output,
                enforce_frozen_expectations=False,
            )
            cuda = result["freeze"]["check_results"]["cuda"]
            self.assertTrue(cuda["available"])
            self.assertEqual(cuda["status"], "PASS")

    def test_cuda_unavailable_branch_is_nonblocking(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            fixture = FrontendFixture(Path(name))
            with mock.patch.object(VALIDATOR.torch.cuda, "is_available", return_value=False):
                result = VALIDATOR.validate_a1_frontend(
                    fixture.project, fixture.dataset, fixture.output,
                    enforce_frozen_expectations=False,
                )
            self.assertEqual(result["freeze"]["check_results"]["cuda"]["status"], "NOT_AVAILABLE_NONBLOCKING")

    def test_wrong_shape_dtype_nonfinite_and_external_link_fail_closed(self) -> None:
        cases = {
            "wrong_shape": "REAL_TENSOR_CONTRACT_MISMATCH",
            "integer_dtype": "HDF5_SCHEMA_MISMATCH",
            "nonfinite": "REAL_TENSOR_NONFINITE",
            "external_link": "HDF5_SCHEMA_MISMATCH",
        }
        for fault, code in cases.items():
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as name:
                fixture = FrontendFixture(Path(name), fault=fault)
                with self.assertRaisesRegex(VALIDATOR.A1FrontendValidationError, rf"^{code}:"):
                    VALIDATOR.validate_a1_frontend(
                        fixture.project, fixture.dataset, fixture.output,
                        enforce_frozen_expectations=False,
                    )

    def test_source_size_and_symlink_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            fixture = FrontendFixture(Path(name), fault="size_drift")
            with self.assertRaisesRegex(VALIDATOR.A1FrontendValidationError, r"^SOURCE_IDENTITY_MISMATCH:"):
                VALIDATOR.validate_a1_frontend(fixture.project, fixture.dataset, fixture.output, enforce_frozen_expectations=False)
        with tempfile.TemporaryDirectory() as name:
            fixture = FrontendFixture(Path(name))
            path = fixture.dataset / fixture._relative("S1")
            target = path.with_suffix(".target")
            os.replace(path, target)
            path.symlink_to(target)
            with self.assertRaisesRegex(VALIDATOR.A1FrontendValidationError, r"^SYMLINK_REJECTED:"):
                VALIDATOR.validate_a1_frontend(fixture.project, fixture.dataset, fixture.output, enforce_frozen_expectations=False)

    def test_fixed_input_tamper_fails_before_dataset_read(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            for relative, _ in VALIDATOR.FIXED_INPUTS.values():
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(PROJECT_ROOT / relative, destination)
            policy = root / VALIDATOR.FIXED_INPUTS["a_policy"][0]
            policy.write_bytes(policy.read_bytes() + b"# tamper\n")
            with self.assertRaisesRegex(VALIDATOR.A1FrontendValidationError, r"^INPUT_HASH_MISMATCH:"):
                VALIDATOR.validate_a1_frontend(root, root / "missing", root / "output", enforce_frozen_expectations=True)

    def test_panel_mismatch_happens_before_any_hdf5_open(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            fixture = FrontendFixture(Path(name))
            eligibility_path = fixture.project / VALIDATOR.FIXED_INPUTS["eligibility"][0]
            rows = [json.loads(line) for line in eligibility_path.read_text(encoding="utf-8").splitlines()]
            rows[0]["window_count"] = 0
            _write_jsonl(eligibility_path, rows)
            with mock.patch.object(VALIDATOR.h5py, "File", side_effect=AssertionError("must not open")):
                with self.assertRaisesRegex(VALIDATOR.A1FrontendValidationError, r"^PANEL_CONTRACT_MISMATCH:"):
                    VALIDATOR.validate_a1_frontend(
                        fixture.project, fixture.dataset, fixture.output,
                        enforce_frozen_expectations=False,
                    )

    def test_atomic_failure_preserves_existing_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            fixture = FrontendFixture(Path(name), fault="nonfinite")
            for relative in VALIDATOR.OUTPUTS.values():
                path = fixture.output / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"sentinel\n")
            with self.assertRaisesRegex(VALIDATOR.A1FrontendValidationError, r"^REAL_TENSOR_NONFINITE:"):
                VALIDATOR.validate_a1_frontend(fixture.project, fixture.dataset, fixture.output, enforce_frozen_expectations=False)
            self.assertTrue(all((fixture.output / relative).read_bytes() == b"sentinel\n" for relative in VALIDATOR.OUTPUTS.values()))

    def test_cpu_repeat_cuda_failure_and_parameter_checks_have_stable_codes(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            fixture = FrontendFixture(Path(name))
            with mock.patch.object(VALIDATOR, "_equal_output", return_value=False):
                with self.assertRaisesRegex(VALIDATOR.A1FrontendValidationError, r"^CPU_REPEAT_MISMATCH:"):
                    VALIDATOR.validate_a1_frontend(fixture.project, fixture.dataset, fixture.output, enforce_frozen_expectations=False)
        with tempfile.TemporaryDirectory() as name:
            fixture = FrontendFixture(Path(name))
            with mock.patch.object(VALIDATOR, "_validate_cuda", side_effect=VALIDATOR.A1FrontendValidationError("CUDA_PARITY_MISMATCH: fixture")):
                with self.assertRaisesRegex(VALIDATOR.A1FrontendValidationError, r"^CUDA_PARITY_MISMATCH:"):
                    VALIDATOR.validate_a1_frontend(fixture.project, fixture.dataset, fixture.output, enforce_frozen_expectations=False)

    def test_unknown_cli_arguments_are_rejected(self) -> None:
        for arguments in (("--dataset-root", "x"), ("--seed", "1"), ("--device", "cpu"), ("--batch", "8")):
            completed = subprocess.run(
                [sys.executable, str(VALIDATOR_PATH), *arguments],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("unrecognized arguments", completed.stderr)

    def test_source_and_output_schema_have_no_forbidden_paths(self) -> None:
        source = VALIDATOR_PATH.read_text(encoding="utf-8").lower()
        for forbidden in (
            "import requests", "import urllib", "torch.optim", ".backward(", "torch.save",
            "load_state_dict_from_url", "huggingface", "labram", "neurolm",
        ):
            self.assertNotIn(forbidden, source)
        with tempfile.TemporaryDirectory() as name:
            fixture = FrontendFixture(Path(name))
            with mock.patch.object(VALIDATOR.torch.cuda, "is_available", return_value=False):
                VALIDATOR.validate_a1_frontend(fixture.project, fixture.dataset, fixture.output, enforce_frozen_expectations=False)
            freeze = yaml.safe_load((fixture.output / VALIDATOR.OUTPUTS["freeze"]).read_text(encoding="utf-8"))
            def keys(value: object) -> list[str]:
                if isinstance(value, dict):
                    return [str(key).lower() for key in value] + [item for child in value.values() for item in keys(child)]
                if isinstance(value, list):
                    return [item for child in value for item in keys(child)]
                return []

            output_keys = keys(freeze)
            for forbidden in ("embedding_values", "tensor_hash", "waveform_hash", "amplitude_mean", "stimulus_sha256"):
                self.assertNotIn(forbidden, output_keys)


if __name__ == "__main__":
    unittest.main()
