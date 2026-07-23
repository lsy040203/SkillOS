import tempfile
import unittest
from pathlib import Path

from skillos.feedback import append_feedback, history_scores


class FeedbackTests(unittest.TestCase):
    def test_aggregates_explicit_local_feedback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "feedback.jsonl"
            append_feedback(path, "review", ["code-review"], 5)
            append_feedback(path, "review", ["code-review"], 3)
            self.assertEqual(history_scores(path)["code-review"], 0.8)


if __name__ == "__main__":
    unittest.main()
