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
1. **Review Context**: Understand the architectural components, infrastructure needs, data models, design systems, and the acceptance criteria.
2. **Define Design Tasks**: Define tasks for the Designer (e.g., configuring CSS vars, setting up Tailwind config, base visual skeleton).
3. **Define Infrastructure Tasks**: If the architecture requires new databases, Terraform, Docker files, CI/CD pipelines, or cloud resources, define these as specific tasks.
4. **Define Data Tasks**: Define tasks for the DBA (e.g., write Prisma schemas, run migrations, create seeders).
5. **Define Backend Tasks**: Write specific tasks for the backend developer (e.g., API endpoints, server logic). **Crucially**, assign any general project setup tasks to this section so the project structure is ready first.
6. **Define Frontend Tasks**: Write specific tasks for the frontend developer (e.g., UI components, state management, consuming the APIs).
7. **Define Performance Tasks**: Write tasks for the Performance Tester (e.g., create k6 or artillery load test scripts).
8. **Define Documentation Tasks**: Write tasks for the Tech Writer (e.g., update README, Swagger, OpenAPI specs).
9. **Define Release Tasks**: Write tasks for the Release Manager (e.g., update package.json version, CHANGELOG.md, create local git tag).
10. **Format the Output**: Ensure you strictly separate the output into the corresponding sections.

## Output
You MUST use the `Write` tool to save your plan to `.devhive/specs/04-tasks.md`.

The markdown file should be structured as follows:

```markdown
# Phase 04: Task Plan

## Executive Summary
[1-3 sentences summarizing the execution plan]

## Design Tasks
- [ ] **Task 1: [Name]**
  - Description: [CSS vars, framework configuration]
  - Files: [Files to modify/create]

## Infrastructure Tasks
- [ ] **Task 1: [Name]**
  - Description: [What infrastructure needs to be provisioned]
  - Files: [Files to modify/create]

## Data Tasks
- [ ] **Task 1: [Name]**
  - Description: [Migrations, seeders, schema definitions]
  - Files: [Files to modify/create]

## Backend Tasks
- [ ] **Task 1: [Name]**
  - Description: [Initial project setup, API routes, server logic]
  - Files: [Files to modify/create]

## Frontend Tasks
- [ ] **Task 1: [Name]**
  - Description: [UI components, consuming backend APIs]
  - Files: [Files to modify/create]

## Performance Tasks
- [ ] **Task 1: [Name]**
  - Description: [Load test scripts for critical paths]
  - Files: [Files to modify/create]

## Documentation Tasks
- [ ] **Task 1: [Name]**
  - Description: [API docs, README updates, user manuals]
  - Files: [Files to modify/create]

## Release Tasks
- [ ] **Task 1: [Name]**
  - Description: [Version bump, CHANGELOG updates, local git tag]
  - Files: [Files to modify/create]
```
