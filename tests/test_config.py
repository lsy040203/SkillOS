import json
import tempfile
import unittest
from pathlib import Path

from skillos.config import load_registry


class RegistryTests(unittest.TestCase):
    def test_duplicate_names_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.json"
            path.write_text(json.dumps({"skills": [{"name": "a"}, {"name": "a"}]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unique"):
                load_registry(path)


if __name__ == "__main__":
    unittest.main()
