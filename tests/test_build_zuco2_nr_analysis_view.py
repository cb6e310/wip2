from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_zuco2_nr_analysis_view.py"
spec = importlib.util.spec_from_file_location("build_zuco2_nr_analysis_view", SCRIPT)
BUILDER = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


ANOMALY_FILES = tuple(
    f"task1 - NR/Preprocessed/YTL/gip_YTL_NR{block}_EEG.mat"
    for block in (3, 5, 6)
)
EXPECTATIONS = BUILDER.Expectations(
    all_rows=17,
    valid_finite_multisample=12,
    admitted=6,
    excluded=11,
    nonfinite_placeholder=1,
    finite_single_sample=4,
    finite_multisample_event_unresolved=6,
    subjects=1,
    sessions=1,
    slots_per_subject=17,
    channels=105,
    blocks=5,
    identity_files=1,
    ytl_finite_event_unresolved_by_block=((3, 1), (5, 1), (6, 4)),
    anomaly_files=ANOMALY_FILES,
)


class BuildAnalysisViewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.inputs = self.root / "inputs"
        self.outputs = self.root / "outputs"
        self.inputs.mkdir()
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
        self.rows: list[dict[str, object]] = []
        self.events: list[dict[str, object]] = []
        finite_bad_blocks = [3, 5, 6, 6, 6, 6]
        for slot in range(1, 18):
            if slot <= 6:
                state, event_valid, block, reason = "VALID_FINITE_MULTISAMPLE", True, 1, None
            elif slot == 7:
                state, event_valid, block, reason = "NONFINITE_PLACEHOLDER", True, 2, "NO_FINITE_EEG_TIMESERIES_VALUES"
            elif slot <= 11:
                state, event_valid, block, reason = "FINITE_SINGLE_SAMPLE_REVIEW_REQUIRED", False, 3 if slot == 8 else 6, "FINITE_BUT_NOT_A_MULTISAMPLE_TIMESERIES;EVENT_OCCURRENCE_UNRESOLVED"
            else:
                state, event_valid, block, reason = "VALID_FINITE_MULTISAMPLE", False, finite_bad_blocks[slot - 12], "EVENT_OCCURRENCE_UNRESOLVED;SEGMENT_CORRESPONDENCE_NOT_EXACT"
            admitted = slot <= 6
            segment = "EXACT_MATCH" if admitted else (
                "NOT_APPLICABLE_EXCLUDED_CELL" if event_valid else "EVENT_UNRESOLVED"
            )
            row = {
                "subject": "YTL", "session": 1, "task": "NR", "block": block,
                "slot": slot, "material_line": slot + 3,
                "occurrence_id": hashlib.sha256(f"occurrence-{slot}".encode()).hexdigest(),
                "stimulus_sha256": hashlib.sha256(f"stimulus-{slot}".encode()).hexdigest(),
                "content_present": True, "eeg_cell_state": state,
                "event_occurrence_valid": event_valid,
                "segment_correspondence_state": segment,
                "final_admission_candidate": admitted,
                "final_exclusion_reason": reason,
                "raw_shape": [100 + slot, 105] if admitted else [1, 1],
                "raw_samples": 100 + slot if admitted else 1,
                "raw_channels": 105 if admitted else 1,
            }
            event = {
                "subject": "YTL", "global_slot": slot, "block": block,
                "material_line": slot + 3, "summary_cell_state": state,
                "segment_correspondence_state": segment,
                "final_admission_candidate": admitted, "exclusion_reason": reason,
                "event_pair_state": "VALID" if event_valid else "INVALID",
            }
            self.rows.append(row)
            self.events.append(event)
        file_contract = [
            {"path": path, "subject": "YTL", "block": block, "event_semantics_bound": False}
            for path, block in zip(ANOMALY_FILES, (3, 5, 6))
        ]
        self.targeted = {
            "schema_version": 3,
            "admission_result": "FAIL",
            "counts": {"rows": 17},
            "summary_schema": [{
                "subject": "YTL", "path": "task1 - NR/Matlab files/resultsYTL_NR.mat",
                "fields": ["content", "rawData", "word", "wordbounds"],
            }],
            "eeg_cell_ledger": {"overall": {
                "VALID_FINITE_MULTISAMPLE": 12,
                "NONFINITE_PLACEHOLDER": 1,
                "FINITE_SINGLE_SAMPLE_REVIEW_REQUIRED": 4,
            }},
            "event_contract": {
                "files_with_semantic_anomaly": list(ANOMALY_FILES),
                "files": file_contract,
            },
            "condition_3_subpredicates": [
                {"id": "unit", "result": "FAIL"},
                {"id": "identity", "result": "PASS"},
            ],
            "physical_schema": {
                "sampling_hz_values": [500],
                "acquisition_reference_values": ["Cz"],
                "processed_reference_values": ["common-average"],
                "unit_values": [],
            },
            "unit_layer_contract": {
                "preprocessed_EEG_data_unit_status": "UNRESOLVED",
                "summary_rawData_unit_status": "UNRESOLVED",
                "summary_rawData_layer_status": "BOUND_BY_EXACT_CORRESPONDENCE",
                "summary_rawData_reference_status": "BOUND_BY_EXACT_CORRESPONDENCE",
            },
            "hash_provenance": {
                "result": "PASS",
                "files": [{"identity_status": "REUSED_VERIFIED_RUN005_NO_REHASH"}],
                "large_files_rehashed": False,
            },
        }
        self.correspondence = {
            "schema_version": 1,
            "counts": {"EVENT_UNRESOLVED": 6, "EXACT_MATCH": 6},
            "segment_convention_global_unique": {
                "result": "PASS", "selected": "EEGLAB_ONE_BASED_FINISH_INCLUSIVE",
            },
        }
        self._save()

    def _save(self) -> None:
        (self.inputs / "targeted.yaml").write_text(yaml.safe_dump(self.targeted, sort_keys=False), encoding="utf-8")
        self._jsonl(self.inputs / "stimulus.jsonl", self.rows)
        self._jsonl(self.inputs / "events.jsonl", self.events)
        (self.inputs / "segments.yaml").write_text(yaml.safe_dump(self.correspondence, sort_keys=False), encoding="utf-8")

    def _paths(self) -> dict[str, Path]:
        return {
            "targeted_manifest": self.inputs / "targeted.yaml",
            "stimulus_manifest": self.inputs / "stimulus.jsonl",
            "event_manifest": self.inputs / "events.jsonl",
            "segment_correspondence": self.inputs / "segments.yaml",
            "output_view": self.outputs / "view.jsonl",
            "output_summary": self.outputs / "summary.yaml",
            "output_data_card": self.outputs / "data-card.yaml",
            "output_data_card_report": self.outputs / "data-card.md",
        }

    def _build(self, **kwargs: object) -> dict[str, object]:
        values: dict[str, object] = self._paths()
        values.update(root=self.root, expectations=EXPECTATIONS)
        values.update(kwargs)
        return BUILDER.build(**values)

    def _assert_error(self, code: str, **kwargs: object) -> None:
        with self.assertRaises(BUILDER.BuildError) as caught:
            self._build(**kwargs)
        self.assertEqual(caught.exception.code, code)

    def test_unknown_unit_and_ledgered_exclusions_produce_pass_data_card(self) -> None:
        result = self._build()
        summary = result["summary"]
        card = result["data_card"]
        self.assertEqual(summary["full_release_diagnostic"]["status"], "FAIL")
        self.assertEqual(summary["analysis_view_admission"]["status"], "PASS")
        self.assertEqual(summary["unit_policy"]["physical_unit_status"], "UNRESOLVED_RELEASE_NATIVE_AMPLITUDE")
        self.assertFalse(summary["unit_policy"]["unit_inference_performed"])
        self.assertEqual(card["analysis_view"]["status"], "PASS")
        self.assertTrue((self.outputs / "data-card.md").is_file())

    def test_admitted_conjunction_fails_closed_for_each_term(self) -> None:
        mutations = (
            ("content_present", False, None),
            ("eeg_cell_state", "NONFINITE_PLACEHOLDER", "summary_cell_state"),
            ("event_occurrence_valid", False, None),
            ("segment_correspondence_state", "EVENT_UNRESOLVED", "segment_correspondence_state"),
            ("final_exclusion_reason", "unexpected", "exclusion_reason"),
        )
        for field, value, event_field in mutations:
            with self.subTest(field=field):
                self._write_fixture()
                self.rows[0][field] = value
                if event_field:
                    self.events[0][event_field] = value
                self._save()
                self._assert_error("ADMITTED_PREDICATE_FAILED")

    def test_excluded_row_requires_reason(self) -> None:
        self.rows[6]["final_exclusion_reason"] = None
        self.events[6]["exclusion_reason"] = None
        self._save()
        self._assert_error("EXCLUSION_REASON_MISSING")

    def test_duplicate_missing_and_mismatched_join_keys_fail(self) -> None:
        self.events[-1] = dict(self.events[0])
        self._save()
        self._assert_error("EVENT_KEY_DUPLICATE")
        self._write_fixture()
        self.events[-1]["global_slot"] = 99
        self._save()
        self._assert_error("EVENT_KEY_MISSING")
        self._write_fixture()
        self.events[0]["block"] = 7
        self._save()
        self._assert_error("JOIN_FIELD_MISMATCH")

    def test_schema_and_input_hash_tamper_fail(self) -> None:
        self.targeted["schema_version"] = 2
        self._save()
        self._assert_error("TARGETED_SCHEMA_MISMATCH")
        self._write_fixture()
        expected = {label: hashlib.sha256(path.read_bytes()).hexdigest() for label, path in list(self._paths().items())[:4]}
        with (self.inputs / "targeted.yaml").open("a", encoding="utf-8") as handle:
            handle.write("# tamper\n")
        self._assert_error("INPUT_HASH_MISMATCH", expected_hashes=expected)

    def test_counts_overlap_and_nr3_nr5_nr6_are_recomputed(self) -> None:
        summary = self._build()["summary"]
        self.assertEqual(summary["counts"]["admitted"], 6)
        self.assertEqual(summary["counts"]["excluded_union"], 11)
        self.assertEqual(summary["exclusion_overlap"]["event_invalid_total"], 10)
        self.assertEqual(summary["exclusion_overlap"]["finite_single_sample_and_event_invalid"], 4)
        self.assertEqual(summary["event_anomalies"]["finite_multisample_event_unresolved_by_block"], {3: 1, 5: 1, 6: 4})
        self.assertEqual(tuple(summary["event_anomalies"]["files"]), ANOMALY_FILES)

    def test_missing_nr5_anomaly_path_fails(self) -> None:
        self.targeted["event_contract"]["files_with_semantic_anomaly"].pop(1)
        self._save()
        self._assert_error("YTL_ANOMALY_PATH_MISMATCH")

    def test_view_has_exact_allowlist_and_no_sensitive_fields(self) -> None:
        self._build()
        view = [json.loads(line) for line in (self.outputs / "view.jsonl").read_text().splitlines()]
        self.assertEqual(len(view), 6)
        self.assertTrue(all(set(row) == set(BUILDER.VIEW_FIELDS) for row in view))
        rendered = json.dumps(view).lower()
        for prohibited in ("stimulus_text", "latency", "eeg_value", "finite_count", "waveform_hash"):
            self.assertNotIn(prohibited, rendered)

    def test_two_builds_are_byte_identical(self) -> None:
        self._build()
        first = {path.name: path.read_bytes() for path in self.outputs.iterdir()}
        self._build()
        second = {path.name: path.read_bytes() for path in self.outputs.iterdir()}
        self.assertEqual(first, second)

    def test_failure_leaves_no_partial_outputs(self) -> None:
        self.rows[0]["content_present"] = False
        self._save()
        self._assert_error("ADMITTED_PREDICATE_FAILED")
        self.assertFalse(self.outputs.exists())

    def test_symlink_path_escape_and_unknown_cli_input_fail(self) -> None:
        outside = Path(self.temp.name).parent / f"outside-{Path(self.temp.name).name}.yaml"
        outside.write_text("schema_version: 3\n", encoding="utf-8")
        try:
            self._assert_error("INPUT_PATH_ESCAPE", targeted_manifest=outside)
        finally:
            outside.unlink(missing_ok=True)
        if hasattr(Path, "symlink_to"):
            link = self.inputs / "link.yaml"
            try:
                link.symlink_to(self.inputs / "targeted.yaml")
            except OSError:
                pass
            else:
                self._assert_error("INPUT_SYMLINK", targeted_manifest=link)
        paths = self._paths()
        argv: list[str] = []
        for option, label in (
            ("--targeted-manifest", "targeted_manifest"),
            ("--stimulus-manifest", "stimulus_manifest"),
            ("--event-manifest", "event_manifest"),
            ("--segment-correspondence", "segment_correspondence"),
            ("--output-view", "output_view"),
            ("--output-summary", "output_summary"),
            ("--output-data-card", "output_data_card"),
            ("--output-data-card-report", "output_data_card_report"),
        ):
            argv.extend((option, str(paths[label])))
        argv.extend(("--unknown-input", "value"))
        with self.assertRaises(SystemExit):
            BUILDER.main(argv)


if __name__ == "__main__":
    unittest.main()
