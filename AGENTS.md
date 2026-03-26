# AGENTS.md - DevHive MCP Server Development Guide

This guide is for AI coding agents working on the DevHive multi-agent development system.

## Project Overview

DevHive is a Python-based MCP (Model Context Protocol) server that orchestrates an AI development team through a sequential pipeline of 8 specialized agents: Explorer → Proposal → Architect → TaskPlanner → Developer → QA → Auditor → Archivist.

**Tech Stack:** Python 3.10+, FastMCP, async/await patterns

## Build, Run & Test Commands

### Running the Server
```bash
# Run MCP server (main entry point)
python3 -m devhive.server

# Run standalone demo
python3 main.py
```

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Testing
**Note:** No test framework is currently configured. When adding tests:
- Use `pytest` as the testing framework
- Place tests in a `tests/` directory
- Run single test: `pytest tests/test_file.py::test_function_name`
- Run all tests: `pytest`

### Linting & Formatting
**Note:** No linter/formatter is currently configured. Recommended tools:
- `black` for code formatting
- `flake8` or `ruff` for linting
- `mypy` for type checking

## Code Style Guidelines

### Import Organization
Group imports in this order with blank lines between groups:
```python
# 1. Standard library
import json
import logging
from typing import Dict, Any
from pathlib import Path

# 2. Third-party packages
from mcp.server.fastmcp import Context

# 3. Local imports
from devhive.agents.base_agent import BaseAgent
from devhive.core.llm import LLM
```

### Naming Conventions
- **Classes:** PascalCase (e.g., `ExplorerAgent`, `ProjectStateManager`)
- **Functions/Methods:** snake_case (e.g., `get_context`, `save_artifact`)
- **Variables:** snake_case (e.g., `project_name`, `artifact_id`)
- **Constants:** UPPER_SNAKE_CASE (e.g., `WORKSPACE_ROOT`, `MAX_TOKENS`)
- **Private methods:** Prefix with underscore (e.g., `_call_llm`, `_parse_json`)

### Type Hints
Always use type hints for function signatures:
```python
async def execute(self, ctx: Context, **kwargs) -> str:
    pass

def save_artifact(self, step_name: str, content: Dict[str, Any]) -> str:
    pass
```

### Async Patterns
All agent methods MUST be async:
```python
class MyAgent(BaseAgent):
    async def execute(self, ctx: Context, **kwargs) -> str:
        # Use await for LLM calls
        resp = await self._call_llm(ctx, sys_prompt, user_prompt)
        return self.save_artifact("step_name", data)
```

### JSON Communication
All inter-agent communication uses JSON:
```python
# Output JSON only in prompts
sys_prompt = "You are the Developer. Output JSON only."

# Parse responses robustly
data = self._parse_json(resp)

# Serialize context with default=str for safety
user_prompt = f"Context: {json.dumps(context, default=str)}"
```

### Error Handling
Use try/except with logging:
```python
import logging
logger = logging.getLogger(__name__)

try:
    result = await some_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    return {"error": str(e)}
```

### File Operations
ALWAYS use filesystem utilities (never direct os/pathlib):
```python
from devhive.utils.filesystem import write_file, read_file, list_files

# Write file (creates parent directories automatically)
write_file("path/to/file.py", content)

# Read file (raises FileNotFoundError if missing)
content = read_file("path/to/file.py")

# Security: Paths are automatically validated against WORKSPACE_ROOT
```

### Logging
Use structured logging throughout:
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Operation started")
logger.warning("Potential issue detected")
logger.error(f"Operation failed: {error_message}")
```

## Architecture Patterns

### Agent Structure
All agents inherit from `BaseAgent`:
```python
from devhive.agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    role = "MyRole"  # Used for context routing
    
    async def execute(self, ctx: Context, **kwargs) -> str:
        # 1. Get context from previous agents
        context = self.get_context()
        
        # 2. Call LLM with structured prompts
        sys_prompt = "You are MyRole. Output JSON only."
        user_prompt = f"Task: ...\nContext: {json.dumps(context, default=str)}"
        resp = await self._call_llm(ctx, sys_prompt, user_prompt)
        
        # 3. Parse and save artifact
        data = self._parse_json(resp)
        return self.save_artifact("artifact_name", data)
```

### LLM Calls
Use the centralized LLM wrapper:
```python
from devhive.core.llm import LLM

# Generate text
text = await LLM.generate(ctx, system_prompt, user_prompt, max_tokens=2000)

# Generate and parse JSON
data = await LLM.generate_json(ctx, system_prompt, user_prompt)
```

### State Management
Access project state through managers:
```python
from devhive.core.project_state_manager import ProjectStateManager

state_manager = ProjectStateManager(project_name)
state = state_manager.get_state()  # Returns dict with stage, artifacts, files
state_manager.update_artifact("step_name", artifact_id)
state_manager.add_files(["file1.py", "file2.py"])
```

## Common Pitfalls

1. **Never bypass filesystem utilities** - Always use `write_file`, `read_file` from utils
2. **Always await async calls** - Missing `await` causes Promise objects instead of results
3. **Handle JSON parsing failures** - LLMs may return malformed JSON; use `_parse_json()`
4. **Use `default=str` in json.dumps** - Handles non-serializable objects (Path, datetime)
5. **Never hardcode file paths** - Use relative paths; filesystem layer handles resolution
6. **Check for None artifacts** - Context may have `None` for artifacts not yet created
7. **Log errors before returning** - Use logger.error() for debugging MCP server issues

## Manual Workflow (OpenCode Compatible)

**IMPORTANT:** OpenCode does not yet support MCP sampling. Use the manual workflow instead of `build_feature()`.

### Available MCP Tools

#### Orchestration
- **`get_next_step(project_name)`** - Returns which agent to run next and the prompts for LLM

#### Agent Execution (Call after getting prompts from `get_next_step`)
- **`execute_explorer(project_name, requirements, llm_response)`** - Initial analysis
- **`execute_proposal(project_name, llm_response)`** - Feature proposal
- **`execute_architect(project_name, llm_response)`** - Architecture design
- **`execute_task_planner(project_name, llm_response)`** - Task breakdown
- **`execute_developer(project_name, llm_response)`** - Implementation + file writing
- **`execute_qa(project_name, llm_response)`** - Test generation + test file writing
- **`execute_auditor(project_name, llm_response)`** - Final verification
- **`execute_archivist(project_name)`** - Archive project (no LLM needed)

#### Utilities
- **`list_workspace_files(path)`** - List files in workspace
- **`read_workspace_file(path)`** - Read file contents

### Workflow Steps

1. **Start Pipeline**: Call `get_next_step("my_project")`
   - Returns: agent name, prompts, expected JSON keys

2. **Send to LLM**: OpenCode sends the returned prompts to LLM
   - System prompt defines agent role
   - User prompt includes context from previous agents

3. **Execute Agent**: Call `execute_<agent>("my_project", llm_response)`
   - Validates LLM response structure
   - Saves artifact
   - Returns success/error

4. **Repeat**: Call `get_next_step("my_project")` again
   - Continues until status="complete"

### Example Session

```python
# Step 1: Get first agent
get_next_step("csv_export")
# Returns: {"agent": "Explorer", "system_prompt": "...", "user_prompt": "..."}

# Step 2: OpenCode sends prompts to LLM, gets JSON response

# Step 3: Execute agent with response
execute_explorer("csv_export", "Add CSV export", '{"user_needs": "...", ...}')
# Returns: {"status": "success", "artifact_id": "exploration_123"}

# Step 4: Continue to next agent
get_next_step("csv_export")
# Returns: {"agent": "Proposal", ...}

# Repeat until complete
```

### Error Handling

All execution tools validate responses and return clear errors:
```json
{
  "status": "error",
  "message": "Missing required keys: user_needs, constraints",
  "expected_keys": ["user_needs", "constraints", "dependencies", "risks"]
}
```

If validation fails, fix the LLM response and retry the same `execute_*` call.

## Testing New Features

When adding features:
1. Test MCP server: `python3 -m devhive.server` (connects via stdio)
2. Verify logging output in stderr
3. Test manual workflow: `get_next_step() -> execute_*() -> repeat`
4. Check generated files in workspace directory
5. Verify state persistence in `{project_name}/project_state.json`

## References

- MCP SDK: https://github.com/modelcontextprotocol/python-sdk
- FastMCP: Part of MCP SDK, provides simplified server creation
- Project structure: `devhive/agents/` (agents), `devhive/core/` (infrastructure)
- Manual Workflow: See WORKFLOW_MANUAL.md for detailed guide
