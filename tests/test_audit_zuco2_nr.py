from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import h5py
import numpy as np
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_zuco2_nr.py"
spec = importlib.util.spec_from_file_location("audit_zuco2_nr", SCRIPT)
AUDIT = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = AUDIT
spec.loader.exec_module(AUDIT)

EVENT_MAPPING = {
    "10": "ORDINARY_ONSET", "11": "ORDINARY_FINISH",
    "12": "CONTROL_ONSET", "13": "CONTROL_FINISH", "15": "CONTROL_RESPONSE",
}


def _chars(group: h5py.Group, name: str, value: str) -> h5py.Dataset:
    data = np.asarray([ord(char) for char in value], dtype=np.uint16).reshape(-1, 1)
    return group.create_dataset(name, data=data)


def _reference_field(group: h5py.Group, name: str, nodes: list[h5py.Dataset]) -> None:
    values = np.empty((len(nodes), 1), dtype=h5py.ref_dtype)
    for index, node in enumerate(nodes):
        values[index, 0] = node.ref
    group.create_dataset(name, data=values)


class AuditZuco2NRTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_compact_ytl_anomalies_include_nr3_nr5_nr6(self) -> None:
        files = [
            {
                "path": f"task1 - NR/Preprocessed/YTL/gip_YTL_NR{block}_EEG.mat",
                "subject": "YTL",
                "events": {"event_semantics_bound": False, "sanitized_anomalies": [{"block": block}]},
            }
            for block in (3, 5, 6)
        ]
        files.extend([
            {"path": "other.mat", "subject": "YTL", "events": {"event_semantics_bound": True}},
            {"path": "nr5-other-subject.mat", "subject": "YAC", "events": {"event_semantics_bound": False}},
        ])
        verdicts = AUDIT.compact_ytl_anomaly_verdicts(files)
        self.assertEqual([item["path"] for item in verdicts], [item["path"] for item in files[:3]])
        self.assertTrue(all(item["verdict"] == "PHYSICAL_ANOMALY_RETAINED" for item in verdicts))

    def _material_files(self, *, mismatch: bool = False) -> tuple[list[Path], list[dict[str, object]]]:
        paths: list[Path] = []
        expected: list[dict[str, object]] = []
        post_counts = [50, 50, 51, 50, 50, 49, 49]
        for block, post_count in enumerate(post_counts, 1):
            path = self.root / f"nr_{block}.csv"
            lines = []
            for offset in range(post_count + 3):
                text = f"practice-{block}-{offset}" if offset < 3 else f"sentence-{block}-{offset}"
                lines.append(f"x;y;{text}\n")
                if offset >= 3:
                    expected.append({"block": block, "text": text})
            path.write_text("".join(lines), encoding="utf-8")
            paths.append(path)
        if mismatch:
            expected[123]["text"] = "mismatch"
        return paths, expected

    def _event_eeg(
        self,
        path: Path,
        *,
        latencies: tuple[float, ...] = (1.0, 9.0),
        types: tuple[str, ...] = ("10", "11"),
    ) -> None:
        with h5py.File(path, "w") as file:
            refs = file.create_group("refs")
            eeg = file.create_group("EEG")
            eeg.create_dataset("data", shape=(10, 105), dtype=np.float64)
            eeg.create_dataset("pnts", data=np.asarray([[10.0]]))
            event = eeg.create_group("event")
            urevent_group = eeg.create_group("urevent")
            urevent_group.create_dataset("latency", data=np.zeros((len(latencies), 1)))
            fields: dict[str, list[h5py.Dataset]] = {
                "latency": [], "duration": [], "urevent": [], "type": [], "value": []
            }
            for index, (latency, event_type) in enumerate(zip(latencies, types), 1):
                fields["latency"].append(refs.create_dataset(f"latency_{index}", data=[[latency]]))
                fields["duration"].append(refs.create_dataset(f"duration_{index}", data=[[0.0]]))
                fields["urevent"].append(refs.create_dataset(f"urevent_{index}", data=[[float(index)]]))
                fields["type"].append(_chars(refs, f"type_{index}", event_type))
                fields["value"].append(_chars(refs, f"value_{index}", "trigger"))
            for name, nodes in fields.items():
                _reference_field(event, name, nodes)

    def _metadata_eeg(
        self,
        path: Path,
        *,
        labels: list[str] | None = None,
        missing_z: bool = False,
    ) -> None:
        self._event_eeg(path)
        labels = labels or [f"E{index}" for index in range(2, 107)]
        with h5py.File(path, "r+") as file:
            refs, eeg = file["refs"], file["EEG"]
            eeg.create_dataset("srate", data=[[500.0]])
            eeg.create_dataset("trials", data=[[1.0]])
            processed = _chars(refs, "processed_reference", "common")
            _reference_field(eeg, "ref", [processed])
            chanlocs = eeg.create_group("chanlocs")
            _reference_field(chanlocs, "labels", [_chars(refs, f"label_{index}", label) for index, label in enumerate(labels)])
            for field in ("X", "Y", "Z", "theta", "radius"):
                nodes = []
                for index in range(105):
                    data = np.empty((0, 1)) if missing_z and field == "Z" and index == 2 else [[float(index + 1)]]
                    nodes.append(refs.create_dataset(f"{field}_{index}", data=data))
                _reference_field(chanlocs, field, nodes)
            automagic = file.create_group("automagic")
            acquisition = _chars(refs, "acquisition_reference", "Cz")
            _reference_field(automagic, "EEGReference", [acquisition])

    def test_cell_states_are_mutually_exclusive(self) -> None:
        path = self.root / "cells.h5"
        with h5py.File(path, "w") as file:
            fixtures = {
                "placeholder": np.asarray([[np.nan]]),
                "single": np.ones((1, 105)),
                "valid": np.ones((2, 105)),
                "partial": np.vstack([np.ones((1, 105)), np.full((1, 105), np.nan)]),
                "empty": np.empty((0, 105)),
                "wrong_axis": np.ones((2, 104)),
            }
            expected = {
                "placeholder": "NONFINITE_PLACEHOLDER",
                "single": "FINITE_SINGLE_SAMPLE_REVIEW_REQUIRED",
                "valid": "VALID_FINITE_MULTISAMPLE",
                "partial": "PARTIAL_NONFINITE",
                "empty": "EMPTY",
                "wrong_axis": "INVALID_AXIS",
            }
            observed = []
            for name, data in fixtures.items():
                result = AUDIT.classify_eeg_cell(True, file.create_dataset(name, data=data))
                self.assertEqual(result["eeg_cell_state"], expected[name])
                self.assertEqual(result["admissible_sentence_eeg"], name == "valid")
                if name != "valid":
                    self.assertTrue(result["missing_or_exclusion_reason"])
                observed.append(result["eeg_cell_state"])
            missing = AUDIT.classify_eeg_cell(False, None)
            self.assertEqual(missing["eeg_cell_state"], "MISSING_REFERENCE")
            observed.append(missing["eeg_cell_state"])
            self.assertEqual(set(observed), set(AUDIT.CELL_STATES))

    def test_practice_exclusion_exact_sequence_and_slot_mismatch(self) -> None:
        paths, expected = self._material_files()
        material = AUDIT.read_material_contract(paths)
        self.assertEqual((material["total_rows"], material["practice_rows_excluded"], material["post_practice_rows"]), (370, 21, 349))
        rows = []
        for subject in ("YAA", "YBB"):
            rows.extend({"subject": subject, "task": "NR", "slot": slot, "stimulus_sha256": AUDIT.stimulus_id(str(item["text"])), "block": None, "material_line": None, "occurrence_id": None} for slot, item in enumerate(expected, 1))
        contract = AUDIT.apply_material_sequence(rows, material)
        self.assertEqual(contract["result"], "PASS")
        self.assertEqual(contract["ordered_exact_match_count"], 698)
        self.assertTrue(all(row["block"] and row["material_line"] and row["occurrence_id"] for row in rows))
        rows[123]["stimulus_sha256"] = AUDIT.stimulus_id("mismatch")
        self.assertEqual(AUDIT.apply_material_sequence(rows, material)["result"], "FAIL")

    def test_cross_block_duplicate_has_distinct_occurrence_ids(self) -> None:
        repeated = AUDIT.stimulus_id("same")
        material = [
            {"block": 1, "material_line": 4, "stimulus_sha256": repeated},
            {"block": 2, "material_line": 4, "stimulus_sha256": repeated},
        ]
        group = AUDIT.duplicate_groups(material)[0]
        self.assertTrue(group["cross_block"])
        self.assertTrue(group["occurrence_ids_distinct"])
        self.assertEqual(group["blocks"], [1, 2])

    def test_event_structure_rejects_bad_latencies(self) -> None:
        checks = AUDIT.validate_event_values([1, 2], [0, 0], [1, 2], pnts=10, urevent_count=2)
        self.assertTrue(all(checks.values()))
        self.assertFalse(AUDIT.validate_event_values([1, np.nan], [0, 0], [1, 2], pnts=10, urevent_count=2)["latency_finite"])
        self.assertFalse(AUDIT.validate_event_values([2, 1], [0, 0], [1, 2], pnts=10, urevent_count=2)["latency_nondecreasing"])
        self.assertFalse(AUDIT.validate_event_values([1, 11], [0, 0], [1, 2], pnts=10, urevent_count=2)["latency_in_sample_bounds"])

    def test_event_semantics_requires_release_mapping(self) -> None:
        path = self.root / "events.mat"
        self._event_eeg(path)
        with h5py.File(path, "r") as file:
            bound = AUDIT.audit_events(file, file["EEG"], semantic_mapping=EVENT_MAPPING)
            unbound = AUDIT.audit_events(file, file["EEG"], semantic_mapping={})
        self.assertTrue(bound["event_structure_valid"])
        self.assertTrue(bound["event_semantics_bound"])
        self.assertTrue(unbound["event_structure_valid"])
        self.assertFalse(unbound["event_semantics_bound"])

    def test_any_failed_condition3_subpredicate_keeps_failure(self) -> None:
        items = [
            {"id": "unit", "result": "PASS"},
            {"id": "layer", "result": "FAIL"},
            {"id": "events", "result": "PASS"},
        ]
        self.assertEqual(AUDIT.condition3_from_subpredicates(items), ("FAIL", ["layer"]))
        items[1]["result"] = "PASS"
        self.assertEqual(AUDIT.condition3_from_subpredicates(items), ("PASS", []))

    def test_output_is_byte_stable_and_contains_no_text_or_values(self) -> None:
        manifest = {"schema_version": 3, "audit_boundaries": {"eeg_values_emitted": False}}
        rows = [{"subject": "YAC", "slot": 1, "stimulus_sha256": AUDIT.stimulus_id("SECRET_SENTENCE"), "raw_shape": [2, 105]}]
        occurrences = [{"subject": "YAC", "global_slot": 1, "event_pair_state": "VALID"}]
        correspondence = {"schema_version": 1, "counts": {"EXACT_MATCH": 1}}
        outputs = []
        for prefix in ("one", "two"):
            paths = (
                self.root / f"{prefix}.yaml", self.root / f"{prefix}.jsonl",
                self.root / f"{prefix}-events.jsonl", self.root / f"{prefix}-segments.yaml",
            )
            AUDIT.write_outputs(manifest, rows, occurrences, correspondence, *paths)
            outputs.append(tuple(path.read_bytes() for path in paths))
        self.assertEqual(outputs[0], outputs[1])
        rendered = b"".join(outputs[0]).decode("utf-8")
        self.assertNotIn("SECRET_SENTENCE", rendered)
        self.assertNotIn("7.25", rendered)

    def test_complete_event_parser_builds_303_plus_46_occurrences(self) -> None:
        codes: list[str] = []
        for _ in range(303):
            codes.extend(("10", "11"))
        for _ in range(46):
            codes.extend(("12", "13", "15"))
        result = AUDIT.parse_task1_events(codes, list(range(1, len(codes) + 1)), EVENT_MAPPING)
        self.assertTrue(result["pair_contract_valid"])
        self.assertEqual((result["ordinary_count"], result["control_count"]), (303, 46))
        self.assertEqual(len(result["occurrences"]), 349)
        self.assertEqual(result["control_response_count"], 46)

    def test_event_parser_detects_orphan_nested_wrong_finish_and_response_errors(self) -> None:
        fixtures = {
            "ORPHAN_FINISH": ["11"],
            "NESTED_ONSET": ["10", "10", "11", "11"],
            "WRONG_FINISH_CLASS": ["10", "13"],
            "MISSING_CONTROL_RESPONSE": ["12", "13", "10", "11"],
            "EXTRA_OR_MISPLACED_CONTROL_RESPONSE": ["15"],
        }
        for reason, codes in fixtures.items():
            with self.subTest(reason=reason):
                result = AUDIT.parse_task1_events(codes, list(range(1, len(codes) + 1)), EVENT_MAPPING)
                self.assertFalse(result["pair_contract_valid"])
                self.assertIn(reason, {item["reason"] for item in result["anomalies"]})

    def test_complete_parser_recovers_control_occurrence_ignored_by_old_projection(self) -> None:
        codes = ["10", "11", "12", "13", "15"]
        result = AUDIT.parse_task1_events(codes, [1, 2, 3, 4, 5], EVENT_MAPPING)
        self.assertTrue(result["pair_contract_valid"])
        self.assertEqual(len(result["occurrences"]), 2)
        self.assertEqual(sum(code == "10" for code in codes), 1)

    def test_event_count_and_material_alignment_mismatch_fail(self) -> None:
        result = AUDIT.parse_task1_events(["10", "11"], [1, 2], EVENT_MAPPING)
        self.assertNotEqual(len(result["occurrences"]), 50)
        self.assertTrue(result["pair_contract_valid"])

    def test_endpoint_conventions_and_exact_comparison(self) -> None:
        data = np.arange(30, dtype=np.float64).reshape(10, 3)
        summary_inclusive = data[1:5]
        exclusive = data[1:4]
        self.assertEqual(AUDIT.compare_segment_arrays(exclusive, summary_inclusive)["state"], "SHAPE_MISMATCH")
        self.assertEqual(AUDIT.compare_segment_arrays(data[1:5], summary_inclusive)["state"], "EXACT_MATCH")
        changed = summary_inclusive.copy()
        changed[0, 0] += 1
        self.assertEqual(AUDIT.compare_segment_arrays(data[1:5], changed)["state"], "VALUE_MISMATCH")
        self.assertEqual(AUDIT._window_bounds(2, 5, AUDIT.ENDPOINT_CONVENTIONS[0]), (1, 4))
        self.assertEqual(AUDIT._window_bounds(2, 5, AUDIT.ENDPOINT_CONVENTIONS[1]), (1, 5))
        counts = {
            AUDIT.ENDPOINT_CONVENTIONS[0]: __import__("collections").Counter({"SHAPE_MISMATCH": 2}),
            AUDIT.ENDPOINT_CONVENTIONS[1]: __import__("collections").Counter({"EXACT_MATCH": 2}),
        }
        self.assertEqual(AUDIT.select_global_convention(counts, 2)["selected"], AUDIT.ENDPOINT_CONVENTIONS[1])
        counts[AUDIT.ENDPOINT_CONVENTIONS[0]] = __import__("collections").Counter({"EXACT_MATCH": 2})
        self.assertEqual(AUDIT.select_global_convention(counts, 2)["result"], "FAIL")

    def test_source_cache_is_allowlisted_hashed_and_fail_closed(self) -> None:
        claim = {"event_mapping": EVENT_MAPPING}
        source = {
            "source_id": "osf_wiki_data_format",
            "url": "https://api.osf.io/v2/wikis/s3nrk/content/",
            "retrieved_at_utc": "2026-08-17T00:00:00Z",
            "raw_response_sha256": AUDIT.OSF_DATA_FORMAT_SHA256,
            "normalized_claim_sha256": AUDIT.stable_hash(claim),
            "source_type": "official_release_wiki",
            "release_applicability": "DIRECT_ZUCO2_TASK1",
            "binds_array_or_event": "task1 events", "locator": "trigger table",
            "extracted_claim": claim, "verdict": "DIRECT_EVENT_SEMANTICS",
        }
        valid = AUDIT.validate_release_source_evidence({"schema_version": 1, "sources": [source]})
        self.assertTrue(valid["valid"])
        timestamp_changed = dict(source, retrieved_at_utc="2099-01-01T00:00:00Z")
        changed = AUDIT.validate_release_source_evidence({"schema_version": 1, "sources": [timestamp_changed]})
        self.assertEqual(valid["scientific_evidence_sha256"], changed["scientific_evidence_sha256"])
        tampered = dict(source, extracted_claim={"event_mapping": {}})
        self.assertFalse(AUDIT.validate_release_source_evidence({"schema_version": 1, "sources": [tampered]})["valid"])
        bad_url = dict(source, url="https://example.invalid/")
        self.assertFalse(AUDIT.validate_release_source_evidence({"schema_version": 1, "sources": [bad_url]})["valid"])
        wrong_scope = dict(source, release_applicability="ZUCO1")
        self.assertFalse(AUDIT.validate_release_source_evidence({"schema_version": 1, "sources": [wrong_scope]})["valid"])

    def test_conditional_data_card_success_failure_and_stale_guard(self) -> None:
        manifest = {
            "admission_conditions": [{"result": "PASS"}],
            "counts": {"subjects": 1, "rows": 2},
            "eeg_cell_ledger": {"final_valid_count": 1, "final_excluded_count": 1},
            "segment_correspondence": {"segment_convention_global_unique": {"selected": AUDIT.ENDPOINT_CONVENTIONS[1]}},
            "unit_layer_contract": {"preprocessed_EEG_data_unit_status": "BOUND"},
        }
        yaml_path, report_path = self.root / "card.yaml", self.root / "card.md"
        self.assertTrue(AUDIT.write_conditional_data_card(manifest, yaml_path, report_path))
        self.assertTrue(yaml_path.exists() and report_path.exists())
        yaml_path.unlink()
        report_path.unlink()
        manifest["admission_conditions"][0]["result"] = "FAIL"
        self.assertFalse(AUDIT.write_conditional_data_card(manifest, yaml_path, report_path))
        yaml_path.write_text("stale", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "STALE_DATA_CARD"):
            AUDIT.write_conditional_data_card(manifest, yaml_path, report_path)

    def test_final_admission_requires_content_event_and_exact_segment(self) -> None:
        base = {
            "content_present": True, "eeg_cell_state": "VALID_FINITE_MULTISAMPLE",
            "missing_or_exclusion_reason": None,
        }
        row = dict(base)
        AUDIT.finalize_row_admission(row, event_valid=True, segment_state="EXACT_MATCH")
        self.assertTrue(row["final_admission_candidate"])
        row = dict(base, content_present=False)
        AUDIT.finalize_row_admission(row, event_valid=True, segment_state="EXACT_MATCH")
        self.assertFalse(row["final_admission_candidate"])
        row = dict(base)
        AUDIT.finalize_row_admission(row, event_valid=True, segment_state="VALUE_MISMATCH")
        self.assertFalse(row["final_admission_candidate"])

    def test_symlink_and_path_escape_are_rejected(self) -> None:
        outside = self.root.parent / (self.root.name + "_outside")
        outside.mkdir(exist_ok=True)
        link = self.root / "escape"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("symlinks unavailable")
        with self.assertRaisesRegex(ValueError, "SYMLINK_REJECTED"):
            AUDIT._within(self.root, link)
        with self.assertRaisesRegex(ValueError, "PATH_OUTSIDE_DATASET_ROOT"):
            AUDIT._within(self.root, outside)

    def test_channel_order_mismatch_is_detected(self) -> None:
        labels = [f"C{index}" for index in range(105)]
        one = self.root / "gip_YAC_NR1_EEG.mat"
        two = self.root / "gip_YAG_NR1_EEG.mat"
        self._metadata_eeg(one, labels=labels)
        self._metadata_eeg(two, labels=list(reversed(labels)))
        self.assertNotEqual(AUDIT.audit_eeg_metadata(one)["channel_labels_sha256"], AUDIT.audit_eeg_metadata(two)["channel_labels_sha256"])

    def test_missing_coordinate_is_detected(self) -> None:
        path = self.root / "gip_YAC_NR1_EEG.mat"
        self._metadata_eeg(path, missing_z=True)
        self.assertFalse(AUDIT.audit_eeg_metadata(path)["coordinates_complete"])

    def test_acquisition_and_processed_references_are_distinct(self) -> None:
        path = self.root / "gip_YAC_NR1_EEG.mat"
        self._metadata_eeg(path)
        result = AUDIT.audit_eeg_metadata(path)
        self.assertEqual(result["acquisition_reference"], "Cz")
        self.assertEqual(result["processed_reference"], "common-average")

    def test_pickle_and_checkpoint_are_never_deserialized(self) -> None:
        with mock.patch("pickle.load", side_effect=AssertionError("pickle read")):
            self.assertIn(".pkl", AUDIT.UNSAFE_SUFFIXES)
            self.assertIn(".pt", AUDIT.UNSAFE_SUFFIXES)


if __name__ == "__main__":
    unittest.main()
