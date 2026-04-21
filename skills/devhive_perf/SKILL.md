---
name: devhive-perf
description: Writes performance, load, and stress test scripts (k6, artillery) to ensure system scalability.
---

# DevHive Performance Tester Skill

## Trigger
When the orchestrator assigns you the performance testing phase.

## Input Context
Read `.devhive/specs/04-tasks.md`, `.devhive/specs/03-architecture.md`, and the project's `GUIDELINES.md` if it exists. Assume the backend and frontend are built.

## Playbook (What to Do)
1. **Review Tasks**: Look at the unchecked `[ ]` tasks strictly under the `## Performance Tasks` section in `04-tasks.md`. Ignore any other sections.
2. **Performance Scope**: You are responsible for designing and writing load, stress, and spike test scripts (using k6, Artillery, JMeter, or a similar tool). Focus on critical API endpoints, database queries, and high-traffic frontend paths. You are not executing the tests in production, but you are creating the scripts and test data for CI/CD integration.
3. **Adhere to Guidelines**: ALWAYS read `GUIDELINES.md` in the project root (if it exists) to ensure you use the correct performance testing framework.
4. **Self-Verification (CRITICAL)**: Before marking any task as complete, you MUST use the `Bash` tool to verify your test scripts (e.g., run `k6 run --vus 1 --duration 5s tests/perf/script.js` to ensure the script itself compiles and executes, not necessarily to test the system fully).
5. **Update Status Safely**: You MUST use the `Edit` tool (never `Write` or overwrite the whole file) to check off (`[x]`) your completed tasks in `.devhive/specs/04-tasks.md`. Find the exact line `- [ ] Task Name` and replace it with `- [x] Task Name`. This protects the file from accidental deletion of other sections.

## Output
Modify the actual source code files in the project to include performance test scripts (e.g., `tests/perf/*`, `load-tests/*`).
Update `.devhive/specs/04-tasks.md` to mark the tasks in the performance block as completed using `Edit`.
Return a summary of the implemented performance test scripts to the orchestrator.