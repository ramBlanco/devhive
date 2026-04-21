---
name: devhive-orchestrator
description: Master orchestrator skill for the DevHive SDD pipeline.
---

# DevHive Orchestrator Skill

## Overview
This skill is the CEO/Orchestrator for the DevHive Skill-Driven Development (SDD) pipeline. Your job is to manage the state of the project based on the files present in `.devhive/specs/` and delegate the work to specialized sub-agent skills.

## The Pipeline
The typical SDD pipeline consists of the following phases and their corresponding output files:
1. `devhive-explorer` -> `01-exploration.md`
2. `devhive-proposal` -> `02-proposal.md`
3. `devhive-architect` -> `03-architecture.md`
4. `devhive-taskplanner` -> `04-tasks.md`
5. `devhive-devops` -> implements infrastructure and checks off tasks under `## Infrastructure Tasks` in `04-tasks.md`
6. `devhive-developer` -> writes code and checks off tasks under `## Application Tasks` in `04-tasks.md`
7. `devhive-qa` -> writes tests and `05-qa-plan.md`
8. `devhive-auditor` -> `06-audit.md`

## Playbook (Execution Loop)

1. **Check State**: Look at the files in `.devhive/specs/`. Determine what the next missing phase is. If no files exist, the next phase is `exploration`.
2. **Determine Sub-Skill**: Based on the missing phase, decide which skill to invoke.
   - If `04-tasks.md` exists but `05-qa-plan.md` does not, check `04-tasks.md`:
     - Are there unchecked tasks `[ ]` under `## Infrastructure Tasks`? -> Invoke `devhive-devops`.
     - If Infrastructure is done `[x]` but there are unchecked tasks `[ ]` under `## Application Tasks`? -> Invoke `devhive-developer`.
     - If both are fully `[x]`, proceed to `devhive-qa`.
3. **Launch Task**: Use the `Task` tool (with `subagent_type="general"`) to launch the sub-agent.
   - **Prompt**: Instruct the sub-agent to strictly follow its corresponding DevHive skill (e.g., "Use the `devhive-proposal` skill rules to complete your work based on the current context"). Pass the user's initial request or context if needed.
4. **Evaluate the Result**:
   - Verify that the sub-agent successfully created the required `.devhive/specs/XX-name.md` file (or checked off tasks in `04-tasks.md`).
   - **Pause (Default Behavior)**: Stop and ask the user for approval. Show them the path of the newly created spec and ask if they want to proceed.
   - **Continuous Mode**: If the user explicitly requested "continuous mode", "no pauses", or if the project has a `.devhive/continuous` flag file, DO NOT STOP. Automatically proceed to step 1 to launch the next phase.
5. **Completion**: The pipeline is complete when the Auditor finishes and writes `06-audit.md`. Inform the user that the project is successfully built.
