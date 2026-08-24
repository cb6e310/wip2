from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = PROJECT_ROOT / "scripts" / "build_a_interface_contract.py"


def _import_builder():
    spec = importlib.util.spec_from_file_location("build_a_interface_contract", BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = _import_builder()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AInterfaceBuilderTests(unittest.TestCase):
    def _build_to(self, root: Path):
        return BUILDER.build(project_root=PROJECT_ROOT, output_root=root)

    def test_fixed_inputs_match_frozen_hashes(self) -> None:
        for label, (relative, expected) in BUILDER.INPUTS.items():
            self.assertEqual(_sha256(PROJECT_ROOT / relative), expected, label)

    def test_exact_counts_schema_order_and_evidence_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            hashes = self._build_to(root)
            contract_path = root / BUILDER.OUTPUTS["contract"]
            eligibility_path = root / BUILDER.OUTPUTS["eligibility"]
            contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
            self.assertEqual(
                list(contract),
                [
                    "schema_version", "artifact", "policy_id", "spec_version", "baseline_commit",
                    "input_artifacts", "input_contract", "preprocessing_contract", "spectral_contract",
                    "encoder_contract", "output_contract", "initialization_contract",
                    "eligibility_contract", "acceptance_counts", "implementation",
                    "prohibited_features", "prohibited_actions", "evidence_scope",
                ],
            )
            self.assertEqual(contract["implementation"]["trainable_parameter_count"], 1_270_528)
            self.assertFalse(contract["implementation"]["real_eeg_validated"])
            self.assertEqual(contract["evidence_scope"], BUILDER.EVIDENCE_SCOPE)
            self.assertEqual(contract["acceptance_counts"]["by_role"], BUILDER.EXPECTED_COUNTS)
            self.assertEqual(contract["acceptance_counts"]["calibration_reserves"], BUILDER.EXPECTED_RESERVES)
            self.assertEqual(hashes["contract"], _sha256(contract_path))

            lines = eligibility_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 5905)
            rows = [json.loads(line, object_pairs_hook=dict) for line in lines]
            expected_fields = [
                "occurrence_id", "subject", "slot", "role", "calibration_reserve",
                "raw_samples", "window_count", "a_interface_status", "action",
            ]
            self.assertTrue(all(list(row) == expected_fields for row in rows))
            self.assertEqual(rows, sorted(rows, key=lambda row: (row["subject"], row["slot"], row["occurrence_id"])))
            short = [row for row in rows if row["a_interface_status"] == "A_INTERFACE_SHORT_SEGMENT"]
            self.assertEqual(len(short), 73)
            self.assertTrue(all(row["window_count"] == 0 and row["action"] == "FORCED_L0_NO_FRONTEND" for row in short))
            self.assertTrue(all("source_locator" not in row and "stimulus_sha256" not in row for row in rows))

    def test_two_external_builds_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as first_name, tempfile.TemporaryDirectory() as second_name:
            first, second = Path(first_name), Path(second_name)
            self._build_to(first)
            self._build_to(second)
            for relative in BUILDER.OUTPUTS.values():
                self.assertEqual((first / relative).read_bytes(), (second / relative).read_bytes(), relative)

    def test_tamper_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            fixture = Path(name)
            for relative, _ in BUILDER.INPUTS.values():
                destination = fixture / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(PROJECT_ROOT / relative, destination)
            code = fixture / "src/rc_hsg/backbones/native_spectral_a1.py"
            code.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(PROJECT_ROOT / "src/rc_hsg/backbones/native_spectral_a1.py", code)
            policy = fixture / BUILDER.INPUTS["a_policy"][0]
            policy.write_bytes(policy.read_bytes() + b"\n# tamper\n")
            with self.assertRaisesRegex(BUILDER.BuildError, r"^INPUT_HASH_MISMATCH:"):
                BUILDER.build(project_root=fixture, output_root=fixture / "output")

    def test_input_symlink_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            fixture = Path(name)
            for relative, _ in BUILDER.INPUTS.values():
                destination = fixture / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(PROJECT_ROOT / relative, destination)
            code = fixture / "src/rc_hsg/backbones/native_spectral_a1.py"
            code.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(PROJECT_ROOT / "src/rc_hsg/backbones/native_spectral_a1.py", code)
            policy = fixture / BUILDER.INPUTS["a_policy"][0]
            target = fixture / "policy-target.yaml"
            os.replace(policy, target)
            policy.symlink_to(target)
            with self.assertRaisesRegex(BUILDER.BuildError, r"^PATH_SYMLINK:"):
                BUILDER.build(project_root=fixture, output_root=fixture / "output")

    def test_output_root_symlink_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            parent = Path(name)
            target = parent / "target"
            target.mkdir()
            link = parent / "output-link"
            link.symlink_to(target, target_is_directory=True)
            with self.assertRaisesRegex(BUILDER.BuildError, r"^PATH_SYMLINK:"):
                BUILDER.build(project_root=PROJECT_ROOT, output_root=link)

    def test_unknown_cli_argument_is_rejected(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(BUILDER_PATH), "--seed", "1"],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("unrecognized arguments", completed.stderr)

    def test_source_has_no_eeg_reader_network_checkpoint_or_external_import(self) -> None:
        model_source = (PROJECT_ROOT / "src/rc_hsg/backbones/native_spectral_a1.py").read_text(encoding="utf-8").lower()
        sources = "\n".join(
            (PROJECT_ROOT / relative).read_text(encoding="utf-8").lower()
            for relative in (
                "src/rc_hsg/backbones/native_spectral_a1.py",
                "scripts/build_a_interface_contract.py",
            )
        )
        for forbidden in (
            "import requests", "import urllib", "socket", "h5py", "loadmat", "scipy.io",
            "torch.load", "load_state_dict_from_url", "huggingface",
        ):
            self.assertNotIn(forbidden, sources)
        for forbidden in ("trust_align", "labram", "neurolm"):
            self.assertNotIn(forbidden, model_source)


if __name__ == "__main__":
    unittest.main()
