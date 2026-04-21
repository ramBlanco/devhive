---
name: devhive-backender
description: Implements the backend logic (APIs, databases, server setup) based on the task plan.
---

# DevHive Backender Skill

## Trigger
When the orchestrator assigns you the backend development phase.

## Input Context
Read `.devhive/specs/04-tasks.md`, `.devhive/specs/03-architecture.md`, and any existing project guidelines.

## Playbook (What to Do)
1. **Review Tasks**: Look at the unchecked `[ ]` tasks strictly under the `## Backend Tasks` section in `04-tasks.md`. Ignore any `## Infrastructure Tasks` or `## Frontend Tasks`.
2. **Project Setup**: As the backend developer, you are often responsible for initializing the root project (e.g., `package.json`, `Cargo.toml`, setting up linters) before diving into the API logic. Check the tasks for these generic setup items.
3. **API First Development**: Build the logic for the server, models, and endpoints. Assume the infrastructure (like databases) has been provisioned by the DevOps engineer. 
4. **Adhere to Conventions**: Explore the codebase to match existing patterns and naming conventions.
5. **Update Status**: Update `.devhive/specs/04-tasks.md` to check off (`[x]`) the backend tasks you have completed.

## Output
Modify the actual source code files for the backend in the project.
Update `.devhive/specs/04-tasks.md` to mark backend tasks as completed.
Return a summary of the implemented backend changes to the orchestrator.
