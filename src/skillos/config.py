"""JSON configuration loading and validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Profile, Skill


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def load_profile(path: str | Path) -> Profile:
    return Profile.from_dict(load_json(path))


def load_registry(path: str | Path) -> list[Skill]:
    registry = load_json(path)
    raw_skills = registry.get("skills")
    if not isinstance(raw_skills, list):
        raise ValueError("Registry must contain a skills array")
    skills = [Skill.from_dict(item) for item in raw_skills if isinstance(item, dict)]
    if not skills:
        raise ValueError("Registry must declare at least one skill")
    names = [skill.name for skill in skills]
    if len(names) != len(set(names)):
        raise ValueError("Registry skill names must be unique")
    return skills


def load_policy(path: str | Path) -> dict[str, Any]:
    policy = load_json(path)
    weights = policy.get("weights")
    if not isinstance(weights, dict):
        raise ValueError("Policy must contain a weights object")
    return policy
