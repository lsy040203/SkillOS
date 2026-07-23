import unittest
from argparse import Namespace
from pathlib import Path

from skillos.cli import _route_result
from skillos.intent import infer_intent


class IntentTests(unittest.TestCase):
    def test_infers_chinese_engineering_review(self) -> None:
        inferred = infer_intent("检查这个 Python 项目的代码质量")
        self.assertEqual(inferred.intent, "engineering")
        self.assertIn("code-review", inferred.needs)

    def test_returns_general_for_unmatched_request(self) -> None:
        inferred = infer_intent("Tell me something unrelated")
        self.assertEqual(inferred.intent, "general")
        self.assertEqual(inferred.needs, ())

    def test_route_passes_inferred_values_to_the_ranker(self) -> None:
        root = Path(__file__).resolve().parents[1]
        args = Namespace(
            request="检查这个 Python 项目的代码质量",
            profile=root / "examples" / "profile.example.json",
            registry=root / "examples" / "registry.example.json",
            available="analyze,code-review,lsp",
            policy=root / "config" / "routing_policy.json",
            history=None,
            allow_expansive=False,
        )
        inferred = infer_intent(args.request)
        result = _route_result(args, inferred.intent, list(inferred.needs), inferred.evidence)
        self.assertEqual(result["intent"], "engineering")
        code_review = next(item for item in result["ranked_skills"] if item["name"] == "code-review")
        self.assertGreater(code_review["factors"]["requested_capability"], 0.0)


if __name__ == "__main__":
    unittest.main()
