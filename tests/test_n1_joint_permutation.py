from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rc_hsg.references as references
from rc_hsg.references import (
    N1JointPermutationSampler,
    N1SamplerContractError,
)
from rc_hsg.references import n1_joint_permutation as n1


def _code(context) -> str:
    return str(context.exception).split(":", 1)[0]


class N1JointPermutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sampler = N1JointPermutationSampler.from_frozen_assignment(ROOT)
        cls.rows = cls.sampler._rows
        cls.keys = cls.sampler._evaluable_row_keys
        cls.excluded = cls.sampler._excluded_row_keys
        cls.expected = yaml.safe_load(
            (ROOT / "artifacts/nulls/n1_block_feasibility.yaml").read_text(encoding="utf-8")
        )["permutation_probe"]["replicates"]

    def test_assignment_scope_is_exact(self) -> None:
        self.assertEqual(len(self.rows), 3541)
        self.assertEqual(len(self.keys), 3481)
        self.assertEqual(len(self.sampler._blocks), 180)
        self.assertEqual(len(self.excluded), 60)
        self.assertEqual(tuple(sorted(self.keys)), self.keys)
        self.assertEqual(tuple(sorted(self.excluded)), self.excluded)
        self.assertTrue(set(self.keys).isdisjoint(self.excluded))

    def test_all_replicates_match_frozen_hashes_and_fixed_points(self) -> None:
        hashes = []
        fixed = []
        expected_keys = set(self.keys)
        for replicate_id, oracle in enumerate(self.expected, start=1):
            batch = self.sampler.build(replicate_id)
            self.assertEqual(batch.replicate_id, replicate_id)
            self.assertEqual(len(batch.pairs), 3481)
            self.assertEqual(len({pair.block_id for pair in batch.pairs}), 180)
            self.assertEqual({pair.recipient_row_key for pair in batch.pairs}, expected_keys)
            self.assertEqual({pair.donor_row_key for pair in batch.pairs}, expected_keys)
            self.assertEqual(batch.excluded_row_keys, self.excluded)
            self.assertEqual(batch.joint_mapping_sha256, oracle["joint_mapping_sha256"])
            self.assertEqual(batch.fixed_points, oracle["fixed_points"])
            self.assertEqual(sum(pair.fixed_point for pair in batch.pairs), batch.fixed_points)
            for pair in batch.pairs:
                recipient = self.sampler._row_by_key[pair.recipient_row_key]
                donor = self.sampler._row_by_key[pair.donor_row_key]
                self.assertEqual(
                    (recipient.role, recipient.subject, recipient.session, recipient.length_bin, recipient.power_bin),
                    (donor.role, donor.subject, donor.session, donor.length_bin, donor.power_bin),
                )
            hashes.append(batch.joint_mapping_sha256)
            fixed.append(batch.fixed_points)
        self.assertEqual(len(set(hashes)), 199)
        self.assertEqual(sum(fixed), 35529)
        self.assertEqual((min(fixed), max(fixed)), (145, 214))

    def test_replicate_validation_rejects_bool_non_integer_and_range(self) -> None:
        for value in (0, 200, True, False, 1.0, "1", None):
            with self.subTest(value=value), self.assertRaises(N1SamplerContractError) as caught:
                self.sampler.build(value)
            self.assertEqual(_code(caught), "N1_SAMPLER_REPLICATE_INVALID")

    def test_donor_lookup_rejects_unknown_and_excluded_rows(self) -> None:
        with self.assertRaises(N1SamplerContractError) as caught:
            self.sampler.donor_for("UNKNOWN", 1)
        self.assertEqual(_code(caught), "N1_SAMPLER_ROW_UNKNOWN")
        with self.assertRaises(N1SamplerContractError) as caught:
            self.sampler.donor_for(self.excluded[0], 1)
        self.assertEqual(_code(caught), "N1_SAMPLER_ROW_NOT_EVALUABLE")
        key = self.keys[0]
        self.assertEqual(self.sampler.donor_for(key, 1), self.sampler.donor_for(key, 1))

    def test_selection_aware_callback_is_shared_ordered_and_recomputed(self) -> None:
        values = {key: index for index, key in enumerate(self.keys)}
        calls: list[tuple[str, str, int, tuple[str, str, str]]] = []

        def select_then_score(recipient: str, source: str, value: int):
            l1 = f"L1_{value % 7}"
            l2 = f"{l1}/L2_{value % 11}"
            l3 = f"{l2}/L3_{value % 13}"
            path = (l1, l2, l3)
            calls.append((recipient, source, value, path))
            return {"winner": f"C_{value}", "path": path, "synthetic_score": value % 17}

        real = self.sampler.evaluate_real(values, select_then_score)
        real_calls = tuple(calls)
        self.assertEqual(len(real_calls), 3481)
        self.assertEqual(tuple(item[0] for item in real_calls), self.keys)
        self.assertTrue(all(recipient == source for recipient, source, _, _ in real_calls))
        calls.clear()
        pseudo = self.sampler.evaluate_pseudo_real(1, values, select_then_score)
        pseudo_calls = tuple(calls)
        self.assertEqual(len(pseudo_calls), 3481)
        self.assertEqual(tuple(item[0] for item in pseudo_calls), self.keys)
        self.assertEqual(tuple(key for key, _ in pseudo.evaluations), self.keys)
        self.assertEqual(real.excluded_row_keys, pseudo.excluded_row_keys)
        self.assertIsNone(real.joint_mapping_sha256)
        self.assertEqual(pseudo.joint_mapping_sha256, self.expected[0]["joint_mapping_sha256"])
        self.assertTrue(any(a[1]["winner"] != b[1]["winner"] for a, b in zip(real.evaluations, pseudo.evaluations)))
        self.assertTrue(all(path[1].startswith(path[0] + "/") and path[2].startswith(path[1] + "/") for _, _, _, path in pseudo_calls))

        changed_values = dict(values)
        target = next(pair for pair in self.sampler.build(1).pairs if not pair.fixed_point)
        changed_values[target.donor_row_key] += 1000003
        calls.clear()
        changed = self.sampler.evaluate_pseudo_real(1, changed_values, select_then_score)
        before = dict(pseudo.evaluations)[target.recipient_row_key]
        after = dict(changed.evaluations)[target.recipient_row_key]
        self.assertNotEqual(before["winner"], after["winner"])
        self.assertEqual(len(calls), 3481)

    def test_value_scope_and_callback_failure_fail_closed(self) -> None:
        values = {key: index for index, key in enumerate(self.keys)}
        missing = dict(values)
        missing.pop(self.keys[0])
        extra = dict(values)
        extra["EXTRA"] = 1
        for invalid in (missing, extra, [], None):
            with self.subTest(kind=type(invalid).__name__), self.assertRaises(N1SamplerContractError) as caught:
                self.sampler.evaluate_real(invalid, lambda *_: None)
            self.assertEqual(_code(caught), "N1_SAMPLER_VALUE_SCOPE_MISMATCH")

        secret = "SYNTHETIC_SECRET_VALUE"
        values[self.keys[0]] = secret
        with self.assertRaises(N1SamplerContractError) as caught:
            self.sampler.evaluate_real(values, lambda *_: (_ for _ in ()).throw(ValueError(secret)))
        self.assertEqual(_code(caught), "N1_SAMPLER_CALLBACK_FAILURE")
        self.assertNotIn(secret, str(caught.exception))

    def test_assignment_hash_schema_scope_and_path_tamper_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            assignment = project / n1.ASSIGNMENT_RELATIVE
            assignment.parent.mkdir(parents=True)
            shutil.copy2(ROOT / n1.ASSIGNMENT_RELATIVE, assignment)
            original = assignment.read_bytes()
            assignment.write_bytes(original + b"\n")
            with self.assertRaises(N1SamplerContractError) as caught:
                N1JointPermutationSampler.from_frozen_assignment(project)
            self.assertEqual(_code(caught), "N1_SAMPLER_INPUT_MISMATCH")

            for field, value in (("role", "other"), ("block_id", "n1b_v1_bad"), ("n1_status", "BAD")):
                rows = [json.loads(line) for line in original.decode("utf-8").splitlines()]
                rows[0][field] = value
                payload = "".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows).encode("utf-8")
                assignment.write_bytes(payload)
                digest = hashlib.sha256(payload).hexdigest()
                with self.subTest(field=field), mock.patch.object(n1, "ASSIGNMENT_SHA256", digest):
                    with self.assertRaises(N1SamplerContractError) as caught:
                        N1JointPermutationSampler.from_frozen_assignment(project)
                    self.assertEqual(_code(caught), "N1_SAMPLER_SCOPE_MISMATCH")

    def test_symlink_and_path_escape_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            link = root / "linked-project"
            if os.name == "nt":
                with mock.patch.object(Path, "is_symlink", return_value=True):
                    with self.assertRaises(N1SamplerContractError) as caught:
                        N1JointPermutationSampler.from_frozen_assignment(ROOT)
            else:
                os.symlink(ROOT, link, target_is_directory=True)
                with self.assertRaises(N1SamplerContractError) as caught:
                    N1JointPermutationSampler.from_frozen_assignment(link)
            self.assertEqual(_code(caught), "N1_SAMPLER_INPUT_MISMATCH")
            with mock.patch.object(n1, "ASSIGNMENT_RELATIVE", "../outside.jsonl"):
                with self.assertRaises(N1SamplerContractError) as caught:
                    N1JointPermutationSampler.from_frozen_assignment(ROOT)
                self.assertEqual(_code(caught), "N1_SAMPLER_INPUT_MISMATCH")

    def test_ast_and_public_exports_exclude_rng_frontend_and_shortcuts(self) -> None:
        path = ROOT / "src/rc_hsg/references/n1_joint_permutation.py"
        source = path.read_text(encoding="utf-8")
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
        self.assertNotIn("audit_n1_block_feasibility", source)
        self.assertNotIn("NativeSpectralA1", source)
        self.assertFalse(
            any(
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "hash"
                for node in ast.walk(tree)
            )
        )
        self.assertEqual(
            set(references.__all__),
            {
                "N1JointPermutationSampler", "N1PermutationBatch", "N1PermutationPair",
                "N1SamplerContractError", "N1SelectionAwareEvaluation",
            },
        )
        self.assertFalse(any("p_value" in name or "candidate" in name for name in dir(self.sampler)))


if __name__ == "__main__":
    unittest.main()
