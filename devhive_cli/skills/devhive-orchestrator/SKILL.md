---
name: devhive-orchestrator
description: Master orchestrator skill for the DevHive SDD pipeline.
---

# DevHive Orchestrator Skill

## Overview
This skill is the CEO/Orchestrator for the DevHive Skill-Driven Development (SDD) pipeline. Your job is to manage the state of the project based on `.devhive/specs/`, optionally ingest an approved PM package from `docs/PRODUCT/`, and delegate the work to specialized sub-agent skills.

## The Pipeline
The typical SDD pipeline consists of the following phases and their corresponding output files:
0. `devhive-analyzer` -> (optional) analyzes existing project, proposes memory entries for approval
1. `devhive-prd` -> `00-prd.md` (and updates `docs/PRODUCT_REQUIREMENTS.md`)
2. `devhive-explorer` -> `01-exploration.md`
3. `devhive-proposal` -> `02-proposal.md`
4. `devhive-architect` -> `03-architecture.md`
5. `devhive-taskplanner` -> `04-tasks.md`
6. `devhive-designer` -> configures design systems under `## Design Tasks` in `04-tasks.md`
7. `devhive-devops` -> implements infrastructure under `## Infrastructure Tasks` in `04-tasks.md`
8. `devhive-dba` -> creates migrations/schemas under `## Data Tasks` in `04-tasks.md`
9. `devhive-backender` -> writes backend logic under `## Backend Tasks` in `04-tasks.md`
10. `devhive-frontender` -> writes frontend logic under `## Frontend Tasks` in `04-tasks.md`
11. `devhive-perf` -> writes load testing scripts under `## Performance Tasks` in `04-tasks.md`
12. `devhive-techwriter` -> writes documentation under `## Documentation Tasks` in `04-tasks.md`
13. `devhive-releaser` -> manages semantic versioning under `## Release Tasks` in `04-tasks.md`
14. `devhive-sast` -> performs security scan and writes `05-sast-report.md`
15. `devhive-qa` -> writes tests and `06-qa-plan.md`
16. `devhive-auditor` -> `07-audit.md`
17. `devhive-reflection` -> generates persistent memory in `.devhive/memory/` and writes `08-reflection.md`

## Playbook (Execution Loop)

**Strict Sequential Enforcement (CRITICAL):** NEVER skip a phase. Even if the user provides a highly detailed plan, architecture, or task list in their initial prompt, treat it ONLY as *input context*. You MUST still invoke the planning skills (`devhive-prd`, `devhive-explorer`, `devhive-proposal`, `devhive-architect`, `devhive-taskplanner`) sequentially. Instruct those sub-agents to ingest and adapt the user's plan into the official `.devhive/specs/` markdown files.

1. **Check State**: Look at the files in `.devhive/specs/`. Determine what the next missing phase is.
   - **Phase 0 (Analyzer)**: If no `.devhive/memory/index.json` exists OR if `.devhive/memory/` is empty, this is a FIRST-TIME project for DevHive. Invoke `devhive-analyzer` FIRST to analyze the project and propose memory entries. Only proceed to Phase 1 after analyzer completes.
   - If memory already exists (`.devhive/memory/index.json` has entries), SKIP the analyzer and go directly to Phase 1.
     - **PM package preflight and pending-work check (before launching planning or implementation phases)**: Inspect `docs/PRODUCT/user-stories.md` and `docs/PRODUCT/backlog.md` when present, and inspect `.devhive/specs/04-tasks.md` when present. Report pending `US-###` stories and unchecked `[ ]` technical tasks, including their IDs and parent `PM-###` where available. A task is in scope only when its task plan clearly belongs to the active Feature PRD; if linkage is missing, stale, or ambiguous, ask before executing it. Treat PM artifacts as authoritative constraints only when the package says `Status: Approved` and matches the active Feature PRD. A PM story is executable only when it maps to a real backlog item and is not blocked. Treat `Execution Status: Pending` and `Execution Status: In Progress` as unfinished, `Completed` as finished, and a missing execution status in a legacy approved package as `Execution Status: Pending`. Never execute stories from a Draft package; report them as awaiting package approval. A Draft package requires explicit user approval before proceeding with that scope. If artifacts are stale or conflict with the active PRD, pause for clarification. Partial artifacts are optional context only; do not fabricate missing backlog items or stories. If unfinished work exists and the user did not explicitly ask to execute it, pause before any implementation and ask what to do, listing the detected work and offering execution of all eligible pending work, selection of specific items, or deferral. Do not confuse approval/review requests with implementation authorization. If no PM package exists, preserve the existing PRD-first pipeline.
     - **Execution scope**: A request naming one `US-###` authorizes only that validated story. A request to execute “all pending stories” or “all pending work” authorizes all eligible pending stories in backlog priority order, then `US-###` order; execute one story at a time and complete its SDD/implementation/validation cycle before starting the next. Do not combine stories or include blocked, stale, Draft, or already-completed stories. Before each story, verify that `.devhive/specs/00-prd.md` matches the active Feature PRD and that story-specific artifacts (`01-exploration.md` through `08-reflection.md` and `04-tasks.md` checkboxes) describe the current story; do not infer the next story is complete from files or checked tasks left by a previous story. Regenerate/update any mismatched planning phase and task plan before implementation, keeping the current story's IDs and acceptance criteria in scope. For multi-story authorization, do not pause for routine phase approvals; pause only for material ambiguity, a blocked/unrecoverable phase, or a validation failure, and do not advance to later stories until the current story succeeds. Set the story's `Execution Status` to `In Progress` when its cycle starts and to `Completed` only after implementation plus required QA/audit validation succeeds. On an incomplete or failed cycle, preserve `In Progress` and report the reason. Keep the selected story's `US-###`, parent `PM-###`, and acceptance criteria in every relevant planning/implementation prompt. If no PM package exists, preserve the existing PRD-first pipeline while applying the same pending-task check to the active task plan.
2. **Determine Sub-Skill**: Based on the missing phase, decide which skill to invoke.
   - If `00-prd.md` does not exist -> Invoke `devhive-prd`.
   - If `00-prd.md` exists but `01-exploration.md` does not -> Invoke `devhive-explorer`.
   - If `01-exploration.md` exists but `02-proposal.md` does not -> Invoke `devhive-proposal`.
   - If `02-proposal.md` exists but `03-architecture.md` does not -> Invoke `devhive-architect`.
   - If `03-architecture.md` exists but `04-tasks.md` does not -> Invoke `devhive-taskplanner`.
   - If `04-tasks.md` exists but `05-sast-report.md` does not, check `04-tasks.md` sequentially:
     - Are there unchecked tasks `[ ]` under `## Design Tasks`? -> Invoke `devhive-designer`.
     - Else, are there unchecked tasks `[ ]` under `## Infrastructure Tasks`? -> Invoke `devhive-devops`.
     - Else, are there unchecked tasks `[ ]` under `## Data Tasks`? -> Invoke `devhive-dba`.
     - Else, are there unchecked tasks `[ ]` under `## Backend Tasks`? -> Invoke `devhive-backender`.
     - Else, are there unchecked tasks `[ ]` under `## Frontend Tasks`? -> Invoke `devhive-frontender`.
     - Else, are there unchecked tasks `[ ]` under `## Performance Tasks`? -> Invoke `devhive-perf`.
     - Else, are there unchecked tasks `[ ]` under `## Documentation Tasks`? -> Invoke `devhive-techwriter`.
     - Else, are there unchecked tasks `[ ]` under `## Release Tasks`? -> Invoke `devhive-releaser`.
     - If ALL sections are fully `[x]`, proceed to `devhive-sast`.
   - If `05-sast-report.md` exists but `06-qa-plan.md` does not -> Invoke `devhive-qa`.
   - If `06-qa-plan.md` exists but `07-audit.md` does not -> Invoke `devhive-auditor`.
   - If `07-audit.md` exists but `08-reflection.md` does not -> Invoke `devhive-reflection`.
3. **Launch Task**: Use the `Task` tool (with `subagent_type="general"`) to launch the sub-agent.
     - **Prompt**: Instruct the sub-agent to strictly follow its corresponding DevHive skill. Instruct the sub-agent to read `.devhive/memory/` files (if they exist) for contextual constraints. When PM preflight validated approved inputs, pass the Feature PRD, backlog/story artifact paths and contents, and require preservation of `PM-###`/`US-###` IDs and acceptance criteria. If a story was selected, explicitly scope the phase to that story and parent backlog item; other package stories are context only, not implementation scope. Do not require these paths when the PM package is absent. If invoking `devhive-reflection`, you MUST pass a summary of the current chat history (human corrections and feedback) as input. Pass the user's initial request or context if needed.
   - **Special Case - Analyzer**: When invoking `devhive-analyzer`, pass the current project directory context and indicate if an `AGENTS.md` or `GUIDELINES.md` file exists. Instruct the analyzer to prioritize extracting memories from these files if they exist.
4. **Evaluate the Result**:
   - Verify that the sub-agent successfully created the required `.devhive/specs/XX-name.md` file (or checked off tasks in `04-tasks.md`).
   - **Pause (Default Behavior)**: For normal pipeline work, stop and ask the user for approval. Show them the path of the newly created spec and ask if they want to proceed. This default pause does not apply to routine phases of stories explicitly authorized by the user for execution; follow the multi-story authorization rule in the PM package preflight.
   - **Continuous Mode**: If the user explicitly requested "continuous mode", "no pauses", or if the project has a `.devhive/continuous` flag file, DO NOT STOP. Automatically proceed to step 1 to launch the next phase.
5. **Completion & Executive Summary**: The pipeline is complete when the Reflection agent finishes and writes `08-reflection.md`. Instead of just saying "done", you MUST output an **Executive Summary** to the user.
   - You MUST use the `Read` tool to extract data from `.devhive/specs/05-sast-report.md` and `.devhive/specs/07-audit.md`.
   - **A. Security Summary**: Output a highly visible Markdown table summarizing the SAST findings. Columns: `Severity` | `Vulnerability Type` | `Affected File` | `Status/Recommendation`.
   - **B. Audit Summary**: Output a brief summary of the auditor's findings. Include the overall "Pass/Fail" status, architecture adherence, and any critical technical debt.
   - Conclude your message by informing the user that the project is successfully built, and remind them that full details are available in the `.devhive/specs/` directory.
