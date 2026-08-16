from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_input_sources.py"
spec = importlib.util.spec_from_file_location("audit_input_sources", SCRIPT)
SCANNER = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = SCANNER
spec.loader.exec_module(SCANNER)


class AuditInputSourcesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        base = Path(self.temp.name)
        self.project = base / "project"
        self.reference = base / "reference"
        self.project.mkdir()
        self.reference.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _audit(self, limit: int = 32):
        return SCANNER.audit(self.project, self.reference, limit)

    def test_requires_two_existing_distinct_roots(self) -> None:
        with self.assertRaises(ValueError):
            SCANNER.audit(self.project, self.project, 10)
        with self.assertRaises(ValueError):
            SCANNER.audit(self.project, self.reference / "missing", 10)

    def test_external_symlink_is_recorded_not_followed(self) -> None:
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (outside / "forbidden.txt").write_text("must-not-appear", encoding="utf-8")
        link = self.project / "external_link"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("symlink creation unavailable")
        payload = self._audit()
        item = next(entry for entry in payload["entries"] if entry["path"] == "external_link")
        self.assertEqual(item["type"], "symlink")
        self.assertFalse(item["followed"])
        self.assertNotIn("forbidden.txt", yaml.safe_dump(payload))

    def test_result_directory_is_stat_only(self) -> None:
        result = self.reference / "results"
        result.mkdir()
        forbidden = result / "read_fails.txt"
        forbidden.write_text("sensitive-result", encoding="utf-8")
        original_open = Path.open

        def guarded(path, *args, **kwargs):
            if path == forbidden:
                raise AssertionError("result content opened")
            return original_open(path, *args, **kwargs)

        with mock.patch.object(Path, "open", guarded):
            payload = self._audit()
        text = yaml.safe_dump(payload)
        self.assertIn("UNREAD_HISTORICAL_RESULT", text)
        self.assertNotIn("read_fails.txt", text)
        self.assertNotIn("sensitive-result", text)

    def test_checkpoint_and_pickle_are_never_opened(self) -> None:
        unsafe = [self.project / "object.pkl", self.reference / "weights.pth"]
        for path in unsafe:
            path.write_bytes(b"unsafe")
        original_open = Path.open

        def guarded(path, *args, **kwargs):
            if path in unsafe:
                raise AssertionError("unsafe file opened")
            return original_open(path, *args, **kwargs)

        with mock.patch.object(Path, "open", guarded):
            payload = self._audit()
        statuses = {item.get("hash_status") for item in payload["entries"] if item["type"] == "file"}
        self.assertEqual(statuses, {"HASH_SKIPPED_UNSAFE_FORMAT"})

    def test_hash_threshold(self) -> None:
        small = self.project / "small.py"
        large = self.project / "large.py"
        small.write_bytes(b"123")
        large.write_bytes(b"123456")
        payload = self._audit(limit=3)
        by_path = {item["path"]: item for item in payload["entries"] if item["root"] == "project"}
        self.assertEqual(by_path["small.py"]["hash_status"], "SHA256")
        self.assertEqual(by_path["large.py"]["hash_status"], "HASH_SKIPPED_TOO_LARGE")

    def test_output_is_sorted_and_byte_stable(self) -> None:
        (self.project / "z.py").write_text("z", encoding="utf-8")
        (self.project / "a.py").write_text("a", encoding="utf-8")
        one = yaml.safe_dump(self._audit(), sort_keys=False)
        two = yaml.safe_dump(self._audit(), sort_keys=False)
        self.assertEqual(one.encode(), two.encode())
        self.assertLess(one.index("a.py"), one.index("z.py"))

    def test_secret_value_does_not_leak(self) -> None:
        value = "DO_NOT_LEAK_VALUE_7b9e"
        (self.project / ".env").write_text("TOKEN=" + value, encoding="utf-8")
        rendered = yaml.safe_dump(self._audit())
        self.assertNotIn(value, rendered)
        self.assertIn("HASH_SKIPPED_SENSITIVE_NAME", rendered)


if __name__ == "__main__":
    unittest.main()
