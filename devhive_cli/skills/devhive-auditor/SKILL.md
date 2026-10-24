---
name: devhive-auditor
description: Verifies project consistency, architecture adherence, and security.
---

# DevHive Auditor Skill

## Trigger
When the orchestrator assigns you the audit phase as the final check.

## Input Context
Read all specs from `.devhive/specs/` and review the final codebase state. You MUST also check for and read `.devhive/memory/index.json` and `.devhive/memory/semantic.md`, `.devhive/memory/anti_patterns.md` (if they exist) to ensure the code does not violate persistent project rules or use known anti-patterns.

## Memory Access
To search memory efficiently:
1. First read `.devhive/memory/index.json` to see all memory entries
2. Filter by tags relevant to your task (e.g., "security", "architecture", "anti-pattern", "quality")
3. Read only the specific memory files you need (don't load everything)
4. Prioritize memories with score >= 0.7 for critical decisions
5. Check for "security" and "anti-pattern" tagged memories to ensure no violations

## Playbook (What to Do)
0. **Load DevHive Skills (CRITICAL)**: Before starting, use the `skill` tool to load only skills bundled with DevHive. Do not install, download, or depend on external skills. If a skill is unavailable, ignore the error and proceed using your best judgment.
1. **Consistency Check**: Verify that the implemented code matches the architecture (`03-architecture.md`) and proposal (`02-proposal.md`).
2. **Security & Quality Audit**: Search for potential vulnerabilities, hardcoded secrets, or poor error handling.
3. **Completeness Check**: Ensure all acceptance criteria are met and all tasks are completed.

## Output
You MUST use the `Write` tool to save your audit report to `.devhive/specs/07-audit.md`.

The markdown file should be structured as follows:

```markdown
# Phase 07: Audit Report

## Executive Summary
[1-3 sentences summarizing the audit result: Pass/Fail]

## Architecture Consistency
[Does the code match the design? Yes/No, with details]

## Security & Quality Risks
- [Any risks found, or "None detected"]

## Missing Pieces
- [Any incomplete criteria or tasks, or "None"]
```
