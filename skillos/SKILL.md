---
name: skillos
description: Privacy-first adaptive skill routing for Codex using a user-provided local SkillOS profile and skill registry. Use when a user wants natural-language routing, an explainable skill recommendation, profile-aware prioritization, or a transparent multi-skill workflow. SkillOS scans a Codex skills directory only after explicit user consent or an explicit --scan command, and otherwise uses a manually maintained registry.
---

# SkillOS

Use SkillOS as a local decision aid. It never transmits profiles, registries, task text, or traces. It scans a user's Codex skills directory only after explicit consent.

## Workflow

1. Ask for a profile and registry path if the user has not supplied one. During initial setup, ask whether the user consents to a local scan of their Codex skills directory. If they decline, use a manually maintained registry.
2. Treat the current session's available skill list as the executable boundary. A registry entry is only a preference or candidate, not permission to invoke an unavailable skill.
3. Interpret the user's natural-language request semantically, then use `skillos route` when a deterministic, inspectable ranking is useful. Allow explicit intent and capability overrides when the heuristic classification is wrong.
4. Select the smallest useful set. Do not activate `team`, `autopilot`, `ralph`, or `ultrawork` unless the user explicitly requests an expansive workflow or grants the requested scope.
5. Read the complete `SKILL.md` for every selected available skill before acting. Follow its instructions rather than replacing them with SkillOS output.
6. Provide the selected skills, score factors, and execution order when the user requests an execution trace. Persist a trace only when the user explicitly enables it. Record feedback only when the user explicitly submits a rating; never infer satisfaction from silence.

## CLI

Run the package from the repository checkout:

```powershell
python -m skillos init-profile --config-dir "$HOME/.skillos"
python -m skillos init-profile --config-dir "$HOME/.skillos" --scan --skills-dir "$HOME/.codex/skills" --language auto
python -m skillos route "Review my Python project" --profile "$HOME/.skillos/profile.json" --registry "$HOME/.skillos/registry.json" --available analyze,code-review,lsp --json
python -m skillos feedback --history "$HOME/.skillos/feedback.jsonl" --task "Review my Python project" --skills code-review,analyze --rating 5
```

The CLI produces a recommendation. Verify availability in the current session before invoking any skill.
