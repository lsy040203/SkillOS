"""Transparent local intent and capability inference for the route command."""

from __future__ import annotations

from dataclasses import dataclass


_INTENT_RULES = {
    "engineering": ("code", "bug", "debug", "test", "review", "refactor", "代码", "报错", "调试", "测试", "重构", "审查"),
    "research": ("research", "paper", "benchmark", "rag", "memory", "论文", "研究", "实验", "基准", "记忆"),
    "visualization": ("figure", "chart", "diagram", "matplotlib", "图", "可视化", "架构图"),
    "collaboration": ("agent", "team", "workflow", "多代理", "协作", "工作流"),
}

_CAPABILITY_RULES = {
    "code-review": ("review", "quality", "审查", "代码质量"),
    "diagnosis": ("bug", "debug", "error", "why", "报错", "调试", "原因"),
    "repository-analysis": ("repository", "architecture", "项目", "仓库", "架构"),
    "academic-visualization": ("figure", "paper", "chart", "论文图", "架构图", "可视化"),
    "planning": ("plan", "design", "规划", "设计"),
}


@dataclass(frozen=True)
class IntentInference:
    intent: str
    needs: tuple[str, ...]
    evidence: dict[str, tuple[str, ...]]


def infer_intent(request: str) -> IntentInference:
    normalized = request.lower()
    domain_matches = {
        domain: tuple(word for word in words if word in normalized)
        for domain, words in _INTENT_RULES.items()
    }
    intent = max(domain_matches, key=lambda domain: (len(domain_matches[domain]), domain))
    if not domain_matches[intent]:
        intent = "general"
    capability_matches = {
        capability: tuple(word for word in words if word in normalized)
        for capability, words in _CAPABILITY_RULES.items()
    }
    needs = tuple(capability for capability, matches in capability_matches.items() if matches)
    evidence = {
        **{f"intent:{domain}": matches for domain, matches in domain_matches.items() if matches},
        **{f"need:{capability}": matches for capability, matches in capability_matches.items() if matches},
    }
    return IntentInference(intent=intent, needs=needs, evidence=evidence)
