---
name: devhive-backender
description: Implements the backend logic (APIs, databases, server setup) based on the task plan.
---

# DevHive Backender Skill

## Trigger
When the orchestrator assigns you the backend development phase.

## Input Context
Read `.devhive/specs/04-tasks.md`, `.devhive/specs/03-architecture.md`, and the project's `GUIDELINES.md` if it exists.

## Playbook (What to Do)
0. **Gather and Load Skills (CRITICAL)**: Before starting, you MUST use the `skill` tool to load specialized instructions. Check `GUIDELINES.md` for global skills, check `04-tasks.md` for task-specific skills, and ALWAYS load your hardcoded skills: `secure-api-design`, `clean-code`.
1. **Review Tasks**: Look at the unchecked `[ ]` tasks strictly under the `## Backend Tasks` section in `04-tasks.md`. Ignore any `## Infrastructure Tasks` or `## Frontend Tasks`.
2. **Project Setup**: As the backend developer, you are often responsible for initializing the root project (e.g., `package.json`, `Cargo.toml`, setting up linters) before diving into the API logic. Check the tasks for these generic setup items.
3. **API First Development**: Build the logic for the server, models, and endpoints. Assume the infrastructure (like databases) has been provisioned by the DevOps engineer. 
4. **Adhere to Guidelines**: ALWAYS read `GUIDELINES.md` in the project root (if it exists) to ensure you use the correct frameworks, versions, and styling conventions.
5. **Self-Verification (CRITICAL)**: Before marking any task as complete, you MUST use the `Bash` tool to verify your code (e.g., run `tsc --noEmit`, syntax checks, linter, or run a test script). Do NOT guess if the code works. If an error is thrown, fix your code and re-test.
6. **Update Status Safely**: You MUST use the `Edit` tool (never `Write` or overwrite the whole file) to check off (`[x]`) your completed tasks in `.devhive/specs/04-tasks.md`. Find the exact line `- [ ] Task Name` and replace it with `- [x] Task Name`. This protects the file from accidental deletion of other sections.

## Output
Modify the actual source code files for the backend in the project.
Update `.devhive/specs/04-tasks.md` to mark backend tasks as completed using `Edit`.
Return a summary of the implemented backend changes to the orchestrator.
