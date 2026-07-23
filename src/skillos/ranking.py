"""Deterministic, explainable ranking over user-declared skill metadata."""

from __future__ import annotations

from collections.abc import Iterable

from .models import Profile, RankedSkill, Skill


def _overlap(left: Iterable[str], right: Iterable[str]) -> float:
    left_set = {item.strip().lower() for item in left if item.strip()}
    right_set = {item.strip().lower() for item in right if item.strip()}
    if not left_set or not right_set:
        return 0.0
    return len(left_set & right_set) / len(right_set)


def rank_skills(
    skills: Iterable[Skill],
    profile: Profile,
    *,
    intent: str,
    needs: Iterable[str] = (),
    available: Iterable[str] = (),
    weights: dict[str, float] | None = None,
    historical_scores: dict[str, float] | None = None,
    allow_expansive: bool = False,
    expansive_workflows: Iterable[str] = (),
) -> tuple[list[RankedSkill], bool]:
    """Rank only skills that are both registered and currently available."""

    policy_weights = {
        "intent_domain": 0.35,
        "requested_capability": 0.30,
        "preferred_skill": 0.20,
        "base_priority": 0.15,
        "historical_success": 0.0,
    }
    policy_weights.update(weights or {})
    available_names = {name.strip() for name in available if name.strip()}
    expansive_names = {name.strip() for name in expansive_workflows if name.strip()}
    filtered_expansive = False
    results: list[RankedSkill] = []

    for skill in skills:
        if available_names and skill.name not in available_names:
            continue
        if not allow_expansive and skill.name in expansive_names:
            filtered_expansive = True
            continue
        domain_score = profile.domains.get(intent, 0.0) if intent in skill.domains else 0.0
        capability_score = _overlap(skill.capabilities, needs)
        preference_score = 1.0 if skill.name in profile.preferred_skills else 0.0
        factors = {
            "intent_domain": domain_score,
            "requested_capability": capability_score,
            "preferred_skill": preference_score,
            "base_priority": max(0.0, min(1.0, skill.base_priority)),
            "historical_success": (historical_scores or {}).get(skill.name, 0.0),
        }
        score = sum(factors[key] * policy_weights[key] for key in factors)
        results.append(RankedSkill(skill=skill, score=round(score, 4), factors=factors))

    return sorted(results, key=lambda item: (-item.score, item.skill.name)), filtered_expansive
