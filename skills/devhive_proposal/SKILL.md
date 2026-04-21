---
name: devhive-proposal
description: Creates a formal feature proposal with scope and acceptance criteria based on exploration.
---

# DevHive Proposal Skill

## Trigger
When the orchestrator assigns you the proposal phase after exploration is complete.

## Input Context
Read the `.devhive/specs/01-exploration.md` file to understand the exploration findings.

## Playbook (What to Do)
0. **Gather and Load Skills (CRITICAL)**: Before starting, you MUST use the `skill` tool to load specialized instructions. Check `GUIDELINES.md` for global skills, check `04-tasks.md` for task-specific skills, and ALWAYS load your hardcoded skills: `agile-user-stories`. If the tool returns an error because a skill is not installed, ignore the error and proceed using your best judgment.
1. **Review Context**: Read the exploration analysis thoroughly.
2. **Define Value**: State clearly why the user needs this feature and what value it provides.
3. **Define Scope**: Clearly mark what is IN scope and what is OUT of scope for this iteration.
4. **Define Acceptance Criteria**: List 3-5 clear, testable acceptance criteria that must be met for the feature to be considered complete.

## Output
You MUST use the `Write` tool to save your proposal to `.devhive/specs/02-proposal.md`.

The markdown file should be structured as follows:

```markdown
# Phase 02: Proposal

## Executive Summary
[1-3 sentences summarizing the proposed solution]

## Feature Description & Value
[Detailed description and the value it provides to the user]

## Scope
**In Scope:**
- [Item 1]

**Out of Scope:**
- [Item 2]

## Acceptance Criteria
1. [Criterion 1]
2. [Criterion 2]
3. [Criterion 3]
```
