# Delegate to Subagents

Portable policy for delegating work only when isolation, parallelism, or context savings justify coordination cost.

## Highlights

- Native subagents first; process-based CLI only as fallback
- Small tasks stay in main agent
- Read-only research and review
- Workspace-write only with exclusive file ownership
- Coordinator reviews evidence and runs final verification

## Install for Codex

```bash
git clone https://github.com/thaikhang113/delegate-to-subagents-skill.git ~/.codex/skills/delegate-to-subagents
```

Update:

```bash
git -C ~/.codex/skills/delegate-to-subagents pull --ff-only
```

Validate:

```bash
python ~/.codex/skills/delegate-to-subagents/scripts/validate.py
```

## Files

- `SKILL.md`: portable delegation policy
- `agents/openai.yaml`: Codex skill metadata
- `scripts/validate.py`: dependency-free smoke validation

Launcher syntax varies by runtime. Skill intentionally avoids unsafe universal shell recipes and relies on native subagent tooling whenever available.
