"""Typed configuration models for the local SkillOS MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    domains: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    triggers: tuple[str, ...] = ()
    base_priority: float = 0.5
    workflow_type: str = "standard"
    source_path: str | None = None

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Skill":
        return cls(
            name=str(value["name"]),
            description=str(value.get("description", "")),
            domains=tuple(map(str, value.get("domains", []))),
            capabilities=tuple(map(str, value.get("capabilities", []))),
            triggers=tuple(map(str, value.get("triggers", []))),
            base_priority=float(value.get("base_priority", 0.5)),
            workflow_type=str(value.get("workflow_type", "standard")),
            source_path=str(value["source_path"]) if value.get("source_path") else None,
        )

    def to_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "domains": list(self.domains),
            "capabilities": list(self.capabilities),
            "triggers": list(self.triggers),
            "base_priority": self.base_priority,
            "workflow_type": self.workflow_type,
        }
        if self.source_path:
            value["source_path"] = self.source_path
        return value


@dataclass(frozen=True)
class Profile:
    language: str = "en"
    domains: dict[str, float] = field(default_factory=dict)
    preferred_skills: tuple[str, ...] = ()
    preferences: dict[str, bool] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Profile":
        return cls(
            language=str(value.get("language", "en")),
            domains={str(key): float(score) for key, score in value.get("domains", {}).items()},
            preferred_skills=tuple(map(str, value.get("preferred_skills", []))),
            preferences={str(key): bool(flag) for key, flag in value.get("preferences", {}).items()},
        )


@dataclass(frozen=True)
class RankedSkill:
    skill: Skill
    score: float
    factors: dict[str, float]
