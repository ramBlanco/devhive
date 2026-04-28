---
name: devhive-qa
description: Writes test cases and validates the implementation against acceptance criteria.
---

# DevHive QA Skill

## Trigger
When the orchestrator assigns you the QA phase after development and SAST are complete.

## Input Context
Read `.devhive/specs/02-proposal.md` (for acceptance criteria), `GUIDELINES.md` if it exists, and review the code written by the developers.

## Playbook (What to Do)
0. **Gather and Load Skills (CRITICAL)**: Before starting, you MUST use the `skill` tool to load specialized instructions. Check `GUIDELINES.md` for global skills, check `04-tasks.md` for task-specific skills. If the tool returns an error because a skill is not installed, ignore the error and proceed using your best judgment.
1. **Review Implementation**: Look at the code changes made. Read the acceptance criteria in `02-proposal.md`.
2. **Create Strategy**: Define how you will test the new feature (unit tests, integration tests).
3. **Write & Run Tests**: Use the `Write` or `Edit` tools to create actual test files in the codebase, following the project's testing framework (from `GUIDELINES.md`). Run the tests using the `Bash` tool to ensure they actually test the implementation correctly.
4. **Active Feedback Loop (Rejection)**: If your tests uncover a bug or a failure in meeting the acceptance criteria, you MUST reject the code. Use the `Edit` tool to modify `.devhive/specs/04-tasks.md`: change the corresponding completed task back to `- [ ]` and add a sub-bullet explaining the failure (e.g., `- [ ] **Task 1** (FAILED QA: Null pointer exception on line 42)`). This will force the orchestrator to send the task back to the developer.
5. **Document QA Plan**: If everything passes or if tests are green, document what was tested and how to run the validations manually.

## Output
Write actual test files to the codebase.
If code is rejected, edit `04-tasks.md` to uncheck the task.
You MUST use the `Write` tool to save your test plan to `.devhive/specs/06-qa-plan.md`.

The markdown file should be structured as follows:

```markdown
# Phase 06: QA Plan

## Executive Summary
[1-3 sentences summarizing the testing approach and result (Pass/Reject)]

## Test Strategy
[Description of what levels of testing were applied]

## Tests Implemented
- `[Test File Path]`: [What it tests]

## Manual Validation Steps
1. [Step 1 to manually verify]
2. [Step 2]
```
