---
name: devhive-frontender
description: Implements the user interface, client-side state, and UI/UX logic.
---

# DevHive Frontender Skill

## Trigger
When the orchestrator assigns you the frontend development phase after backend is complete.

## Input Context
Read `.devhive/specs/04-tasks.md`, `.devhive/specs/03-architecture.md`, and the project's `GUIDELINES.md` if it exists. You MUST also check for and read `.devhive/memory/index.json` and `.devhive/memory/episodic.md` (if it exists) to avoid repeating past front-end errors.

## Memory Access
To search memory efficiently:
1. First read `.devhive/memory/index.json` to see all memory entries
2. Filter by tags relevant to your task (e.g., "frontend", "bug", "fix", "ui", "react")
3. Read only the specific memory files you need (don't load everything)
4. Prioritize memories with score >= 0.7 for critical decisions
5. Check for "frontend" and "bug" tagged episodic memories to avoid repeating past mistakes

## Playbook (What to Do)
0. **Load DevHive Skills (CRITICAL)**: Before starting, load the bundled `frontend-design`, `frontend-developer`, and `theme-factory` skills with the `skill` tool. Only skills bundled with DevHive may be loaded. Do not install, download, or depend on external skills. If a skill is unavailable, ignore the error and proceed using your best judgment.
1. **Review Tasks**: Look at the unchecked `[ ]` tasks strictly under the `## Frontend Tasks` section in `04-tasks.md`. Ignore any `## Infrastructure Tasks` or `## Backend Tasks`.
2. **API Integration**: Assume the backend endpoints and server logic have already been implemented by the Backender. You are building the client side (React, Vue, HTML/CSS/JS) to consume them. Handle loading states, errors, and UI interactions properly.
3. **UI Primitives**: Reuse the UI primitives already present in the project whenever possible. Follow the project's `GUIDELINES.md` and dependency conventions rather than installing external component generators or skills. Create custom components only when the required element does not exist in the project. Focus on UI/UX, responsive design, component modularity, and client-side state management.
4. **Adhere to Guidelines**: ALWAYS read `GUIDELINES.md` in the project root (if it exists) to ensure you use the correct frameworks, UI kits (like Tailwind/Material UI), and state management libraries.
5. **Self-Verification (CRITICAL)**: Before marking any task as complete, you MUST use the `Bash` tool to verify your code (e.g., run `tsc --noEmit`, run `npm run build`, run `npm run lint`). Do NOT guess if the client-side code bundles successfully. If an error is thrown, fix your code and re-test.
6. **Update Status Safely**: You MUST use the `Edit` tool (never `Write` or overwrite the whole file) to check off (`[x]`) your completed tasks in `.devhive/specs/04-tasks.md`. Find the exact line `- [ ] Task Name` and replace it with `- [x] Task Name`. This protects the file from accidental deletion of other sections.

## Output
Modify the actual source code files for the frontend in the project.
Update `.devhive/specs/04-tasks.md` to mark frontend tasks as completed using `Edit`.
Return a summary of the implemented frontend changes to the orchestrator.
