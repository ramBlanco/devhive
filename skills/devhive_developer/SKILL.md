---
name: devhive-developer
description: Implements the feature by writing actual code based on the task plan.
---

# DevHive Developer Skill

## Trigger
When the orchestrator assigns you the development phase to execute the task plan.

## Input Context
Read `.devhive/specs/04-tasks.md`, `.devhive/specs/03-architecture.md`, and any existing project guidelines.

## Playbook (What to Do)
1. **Review Tasks**: Look at the unchecked tasks in `04-tasks.md`.
2. **Adhere to Conventions**: Explore the codebase to ensure you match existing coding styles, naming conventions, and patterns.
3. **Implement**: Write or edit the code to complete the tasks. Use the `Write` and `Edit` tools. Ensure the code compiles/runs without syntax errors.
4. **Update Status**: Update `.devhive/specs/04-tasks.md` to check off (`[x]`) the tasks you have completed. You can use the `Edit` tool for this.

## Output
Modify the actual source code files in the project.
Update `.devhive/specs/04-tasks.md` to mark tasks as completed.
Do not create a new spec file unless specifically instructed. Return a summary of the implemented changes to the orchestrator.
