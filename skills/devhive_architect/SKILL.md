---
name: devhive-architect
description: Designs the technical architecture, components, data models, and infrastructure for the feature.
---

# DevHive Architect Skill

## Trigger
When the orchestrator assigns you the architecture phase after the proposal is complete.

## Input Context
Read `.devhive/specs/01-exploration.md` and `.devhive/specs/02-proposal.md`.

## Playbook (What to Do)
0. **Gather and Load Skills (CRITICAL)**: Before starting, you MUST use the `skill` tool to load specialized instructions. Check `GUIDELINES.md` for global skills, check `04-tasks.md` for task-specific skills. If the tool returns an error because a skill is not installed, ignore the error and proceed using your best judgment.
1. **Review Context**: Understand the scope and acceptance criteria from the proposal.
2. **System Design**: Decide on the architectural pattern to use (e.g., MVC, specific design patterns, service layers) that aligns with the existing codebase.
3. **Component Breakdown**: Identify the new components, classes, or modules that need to be created or modified.
4. **Interface Design**: Design the APIs/interfaces that will connect the components.
5. **Data Architecture**: Design the data models, database schemas, entities, relationships, indexes, and migration strategies.
6. **UX/UI & Design System**: Define the core visual language, layout structure, color palettes, accessibility standards, and a "Design System" skeleton for the frontend.
7. **Infrastructure & Deployment**: Determine what infrastructure is needed (e.g., Docker, Terraform, AWS services, databases) to support this architecture.

## Output
You MUST use the `Write` tool to save your design to `.devhive/specs/03-architecture.md`.

The markdown file should be structured as follows:

```markdown
# Phase 03: Architecture

## Executive Summary
[1-3 sentences summarizing the architectural approach]

## Architecture Pattern
[Description of the pattern chosen and why]

## UX/UI & Design System
[Color palettes, typography, accessibility rules, layout wireframes in text, component library selection]

## Components & Modules
- **[Component Name]**: [Description of its responsibility]

## Data Architecture & Models
- **[Model Name]**: [Description of fields, relationships, indexes, and migration plan]

## APIs / Interfaces
- `[Function/Endpoint Signature]`: [Description of inputs/outputs]

## Infrastructure & Deployment
[Decisions on Cloud, IaC tools like Terraform/AWS CDK, Docker, databases, etc.]
```
