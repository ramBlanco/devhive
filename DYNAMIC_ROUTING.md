# Dynamic Routing & Complexity-Based Workflows

DevHive now employs a **Dynamic Routing** system that adapts the development pipeline based on the complexity of the task. Instead of running all 8 agents for every request, the **CEO Agent** intelligently determines the most efficient workflow.

## Overview

The routing decision is made early in the process by the **Explorer Agent**, which analyzes the initial requirements and assigns a `complexity` level to the project. The CEO then uses this complexity level to skip unnecessary steps while ensuring quality and safety.

## Complexity Levels & Workflows

### 1. Low Complexity (Fast Track)
**Use Case:** Simple bug fixes, minor text changes, configuration updates, or small refactors that don't require architectural changes.

**Workflow:**
1.  **Explorer** (Analysis & Complexity Assessment)
2.  **Developer** (Implementation directly from Requirements)
3.  **QA** (Verification)
4.  **Archivist** (Completion)

**Skipped Agents:** Proposal, Architect, TaskPlanner, Auditor.

### 2. Medium Complexity (Standard)
**Use Case:** New features of moderate size, enhancements to existing features, or changes that require product definition but fit within the existing architecture.

**Workflow:**
1.  **Explorer** (Analysis)
2.  **Proposal** (Feature Definition & Acceptance Criteria)
3.  **Developer** (Implementation from Proposal)
4.  **QA** (Verification against Acceptance Criteria)
5.  **Archivist** (Completion)

**Skipped Agents:** Architect, TaskPlanner, Auditor.

### 3. High Complexity (Comprehensive)
**Use Case:** Large new features, significant architectural changes, security-critical updates, or complex integrations. This is the default safety mode.

**Workflow:**
1.  **Explorer**
2.  **Proposal**
3.  **Architect**
4.  **TaskPlanner**
5.  **Developer**
6.  **QA**
7.  **Auditor**
8.  **Archivist**

**Skipped Agents:** None.

## How It Works

### 1. Complexity Assessment
The **Explorer Agent** analyzes the user's request and outputs a JSON artifact containing a `complexity` field:
```json
{
  "user_needs": "...",
  "constraints": [...],
  "complexity": "low", // "low", "medium", or "high"
  "suggested_workflow": "fast_track"
}
```

### 2. Intelligent Routing (CEO)
The **CEO Agent** reads this artifact. When determining the next step, it checks the `complexity`:
- If `complexity` is **low**, it skips the *Proposal*, *Architect*, and *TaskPlanner* stages, proceeding directly to *Developer*.
- If `complexity` is **medium**, it ensures a *Proposal* is created but skips *Architect* and *TaskPlanner*.

### 3. Context Adaptation
Because some agents (like Architect) might be skipped, downstream agents need to know where to look for instructions. The **Context Router** automatically handles this:
- **Developer Context:** If *Architecture* and *Tasks* are missing, the Router injects the *Exploration* (Requirements) and *Proposal* artifacts directly into the Developer's context.
- **QA Context:** If *Architecture* is missing, the Router provides the *Exploration* and *Proposal* to help QA generate test cases based on the original requirements.

## Benefits

- **Efficiency:** Reduces latency and token usage for simple tasks.
- **Responsiveness:** Faster turnaround for bug fixes and minor updates.
- **Scalability:** Allows the system to handle a wider range of request types without overhead.
