---
name: devhive-taskplanner
description: Breaks down the architecture into actionable infrastructure, backend, and frontend tasks.
---

# DevHive TaskPlanner Skill

## Trigger
When the orchestrator assigns you the task planning phase after the architecture is designed.

## Input Context
Read `.devhive/specs/03-architecture.md` and `.devhive/specs/02-proposal.md`. If the orchestrator supplies a PM package, also read the matching Feature PRD, `docs/PRODUCT/backlog.md`, and `docs/PRODUCT/user-stories.md`. Use PM product inputs only when the story package explicitly says `Status: Approved` and matches the active Feature PRD; otherwise pause for clarification or continue without treating the package as approved. If PM artifacts are absent, use the existing proposal/architecture inputs and do not require stories. You MUST also check for and read `.devhive/memory/index.json` and `.devhive/memory/semantic.md` to integrate any historical rules into your task definitions.

## Memory Access
To search memory efficiently:
1. First read `.devhive/memory/index.json` to see all memory entries
2. Filter by tags relevant to your task (e.g., "architecture", "backend", "frontend", "devops")
3. Read only the specific memory files you need (don't load everything)
4. Prioritize memories with score >= 0.7 for critical decisions

## Playbook (What to Do)
0. **Load DevHive Skills (CRITICAL)**: Before starting, use the `skill` tool to load only skills bundled with DevHive. Do not install, download, or depend on external skills. If a skill is unavailable, ignore the error and proceed using your best judgment.
1. **Review Context**: Understand the architectural components, infrastructure needs, data models, design systems, and the acceptance criteria.
2. **Map Product Scope (when present)**: For each approved PM story requiring implementation, preserve its `PM-###` backlog ID, `US-###` story ID, and Given/When/Then acceptance criteria in the relevant technical task(s). Expand product mini-plan bullets into technical work only where needed; do not treat them as architecture or silently widen scope. Do not create implementation tasks for stories marked blocked. If no PM package is provided, do not invent product IDs and follow the existing PRD/proposal/architecture planning flow.
3. **Define Design Tasks**: Define tasks for the Designer (e.g., configuring CSS vars, setting up Tailwind config, base visual skeleton).
4. **Define Infrastructure Tasks**: If the architecture requires new databases, Terraform, Docker files, CI/CD pipelines, or cloud resources, define these as specific tasks.
5. **Define Data Tasks**: Define tasks for the DBA (e.g., write Prisma schemas, run migrations, create seeders).
6. **Define Backend Tasks**: Write specific tasks for the backend developer (e.g., API endpoints, server logic). **Crucially**, assign any general project setup tasks to this section so the project structure is ready first.
7. **Define Frontend Tasks**: Write specific tasks for the frontend developer (e.g., UI components, state management, consuming the APIs).
8. **Define Performance Tasks**: Write tasks for the Performance Tester (e.g., create k6 or artillery load test scripts).
9. **Define Documentation Tasks**: Write tasks for the Tech Writer (e.g., update README, Swagger, OpenAPI specs).
10. **Define Release Tasks**: Write tasks for the Release Manager (e.g., update package.json version, CHANGELOG.md, create local git tag).
11. **Format the Output**: Ensure you strictly separate the output into the corresponding sections.
12. **Empty Domains**: If a specific domain (e.g., Backend, Data, Infrastructure) is not needed for the project, DO NOT use checkboxes (`[ ]`). Instead, simply write "*None required*" under that section. This prevents the orchestrator from launching unnecessary agents.

## Output
You MUST use the `Write` tool to save your plan to `.devhive/specs/04-tasks.md`.

For **every applicable task in any domain section**, include `Product Backlog ID`, `User Story ID`, and `Acceptance Criteria` metadata (or explicit references) in the task details. The example below shows these optional metadata fields once; they are not limited to Design Tasks. Omit them for unrelated work and for the no-PM-artifact fallback.

The markdown file should be structured as follows:

```markdown
# Phase 04: Task Plan

## Executive Summary
[1-3 sentences summarizing the execution plan]

## Design Tasks
[If applicable, list tasks with `- [ ] **Task Name**`. Otherwise, write "*None required*"]
- [ ] **Task 1: [Name]**
  - Description: [CSS vars, framework configuration]
  - Files: [Files to modify/create]
  - Skills: [Comma-separated list of bundled DevHive skills, or None]
  - Product Backlog ID: [PM-###, when applicable]
  - User Story ID: [US-###, when applicable]
  - Acceptance Criteria: [Reference or concise Given/When/Then criteria, when applicable]

## Infrastructure Tasks
[If applicable, list tasks with `- [ ] **Task Name**`. Otherwise, write "*None required*"]
- [ ] **Task 1: [Name]**
  - Description: [What infrastructure needs to be provisioned]
  - Files: [Files to modify/create]
  - Skills: [Comma-separated list of bundled DevHive skills, or None]

## Data Tasks
[If applicable, list tasks with `- [ ] **Task Name**`. Otherwise, write "*None required*"]
- [ ] **Task 1: [Name]**
  - Description: [Migrations, seeders, schema definitions]
  - Files: [Files to modify/create]
  - Skills: [Comma-separated list of bundled DevHive skills, or None]

## Backend Tasks
[If applicable, list tasks with `- [ ] **Task Name**`. Otherwise, write "*None required*"]
- [ ] **Task 1: [Name]**
  - Description: [Initial project setup, API routes, server logic]
  - Files: [Files to modify/create]
  - Skills: [Comma-separated list of bundled DevHive skills, or None]

## Frontend Tasks
[If applicable, list tasks with `- [ ] **Task Name**`. Otherwise, write "*None required*"]
- [ ] **Task 1: [Name]**
  - Description: [UI components, consuming backend APIs]
  - Files: [Files to modify/create]
  - Skills: [Comma-separated list of bundled DevHive skills, or None]

## Performance Tasks
- [ ] **Task 1: [Name]**
  - Description: [Load test scripts for critical paths]
  - Files: [Files to modify/create]
  - Skills: [Comma-separated list of bundled DevHive skills, or None]

## Documentation Tasks
- [ ] **Task 1: [Name]**
  - Description: [API docs, README updates, user manuals]
  - Files: [Files to modify/create]
  - Skills: [Comma-separated list of bundled DevHive skills, or None]

## Release Tasks
- [ ] **Task 1: [Name]**
  - Description: [Version bump, CHANGELOG updates, local git tag]
  - Files: [Files to modify/create]
  - Skills: [Comma-separated list of bundled DevHive skills, or None]
```
