---
name: devhive-explorer
description: Analyzes requirements, constraints, and dependencies for a new feature or change.
---

# DevHive Explorer Skill

## Trigger
When the orchestrator assigns you the exploration phase for a feature request.

## Input Context
You will read `.devhive/specs/00-prd.md` and `docs/PRODUCT_REQUIREMENTS.md` (if they exist) to understand the product requirements. When the orchestrator passes a validated PM package, also read `docs/PRODUCT/backlog.md` and `docs/PRODUCT/user-stories.md`; treat their IDs, approved stories, criteria, and exclusions as requirements and report any material mismatch with the Feature PRD. PM artifacts are optional: if they are absent, explore from the Feature PRD and user request as before. You MUST also check for and read `.devhive/memory/index.json` and `.devhive/memory/semantic.md`, `.devhive/memory/anti_patterns.md` to ensure your exploration respects historical persistent memory constraints.

## Memory Access
To search memory efficiently:
1. First read `.devhive/memory/index.json` to see all memory entries
2. Filter by tags relevant to your task (e.g., "architecture", "backend", "security")
3. Read only the specific memory files you need (don't load everything)
4. Prioritize memories with score >= 0.7 for critical decisions

## Playbook (What to Do)
0. **Load DevHive Skills (CRITICAL)**: Before starting, use the `skill` tool to load only skills bundled with DevHive. Do not install, download, or depend on external skills. If a skill is unavailable, ignore the error and proceed using your best judgment.
1. **Understand the Requirements**: Read `.devhive/specs/00-prd.md` to understand the specific feature, and `docs/PRODUCT_REQUIREMENTS.md` to understand the broader product context. Determine if it is a new feature, a bug fix, or a refactor.
2. **Project Guidelines**: Use your tools to check if a `GUIDELINES.md` or `AGENTS.md` file exists in the root of the project.
   - **If YES**: Read it to understand the enforced tech stack and architectural rules.
   - **If NO**: Deduce the tech stack from the prompt and existing files (package.json, pyproject.toml, imports, framework config) and report it in your exploration output. **DO NOT create `GUIDELINES.md`, `AGENTS.md`, or any other guidance file in the project root.** DevHive never writes guidance files into the user's project.
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
