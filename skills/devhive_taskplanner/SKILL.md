---
name: devhive-taskplanner
description: Breaks down the architecture into actionable development tasks.
---

# DevHive TaskPlanner Skill

## Trigger
When the orchestrator assigns you the task planning phase after the architecture is designed.

## Input Context
Read `.devhive/specs/03-architecture.md` and `.devhive/specs/02-proposal.md`.

## Playbook (What to Do)
1. **Review Context**: Understand the architectural components and the acceptance criteria.
2. **Define Epics**: Group related work into high-level epics (e.g., "Database Models", "UI Implementation").
3. **Extract Tasks**: Write specific, actionable, and granular tasks for the developer. Each task should mention the files involved if known.
4. **Sequence Tasks**: Order the tasks logically (e.g., backend before frontend, core logic before UI).

## Output
You MUST use the `Write` tool to save your plan to `.devhive/specs/04-tasks.md`.

The markdown file should be structured as follows:

```markdown
# Phase 04: Task Plan

## Executive Summary
[1-3 sentences summarizing the execution plan]

## Epics
- [Epic 1]
- [Epic 2]

## Tasks
- [ ] **Task 1: [Name]**
  - Description: [What needs to be done]
  - Files: [Files to modify/create]
- [ ] **Task 2: [Name]**
  - Description: [What needs to be done]
  - Files: [Files to modify/create]
```
