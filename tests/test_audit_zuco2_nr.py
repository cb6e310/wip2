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


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_zuco2_nr.py"
spec = importlib.util.spec_from_file_location("audit_zuco2_nr", SCRIPT)
AUDIT = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = AUDIT
spec.loader.exec_module(AUDIT)


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
            bound = AUDIT.audit_events(file, file["EEG"])
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
        manifest = {"schema_version": 2, "audit_boundaries": {"eeg_values_emitted": False}}
        rows = [{"subject": "YAC", "slot": 1, "stimulus_sha256": AUDIT.stimulus_id("SECRET_SENTENCE"), "raw_shape": [2, 105]}]
        source = {"schema_version": 1, "retrieved_at_utc": "fixed"}
        outputs = []
        for prefix in ("one", "two"):
            paths = (self.root / f"{prefix}.yaml", self.root / f"{prefix}.jsonl", self.root / f"{prefix}-source.yaml")
            AUDIT.write_outputs(manifest, rows, source, *paths)
            outputs.append(tuple(path.read_bytes() for path in paths))
        self.assertEqual(outputs[0], outputs[1])
        rendered = b"".join(outputs[0]).decode("utf-8")
        self.assertNotIn("SECRET_SENTENCE", rendered)
        self.assertNotIn("7.25", rendered)

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
