---
name: delegate-to-subagents
description: MUST use before repo inspection, workspace scan, web or local search, research, coding, debugging, refactor, code review, file triage, document analysis, planning, comparison, implementation, or verification when more than a tiny one-file check. Triggers include broad multi-step work and any task where subagents can gather evidence.
---

# Delegate To Subagents

## Purpose

Use the main model as coordinator, planner, and reviewer. Delegate context-heavy exploration, search, research, implementation, verification, and evidence gathering to subagents whenever the runtime provides a subagent tool and the work can be scoped safely.

This skill optimizes token use: the main model should avoid loading large web, file, repo, log, or document context when a subagent can discover and summarize it independently.

## Delegation Decision

Hard rule: for repo inspection, workspace scan, web/current research, broad file search, log analysis, code review, debugging, refactor planning, implementation, or verification that is more than a tiny one-file check, delegate first. Do not start broad `rg`, directory scans, long file reads, web searches, or test exploration in the main model before launching at least one subagent.

Delegate before doing broad search, reading many files, scanning long logs, analyzing large documents, or starting broad implementation when all are true:

- The task has a clear objective or can be split into clear objectives.
- A subagent can inspect the workspace, search the web, read sources, or run local commands itself.
- The work is not an irreversible production action.
- The main model can review the result from summary, citations, changed files, diff, or verification evidence.

Default to delegating when unsure. The main model may inspect only the minimum needed to write a safe subagent prompt, such as the cwd, explicit user target path, or current config line naming the subagent model.

Keep the work in the main model when:

- The user only asks a small question or one-line command.
- The change is tiny and cheaper to do directly.
- The task requires sensitive credentials, live production mutation, or explicit user approval.
- No subagent tool or safe Codex exec fallback is available in the current runtime.

If no native subagent tool is available in Codex, prefer the `codex exec` fallback below for non-trivial independent work before doing broad context loading in the main model. State that native subagent tooling is unavailable only when both native delegation and the fallback are unavailable or unsuitable.

## Codex CLI Fallback

When running in Codex without a visible `Task` or `subagent` tool, spawn subagents with `codex exec` from the shell for independent, context-heavy tasks. Resolve the subagent model from `$CODEX_HOME/config.toml` or `$env:USERPROFILE\.codex\config.toml` at runtime. Prefer `[agents.subagent].model`; if it is missing, omit `-m` and let Codex use the active default model.

Use this pattern:

```powershell
$prompt = @'
You are dispatched as a subagent. Skip `using-superpowers`, skip `delegate-to-subagents`, and do not spawn more subagents.
Task: <objective>
Workspace: <path>
Constraints: keep changes scoped; preserve unrelated changes; avoid production mutation.
Acceptance: <observable done criteria>
Verification: run relevant checks or explain why not possible.
Return: summary, evidence/file refs, commands run, results, blockers.
Explore independently. Do not assume hidden context.
'@
$cfg = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'config.toml' } else { Join-Path $env:USERPROFILE '.codex\config.toml' }
$subagentModel = if (Test-Path -LiteralPath $cfg) {
  $text = Get-Content -LiteralPath $cfg -Raw
  $match = [regex]::Match($text, '(?ms)^\[agents\.subagent\].*?^model\s*=\s*"([^"]+)"')
  if ($match.Success) { $match.Groups[1].Value }
}
if ($subagentModel) {
  codex exec -m $subagentModel --cd "<path>" --sandbox danger-full-access --skip-git-repo-check --output-last-message "<tmp-output>.md" $prompt
} else {
  codex exec --cd "<path>" --sandbox danger-full-access --skip-git-repo-check --output-last-message "<tmp-output>.md" $prompt
}
```

For parallel independent subagents, start separate PowerShell jobs or processes, each with a distinct output file, then wait and review all outputs before editing or claiming completion. Use a practical timeout for each child run; if it hangs, stop that child process and either retry once with a narrower prompt or continue in the main model with the blocker stated. Do not use this fallback for tasks that require secrets, live production mutation, or irreversible actions unless the user explicitly approved that exact action.

## Cross-CLI Adapters

The policy here is portable; the launcher is not. Keep the same delegation rule, but bind it to the host CLI's own tool surface:

- **Codex CLI**: load this skill, then use `codex exec` as the fallback launcher. Resolve the subagent model from local Codex config at runtime; do not hardcode it in shared policy text.
- **Claude Code**: load this skill with the `Skill` tool, then use Claude Code's native task/subagent mechanism if available. If the runtime has no native subagent tool, use the closest shell/process fallback the host CLI provides, but keep this skill's prompt shape and stop-guard text.
- **Gemini CLI**: activate this skill with `activate_skill`, then use Gemini's native agent/task mechanism if available. If the runtime has no native subagent tool, use the closest shell/process fallback the host CLI provides, but keep this skill's prompt shape and stop-guard text.

Shared prompt invariant: the child prompt should still begin with a stop-guard like `You are dispatched as a subagent. Skip using-superpowers, skip delegate-to-subagents, and do not spawn more subagents.`

If the main model catches itself doing broad local search, repo inspection, or web research before a subagent launch, stop, launch the subagent, then continue only after reviewing its output.

## Main Model Workflow

1. Inspect only enough context to understand the request and risks.
2. Define the objective, constraints, acceptance criteria, and verification method.
3. Split independent work into subagent-sized tasks.
4. Delegate with short prompts; do not preload large files, web pages, logs, or conclusions.
5. Wait for subagent output.
6. Review the returned summary, sources, changed files, diff, tests, and blockers.
7. Read only sources, files, or diffs needed to validate risk.
8. Ask a subagent for focused follow-up if evidence is missing or a bug remains.
9. Run final verification in the main session when practical.
10. Report what was found or changed, what evidence supports it, and any residual risk.

## Subagent Prompt Pattern

Use concise prompts like:

```text
You are dispatched as a subagent. Skip `using-superpowers`, skip `delegate-to-subagents`, and do not spawn more subagents.
Task: <objective>
Workspace: <path if relevant>
Constraints: keep changes scoped; preserve existing behavior; do not revert unrelated changes.
Acceptance: <observable done criteria>
Verification: run relevant checks, cite sources, or explain why not possible.
Return: summary, evidence/sources, files changed if any, commands run, results, blockers.
Explore the repo yourself. Do not assume hidden context.
```

For search or research:

```text
Research <question>. Search independently. Prefer primary/current sources when accuracy may drift. Return concise findings, links or citations, dates, conflicts between sources, and confidence. Do not dump full pages.
```

For local file or document analysis:

```text
Analyze <files/topic>. Locate relevant files yourself. Return concise findings, exact file refs, important excerpts only when necessary, and open questions. Do not summarize unrelated content.
```

For debugging:

```text
Investigate and fix <symptom>. Reproduce first if possible. Find root cause before editing. Keep the patch minimal. Run the narrowest useful verification. Return root cause, patch summary, files changed, commands, results, blockers.
```

For review-only work:

```text
Review the current diff for bugs, regressions, missing tests, and risky assumptions. Prioritize concrete findings with file and line refs. Do not rewrite code unless asked. Return findings first, then residual risk.
```

## Token Discipline

- Do not paste large file contents, logs, documents, or search results into a subagent prompt when the subagent can fetch or read them itself.
- Do not summarize the whole repo, website, or document set for the subagent.
- Do not leak the expected answer, suspected fix, or review conclusion unless the task explicitly requires it.
- Prefer one subagent per independent task over one broad vague subagent.
- Ask subagents to return evidence, not full logs or full page text, unless content is short or diagnostic.
- Main model should inspect only the returned sources, diffs, and high-risk artifacts after subagent completion.

## Review Gate

Before accepting subagent work, verify:

- The result satisfies the acceptance criteria.
- Claims are supported by sources, commands, file refs, or tests.
- For edits, the patch is scoped to the task and no unrelated user changes were reverted.
- Tests or checks ran when relevant, or the reason they could not run is explicit.
- Edge cases, freshness, and source reliability are reasonable for the task.
- The final answer does not overclaim beyond evidence.

If any item fails, send a focused follow-up task to a subagent or fix directly if the patch is small.

## Parallelism

Use parallel subagents only when tasks are independent and unlikely to edit the same files. For overlapping files, sequence the work to avoid conflicting patches.

Good parallel tasks:

- One subagent searches current web sources while another inspects local docs.
- One subagent investigates backend failure while another checks frontend regression.
- One subagent writes tests while another traces root cause.
- One subagent audits docs/config while another validates runtime behavior.

Bad parallel tasks:

- Two subagents refactor the same module.
- Multiple subagents perform broad formatting or rename work.
- Any task touching live production state without explicit approval.

## Completion

Finish only after main-model review and final verification are complete or clearly blocked. In the final response, include concise evidence: key sources or file refs, files changed if any, checks run, pass/fail, and remaining blockers.
