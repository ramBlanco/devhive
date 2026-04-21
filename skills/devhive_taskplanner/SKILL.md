---
name: devhive-taskplanner
description: Breaks down the architecture into actionable development and infrastructure tasks.
---

# DevHive TaskPlanner Skill

## Trigger
When the orchestrator assigns you the task planning phase after the architecture is designed.

## Input Context
Read `.devhive/specs/03-architecture.md` and `.devhive/specs/02-proposal.md`.

## Playbook (What to Do)
1. **Review Context**: Understand the architectural components, infrastructure needs, and the acceptance criteria.
2. **Define Infrastructure Tasks**: If the architecture requires new databases, Terraform, Docker files, CI/CD pipelines, or cloud resources, define these as specific tasks.
3. **Define Application Tasks**: Write specific, actionable, and granular tasks for the software developer (e.g., API endpoints, UI components, logic). Each task should mention the files involved if known.
4. **Format the Output**: Ensure you strictly separate the output into `## Infrastructure Tasks` and `## Application Tasks`.

## Output
You MUST use the `Write` tool to save your plan to `.devhive/specs/04-tasks.md`.

The markdown file should be structured as follows:

```markdown
# Phase 04: Task Plan

## Executive Summary
[1-3 sentences summarizing the execution plan]

## Infrastructure Tasks
- [ ] **Task 1: [Name]**
  - Description: [What infrastructure needs to be provisioned (e.g., Dockerfile, Terraform for RDS)]
  - Files: [Files to modify/create]

## Application Tasks
- [ ] **Task 1: [Name]**
  - Description: [What logic needs to be implemented]
  - Files: [Files to modify/create]
- [ ] **Task 2: [Name]**
  - Description: [What needs to be done]
  - Files: [Files to modify/create]
```
