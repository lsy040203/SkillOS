"""Explicit, local-only feedback storage and aggregation."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable


def append_feedback(path: str | Path, task: str, skills: Iterable[str], rating: int) -> None:
    if not 1 <= rating <= 5:
        raise ValueError("Feedback rating must be between 1 and 5")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    record = {"task": task, "skills": list(skills), "rating": rating}
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def history_scores(path: str | Path | None) -> dict[str, float]:
    """Return a 0..1 mean rating by skill; ignore malformed local records."""

    if path is None or not Path(path).is_file():
        return {}
    totals: dict[str, list[int]] = defaultdict(list)
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
            rating = int(record["rating"])
            if not 1 <= rating <= 5:
                continue
            for skill in record.get("skills", []):
                totals[str(skill)].append(rating)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            continue
    return {skill: sum(ratings) / (5 * len(ratings)) for skill, ratings in totals.items()}
