"""Exercise the offline validator in an isolated, writable package tree."""
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "validate_library", Path(__file__).resolve().parents[1] / "tools/validate_library.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class ValidatorTests(unittest.TestCase):
    def check_fixture(self, second_source):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder, source in [("first", "value = 1\n"), ("second", second_source)]:
                target = root / folder / "example.py"
                target.parent.mkdir()
                target.write_text(source, encoding="utf-8")
            manifest = root / "MANIFEST.json"
            with patch.object(validator, "ROOT", root), patch.object(validator, "MANIFEST", manifest):
                manifest.write_text(json.dumps({"files": validator.tracked_files()}), encoding="utf-8")
                output = io.StringIO()
                with patch("sys.argv", ["validate_library", "--check"]), contextlib.redirect_stdout(output):
                    result = validator.main()
                self.assertFalse(list(root.rglob("*.pyc")))
                return result, output.getvalue()

    def test_valid_sources_with_same_basename(self):
        result, output = self.check_fixture("value = 2\n")
        self.assertEqual(result, 0, output)

    def test_reports_invalid_source_in_its_relative_folder(self):
        result, output = self.check_fixture("def broken(\n")
        self.assertEqual(result, 1)
        self.assertIn(str(Path("second/example.py")), output)
        self.assertIn("Python syntax error", output)


if __name__ == "__main__":
    unittest.main()
