# SkillOS

SkillOS 是面向 Codex 的本地、自主配置、可解释的 Skill 路由层。它根据用户自己填写的偏好和技能注册表，或用户明确同意后的本地 skills 扫描结果，为自然语言请求推荐合适的 Skill 与执行顺序。

它不会读取其他用户的安装目录，不上传提示词或配置，也不会在未明确开启时保存执行记录。只有获得当前用户明确同意后，它才会扫描一个指定的本地 Codex skills 目录。

English documentation: [README.md](README.md).

## 能力

- 通过交互式 CLI 让用户填写本地工作偏好；
- 支持用户手动维护 Skill 注册表，或在明确同意后扫描一个 Codex skills 目录；
- 对中英文自然语言请求做本地意图和能力提示推断，并允许用户显式覆盖；
- 基于任务意图、能力需求、用户偏好、主动提交的本地反馈、基础优先级与安全策略进行可解释排序；
- 输出可审计的候选分数与工作流；
- 仅在用户显式指定时，将执行追踪写入本地 JSONL 文件；
- 提供可安装的 `skillos` Codex Skill，并始终以当前会话真正可用的 Skill 为执行边界。

## 不做什么

- 未获明确同意时不扫描任何目录，默认不扫描插件缓存；
- 不上传 profile、任务文本、注册表或 trace；
- 不绕过 Codex 的会话级 Skill 可用性和触发机制；
- 不会静默启动 `team`、`autopilot`、`ralph` 或 `ultrawork` 等高范围工作流。

## 快速开始

需要 Python 3.11+。MVP 没有第三方运行时依赖。

```powershell
git clone <你的仓库地址> SkillOS
cd SkillOS
python -m pip install -e .
python -m skillos init-profile --config-dir "$HOME/.skillos"
python -m skillos init-profile --config-dir "$HOME/.skillos" --scan --skills-dir "$HOME/.codex/skills" --language auto
python -m skillos rank "检查我的 Python 项目代码质量" --profile "$HOME/.skillos/profile.json" --registry "$HOME/.skillos/registry.json" --intent engineering --need code-review --available analyze,code-review,lsp
python -m skillos route "检查我的 Python 项目代码质量" --profile "$HOME/.skillos/profile.json" --registry "$HOME/.skillos/registry.json" --available analyze,code-review,lsp --json
python -m skillos feedback --history "$HOME/.skillos/feedback.jsonl" --task "检查我的 Python 项目代码质量" --skills code-review,analyze --rating 5
```

首次配置会询问你的主要工作领域、偏好 Skill、回复风格，以及是否同意扫描本机 Codex skills 目录。`--language auto` 会根据系统语言选择中文或英文提示，也可以显式指定语言。获得同意后，SkillOS 只解析指定目录下的 `SKILL.md`，并将结果写入本机的 `registry.json`；拒绝后则创建或保留手动 registry。

## 配置方式

技能清单可以由用户主动声明。例如：

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

`route` 命令会对中英文请求做本地、可解释的意图和能力提示推断，并在输出中给出命中的证据；用户可使用 `--intent` 或 `--need` 覆盖推断。排序器结合意图、能力需求、领域权重、偏好 Skill、主动提交的本地反馈、注册表元数据与安全策略。获授权的扫描器只提取前置元数据和轻量本地信息；对自然语言的深层语义理解仍由 Codex 模型和实际 Skill 的说明负责。

## 安装 Codex Skill

可安装的 Skill 位于 [`skillos/`](skillos/)。将该目录复制到 Codex skills 目录后，重启或新建 Codex 会话。只有当用户明确提供配置路径或要求使用 SkillOS 时，该 Skill 才会读取 profile 与 registry。

## 开发与测试

```powershell
python -m unittest discover -s tests -v
python C:\Users\Lenovo\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\skillos
```

## 许可证

MIT，详见 [LICENSE](LICENSE)。
