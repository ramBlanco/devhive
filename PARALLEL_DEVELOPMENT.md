# Parallel Development Guide

## Overview

DevHive now supports **parallel development** through multiple independent Developer agents working on separate tasks simultaneously. This feature dramatically improves efficiency for large projects with multiple independent components.

## Key Features

- **Up to 5 parallel developers** working on independent tasks
- **Automatic dependency management** (explicit + inferred)
- **Isolated context per developer** to prevent interference
- **Smart task distribution** based on dependency graph
- **Token limit handling** with automatic task splitting
- **Seamless integration** with existing pipeline

## How It Works

### 1. Enhanced TaskPlanner

The TaskPlanner agent now generates tasks with dependency information:

```json
{
  "epics": ["Backend", "Frontend", "Testing"],
  "tasks": [
    {
      "id": "task_1",
      "name": "Create database models",
      "description": "Define User and Post models",
      "depends_on": [],
      "estimated_tokens": 1500,
      "files_involved": ["models/user.py", "models/post.py"]
    },
    {
      "id": "task_2",
      "name": "Create API endpoints",
      "description": "Build REST API",
      "depends_on": ["task_1"],
      "estimated_tokens": 2000,
      "files_involved": ["api/routes.py"]
    }
  ],
  "estimated_complexity": "high"
}
```

### 2. Dependency Analysis

The **DependencyManager** analyzes tasks using a hybrid approach:

#### Explicit Dependencies
Tasks can explicitly declare dependencies via `depends_on` field.

#### Inferred Dependencies
The system automatically detects dependencies based on:
- **File relationships**: If Task B modifies files that Task A creates → dependency
- **Naming patterns**: API routes depend on models, tests depend on implementation
- **Import relationships**: Tasks that import from other tasks' files

#### Circular Dependency Detection
The system validates there are no circular dependencies before execution.

### 3. Task Distribution

The **TaskDistributor** coordinates parallel execution:

```
Batch 1: task_1, task_3, task_4  (no dependencies - run in parallel)
  ↓
Batch 2: task_2  (depends on task_1 - wait for completion)
  ↓
Batch 3: task_5  (depends on task_2 and task_3 - wait for both)
```

### 4. Developer Agents

Each **ParallelDeveloperAgent** instance:
- Has its own state file: `.devhive/{project}/developers/dev_task_1_state.json`
- Receives task-scoped context (only relevant information)
- Accesses shared artifacts (exploration, proposal, architecture) - read-only
- Loads outputs from dependency tasks
- Writes files independently then merges results

### 5. Result Aggregation

After all tasks complete, the TaskDistributor aggregates:
- All generated files
- Implementation strategies from each developer
- File structure list
- Task completion metadata

## Usage

### Automatic Mode (Recommended)

The parallel development system activates automatically when:
- TaskPlanner generates **more than 1 task**
- Tasks are properly structured with IDs and dependencies

No configuration needed - the CEO agent automatically routes to TaskDistributor.

### Manual Testing

You can test the parallel development workflow:

```python
# 1. Start pipeline and complete TaskPlanner
devhive_start_pipeline("my_project", "Build a user management system")

# 2. Execute through Explorer → Proposal → Architect → TaskPlanner
# (generates tasks with dependencies)

# 3. CEO automatically detects multiple tasks and routes to TaskDistributor
get_next_step("my_project")
# Returns: {"agent": "TaskDistributor", ...}

# 4. Execute TaskDistributor
execute_task_distributor("my_project", ctx)
# Spawns 5 parallel developers, executes tasks in batches

# 5. Continue to QA
get_next_step("my_project")
# Returns: {"agent": "QA", ...}
```

### Monitoring Progress

Check developer status during execution:

```python
get_developer_status("my_project")
```

Returns:
```json
{
  "status": "in_progress",
  "queue": {
    "total_tasks": 5,
    "pending": 1,
    "in_progress": 3,
    "completed": 1,
    "failed": 0
  },
  "active_developers": ["dev_task_2", "dev_task_3", "dev_task_4"],
  "max_developers": 5
}
```

## Task Breakdown Best Practices

### Good Task Structure

```json
{
  "id": "task_1",
  "name": "Create authentication models",
  "description": "Define User, Session, and Token models with SQLAlchemy",
  "depends_on": [],
  "estimated_tokens": 1200,
  "files_involved": [
    "models/user.py",
    "models/session.py",
    "models/token.py"
  ]
}
```

**Why it's good:**
- Clear scope (authentication models only)
- 3 related files (manageable size)
- No dependencies (can run immediately)
- Reasonable token estimate

### Task Structure to Avoid

```json
{
  "id": "task_bad",
  "name": "Implement everything",
  "description": "Build entire backend",
  "depends_on": [],
  "estimated_tokens": 8000,
  "files_involved": [
    "models/user.py",
    "models/post.py",
    "api/auth.py",
    "api/posts.py",
    "services/email.py",
    "tests/test_auth.py",
    "tests/test_posts.py"
  ]
}
```

**Why it's bad:**
- Scope too broad ("entire backend")
- Too many files (7+)
- Exceeds token limits (8000 tokens)
- Should be split into 3-4 tasks

### Optimal Task Size

- **Files per task**: 2-4 files
- **Estimated tokens**: < 2500 per task
- **Scope**: Single feature or component
- **Dependencies**: Clearly identified

## Dependency Specification

### Example: E-commerce System

```json
{
  "tasks": [
    {
      "id": "models",
      "name": "Create database models",
      "depends_on": [],
      "files_involved": ["models/product.py", "models/order.py"]
    },
    {
      "id": "api_products",
      "name": "Product API endpoints",
      "depends_on": ["models"],
      "files_involved": ["api/products.py"]
    },
    {
      "id": "api_orders",
      "name": "Order API endpoints",
      "depends_on": ["models"],
      "files_involved": ["api/orders.py"]
    },
    {
      "id": "frontend_catalog",
      "name": "Product catalog UI",
      "depends_on": ["api_products"],
      "files_involved": ["ui/catalog.tsx"]
    },
    {
      "id": "frontend_cart",
      "name": "Shopping cart UI",
      "depends_on": ["api_orders"],
      "files_involved": ["ui/cart.tsx"]
    }
  ]
}
```

**Execution Plan:**
- Batch 1: `models` (1 task)
- Batch 2: `api_products`, `api_orders` (2 tasks in parallel)
- Batch 3: `frontend_catalog`, `frontend_cart` (2 tasks in parallel)

## Token Limit Handling

### Problem
A single task's context exceeds the 4000 token limit for the LLM.

### Solution Strategy

The system handles this automatically in 3 phases:

#### Phase 1: Context Reduction
- Summarize large artifacts (exploration, proposal)
- Keep only file paths from dependencies (not full content)
- Reduce acceptance criteria lists

#### Phase 2: Automatic Task Splitting
If context still too large:
- Split task by files (2-3 files per sub-task)
- Create sub-tasks with IDs like `task_1_part_0`, `task_1_part_1`
- Maintain dependencies

#### Phase 3: Graceful Failure
If task cannot be split:
- Return clear error message
- Suggest re-running TaskPlanner with more granular breakdown
- Preserve progress from other tasks

### Example Error Message

```
Task task_3 is too large and involves 8 files.
Please re-run TaskPlanner with instruction to split this task
into smaller subtasks (e.g., 2-3 files per task).
```

## Context Isolation

### Developer State Files

Each developer maintains isolated state:

```
.devhive/my_project/
├── project_state.json           # Global project state
├── artifacts/                   # Shared artifacts
│   ├── exploration_abc123
│   ├── proposal_def456
│   └── architecture_ghi789
├── developers/                  # NEW: Developer-specific states
│   ├── dev_task_1_state.json   # Developer 1's state
│   ├── dev_task_2_state.json   # Developer 2's state
│   └── dev_task_3_state.json   # Developer 3's state
└── memory.db                    # Memory store
```

### Context Sharing Model

**Shared (Read-Only):**
- Exploration artifact
- Proposal artifact
- Architecture artifact
- Tasks artifact
- Project guidelines

**Developer-Specific (Isolated):**
- Current task details
- Files to create
- Dependency task outputs
- Implementation state

### File Writing

Developers write files directly to the workspace, but:
- Each developer focuses on its assigned files
- File conflicts are prevented by dependency management
- Final aggregation merges all file lists

## Performance Considerations

### Token Efficiency

Parallel development uses task-scoped context:
- **Traditional**: All developers get full context (5 × full_size)
- **Parallel**: Each developer gets task + shared context (5 × reduced_size)
- **Savings**: ~40-60% token reduction per developer

### Execution Time

In a true async environment:
- **Sequential**: Task 1 → Task 2 → Task 3 → Task 4 → Task 5 (5× time)
- **Parallel**: [Task 1, Task 2, Task 3] → [Task 4, Task 5] (2× time)
- **Speedup**: ~60% faster for independent tasks

In OpenCode's manual workflow:
- Execution is still sequential but tracked as parallel batches
- Enables future async execution when MCP sampling is available

## Troubleshooting

### Circular Dependencies Detected

**Error:** "Circular dependencies detected in task graph"

**Cause:** Task A depends on Task B, Task B depends on Task C, Task C depends on Task A

**Solution:**
- Review task dependencies in TaskPlanner output
- Break the circular chain
- Re-run TaskPlanner with corrected dependencies

### Task Deadlock

**Error:** "Deadlock detected: 3 tasks pending but none have satisfied dependencies"

**Cause:** All pending tasks have dependencies that will never be satisfied

**Solution:**
- Check for missing task IDs in `depends_on` fields
- Ensure all referenced tasks exist
- Verify no typos in task IDs

### Token Limit Exceeded

**Error:** "Task task_5 context exceeds token limits and cannot be split further"

**Cause:** Single task is inherently too complex

**Solution:**
1. Go back to TaskPlanner stage
2. Provide guidance: "Split task_5 into 3 smaller tasks"
3. Re-execute TaskPlanner
4. Continue with refined task breakdown

## Advanced Usage

### Custom Max Developers

Modify `max_developers` in TaskDistributor:

```python
distributor = TaskDistributor(project_name)
distributor.max_developers = 3  # Limit to 3 parallel developers
```

### Manual Dependency Override

Force dependencies during TaskPlanner:

```
"In your task breakdown, ensure that all API tasks depend on the models task,
and all frontend tasks depend on their respective API tasks."
```

### Retry Failed Tasks

```python
# If a task fails, you can retry it
from devhive.core.task_queue import TaskQueue

queue = TaskQueue(tasks)
queue.retry_failed_task("task_3")
```

## MCP Tools Reference

### `execute_task_distributor(project_name, ctx)`
Executes the parallel development workflow.

**Returns:**
```json
{
  "status": "success",
  "agent": "TaskDistributor",
  "artifact_id": "impl_xyz789",
  "total_tasks": 5,
  "files_written": 12,
  "message": "TaskDistributor completed 5 tasks. Wrote 12 files."
}
```

### `get_developer_status(project_name)`
Gets current status of parallel developers.

**Returns:**
```json
{
  "status": "success",
  "developer_status": {
    "status": "in_progress",
    "queue": {...},
    "active_developers": ["dev_task_1", "dev_task_3"],
    "max_developers": 5
  }
}
```

## Benefits

1. **Efficiency**: Multiple tasks execute in logical parallel batches
2. **Scalability**: Handles large projects with many independent components
3. **Safety**: Dependency management prevents conflicts
4. **Context Optimization**: Task-scoped context reduces token usage
5. **Transparency**: Clear task breakdown and progress tracking
6. **Automatic**: No configuration needed - activates when beneficial

## Limitations

1. **Max Parallelism**: Limited to 5 developers (configurable)
2. **Sequential in OpenCode**: True parallelism requires MCP sampling support
3. **Token Limits**: Very large tasks may still exceed limits
4. **Dependency Complexity**: Deeply nested dependencies may create many sequential batches

## Future Enhancements

- **True async execution** when MCP sampling is available
- **Configurable max_developers** via environment variable
- **Smart batching** based on estimated token usage
- **Progress callbacks** for real-time monitoring
- **Task retry strategies** with exponential backoff
- **Partial completion** handling (some tasks succeed, others fail)

---

**Questions or issues?** See AGENTS.md for development guidelines or open an issue on GitHub.
