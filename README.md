# Delegate to Subagents

Portable Codex skill for delegating broad work to subagents before the main model starts heavy repo/web/log exploration.

## What it covers

- Repo inspection
- Workspace scans
- Web or local research
- Debugging, refactor, implementation, review, verification
- Cross-CLI delegation patterns for Codex, Claude Code, and Gemini CLI

## Files

- `SKILL.md`: main policy and workflow
- `agents/openai.yaml`: Codex skill metadata

## Codex usage

The fallback launcher resolves the subagent model from local Codex config at runtime:

- `C:\Users\<you>\.codex\config.toml`
- `~/.codex/config.toml` via `$CODEX_HOME` when set

If `[agents.subagent].model` exists, it uses that model for `codex exec`. If not, it falls back to the active default model.

## Child prompt shape

Subagent prompts should include the stop guard:

```text
You are dispatched as a subagent. Skip using-superpowers, skip delegate-to-subagents, and do not spawn more subagents.
```

## Status

This repo stores the portable skill definition itself. The skill is designed to be reused across CLI runtimes by adapting only the launcher layer.
