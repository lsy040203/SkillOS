"""Safe, deterministic ordering for a selected group of skill candidates."""

from __future__ import annotations

from collections.abc import Iterable

from .models import RankedSkill


_PHASES = {
    "analysis": 10,
    "research": 10,
    "planning": 20,
    "review": 30,
    "execution": 40,
    "verification": 50,
    "visualization": 60,
}


def plan_workflow(selected: Iterable[RankedSkill]) -> list[str]:
    """Order selected skills without introducing unselected workflow steps."""

    ordered = sorted(
        selected,
        key=lambda item: (_PHASES.get(item.skill.workflow_type, 35), -item.score, item.skill.name),
    )
    return [item.skill.name for item in ordered]
