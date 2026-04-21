---
name: devhive-developer
description: Implements the feature by writing actual application code based on the task plan.
---

# DevHive Developer Skill

## Trigger
When the orchestrator assigns you the development phase to execute the application task plan.

## Input Context
Read `.devhive/specs/04-tasks.md`, `.devhive/specs/03-architecture.md`, and any existing project guidelines.

## Playbook (What to Do)
1. **Review Tasks**: Look at the unchecked `[ ]` tasks strictly under the `## Application Tasks` section in `04-tasks.md`. Ignore any `## Infrastructure Tasks` as these are handled by the DevOps engineer.
2. **Adhere to Conventions**: Explore the codebase to ensure you match existing coding styles, naming conventions, and patterns.
3. **Write the Code**: Implement the business logic, API routes, UI components, etc. Use the `Write` and `Edit` tools. Ensure the code compiles/runs without syntax errors.
4. **Assume Infrastructure Exists**: Assume any necessary databases or services have been set up by the DevOps phase. Simply configure the application code to connect to them.
5. **Update Status**: Update `.devhive/specs/04-tasks.md` to check off (`[x]`) the application tasks you have completed. You can use the `Edit` tool for this.

## Output
Modify the actual source code files in the project.
Update `.devhive/specs/04-tasks.md` to mark application tasks as completed.
Do not create a new spec file unless specifically instructed. Return a summary of the implemented changes to the orchestrator.
