import tempfile
import unittest
from pathlib import Path

from skillos.scanner import parse_skill_file, scan_skills


class ScannerTests(unittest.TestCase):
    def test_parses_folded_frontmatter_description(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "code-review" / "SKILL.md"
            path.parent.mkdir()
            path.write_text(
                "---\nname: code-review\ndescription: >-\n  Review code correctness and tests.\n---\n# Review\n",
                encoding="utf-8",
            )
            skill = parse_skill_file(path)
            self.assertEqual(skill.name, "code-review")
            self.assertEqual(skill.description, "Review code correctness and tests.")
            self.assertIn("engineering", skill.domains)

    def test_scans_only_the_supplied_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "skills"
            file_path = root / "demo" / "SKILL.md"
            file_path.parent.mkdir(parents=True)
            file_path.write_text("---\nname: demo\ndescription: Test skill\n---\n", encoding="utf-8")
            scanned = scan_skills(root)
            self.assertEqual([skill.name for skill in scanned], ["demo"])
            self.assertEqual(scanned[0].source_path, str(file_path))


if __name__ == "__main__":
    unittest.main()
