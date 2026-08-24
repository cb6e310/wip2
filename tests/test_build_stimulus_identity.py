from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_stimulus_identity.py"
spec = importlib.util.spec_from_file_location("build_stimulus_identity", SCRIPT)
BUILDER = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class BuildStimulusIdentityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.project = self.base / "project"
        self.output = self.base / "output"
        for _, (relative, _) in BUILDER.INPUTS.items():
            destination = self.project / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
        self.hashes = {label: digest for label, (_, digest) in BUILDER.INPUTS.items()}

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _build(self, **kwargs):
        values = {
            "project_root": self.project,
            "output_root": self.output,
            "expected_hashes": self.hashes,
        }
        values.update(kwargs)
        return BUILDER.build(**values)

    def _assert_error(self, code: str, **kwargs) -> None:
        with self.assertRaises(BUILDER.IdentityError) as caught:
            self._build(**kwargs)
        self.assertEqual(caught.exception.code, code)

    def _input(self, label: str) -> Path:
        return self.project / BUILDER.INPUTS[label][0]

    def _rehash(self, label: str) -> dict[str, str]:
        hashes = dict(self.hashes)
        hashes[label] = BUILDER.sha256_file(self._input(label))
        return hashes

    @staticmethod
    def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
        path.write_text(
            "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
            encoding="utf-8",
        )

    def test_fixed_input_hashes_and_full_contract(self) -> None:
        for label, (relative, expected) in BUILDER.INPUTS.items():
            self.assertEqual(BUILDER.sha256_file(ROOT / relative), expected, label)
        result = self._build()
        counts = result["identity"]["counts"]
        self.assertEqual(counts["exact_identities"], 344)
        self.assertEqual(counts["occurrences"], 349)
        self.assertEqual(counts["inter_identity_edges"], 2)
        self.assertEqual(counts["unjoined_broad_candidates"], 9)
        self.assertEqual(counts["groups"], 342)
        self.assertEqual(counts["group_kinds"], {
            "EXACT_DUPLICATE_OCCURRENCES": 5,
            "NEAR_DUPLICATE_LEAKAGE_RISK": 2,
            "SINGLETON": 335,
        })
        self.assertEqual(counts["occurrence_group_sizes"], {
            "one_occurrence": 335, "two_occurrences": 7, "larger_than_two": 0,
        })

    def test_threshold_boundaries_union_find_and_stable_group_id(self) -> None:
        row = {"edit_similarity": 0.949999, "token_jaccard": 0.899999, "embedding_cosine": 0.899999}
        self.assertFalse(BUILDER.is_policy_edge(row))
        for field, value in (("edit_similarity", 0.95), ("token_jaccard", 0.90), ("embedding_cosine", 0.90)):
            candidate = dict(row)
            candidate[field] = value
            self.assertTrue(BUILDER.is_policy_edge(candidate), field)
        left, right = "0" * 64, "f" * 64
        expected = "sg_v1_" + hashlib.sha256(
            b"NC_HSG_STIMULUS_GROUP_V1\0" + left.encode() + b"\n" + right.encode()
        ).hexdigest()
        self.assertEqual(BUILDER.stimulus_group_id((right, left)), expected)
        self.assertEqual(BUILDER._union_components([left, right], [(right, left)]), [[left, right]])

    def test_occurrences_candidates_and_decisions_are_complete(self) -> None:
        result = self._build()
        identity = result["identity"]
        occurrences = identity["occurrences"]
        self.assertEqual([row["slot"] for row in occurrences], list(range(1, 350)))
        self.assertTrue(all(row["occurrence_preserved"] for row in occurrences))
        decisions = identity["candidate_decisions"]
        self.assertEqual(len(decisions), 11)
        by_slots = {tuple(sorted(row["slots_a"] + row["slots_b"])): row for row in decisions}
        self.assertEqual(by_slots[(97, 327)]["decision"], "GROUP_LEXICAL_EQUIVALENCE_RISK")
        self.assertEqual(
            by_slots[(307, 308)]["decision"],
            "GROUP_EMBEDDING_NEAR_DUPLICATE_LEAKAGE_RISK",
        )
        self.assertEqual(sum(row["decision"] == BUILDER.UNJOINED_DECISION for row in decisions), 9)
        self.assertEqual(len(identity["exact_duplicate_occurrences"]), 5)
        self.assertTrue(all(row["occurrences_remain_distinct"] for row in identity["exact_duplicate_occurrences"]))

    def test_metadata_paraphrase_and_forbidden_fields(self) -> None:
        self._build()
        identity = yaml.safe_load((self.output / "artifacts/stimulus_identity.yaml").read_text())
        groups = json.loads((self.output / "artifacts/stimulus_groups.json").read_text())
        self.assertIsInstance(groups, dict)
        for row in identity["candidate_decisions"] + groups["groups"]:
            self.assertFalse(row["paraphrase_verified"])
            self.assertEqual(row["paraphrase_status"], BUILDER.PARAPHRASE_STATUS)
            self.assertIsNone(row["document_id"])
            self.assertIsNone(row["paragraph_id"])
            self.assertEqual(row["document_status"], BUILDER.METADATA_STATUS)
            self.assertEqual(row["paragraph_status"], BUILDER.METADATA_STATUS)

        keys: set[str] = set()

        def visit(value) -> None:
            if isinstance(value, dict):
                keys.update(str(key).lower() for key in value)
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)

        visit(identity)
        visit(groups)
        self.assertFalse(any("split" in key for key in keys))
        for prohibited in ("text", "tokens", "ngrams", "embedding_vector", "eeg", "event", "outcome"):
            self.assertNotIn(prohibited, keys)

    def test_hash_tamper_fails_for_each_fixed_input(self) -> None:
        for label in BUILDER.INPUTS:
            with self.subTest(label=label):
                path = self._input(label)
                original = path.read_bytes()
                path.write_bytes(original + b"\n")
                self._assert_error("STIMULUS_GROUP_INPUT_HASH_MISMATCH")
                path.write_bytes(original)

    def test_missing_extra_and_malformed_candidate_fail_closed(self) -> None:
        path = self._input("candidates")
        original = [json.loads(line) for line in path.read_text().splitlines()]
        cases = []
        cases.append((original[:-1], "CANDIDATE_COUNT_MISMATCH"))
        cases.append((original + [dict(original[-1])], "CANDIDATE_COUNT_MISMATCH"))
        malformed = [dict(row) for row in original]
        malformed[0]["unexpected"] = True
        cases.append((malformed, "CANDIDATE_SCHEMA_MISMATCH"))
        reversed_rows = list(reversed(original))
        cases.append((reversed_rows, "CANDIDATE_ORDER_MISMATCH"))
        excessive_precision = [dict(row) for row in original]
        excessive_precision[0]["embedding_cosine"] = 0.9000001
        cases.append((excessive_precision, "CANDIDATE_SCORE_MISMATCH"))
        for rows, code in cases:
            with self.subTest(code=code):
                self._write_jsonl(path, rows)
                self._assert_error(code, expected_hashes=self._rehash("candidates"))
        self._write_jsonl(path, original)

    def test_source_and_diagnostic_contract_tamper_fail(self) -> None:
        source_path = self._input("source_binding")
        source = yaml.safe_load(source_path.read_text())
        source["counts"]["post_practice_slots"] = 348
        source_path.write_text(yaml.safe_dump(source, sort_keys=False), encoding="utf-8")
        self._assert_error("SOURCE_COUNT_MISMATCH", expected_hashes=self._rehash("source_binding"))

        shutil.copyfile(ROOT / BUILDER.INPUTS["source_binding"][0], source_path)
        diagnostic_path = self._input("diagnostic")
        diagnostic = yaml.safe_load(diagnostic_path.read_text())
        diagnostic["counts"]["unordered_pairs"] = 1
        diagnostic_path.write_text(yaml.safe_dump(diagnostic, sort_keys=False), encoding="utf-8")
        self._assert_error("DIAGNOSTIC_CONTRACT_MISMATCH", expected_hashes=self._rehash("diagnostic"))

    def test_relative_escape_and_input_output_overlap_fail(self) -> None:
        self._assert_error("OUTPUT_PATH_ESCAPE", output_root=Path("../escape"))
        overlap_root = self.base / "overlap"
        overlap = overlap_root / BUILDER.OUTPUTS["identity"]
        overlap.parent.mkdir(parents=True)
        overlap.write_text("sentinel", encoding="utf-8")
        with self.assertRaises(BUILDER.IdentityError) as caught:
            BUILDER._safe_outputs(overlap_root, {"source": overlap})
        self.assertEqual(caught.exception.code, "INPUT_OUTPUT_OVERLAP")

    def test_input_and_output_symlinks_fail(self) -> None:
        candidate = self._input("candidates")
        outside = self.base / "outside.jsonl"
        outside.write_bytes(candidate.read_bytes())
        candidate.unlink()
        try:
            candidate.symlink_to(outside)
        except OSError:
            with mock.patch.object(Path, "is_symlink", autospec=True, side_effect=lambda path: path == candidate):
                self._assert_error("INPUT_SYMLINK")
        else:
            self._assert_error("INPUT_SYMLINK")

        candidate.unlink(missing_ok=True)
        shutil.copyfile(ROOT / BUILDER.INPUTS["candidates"][0], candidate)
        output_root = self.base / "linked-output"
        real_output = self.base / "real-output"
        real_output.mkdir()
        try:
            output_root.symlink_to(real_output, target_is_directory=True)
        except OSError:
            with mock.patch.object(Path, "is_symlink", autospec=True, side_effect=lambda path: path == output_root):
                self._assert_error("OUTPUT_SYMLINK", output_root=output_root)
        else:
            self._assert_error("OUTPUT_SYMLINK", output_root=output_root)

    def test_unknown_input_and_threshold_cli_parameters_are_rejected(self) -> None:
        for argv in (("--input", "x"), ("--threshold", "0.1"), ("--output-root", str(self.output), "extra")):
            with self.subTest(argv=argv), self.assertRaises(SystemExit):
                BUILDER.main(list(argv))

    def test_atomic_failure_preserves_existing_outputs(self) -> None:
        self._build()
        before = {path.name: path.read_bytes() for path in self.output.rglob("*") if path.is_file()}
        with self._input("candidates").open("ab") as handle:
            handle.write(b"\n")
        self._assert_error("STIMULUS_GROUP_INPUT_HASH_MISMATCH")
        after = {path.name: path.read_bytes() for path in self.output.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_two_distinct_output_roots_are_byte_identical(self) -> None:
        first_root = self.base / "first"
        second_root = self.base / "second"
        self._build(output_root=first_root)
        self._build(output_root=second_root)
        for relative in BUILDER.OUTPUTS.values():
            self.assertEqual((first_root / relative).read_bytes(), (second_root / relative).read_bytes())
            self.assertTrue((first_root / relative).read_bytes().endswith(b"\n"))


if __name__ == "__main__":
    unittest.main()
