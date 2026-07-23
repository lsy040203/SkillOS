# SkillOS

SkillOS is a privacy-first adaptive skill intelligence layer for Codex. It helps a user rank and compose skills from either a registry that they write themselves or an explicitly approved local scan of their Codex skills directory.

It never inspects other users' installations, transmits prompts, or persists a trace unless the user explicitly asks it to. It scans only one user-approved local Codex skills directory after consent.

Chinese documentation: [README.zh-CN.md](README.zh-CN.md).

## What it does

- collects a local, user-owned preference profile through an interactive CLI;
- supports an explicit local skill registry or an opt-in scan of one Codex skills directory;
- infers local English and Chinese intent/capability hints, with explicit CLI overrides;
- ranks declared skills using task intent, requested capabilities, user preferences, explicit local feedback, base priority, and safe workflow compatibility;
- emits an inspectable ranking and optional local JSONL execution trace;
- ships a `skillos` Codex skill that treats the active session's available skills as the final execution boundary.

## What it does not do

- scan any directory without explicit user consent, or scan plugin caches by default;
- upload profile data, task text, registry contents, or traces;
- bypass Codex's session-level skill availability and trigger rules;
- silently start expansive workflows such as `team`, `autopilot`, `ralph`, or `ultrawork`.

## Quick start

Requires Python 3.11 or newer. The MVP has no third-party runtime dependencies.

```powershell
git clone <your-repository-url> SkillOS
cd SkillOS
python -m pip install -e .
python -m skillos init-profile --config-dir "$HOME/.skillos"
python -m skillos init-profile --config-dir "$HOME/.skillos" --scan --skills-dir "$HOME/.codex/skills" --language auto
python -m skillos rank "Review my Python project" --profile "$HOME/.skillos/profile.json" --registry "$HOME/.skillos/registry.json" --intent engineering --need code-review --available analyze,code-review,lsp
python -m skillos route "Review my Python project" --profile "$HOME/.skillos/profile.json" --registry "$HOME/.skillos/registry.json" --available analyze,code-review,lsp --json
python -m skillos feedback --history "$HOME/.skillos/feedback.jsonl" --task "Review my Python project" --skills code-review,analyze --rating 5
```

The setup command asks the user to choose work domains, preferred skills, response preferences, and whether to allow a local scan. Its prompts use the selected `--language` value or a Chinese/English locale default. With consent, it parses `SKILL.md` files below the one supplied skills root and writes a local `registry.json`; without consent, it creates or preserves a manual registry. It writes only local JSON files.

## Example result

```json
{
  "selected_skills": ["code-review", "analyze"],
  "workflow": ["code-review", "analyze"],
  "expansive_workflows_filtered": true
}
```

Use `route` for a natural-language request; it returns matching words as inference evidence and accepts `--intent` or `--need` overrides. Use `--json` to include per-skill score factors. Add `--trace PATH` only when a local JSONL trace is wanted. The `feedback` command records a 1-5 rating only after the user explicitly submits it; passing `--history` to `rank` or `route` adds its local per-skill aggregate to the score.

## Configuration model

The registry can be declared manually by the user:

```json
{
  "skills": [
    {
      "name": "code-review",
      "description": "Review correctness, regressions, risks, and missing tests.",
      "domains": ["engineering"],
      "capabilities": ["code-review", "quality"],
      "triggers": ["review", "quality", "bug"],
      "base_priority": 0.8,
      "workflow_type": "review"
    }
  ]
}
```

The ranker combines declared intent and requested capabilities with profile domain weights, preferred skills, registry metadata, and safety policy. This makes its decisions reproducible. A consented scan extracts frontmatter and lightweight local metadata; semantic interpretation remains the responsibility of the Codex model and the installed skill instructions.

## Codex skill

The installable skill lives in [`skillos/`](skillos/). Copy that directory to your Codex skills directory, then restart or begin a new Codex session. The skill reads a profile and registry only when the user explicitly provides paths or asks to use SkillOS.

## Development

```powershell
python -m unittest discover -s tests -v
python C:\Users\Lenovo\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\skillos
```

## Roadmap

- optional, user-approved feedback records and local weight updates;
- schema adapters for popular `SKILL.md` conventions;
- visual trace viewer;
- opt-in local embeddings for richer candidate matching.

## License

MIT. See [LICENSE](LICENSE).
