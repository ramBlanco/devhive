---
name: devhive-auditor
description: Verifies project consistency, architecture adherence, and security.
---

# DevHive Auditor Skill

## Trigger
When the orchestrator assigns you the audit phase as the final check.

## Input Context
Read all specs from `.devhive/specs/` and review the final codebase state.

## Playbook (What to Do)
1. **Consistency Check**: Verify that the implemented code matches the architecture (`03-architecture.md`) and proposal (`02-proposal.md`).
2. **Security & Quality Audit**: Search for potential vulnerabilities, hardcoded secrets, or poor error handling.
3. **Completeness Check**: Ensure all acceptance criteria are met and all tasks are completed.

## Output
You MUST use the `Write` tool to save your audit report to `.devhive/specs/06-audit.md`.

The markdown file should be structured as follows:

```markdown
# Phase 06: Audit Report

## Executive Summary
[1-3 sentences summarizing the audit result: Pass/Fail]

## Architecture Consistency
[Does the code match the design? Yes/No, with details]

## Security & Quality Risks
- [Any risks found, or "None detected"]

## Missing Pieces
- [Any incomplete criteria or tasks, or "None"]
```
