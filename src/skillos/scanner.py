"""Opt-in parsing of SKILL.md files from one user-approved directory."""

from __future__ import annotations

import os
import re
from pathlib import Path

from .models import Skill


_DOMAIN_KEYWORDS = {
    "engineering": ("code", "debug", "repository", "test", "lsp", "review", "refactor", "代码", "调试", "测试", "审查", "重构"),
    "research": ("research", "paper", "academic", "benchmark", "rag", "memory", "研究", "论文", "实验", "记忆"),
    "visualization": ("figure", "matplotlib", "visual", "diagram", "chart", "图", "可视化", "架构图"),
    "collaboration": ("team", "agent", "workflow", "orchestrat", "多代理", "协作", "工作流"),
}


def default_codex_skills_dir() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    return Path(codex_home) / "skills" if codex_home else Path.home() / ".codex" / "skills"


def _read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gbk"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def _frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return ""
    match = re.match(r"^---\s*\n(.*?)\n---\s*$", text, flags=re.DOTALL | re.MULTILINE)
    return match.group(1) if match else ""


def _scalar(frontmatter: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*([^\n]+)$", frontmatter, flags=re.MULTILINE)
    if not match:
        return ""
    value = match.group(1).strip().strip("\"'")
    if value not in {">", ">-", "|", "|-"}:
        return value
    lines = frontmatter[match.end() :].splitlines()
    collected: list[str] = []
    for line in lines:
        if line and not line.startswith((" ", "\t")):
            break
        if line.strip():
            collected.append(line.strip())
    return " ".join(collected)


def _keywords(text: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    normalized = text.lower()
    domains = tuple(domain for domain, words in _DOMAIN_KEYWORDS.items() if any(word in normalized for word in words))
    capabilities = tuple(word for words in _DOMAIN_KEYWORDS.values() for word in words if word in normalized)
    return domains, tuple(dict.fromkeys(capabilities))


def parse_skill_file(path: str | Path) -> Skill:
    file_path = Path(path)
    text = _read_text(file_path)
    metadata = _frontmatter(text)
    name = _scalar(metadata, "name") or file_path.parent.name
    description = _scalar(metadata, "description")
    if not description:
        title = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
        description = title.group(1).strip() if title else "No description declared."
    domains, capabilities = _keywords(description + "\n" + text[:4000])
    trigger_markers = ("when", "use", "trigger", "适用", "使用", "触发")
    triggers = tuple(
        match.group(1).strip()
        for match in re.finditer(r"^-\s+(.+)$", text, flags=re.MULTILINE)
        if any(marker in match.group(1).lower() for marker in trigger_markers)
    )
    return Skill(
        name=name,
        description=description,
        domains=domains,
        capabilities=capabilities,
        triggers=triggers[:8],
        workflow_type="discovered",
        source_path=str(file_path),
    )


def scan_skills(root: str | Path) -> list[Skill]:
    """Read SKILL.md files only beneath a user-approved skills root."""

    root_path = Path(root).expanduser()
    if not root_path.is_dir():
        raise ValueError(f"Codex skills directory does not exist: {root_path}")
    discovered = [parse_skill_file(path) for path in root_path.rglob("SKILL.md")]
    if not discovered:
        raise ValueError(f"No SKILL.md files found beneath: {root_path}")
    return sorted(discovered, key=lambda skill: skill.name)
