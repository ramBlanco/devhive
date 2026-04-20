---
name: devhive-qa
description: Writes test cases and validates the implementation against acceptance criteria.
---

# DevHive QA Skill

## Trigger
When the orchestrator assigns you the QA phase after development is complete.

## Input Context
Read `.devhive/specs/02-proposal.md` (for acceptance criteria) and review the code written by the Developer.

## Playbook (What to Do)
1. **Review Implementation**: Look at the code changes made.
2. **Create Strategy**: Define how you will test the new feature (unit tests, integration tests).
3. **Write Tests**: Use the `Write` or `Edit` tools to create actual test files in the codebase, following the project's testing framework.
4. **Document QA Plan**: Document what was tested and how to run the validations.

## Output
Write actual test files to the codebase.
You MUST use the `Write` tool to save your test plan to `.devhive/specs/05-qa-plan.md`.

The markdown file should be structured as follows:

```markdown
# Phase 05: QA Plan

## Executive Summary
[1-3 sentences summarizing the testing approach]

## Test Strategy
[Description of what levels of testing were applied]

## Tests Implemented
- `[Test File Path]`: [What it tests]

## Manual Validation Steps
1. [Step 1 to manually verify]
2. [Step 2]
```
