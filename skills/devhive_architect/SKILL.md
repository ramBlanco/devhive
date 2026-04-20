---
name: devhive-architect
description: Designs the technical architecture, components, and data models for the feature.
---

# DevHive Architect Skill

## Trigger
When the orchestrator assigns you the architecture phase after the proposal is complete.

## Input Context
Read `.devhive/specs/01-exploration.md` and `.devhive/specs/02-proposal.md`.

## Playbook (What to Do)
1. **Review Context**: Understand the scope and acceptance criteria from the proposal.
2. **System Design**: Decide on the architectural pattern to use (e.g., MVC, specific design patterns, service layers) that aligns with the existing codebase.
3. **Component Breakdown**: Identify the new components, classes, or modules that need to be created or modified.
4. **Interface Design**: Design the data models, schemas, and APIs/interfaces that will connect the components.

## Output
You MUST use the `Write` tool to save your design to `.devhive/specs/03-architecture.md`.

The markdown file should be structured as follows:

```markdown
# Phase 03: Architecture

## Executive Summary
[1-3 sentences summarizing the architectural approach]

## Architecture Pattern
[Description of the pattern chosen and why]

## Components & Modules
- **[Component Name]**: [Description of its responsibility]

## Data Models / State
- **[Model Name]**: [Description of fields/state]

## APIs / Interfaces
- `[Function/Endpoint Signature]`: [Description of inputs/outputs]
```
