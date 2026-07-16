from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
skill = (root / "SKILL.md").read_text(encoding="utf-8")
metadata = (root / "agents" / "openai.yaml").read_text(encoding="utf-8")

assert skill.startswith("---\n"), "SKILL.md must start with YAML frontmatter"
match = re.match(r"---\n(.*?)\n---\n\n(.+)", skill, re.S)
assert match, "frontmatter must close and body must be non-empty"
frontmatter, body = match.groups()
name = re.search(r"^name:\s*(.+)$", frontmatter, re.M)
description = re.search(r"^description:\s*(.+)$", frontmatter, re.M)
assert name and name.group(1).strip() == "delegate-to-subagents"
assert description and description.group(1).strip().startswith("Use when ")
assert len(description.group(1).strip()) <= 500
assert len(body.split()) <= 900, "frequently loaded skill must stay compact"

for unsafe in ("danger-full-access", "[agents.subagent]", "Default to delegating when unsure"):
    assert unsafe not in skill, f"unsafe or obsolete guidance remains: {unsafe}"

for required in (
    "native subagent",
    "read-only",
    "workspace-write",
    "exclusive file ownership",
    "final verification",
):
    assert required.lower() in skill.lower(), f"missing required rule: {required}"

assert "$delegate-to-subagents" in metadata
assert "allow_implicit_invocation: true" in metadata
print("delegate-to-subagents skill validation passed")
