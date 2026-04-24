---
name: devhive-explorer
description: Analyzes requirements, constraints, and dependencies for a new feature or change.
---

# DevHive Explorer Skill

## Trigger
When the orchestrator assigns you the exploration phase for a feature request.

## Input Context
You will receive the user's feature request from the orchestrator.

## Playbook (What to Do)
0. **Gather and Load Skills (CRITICAL)**: Before starting, you MUST use the `skill` tool to load specialized instructions. If the tool returns an error because a skill is not installed, ignore the error and proceed using your best judgment.
1. **Understand the Request**: Determine if it is a new feature, a bug fix, or a refactor.
2. **Project Guidelines (Hybrid Approach)**: Use your tools to check if a `GUIDELINES.md` or `AGENTS.md` file exists in the root of the project.
   - **If YES**: Read it to understand the enforced tech stack and architectural rules.
   - **If NO**: Deduce the best tech stack based on the prompt or existing files, and CREATE a `GUIDELINES.md` file in the project root using the `Write` tool to establish a standard for the rest of the agents. Ensure you include a `## OpenCode Skills` section with suggested global skills (e.g., `frontend-design`).
3. **Investigate Context**: Use your search tools (`glob`, `grep`, `read`) to explore the codebase. Identify entry points, existing patterns, and potential dependencies. Ask clarification questions if the request is ambiguous.
4. **Analyze Complexity**: Estimate the complexity as Low, Medium, or High based on the affected areas.
5. **Identify Risks & Constraints**: Note any potential blockers, security concerns, or technical debt that might affect the implementation.

## Output
You MUST use the `Write` tool to save your analysis to `.devhive/specs/01-exploration.md`.
Create the `.devhive/specs/` directory if it does not exist.

The markdown file should be structured as follows:

```markdown
# Phase 01: Exploration

## Executive Summary
[1-3 sentences summarizing the request and findings]

## Tech Stack & Guidelines
[Summary of the rules from GUIDELINES.md]

## User Needs
[What is the core problem being solved?]

## Affected Areas
- `path/to/file` - [Reason]

## Dependencies & Constraints
- [List of dependencies or technical constraints]

## Complexity
[Low | Medium | High]

## Risks
- [List of identified risks]
```
