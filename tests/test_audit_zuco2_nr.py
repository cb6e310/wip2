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
    return group.create_dataset(name, data=np.asarray([ord(c) for c in value], dtype=np.uint16).reshape(-1, 1))


class AuditZuco2NRTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _summary(self, path: Path, slots: int = 349) -> None:
        with h5py.File(path, "w") as file:
            refs = file.create_group("refs")
            sentence = file.create_group("sentenceData")
            for field in AUDIT.EXPECTED_SUMMARY_FIELDS:
                values = np.empty((slots, 1), dtype=h5py.ref_dtype)
                for index in range(slots):
                    if field == "content":
                        node = _chars(refs, f"c_{index}", "  Alpha\u00a0 beta  " if index < 2 else f"item {index}")
                    elif field == "rawData":
                        node = refs.create_dataset(f"r_{index}", data=np.full((2, 105), 7.25))
                    else:
                        node = refs.create_dataset(f"{field}_{index}", data=np.asarray([[1.0]]))
                    values[index, 0] = node.ref
                sentence.create_dataset(field, data=values)

    def _eeg(self, path: Path, labels: list[str] | None = None, missing_z: bool = False) -> None:
        labels = labels or [f"E{i}" for i in range(2, 107)]
        with h5py.File(path, "w") as file:
            refs = file.create_group("refs")
            eeg = file.create_group("EEG")
            eeg.create_dataset("data", shape=(20, 105), dtype=np.float64)
            eeg.create_dataset("srate", data=np.asarray([[500.0]]))
            eeg.create_dataset("trials", data=np.asarray([[1.0]]))
            ref = _chars(refs, "processed_ref", "common")
            eeg.create_dataset("ref", data=np.asarray([[ref.ref]], dtype=h5py.ref_dtype))
            event = eeg.create_group("event")
            event.create_dataset("latency", data=np.asarray([[1.0]]))
            event.create_dataset("type", data=np.asarray([[1.0]]))
            chanlocs = eeg.create_group("chanlocs")
            label_refs = np.empty((105, 1), dtype=h5py.ref_dtype)
            for index, label in enumerate(labels):
                label_refs[index, 0] = _chars(refs, f"label_{index}", label).ref
            chanlocs.create_dataset("labels", data=label_refs)
            for field in ("X", "Y", "Z", "theta", "radius"):
                coordinate_refs = np.empty((105, 1), dtype=h5py.ref_dtype)
                for index in range(105):
                    value = np.empty((0, 1)) if missing_z and field == "Z" and index == 2 else np.asarray([[float(index + 1)]])
                    coordinate_refs[index, 0] = refs.create_dataset(f"{field}_{index}", data=value).ref
                chanlocs.create_dataset(field, data=coordinate_refs)
            automagic = file.create_group("automagic")
            acquisition = _chars(refs, "acquisition_ref", "Cz")
            automagic.create_dataset("EEGReference", data=np.asarray([[acquisition.ref]], dtype=h5py.ref_dtype))

    def test_symlink_escape_is_rejected(self) -> None:
        outside = self.root.parent / (self.root.name + "_outside")
        outside.mkdir(exist_ok=True)
        link = self.root / "escape"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("symlinks unavailable")
        with self.assertRaisesRegex(ValueError, "SYMLINK_REJECTED"):
            AUDIT._within(self.root, link)
        with self.assertRaisesRegex(ValueError, "SYMLINK_REJECTED"):
            AUDIT._within(self.root, link / "nested.mat", must_exist=False)

    def test_summary_fields_and_349_slots_are_checked(self) -> None:
        good = self.root / "resultsYAC_NR.mat"
        self._summary(good)
        summary, rows = AUDIT.audit_summary(good)
        self.assertEqual(summary["slot_count"], 349)
        self.assertEqual(len(rows), 349)
        bad = self.root / "resultsYAG_NR.mat"
        self._summary(bad, slots=3)
        with self.assertRaisesRegex(ValueError, "SUMMARY_SLOT_COUNT_MISMATCH"):
            AUDIT.audit_summary(bad)

    def test_channel_order_mismatch_has_distinct_contract_hash(self) -> None:
        one = self.root / "gip_YAC_NR1_EEG.mat"
        two = self.root / "gip_YAG_NR1_EEG.mat"
        labels = [f"C{i}" for i in range(105)]
        self._eeg(one, labels)
        self._eeg(two, list(reversed(labels)))
        self.assertNotEqual(AUDIT.audit_eeg_metadata(one)["channel_labels_sha256"], AUDIT.audit_eeg_metadata(two)["channel_labels_sha256"])

    def test_missing_coordinate_is_detected(self) -> None:
        path = self.root / "gip_YAC_NR1_EEG.mat"
        self._eeg(path, missing_z=True)
        self.assertFalse(AUDIT.audit_eeg_metadata(path)["coordinates_complete"])

    def test_acquisition_and_processed_references_are_distinct(self) -> None:
        path = self.root / "gip_YAC_NR1_EEG.mat"
        self._eeg(path)
        item = AUDIT.audit_eeg_metadata(path)
        self.assertEqual(item["acquisition_reference"], "Cz")
        self.assertEqual(item["processed_reference"], "common-average")

    def test_stimulus_normalization_hash_and_duplicate_are_stable(self) -> None:
        self.assertEqual(AUDIT.normalize_stimulus("  Alpha\u00a0 beta  "), "Alpha beta")
        self.assertEqual(AUDIT.stimulus_id("Alpha  beta"), AUDIT.stimulus_id(" Alpha\u00a0beta "))
        self.assertEqual(len(AUDIT.stimulus_id("Alpha beta")), 64)

    def test_output_is_byte_stable_and_contains_no_raw_values_or_text(self) -> None:
        manifest = {"schema_version": 1, "eeg_values_emitted": False}
        rows = [{"subject": "YAC", "slot": 1, "stimulus_sha256": AUDIT.stimulus_id("SECRET_SENTENCE"), "raw_shape": [2, 105]}]
        one_y, one_j = self.root / "one.yaml", self.root / "one.jsonl"
        two_y, two_j = self.root / "two.yaml", self.root / "two.jsonl"
        AUDIT.write_outputs(manifest, rows, one_y, one_j)
        AUDIT.write_outputs(manifest, rows, two_y, two_j)
        self.assertEqual(one_y.read_bytes(), two_y.read_bytes())
        self.assertEqual(one_j.read_bytes(), two_j.read_bytes())
        rendered = one_y.read_text() + one_j.read_text()
        self.assertNotIn("SECRET_SENTENCE", rendered)
        self.assertNotIn("7.25", rendered)

    def test_pickle_and_checkpoint_are_never_deserialized(self) -> None:
        with mock.patch("pickle.load", side_effect=AssertionError("pickle read")):
            self.assertIn(".pkl", AUDIT.UNSAFE_SUFFIXES)
            self.assertIn(".pt", AUDIT.UNSAFE_SUFFIXES)


if __name__ == "__main__":
    unittest.main()
