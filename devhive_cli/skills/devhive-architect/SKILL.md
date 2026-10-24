---
name: devhive-architect
description: Designs the technical architecture, components, data models, and infrastructure for the feature.
---

# DevHive Architect Skill

## Trigger
When the orchestrator assigns you the architecture phase after the proposal is complete.

## Input Context
Read `.devhive/specs/01-exploration.md` and `.devhive/specs/02-proposal.md`. If the orchestrator supplied an approved PM package, read the matching Feature PRD, `docs/PRODUCT/backlog.md`, and `docs/PRODUCT/user-stories.md`; retain approved story boundaries and acceptance criteria in the design. If PM artifacts are absent, do not require them. You MUST also check for and read `.devhive/memory/index.json` and `.devhive/memory/semantic.md`, `.devhive/memory/anti_patterns.md` to ensure your design does not violate historical architectural decisions or repeat past mistakes.

## Memory Access
To search memory efficiently:
1. First read `.devhive/memory/index.json` to see all memory entries
2. Filter by tags relevant to your task (e.g., "architecture", "backend", "database", "security")
3. Read only the specific memory files you need (don't load everything)
4. Prioritize memories with score >= 0.7 for critical decisions
5. Check for "architecture" and "convention" tagged memories to ensure design consistency

## Playbook (What to Do)
0. **Load DevHive Skills (CRITICAL)**: Before starting, load the bundled `architecture-patterns` and `backend-architect` skills with the `skill` tool. Only skills bundled with DevHive may be loaded. Do not install, download, or depend on external skills. If a skill is unavailable, ignore the error and proceed using your best judgment.
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
