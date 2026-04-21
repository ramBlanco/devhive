---
name: devhive-taskplanner
description: Breaks down the architecture into actionable infrastructure, backend, and frontend tasks.
---

# DevHive TaskPlanner Skill

## Trigger
When the orchestrator assigns you the task planning phase after the architecture is designed.

## Input Context
Read `.devhive/specs/03-architecture.md` and `.devhive/specs/02-proposal.md`.

## Playbook (What to Do)
1. **Review Context**: Understand the architectural components, infrastructure needs, and the acceptance criteria.
2. **Define Infrastructure Tasks**: If the architecture requires new databases, Terraform, Docker files, CI/CD pipelines, or cloud resources, define these as specific tasks.
3. **Define Backend Tasks**: Write specific tasks for the backend developer (e.g., API endpoints, server logic, database connections). **Crucially**, assign any general project setup tasks (like initializing the repository, creating `package.json`, or setting up global linters) to this backend section so the project structure is ready first.
4. **Define Frontend Tasks**: Write specific tasks for the frontend developer (e.g., UI components, state management, consuming the APIs).
5. **Format the Output**: Ensure you strictly separate the output into `## Infrastructure Tasks`, `## Backend Tasks`, and `## Frontend Tasks`.

## Output
You MUST use the `Write` tool to save your plan to `.devhive/specs/04-tasks.md`.

The markdown file should be structured as follows:

```markdown
# Phase 04: Task Plan

## Executive Summary
[1-3 sentences summarizing the execution plan]

## Infrastructure Tasks
- [ ] **Task 1: [Name]**
  - Description: [What infrastructure needs to be provisioned]
  - Files: [Files to modify/create]

## Backend Tasks
- [ ] **Task 1: [Name]**
  - Description: [Initial project setup, API routes, database logic]
  - Files: [Files to modify/create]

## Frontend Tasks
- [ ] **Task 1: [Name]**
  - Description: [UI components, consuming backend APIs]
  - Files: [Files to modify/create]
```
