import unittest

from skillos.models import Profile, Skill
from skillos.ranking import rank_skills


class RankingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = Profile(
            domains={"engineering": 0.9},
            preferred_skills=("code-review",),
            preferences={},
        )
        self.skills = [
            Skill("analyze", "Analysis", ("engineering",), ("diagnosis",), base_priority=0.7),
            Skill("code-review", "Review", ("engineering",), ("code-review",), base_priority=0.8),
            Skill("team", "Coordinate agents", ("engineering",), ("coordination",), base_priority=1.0),
        ]

    def test_preferred_capability_ranks_first(self) -> None:
        ranked, filtered = rank_skills(
            self.skills,
            self.profile,
            intent="engineering",
            needs=("code-review",),
            available=("analyze", "code-review", "team"),
            expansive_workflows=("team",),
        )
        self.assertTrue(filtered)
        self.assertEqual([item.skill.name for item in ranked], ["code-review", "analyze"])

    def test_unavailable_skill_is_not_selected(self) -> None:
        ranked, _ = rank_skills(
            self.skills,
            self.profile,
            intent="engineering",
            available=("analyze",),
        )
        self.assertEqual([item.skill.name for item in ranked], ["analyze"])

    def test_feedback_can_change_the_order(self) -> None:
        ranked, _ = rank_skills(
            self.skills,
            Profile(domains={"engineering": 1.0}, preferred_skills=(), preferences={}),
            intent="engineering",
            available=("analyze", "code-review"),
            weights={"historical_success": 1.0, "intent_domain": 0.0, "requested_capability": 0.0, "preferred_skill": 0.0, "base_priority": 0.0},
            historical_scores={"analyze": 1.0, "code-review": 0.2},
        )
        self.assertEqual(ranked[0].skill.name, "analyze")


if __name__ == "__main__":
    unittest.main()
