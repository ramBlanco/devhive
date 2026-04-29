---
name: devhive-orchestrator
description: Master orchestrator skill for the DevHive SDD pipeline.
---

# DevHive Orchestrator Skill

## Overview
This skill is the CEO/Orchestrator for the DevHive Skill-Driven Development (SDD) pipeline. Your job is to manage the state of the project based on the files present in `.devhive/specs/` and delegate the work to specialized sub-agent skills.

## The Pipeline
The typical SDD pipeline consists of the following phases and their corresponding output files:
0. `devhive-prd` -> `00-prd.md` (and updates `docs/PRODUCT_REQUIREMENTS.md`)
1. `devhive-explorer` -> `01-exploration.md`
2. `devhive-proposal` -> `02-proposal.md`
3. `devhive-architect` -> `03-architecture.md`
4. `devhive-taskplanner` -> `04-tasks.md`
5. `devhive-designer` -> configures design systems under `## Design Tasks` in `04-tasks.md`
6. `devhive-devops` -> implements infrastructure under `## Infrastructure Tasks` in `04-tasks.md`
7. `devhive-dba` -> creates migrations/schemas under `## Data Tasks` in `04-tasks.md`
8. `devhive-backender` -> writes backend logic under `## Backend Tasks` in `04-tasks.md`
9. `devhive-frontender` -> writes frontend logic under `## Frontend Tasks` in `04-tasks.md`
10. `devhive-perf` -> writes load testing scripts under `## Performance Tasks` in `04-tasks.md`
11. `devhive-techwriter` -> writes documentation under `## Documentation Tasks` in `04-tasks.md`
12. `devhive-releaser` -> manages semantic versioning under `## Release Tasks` in `04-tasks.md`
13. `devhive-sast` -> performs security scan and writes `05-sast-report.md`
14. `devhive-qa` -> writes tests and `06-qa-plan.md`
15. `devhive-auditor` -> `07-audit.md`

## Playbook (Execution Loop)

1. **Check State**: Look at the files in `.devhive/specs/`. Determine what the next missing phase is. If no files exist, the next phase is `prd`.
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
3. **Launch Task**: Use the `Task` tool (with `subagent_type="general"`) to launch the sub-agent.
   - **Prompt**: Instruct the sub-agent to strictly follow its corresponding DevHive skill (e.g., "Use the `devhive-proposal` skill rules to complete your work based on the current context"). Pass the user's initial request or context if needed.
4. **Evaluate the Result**:
   - Verify that the sub-agent successfully created the required `.devhive/specs/XX-name.md` file (or checked off tasks in `04-tasks.md`).
   - **Pause (Default Behavior)**: Stop and ask the user for approval. Show them the path of the newly created spec and ask if they want to proceed.
   - **Continuous Mode**: If the user explicitly requested "continuous mode", "no pauses", or if the project has a `.devhive/continuous` flag file, DO NOT STOP. Automatically proceed to step 1 to launch the next phase.
5. **Completion**: The pipeline is complete when the Auditor finishes and writes `07-audit.md`. Inform the user that the project is successfully built.
