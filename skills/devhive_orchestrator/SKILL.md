---
name: devhive-orchestrator
description: Master orchestrator skill that drives the DevHive Skill-Driven Development (SDD) pipeline.
---

# DevHive Orchestrator Skill

## Overview
This skill replaces the old DevHive MCP server. You are the CEO/Orchestrator. Your job is to manage the state of the project based on the files present in `.devhive/specs/` and delegate the work to specialized sub-agent skills.

## The Pipeline
The typical SDD pipeline consists of the following phases and their corresponding output files:
1. `devhive-explorer` -> `01-exploration.md`
2. `devhive-proposal` -> `02-proposal.md`
3. `devhive-architect` -> `03-architecture.md`
4. `devhive-taskplanner` -> `04-tasks.md`
5. `devhive-developer` -> writes code and checks off tasks in `04-tasks.md`
6. `devhive-qa` -> writes tests and `05-qa-plan.md`
7. `devhive-auditor` -> `06-audit.md`

## Playbook (Execution Loop)

1. **Check State**: Look at the files in `.devhive/specs/`. Determine what the next missing phase is. If no files exist, the next phase is `exploration`.
2. **Determine Sub-Skill**: Based on the missing phase, decide which skill to invoke (e.g., if `01-exploration.md` exists but `02-proposal.md` does not, you need `devhive-proposal`).
3. **Launch Task**: Use the `Task` tool (with `subagent_type="general"`) to launch the sub-agent.
   - **Prompt**: Instruct the sub-agent to strictly follow its corresponding DevHive skill (e.g., "Use the `devhive-proposal` skill rules to complete your work based on the current context"). Pass the user's initial request or context if needed.
4. **Evaluate the Result**:
   - Verify that the sub-agent successfully created the required `.devhive/specs/XX-name.md` file.
   - **Pause (Default Behavior)**: Stop and ask the user for approval. Show them the path of the newly created spec and ask if they want to proceed.
   - **Continuous Mode**: If the user explicitly requested "continuous mode" or "no pauses" in their initial prompt, DO NOT STOP. Automatically proceed to step 1 to launch the next phase.
5. **Completion**: The pipeline is complete when the Auditor finishes and writes `06-audit.md`. Inform the user that the project is successfully built.
