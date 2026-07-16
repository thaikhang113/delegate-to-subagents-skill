---
name: delegate-to-subagents
description: Use when work has multiple independent investigations, context-heavy exploration, long logs or documents, parallel verification, or bounded tasks that can return evidence independently.
---

# Delegate to Subagents

## Core rule

Delegate only when isolation, parallelism, or context savings outweigh coordination cost. Keep small lookups, one-command checks, and localized edits in the main agent.

## Decision gate

Delegate when at least one condition holds:

- Two or more independent workstreams exist.
- Exploration would load large files, logs, documents, or web results into main context.
- Independent verification materially improves confidence.
- A bounded worker can return evidence without user interaction.

Do not delegate when:

- Task is one command, one lookup, or one small localized edit.
- Tasks share mutable files or must run sequentially.
- Work needs secrets, interactive decisions, production mutation, or irreversible action.
- Worker setup, review, and merge cost likely exceeds direct execution.

## Dispatch

1. Use runtime-native subagent tooling first. Use process-based CLI fallback only when native subagent support is unavailable and child completion can be verified.
2. Give each worker one bounded objective, explicit scope, access level, completion criteria, and required evidence.
3. Use `read-only` for exploration, research, review, and non-mutating verification. Use `workspace-write` only for an implementation worker with exclusive file ownership.
4. Parallelize independent tasks only. Sequence dependent tasks and overlapping writes.
5. Wait for every bounded worker before final verification.

Prompt contract:

```text
Task: <bounded objective>
Scope: <files, subsystem, or sources>
Access: <read-only | workspace-write>
Ownership: <files this worker may edit; none for review>
Constraints: preserve unrelated work; no secrets or production mutation.
Done when: <observable acceptance criteria>
Verify: <commands or evidence required>
Return: result, exact references, commands, pass/fail, blockers.
```

## Writer safety

- Assign exclusive file ownership before spawning writers.
- Never run two writers against same file or generated artifact.
- Review-only workers must remain read-only.
- Coordinator must not edit worker-owned files until worker exits.
- Treat sibling changes as invalidation: re-read affected files and reconcile intentionally.
- After last worker exits, re-read final diff and test inventory. Green tests with missing or replaced tests do not count.

## Review gate

Worker output is evidence to inspect, not proof by itself. Before completion:

- Check returned sources, file references, or diff.
- Confirm scope and acceptance criteria.
- Confirm no unrelated files changed.
- Run final verification in coordinator session when practical.
- Report missing checks and blockers without guessing.

## CLI fallback safety

When a process-based fallback is unavoidable:

- Inherit runtime model configuration; do not parse config with regex or hardcode a model.
- Prefer ephemeral child sessions.
- Use `read-only` by default; elevate only to `workspace-write` for explicit implementation scope.
- Never default to unrestricted filesystem access.
- Add non-repository overrides only after confirming they are required.
- Give each process a timeout and distinct output file; stop or narrow a hung child.

## Completion

Finish only after all workers stop, owned changes are reconciled, and coordinator review passes. Report concise evidence: delegated scopes, key references or changed files, checks run, results, and residual risk.
