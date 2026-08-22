from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import random
import string
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_stimulus_similarity_diagnostic.py"
spec = importlib.util.spec_from_file_location("build_stimulus_similarity_diagnostic", SCRIPT)
BUILDER = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


EXPECTATIONS = BUILDER.Expectations(
    material_rows=10,
    practice_rows=6,
    task_slots=4,
    per_block_slots=(2, 2),
    unique_identities=3,
    exact_duplicate_groups=1,
    analysis_view_rows=6,
    stimulus_subjects=2,
    model_dimension=2,
    max_wordpieces=16,
)


class MockBackend:
    def __init__(self, token_count: int = 4):
        self.token_count = token_count

    def embed(self, texts, model_dir, expected_dimension):
        vectors = []
        for text in texts:
            angle = (int(hashlib.sha256(text.encode()).hexdigest()[:8], 16) % 1000) / 1000
            vector = [1.0, angle]
            norm = math.sqrt(sum(value * value for value in vector))
            vectors.append([value / norm for value in vector])
        return vectors, [self.token_count] * len(texts), {"mock": "1"}


class BuildStimulusSimilarityDiagnosticTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.inputs = self.root / "inputs"
        self.outputs = self.root / "outputs"
        self.dataset = self.root / "zuco_2.0"
        self.materials = self.dataset / "task_materials"
        self.model = self.root / "model-cache" / "test-revision"
        self.inputs.mkdir()
        self.materials.mkdir(parents=True)
        self.model.mkdir(parents=True)
        self._write_fixture()

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def _jsonl(path: Path, rows: list[dict[str, object]]) -> None:
        path.write_text(
            "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
            encoding="utf-8",
        )

    def _write_fixture(self) -> None:
        blocks = (("Practice A", "Practice B", "Practice C", "Alpha!", "Beta"),
                  ("Practice D", "Practice E", "Practice F", "Alpha!", "Gamma"))
        self.csv_hashes = {}
        task = []
        for block, texts in enumerate(blocks, 1):
            path = self.materials / f"nr_{block}.csv"
            path.write_text("".join(f"0;0;{text}\n" for text in texts), encoding="utf-8")
            self.csv_hashes[path.name] = BUILDER.sha256_file(path)
            for line, text in enumerate(texts[3:], 4):
                exact = BUILDER.normalize_exact(text)
                task.append({
                    "block": block,
                    "material_line": line,
                    "stimulus_sha256": BUILDER.sha256_text(exact),
                    "text": exact,
                })
        stimulus = []
        for subject in ("S1", "S2"):
            for slot, row in enumerate(task, 1):
                stimulus.append({
                    "subject": subject,
                    "slot": slot,
                    "block": row["block"],
                    "material_line": row["material_line"],
                    "stimulus_sha256": row["stimulus_sha256"],
                    "stimulus_length_chars": len(row["text"]),
                })
        duplicate_id = task[0]["stimulus_sha256"]
        targeted = {
            "schema_version": 3,
            "counts": {"rows": len(stimulus)},
            "material_contract": {
                "sequence": {
                    "result": "PASS",
                    "ordered_exact_match_count": len(stimulus),
                    "ordered_expected_match_count": len(stimulus),
                    "mismatches": [],
                },
                "cross_block_duplicate_groups": [{"stimulus_sha256": duplicate_id}],
            },
        }
        identities = sorted({row["stimulus_sha256"] for row in task})
        view = [{"stimulus_sha256": identities[index % len(identities)]} for index in range(6)]
        (self.inputs / "targeted.yaml").write_text(yaml.safe_dump(targeted), encoding="utf-8")
        self._jsonl(self.inputs / "stimulus.jsonl", stimulus)
        self._jsonl(self.inputs / "view.jsonl", view)
        (self.inputs / "summary.yaml").write_text(
            yaml.safe_dump({"analysis_view_admission": {"status": "PASS"}}), encoding="utf-8",
        )
        (self.inputs / "card.yaml").write_text(
            yaml.safe_dump({"analysis_view": {"status": "PASS"}}), encoding="utf-8",
        )
        (self.model / "model.safetensors").write_bytes(b"safe tensor fixture")
        (self.model / "config.json").write_text("{}\n", encoding="utf-8")
        self.model_hashes = {
            path.name: BUILDER.sha256_file(path) for path in self.model.iterdir()
        }

    def _paths(self) -> dict[str, Path]:
        return {
            "dataset_root": self.dataset,
            "targeted_manifest": self.inputs / "targeted.yaml",
            "stimulus_manifest": self.inputs / "stimulus.jsonl",
            "analysis_view": self.inputs / "view.jsonl",
            "analysis_summary": self.inputs / "summary.yaml",
            "data_card": self.inputs / "card.yaml",
            "model_dir": self.model,
            "output_source_binding": self.outputs / "source.yaml",
            "output_diagnostic": self.outputs / "diagnostic.yaml",
            "output_candidates": self.outputs / "candidates.jsonl",
            "output_report": self.outputs / "report.md",
        }

    def _build(self, **kwargs):
        values = self._paths()
        values.update({
            "root": self.root,
            "expectations": EXPECTATIONS,
            "csv_hashes": self.csv_hashes,
            "expected_model_hashes": self.model_hashes,
            "expected_model_revision": "test-revision",
            "embedding_backend": MockBackend(),
        })
        values.update(kwargs)
        return BUILDER.build(**values)

    def _assert_error(self, code: str, **kwargs) -> None:
        with self.assertRaises(BUILDER.DiagnosticError) as caught:
            self._build(**kwargs)
        self.assertEqual(caught.exception.code, code)

    def test_normalization_metrics_rounding_and_pair_formula(self) -> None:
        self.assertEqual(BUILDER.normalize_exact("  A\u3000Ｂ  "), "A B")
        self.assertEqual(BUILDER.normalize_lexical("  Hello, WORLD! "), "hello world")
        self.assertEqual(BUILDER.levenshtein_distance("kitten", "sitting"), 3)
        self.assertEqual(BUILDER.token_jaccard(("a", "b"), ("b", "c")), 1 / 3)
        self.assertEqual(BUILDER.cosine((1.0, 0.0), (0.5, 0.5)), 0.5)
        self.assertEqual(BUILDER.round_half_even(0.1234565), 0.123456)
        self.assertEqual(BUILDER.unordered_pair_count(344), 58996)

    def test_myers_matches_reference_dynamic_programming(self) -> None:
        rng = random.Random(19)
        for _ in range(200):
            left = "".join(rng.choice(string.ascii_lowercase) for _ in range(rng.randrange(35)))
            right = "".join(rng.choice(string.ascii_lowercase) for _ in range(rng.randrange(35)))
            prior = list(range(len(right) + 1))
            for i, left_char in enumerate(left, 1):
                current = [i]
                for j, right_char in enumerate(right, 1):
                    current.append(min(current[-1] + 1, prior[j] + 1, prior[j - 1] + (left_char != right_char)))
                prior = current
            self.assertEqual(BUILDER.levenshtein_distance(left, right), prior[-1])

    def test_build_binds_counts_duplicates_and_all_pairs(self) -> None:
        result = self._build()
        binding, diagnostic = result["source_binding"], result["diagnostic"]
        self.assertEqual(binding["counts"]["material_rows"], 10)
        self.assertEqual(binding["counts"]["practice_rows_excluded"], 6)
        self.assertEqual(binding["counts"]["post_practice_slots"], 4)
        self.assertEqual(len(binding["identities"]), 3)
        self.assertTrue(binding["exact_duplicate_groups"][0]["occurrences_remain_distinct"])
        self.assertEqual(diagnostic["counts"]["unordered_pairs"], 3)
        self.assertTrue(all(row["id_a"] < row["id_b"] for row in result["candidates"]))
        self.assertEqual(
            [(row["id_a"], row["id_b"]) for row in result["candidates"]],
            sorted((row["id_a"], row["id_b"]) for row in result["candidates"]),
        )
        self.assertFalse(diagnostic["grouping_policy"]["final_threshold_selected"])
        self.assertFalse(diagnostic["grouping_policy"]["near_duplicate_groups_emitted"])
        self.assertIsNone(binding["metadata_availability"]["document_id"])
        self.assertIsNone(binding["metadata_availability"]["paragraph_id"])

    def test_candidate_is_broad_or_prefilter_not_a_grouping_policy(self) -> None:
        result = self._build()
        diagnostic = result["diagnostic"]
        self.assertIn(" OR ", diagnostic["broad_diagnostic_prefilter"]["rule"])
        self.assertFalse(diagnostic["broad_diagnostic_prefilter"]["final_grouping_threshold"])
        self.assertTrue(all(set(row) == set(BUILDER.CANDIDATE_FIELDS) for row in result["candidates"]))
        self.assertTrue(all(item["formal_group_ids_emitted"] is False
                            for groups in diagnostic["component_risk_diagnostics"].values()
                            for item in groups))

    def test_outputs_contain_no_text_tokens_or_vectors(self) -> None:
        self._build()
        rendered = b"\n".join(path.read_bytes() for path in self.outputs.iterdir()).lower()
        for prohibited in (b"alpha!", b"beta", b"gamma", b"practice a"):
            self.assertNotIn(prohibited, rendered)
        candidates = [json.loads(line) for line in (self.outputs / "candidates.jsonl").read_text().splitlines()]
        self.assertTrue(all(set(row) == set(BUILDER.CANDIDATE_FIELDS) for row in candidates))

    def test_source_hash_slot_length_and_sequence_tamper_fail_closed(self) -> None:
        with (self.materials / "nr_1.csv").open("a", encoding="utf-8") as handle:
            handle.write("0;0;tamper\n")
        self._assert_error("STIMULUS_SOURCE_HASH_MISMATCH")
        self._write_fixture()
        with (self.materials / "nr_1.csv").open("a", encoding="utf-8") as handle:
            handle.write("0;0;extra row\n")
        self.csv_hashes["nr_1.csv"] = BUILDER.sha256_file(self.materials / "nr_1.csv")
        self._assert_error("MATERIAL_COUNT_MISMATCH")
        self._write_fixture()
        rows = [json.loads(line) for line in (self.inputs / "stimulus.jsonl").read_text().splitlines()]
        rows[0]["stimulus_sha256"] = "0" * 64
        self._jsonl(self.inputs / "stimulus.jsonl", rows)
        self._assert_error("SLOT_HASH_MISMATCH")
        self._write_fixture()
        rows = [json.loads(line) for line in (self.inputs / "stimulus.jsonl").read_text().splitlines()]
        rows[0]["stimulus_length_chars"] += 1
        self._jsonl(self.inputs / "stimulus.jsonl", rows)
        self._assert_error("SLOT_LENGTH_MISMATCH")
        self._write_fixture()
        rows = [json.loads(line) for line in (self.inputs / "stimulus.jsonl").read_text().splitlines()]
        rows[0]["material_line"] = 99
        self._jsonl(self.inputs / "stimulus.jsonl", rows)
        self._assert_error("SLOT_SOURCE_POSITION_MISMATCH")
        self._write_fixture()
        targeted = yaml.safe_load((self.inputs / "targeted.yaml").read_text())
        targeted["material_contract"]["sequence"]["ordered_exact_match_count"] = 7
        (self.inputs / "targeted.yaml").write_text(yaml.safe_dump(targeted), encoding="utf-8")
        self._assert_error("TARGETED_MATERIAL_SEQUENCE_MISMATCH")

    def test_analysis_view_coverage_and_admission_fail_closed(self) -> None:
        rows = [json.loads(line) for line in (self.inputs / "view.jsonl").read_text().splitlines()]
        rows[:] = [rows[0]] * len(rows)
        self._jsonl(self.inputs / "view.jsonl", rows)
        self._assert_error("ANALYSIS_VIEW_IDENTITY_MISSING")
        self._write_fixture()
        (self.inputs / "summary.yaml").write_text(
            yaml.safe_dump({"analysis_view_admission": {"status": "FAIL"}}), encoding="utf-8",
        )
        self._assert_error("ANALYSIS_VIEW_NOT_ADMITTED")

    def test_model_revision_allowlist_hash_and_wordpiece_limit_fail(self) -> None:
        self._assert_error("MODEL_REVISION_MISMATCH", expected_model_revision="other")
        (self.model / "weights.bin").write_bytes(b"unsafe")
        self._assert_error("UNSAFE_MODEL_FILE")
        (self.model / "weights.bin").unlink()
        self._assert_error("MODEL_FILE_HASH_MISMATCH", expected_model_hashes={**self.model_hashes, "config.json": "0" * 64})
        self._assert_error("STIMULUS_EMBEDDING_TRUNCATION_REQUIRED", embedding_backend=MockBackend(17))
        (self.model / "model.safetensors").unlink()
        hashes_without_weights = {"config.json": self.model_hashes["config.json"]}
        self._assert_error("MODEL_SAFETENSORS_MISSING", expected_model_hashes=hashes_without_weights)

    def test_committed_input_hash_tamper_fails(self) -> None:
        paths = self._paths()
        hashes = {
            label: BUILDER.sha256_file(paths[label])
            for label in ("targeted_manifest", "stimulus_manifest", "analysis_view", "analysis_summary", "data_card")
        }
        hashes["data_card"] = "0" * 64
        self._assert_error("COMMITTED_INPUT_HASH_MISMATCH", committed_hashes=hashes)

    def test_two_builds_are_byte_identical(self) -> None:
        self._build()
        first = {path.name: path.read_bytes() for path in self.outputs.iterdir()}
        self._build()
        second = {path.name: path.read_bytes() for path in self.outputs.iterdir()}
        self.assertEqual(first, second)

    def test_failure_leaves_no_partial_outputs(self) -> None:
        self._assert_error("STIMULUS_EMBEDDING_TRUNCATION_REQUIRED", embedding_backend=MockBackend(17))
        self.assertFalse(self.outputs.exists())

    def test_path_escape_symlink_and_unknown_cli_fail(self) -> None:
        outside = Path(self.temp.name).parent / f"outside-{Path(self.temp.name).name}.yaml"
        outside.write_text("schema_version: 3\n", encoding="utf-8")
        try:
            self._assert_error("INPUT_PATH_ESCAPE", targeted_manifest=outside)
        finally:
            outside.unlink(missing_ok=True)
        link = self.inputs / "target-link.yaml"
        try:
            link.symlink_to(self.inputs / "targeted.yaml")
        except OSError:
            pass
        else:
            self._assert_error("INPUT_SYMLINK", targeted_manifest=link)
        paths = self._paths()
        argv = []
        for option, label in (
            ("--dataset-root", "dataset_root"),
            ("--targeted-manifest", "targeted_manifest"),
            ("--stimulus-manifest", "stimulus_manifest"),
            ("--analysis-view", "analysis_view"),
            ("--analysis-summary", "analysis_summary"),
            ("--data-card", "data_card"),
            ("--model-dir", "model_dir"),
            ("--output-source-binding", "output_source_binding"),
            ("--output-diagnostic", "output_diagnostic"),
            ("--output-candidates", "output_candidates"),
            ("--output-report", "output_report"),
        ):
            argv.extend((option, str(paths[label])))
        argv.extend(("--unknown-input", "value"))
        with self.assertRaises(SystemExit):
            BUILDER.main(argv)


if __name__ == "__main__":
    unittest.main()
