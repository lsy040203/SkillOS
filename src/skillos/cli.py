"""Command-line interface for local SkillOS configuration and ranking."""

from __future__ import annotations

import argparse
import json
import locale
from pathlib import Path
from typing import Sequence

from .config import load_policy, load_profile, load_registry
from .feedback import append_feedback, history_scores
from .intent import infer_intent
from .ranking import rank_skills
from .scanner import default_codex_skills_dir, scan_skills
from .trace import append_trace
from .workflow import plan_workflow


DEFAULT_POLICY = Path(__file__).resolve().parents[2] / "config" / "routing_policy.json"
DEFAULT_EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


MESSAGES = {
    "en": {
        "notice": "SkillOS stores this configuration locally. It does not upload data.",
        "domains": "Primary domains (comma separated, e.g. engineering,research): ",
        "preferred": "Preferred skills (comma separated, optional): ",
        "deep": "Prefer deep analysis? [y/N]: ",
        "verify": "Prefer verification-first responses? [y/N]: ",
        "agent": "Allow multi-agent recommendations? [y/N]: ",
        "scan": "Allow a local scan of your Codex skills directory? [y/N]: ",
        "created_profile": "Created",
        "created_registry": "Created or preserved",
    },
    "zh-CN": {
        "notice": "SkillOS 只在本机保存配置，不会上传数据。",
        "domains": "主要工作领域（逗号分隔，例如 engineering,research）：",
        "preferred": "偏好 Skill（逗号分隔，可留空）：",
        "deep": "偏好深度分析？[y/N]：",
        "verify": "偏好优先验证？[y/N]：",
        "agent": "允许推荐多代理工作流？[y/N]：",
        "scan": "是否同意在本机扫描 Codex skills 目录？[y/N]：",
        "created_profile": "已创建",
        "created_registry": "已创建或保留",
    },
}


def _language(value: str) -> str:
    if value != "auto":
        return value
    system_language = (locale.getlocale()[0] or "").lower()
    return "zh-CN" if system_language.startswith("zh") else "en"


def _prompt_csv(question: str) -> list[str]:
    return _csv(input(question).strip())


def _yes_no(question: str) -> bool:
    return input(question).strip().lower() in {"y", "yes"}


def init_profile(config_dir: Path, language: str, scan: bool | None, skills_dir: Path, replace_registry: bool) -> None:
    messages = MESSAGES[language]
    print(messages["notice"])
    domains = _prompt_csv(messages["domains"])
    preferred = _prompt_csv(messages["preferred"])
    deep_analysis = _yes_no(messages["deep"])
    verification = _yes_no(messages["verify"])
    multi_agent = _yes_no(messages["agent"])
    should_scan = _yes_no(messages["scan"]) if scan is None else scan
    config_dir.mkdir(parents=True, exist_ok=True)
    profile = {
        "language": language,
        "domains": {domain: 1.0 for domain in domains},
        "preferred_skills": preferred,
        "preferences": {
            "deep_analysis": deep_analysis,
            "verification_first": verification,
            "multi_agent": multi_agent,
        },
    }
    profile_target = config_dir / "profile.json"
    profile_target.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    registry_target = config_dir / "registry.json"
    if should_scan:
        if registry_target.exists() and not replace_registry:
            raise FileExistsError("Registry exists; pass --replace-registry to replace it with scanned metadata")
        scanned = {"skills": [skill.to_dict() for skill in scan_skills(skills_dir)]}
        registry_target.write_text(json.dumps(scanned, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    elif not registry_target.exists():
        registry_target.write_text((DEFAULT_EXAMPLES / "registry.example.json").read_text(encoding="utf-8"), encoding="utf-8")
    print(f"{messages['created_profile']} {profile_target}")
    print(f"{messages['created_registry']} {registry_target}")


def _route_result(args: argparse.Namespace, intent: str, needs: list[str], evidence: dict[str, tuple[str, ...]] | None = None) -> dict[str, object]:
    profile = load_profile(args.profile)
    skills = load_registry(args.registry)
    policy = load_policy(args.policy)
    ranked, filtered_expansive = rank_skills(
        skills,
        profile,
        intent=intent,
        needs=needs,
        available=_csv(args.available),
        weights=policy["weights"],
        historical_scores=history_scores(args.history),
        allow_expansive=args.allow_expansive,
        expansive_workflows=policy.get("expansive_workflows", []),
    )
    selected = ranked[: policy.get("max_selected_skills", 3)]
    result: dict[str, object] = {
        "task": args.request,
        "intent": intent,
        "selected_skills": [item.skill.name for item in selected],
        "workflow": plan_workflow(selected),
        "expansive_workflows_filtered": filtered_expansive,
        "ranked_skills": [
            {"name": item.skill.name, "score": item.score, "factors": item.factors}
            for item in ranked
        ],
    }
    if evidence is not None:
        result["inference_evidence"] = evidence
    return result


def _print_result(args: argparse.Namespace, result: dict[str, object]) -> int:
    if args.trace:
        append_trace(args.trace, result)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Selected skills: " + ", ".join(result["selected_skills"]))
        if filtered_expansive:
            print("Expansive workflows were filtered; pass --allow-expansive only with explicit user approval.")
    return 0


def rank_command(args: argparse.Namespace) -> int:
    return _print_result(args, _route_result(args, args.intent, _csv(args.need)))


def route_command(args: argparse.Namespace) -> int:
    inferred = infer_intent(args.request)
    intent = args.intent or inferred.intent
    needs = list(dict.fromkeys([*inferred.needs, *_csv(args.need)]))
    return _print_result(args, _route_result(args, intent, needs, inferred.evidence))


def feedback_command(args: argparse.Namespace) -> int:
    append_feedback(args.history, args.task, _csv(args.skills), args.rating)
    print(f"Recorded local feedback for {len(_csv(args.skills))} skill(s).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skillos", description="Local, user-configured skill routing for Codex")
    subparsers = parser.add_subparsers(dest="command", required=True)
    setup = subparsers.add_parser("init-profile", help="Create a local profile and opt in to scanning if desired")
    setup.add_argument("--config-dir", type=Path, required=True)
    setup.add_argument("--skills-dir", type=Path, default=default_codex_skills_dir())
    setup.add_argument("--language", choices=("auto", "en", "zh-CN"), default="auto")
    scan_group = setup.add_mutually_exclusive_group()
    scan_group.add_argument("--scan", action="store_true", help="Explicitly consent to local scanning")
    scan_group.add_argument("--manual", action="store_true", help="Skip scanning and use a manual registry")
    setup.add_argument("--replace-registry", action="store_true")
    setup.set_defaults(
        handler=lambda args: init_profile(
            args.config_dir,
            _language(args.language),
            True if args.scan else False if args.manual else None,
            args.skills_dir,
            args.replace_registry,
        ) or 0
    )

    rank = subparsers.add_parser("rank", help="Rank declared skills that are available in the current session")
    rank.add_argument("request")
    rank.add_argument("--profile", type=Path, required=True)
    rank.add_argument("--registry", type=Path, required=True)
    rank.add_argument("--intent", required=True)
    rank.add_argument("--need", default="")
    rank.add_argument("--available", required=True, help="Comma-separated names available in the current Codex session")
    rank.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    rank.add_argument("--allow-expansive", action="store_true")
    rank.add_argument("--history", type=Path, help="Optional local feedback JSONL")
    rank.add_argument("--trace", type=Path)
    rank.add_argument("--json", action="store_true")
    rank.set_defaults(handler=rank_command)

    route = subparsers.add_parser("route", help="Infer intent and rank current-session skills from a natural-language request")
    route.add_argument("request")
    route.add_argument("--profile", type=Path, required=True)
    route.add_argument("--registry", type=Path, required=True)
    route.add_argument("--available", required=True, help="Comma-separated names available in the current Codex session")
    route.add_argument("--intent", help="Optional explicit override for inferred intent")
    route.add_argument("--need", default="", help="Optional additional capabilities")
    route.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    route.add_argument("--history", type=Path, help="Optional local feedback JSONL")
    route.add_argument("--allow-expansive", action="store_true")
    route.add_argument("--trace", type=Path)
    route.add_argument("--json", action="store_true")
    route.set_defaults(handler=route_command)

    feedback = subparsers.add_parser("feedback", help="Record explicit local feedback for a completed routing decision")
    feedback.add_argument("--history", type=Path, required=True)
    feedback.add_argument("--task", required=True)
    feedback.add_argument("--skills", required=True)
    feedback.add_argument("--rating", type=int, choices=range(1, 6), required=True)
    feedback.set_defaults(handler=feedback_command)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.handler(args)
