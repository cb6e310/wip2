from __future__ import annotations

import ast
import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_n2_sampler_contract.py"
MODULE = ROOT / "src/rc_hsg/references/n2_common_phase.py"


def _import(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


builder = _import("build_n2_sampler_contract", SCRIPT)


class BuildN2SamplerContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        root = Path(cls.temporary.name)
        cls.canonical = root / "canonical"
        cls.verify_a = root / "verify-a"
        cls.verify_b = root / "verify-b"
        cls.hashes = builder.build_n2_sampler_contract(
            ROOT, cls.canonical, (cls.verify_a, cls.verify_b)
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_three_roots_are_byte_identical_and_hashes_match(self) -> None:
        self.assertEqual(set(self.hashes), set(builder.OUTPUTS.values()))
        for relative, digest in self.hashes.items():
            canonical = (self.canonical / relative).read_bytes()
            self.assertEqual(canonical, (self.verify_a / relative).read_bytes())
            self.assertEqual(canonical, (self.verify_b / relative).read_bytes())
            self.assertEqual(hashlib.sha256(canonical).hexdigest(), digest)

    def test_contract_header_order_and_boundary_are_exact(self) -> None:
        contract = yaml.safe_load(
            (self.canonical / builder.OUTPUTS["contract"]).read_text(encoding="utf-8")
        )
        self.assertEqual(
            list(contract),
            [
                "schema_version", "artifact", "spec_version", "baseline_commit", "task",
                "policy_id", "evidence_scope", "input_artifacts", "scientific_basis",
                "transform_contract", "seed_contract", "input_output_contract",
                "synthetic_fixtures", "preservation_thresholds", "synthetic_diagnostics",
                "artifact_diagnostics_schema", "implementation", "prohibited", "safety",
                "downstream_boundary",
            ],
        )
        self.assertEqual(contract["artifact"], builder.POLICY_ID)
        self.assertEqual(contract["spec_version"], "v2.8")
        self.assertEqual(contract["baseline_commit"], builder.BASELINE_COMMIT)
        self.assertTrue(contract["transform_contract"]["common_phase_across_channels"])
        self.assertTrue(contract["transform_contract"]["valid_unpadded_prefix_only"])
        self.assertFalse(contract["downstream_boundary"]["n2_primary_admitted"])
        self.assertFalse(contract["downstream_boundary"]["gate_r0_executed"])
        self.assertEqual(contract["downstream_boundary"]["next_task"], "GATE_R0")
        self.assertEqual(contract["safety"]["real_outer_train_reads"], 0)
        self.assertEqual(contract["safety"]["text_outcome_test_identity_reads"], 0)

    def test_grid_replay_thresholds_and_hex_diagnostics_are_exact(self) -> None:
        contract = yaml.safe_load(
            (self.canonical / builder.OUTPUTS["contract"]).read_text(encoding="utf-8")
        )
        diagnostics = contract["synthetic_diagnostics"]
        self.assertEqual(diagnostics["grid_cases"], 15)
        self.assertEqual(len(diagnostics["cases"]), 15)
        self.assertTrue(diagnostics["all_preservation_checks_pass"])
        self.assertEqual(diagnostics["replicate_replay"]["replicates"], 199)
        self.assertEqual(diagnostics["replicate_replay"]["unique_seed_hashes"], 199)
        self.assertEqual(diagnostics["replicate_replay"]["unique_output_fingerprints"], 199)
        self.assertTrue(diagnostics["replicate_replay"]["bitwise_replay"])
        self.assertTrue(diagnostics["padded_fixture"]["nonfinite_padding_ignored"])
        for case in diagnostics["cases"]:
            self.assertRegex(case["phase_seed_sha256"], r"^[0-9a-f]{64}$")
            for value in case["metrics"].values():
                self.assertRegex(value, r"^-?0x[0-9a-f.]+p[+-][0-9]+$")
            for label in (
                "psd_relative_norm", "covariance_relative_norm", "mean_relative_norm",
                "cross_spectrum_relative_norm",
            ):
                self.assertLessEqual(float.fromhex(case["metrics"][label]), 1e-6)

    def test_provenance_correction_is_append_only_and_exact(self) -> None:
        correction = yaml.safe_load(
            (self.canonical / builder.OUTPUTS["correction"]).read_text(encoding="utf-8")
        )
        self.assertEqual(correction["historical_run"]["sha256"], builder.FROZEN_INPUTS["run018"][1])
        self.assertFalse(correction["historical_run"]["modified"])
        self.assertEqual(correction["recorded_sha256"], builder.RUN018_RECORDED_NEXT_TASK_HASH)
        self.assertEqual(correction["corrected_sha256"], builder.RUN018_CORRECTED_NEXT_TASK_HASH)
        self.assertEqual(correction["source_zip_sha256"], builder.RUN018_PACKAGE_ZIP_HASH)
        self.assertFalse(correction["scientific_state_changed"])

    def test_outputs_have_no_fixture_arrays_or_large_binary_content(self) -> None:
        combined = b"".join(
            (self.canonical / relative).read_bytes() for relative in builder.OUTPUTS.values()
        ).lower()
        for forbidden in (
            b"waveform_values", b"fft_values", b"phase_angles", b"seed_integer:",
            b"eeg_values", b"embedding_values", b"reference_scores", b"outcome_values",
            b"stimulus_text", b"dataset_root",
        ):
            self.assertNotIn(forbidden, combined)
        self.assertLess(
            sum((self.canonical / relative).stat().st_size for relative in builder.OUTPUTS.values()),
            500_000,
        )

    def test_fixed_input_tamper_fails_before_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            for relative, _ in {**builder.FROZEN_INPUTS, **builder.CONTROL_INPUTS}.values():
                target = project / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, target)
            for relative in (
                "src/rc_hsg/references/n2_common_phase.py",
                "scripts/build_n2_sampler_contract.py",
            ):
                target = project / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, target)
            path = project / builder.FROZEN_INPUTS["n1_contract"][0]
            path.write_bytes(path.read_bytes() + b"\n")
            with self.assertRaises(builder.N2CommonPhaseContractError) as caught:
                builder.build_n2_sampler_contract(
                    project,
                    Path(temporary) / "canonical",
                    (Path(temporary) / "a", Path(temporary) / "b"),
                )
            self.assertTrue(str(caught.exception).startswith("N2_COMMON_PHASE_INPUT_MISMATCH"))
            self.assertFalse((Path(temporary) / "canonical").exists())

    def test_atomic_failure_is_stable_and_leaves_no_temp(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            rendered = {label: label.encode("ascii") for label in builder.OUTPUTS}
            with mock.patch.object(builder.os, "replace", side_effect=OSError("synthetic")):
                with self.assertRaises(builder.N2CommonPhaseContractError) as caught:
                    builder._atomic_write(root, rendered)
            self.assertTrue(str(caught.exception).startswith("N2_COMMON_PHASE_OUTPUT_FAILURE"))
            self.assertEqual([path for path in root.rglob("*") if path.is_file()], [])

    def test_symlink_and_verification_path_escape_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            link = root / "linked"
            if os.name == "nt":
                with mock.patch.object(Path, "is_symlink", autospec=True, side_effect=lambda path: path == link):
                    with self.assertRaises(builder.N2CommonPhaseContractError):
                        builder.build_n2_sampler_contract(ROOT, root / "canonical", (link, root / "b"))
            else:
                os.symlink(root / "target", link, target_is_directory=True)
                with self.assertRaises(builder.N2CommonPhaseContractError):
                    builder.build_n2_sampler_contract(ROOT, root / "canonical", (link, root / "b"))
        with self.assertRaises(builder.N2CommonPhaseContractError):
            builder.build_n2_sampler_contract(
                ROOT,
                ROOT,
                (ROOT / "verification-a", ROOT.parent / "verification-b"),
            )

    def test_cli_rejects_unknown_and_forbidden_options(self) -> None:
        for argument in (
            "--dataset-root", "--input", "--role", "--seed", "--replicates", "--fft",
            "--dtype", "--device", "--tolerance", "--fixture", "--resume", "--hash-override",
        ):
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), argument, "x"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 2, (argument, completed.stderr))

    def test_module_and_builder_ast_enforce_io_and_import_firewall(self) -> None:
        module_source = MODULE.read_text(encoding="utf-8")
        module_tree = ast.parse(module_source)
        module_imports = {
            alias.name
            for node in ast.walk(module_tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        module_imports |= {
            node.module or "" for node in ast.walk(module_tree) if isinstance(node, ast.ImportFrom)
        }
        for forbidden in ("h5py", "pathlib", "os", "importlib", "random"):
            self.assertNotIn(forbidden, module_imports)
        for forbidden in (
            "NativeSpectralA1", "frontend", "dataset", "split_loader", "open(",
            "torch.save", "np.save", "optimizer",
        ):
            self.assertNotIn(forbidden, module_source)
        called_attributes = {
            node.func.attr
            for node in ast.walk(module_tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        self.assertNotIn("backward", called_attributes)

        builder_source = SCRIPT.read_text(encoding="utf-8")
        builder_tree = ast.parse(builder_source)
        imports = {
            alias.name
            for node in ast.walk(builder_tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports |= {node.module or "" for node in ast.walk(builder_tree) if isinstance(node, ast.ImportFrom)}
        for forbidden in ("h5py", "importlib", "random"):
            self.assertNotIn(forbidden, imports)
        self.assertNotIn("NativeSpectralA1", builder_source)
        self.assertIsNone(re.search(r"from\s+scripts\.", builder_source))


if __name__ == "__main__":
    unittest.main()
