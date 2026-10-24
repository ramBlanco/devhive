---
name: devhive-proposal
description: Creates a formal feature proposal with scope and acceptance criteria based on exploration.
---

# DevHive Proposal Skill

## Trigger
When the orchestrator assigns you the proposal phase after exploration is complete.

## Input Context
Read `.devhive/specs/01-exploration.md` to understand the exploration findings. If the orchestrator supplied an approved PM package, also consult its Feature PRD, `docs/PRODUCT/backlog.md`, and `docs/PRODUCT/user-stories.md`; preserve story IDs and acceptance criteria in the proposal and flag conflicts. If no package is supplied, use the existing exploration/PRD context without requiring PM artifacts.

## Playbook (What to Do)
0. **Load DevHive Skills (CRITICAL)**: Before starting, use the `skill` tool to load only skills bundled with DevHive. Do not install, download, or depend on external skills. If a skill is unavailable, ignore the error and proceed using your best judgment.
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
