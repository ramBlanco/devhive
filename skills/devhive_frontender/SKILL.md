---
name: devhive-frontender
description: Implements the user interface, client-side state, and UI/UX logic.
---

# DevHive Frontender Skill

## Trigger
When the orchestrator assigns you the frontend development phase after backend is complete.

## Input Context
Read `.devhive/specs/04-tasks.md`, `.devhive/specs/03-architecture.md`, and any existing project guidelines.

## Playbook (What to Do)
1. **Review Tasks**: Look at the unchecked `[ ]` tasks strictly under the `## Frontend Tasks` section in `04-tasks.md`. Ignore any `## Infrastructure Tasks` or `## Backend Tasks`.
2. **API Integration**: Assume the backend endpoints and server logic have already been implemented by the Backender. You are building the client side (React, Vue, HTML/CSS/JS) to consume them. Handle loading states, errors, and UI interactions properly.
3. **Design & UX**: Focus on UI/UX, responsive design, component modularity, and client-side state management.
4. **Adhere to Conventions**: Look around the codebase to see how styling (e.g. Tailwind, CSS Modules) and components are structured.
5. **Update Status**: Update `.devhive/specs/04-tasks.md` to check off (`[x]`) the frontend tasks you have completed.

## Output
Modify the actual source code files for the frontend in the project.
Update `.devhive/specs/04-tasks.md` to mark frontend tasks as completed.
Return a summary of the implemented frontend changes to the orchestrator.
