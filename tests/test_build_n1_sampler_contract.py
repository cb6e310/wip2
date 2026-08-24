from __future__ import annotations

import ast
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
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_n1_sampler_contract.py"


def _import(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


builder = _import("build_n1_sampler_contract", SCRIPT)


class BuildN1SamplerContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        root = Path(cls.temporary.name)
        cls.canonical = root / "canonical"
        cls.verify_a = root / "verify-a"
        cls.verify_b = root / "verify-b"
        cls.hashes = builder.build_n1_sampler_contract(
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

    def test_contract_header_order_scope_parity_and_safety_are_exact(self) -> None:
        contract = yaml.safe_load(
            (self.canonical / builder.OUTPUTS["contract"]).read_text(encoding="utf-8")
        )
        self.assertEqual(
            list(contract),
            [
                "schema_version", "artifact", "spec_version", "baseline_commit", "task",
                "policy_id", "evidence_scope", "input_artifacts", "assignment_scope",
                "permutation_contract", "parity", "selection_aware_boundary", "implementation",
                "outputs", "safety", "downstream_boundary",
            ],
        )
        self.assertEqual(contract["artifact"], "RC_HSG_N1_JOINT_PERMUTATION_SAMPLER_V1")
        self.assertEqual(contract["spec_version"], "v2.7")
        self.assertEqual(contract["assignment_scope"]["outer_train_rows"], 3541)
        self.assertEqual(contract["assignment_scope"]["evaluable_rows"], 3481)
        self.assertEqual(contract["assignment_scope"]["evaluable_blocks"], 180)
        self.assertEqual(contract["assignment_scope"]["excluded_rows"], 60)
        self.assertEqual(contract["parity"]["replicates"], 199)
        self.assertEqual(contract["parity"]["exact_hash_matches"], 199)
        self.assertEqual(contract["parity"]["fixed_points_total"], 35529)
        self.assertEqual(
            (contract["parity"]["fixed_points_min"], contract["parity"]["fixed_points_max"]),
            (145, 214),
        )
        self.assertEqual(contract["safety"]["production_eeg_reads"], 0)
        self.assertEqual(contract["safety"]["text_or_outcome_reads"], 0)
        self.assertEqual(contract["downstream_boundary"]["next_task"], "S0_N2_SAMPLER")

    def test_manifest_has_199_summary_only_rows_in_exact_order(self) -> None:
        path = self.canonical / builder.OUTPUTS["manifest"]
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(rows), 199)
        self.assertEqual([row["replicate_id"] for row in rows], list(range(1, 200)))
        self.assertTrue(all(tuple(row) == builder.MANIFEST_FIELDS for row in rows))
        self.assertEqual(len({row["joint_mapping_sha256"] for row in rows}), 199)
        self.assertEqual(sum(row["fixed_points"] for row in rows), 35529)
        self.assertEqual(
            [row["fixed_point_rate"] for row in rows],
            [format(row["fixed_points"] / 3481, ".12f") for row in rows],
        )
        lower = path.read_bytes().lower()
        for forbidden in (
            b"recipient_row_key", b"donor_row_key", b"block_id", b"pairs",
            b"source_file", b"occurrence_id", b"values_by_row",
        ):
            self.assertNotIn(forbidden, lower)

    def test_all_outputs_exclude_values_relations_and_large_content(self) -> None:
        combined = b"".join(
            (self.canonical / relative).read_bytes() for relative in builder.OUTPUTS.values()
        ).lower()
        for forbidden in (
            b"eeg_value", b"token_value", b"embedding_value", b"proxy_value",
            b"waveform_value", b"recipient_row_key", b"donor_row_key",
            b'"donor":', b'"recipient":', b"stimulus_text", b"outcome_value",
        ):
            self.assertNotIn(forbidden, combined)
        self.assertLess(sum((self.canonical / relative).stat().st_size for relative in builder.OUTPUTS.values()), 500000)

    def test_feasibility_yaml_parity_tamper_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            for relative, _ in builder.FIXED_INPUTS.values():
                source = ROOT / relative
                target = project / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
            for relative in (
                "src/rc_hsg/references/n1_joint_permutation.py",
                "scripts/build_n1_sampler_contract.py",
            ):
                target = project / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, target)
            path = project / builder.FIXED_INPUTS["feasibility"][0]
            value = yaml.safe_load(path.read_text(encoding="utf-8"))
            value["permutation_probe"]["replicates"][0]["fixed_points"] += 1
            path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            patched = dict(builder.FIXED_INPUTS)
            patched["feasibility"] = (patched["feasibility"][0], digest)
            with mock.patch.object(builder, "FIXED_INPUTS", patched):
                with self.assertRaises(builder.N1SamplerContractError) as caught:
                    builder.build_n1_sampler_contract(
                        project,
                        Path(temporary) / "canonical",
                        (Path(temporary) / "a", Path(temporary) / "b"),
                    )
            self.assertTrue(str(caught.exception).startswith("N1_SAMPLER_SCOPE_MISMATCH"))

    def test_atomic_write_failure_is_stable_and_leaves_no_temp(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            rendered = {label: label.encode("ascii") for label in builder.OUTPUTS}
            with mock.patch.object(builder.os, "replace", side_effect=OSError("synthetic")):
                with self.assertRaises(builder.N1SamplerContractError) as caught:
                    builder._atomic_write(root, rendered)
            self.assertTrue(str(caught.exception).startswith("N1_SAMPLER_OUTPUT_FAILURE"))
            self.assertEqual([path for path in root.rglob("*") if path.is_file()], [])

    def test_symlink_verification_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            link = root / "linked"
            if os.name == "nt":
                with mock.patch.object(Path, "is_symlink", autospec=True, side_effect=lambda path: path == root):
                    with self.assertRaises(builder.N1SamplerContractError) as caught:
                        builder.build_n1_sampler_contract(
                            ROOT, root / "canonical", (link, root / "verify-b")
                        )
            else:
                os.symlink(root / "target", link, target_is_directory=True)
                with self.assertRaises(builder.N1SamplerContractError) as caught:
                    builder.build_n1_sampler_contract(
                        ROOT, root / "canonical", (link, root / "verify-b")
                    )
            self.assertTrue(str(caught.exception).startswith("N1_SAMPLER_OUTPUT_FAILURE"))

    def test_cli_rejects_unknown_or_forbidden_options(self) -> None:
        for argument in ("--seed", "--dataset-root", "--candidate", "--device", "--hash-override"):
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), argument, "x"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 2)

    def test_builder_ast_has_no_data_frontend_rng_or_feasibility_import(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports |= {
            node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        }
        for forbidden in ("random", "numpy", "torch", "h5py"):
            self.assertNotIn(forbidden, imports)
        self.assertNotIn("NativeSpectralA1", source)
        self.assertNotIn("dataset_root", source)
        self.assertNotIn("importlib", imports)


if __name__ == "__main__":
    unittest.main()
