# DevHive MCP Server Integration

This document explains how to run the DevHive Multi-Agent System as an MCP Server.

## Prerequisites

You need the `mcp` Python SDK installed:

```bash
pip install mcp
```

## Running the Server

You can run the MCP server using Python directly. From the project root directory:

```bash
python3 -m devhive.server
```

This starts the server on stdio, ready to be connected to an MCP client like Claude Desktop, Cursor, or OpenCode.

## Connecting to Claude Desktop

To use this with Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "devhive": {
      "command": "python3",
      "args": [
        "-m",
        "devhive.server"
      ],
      "cwd": "/absolute/path/to/devhive",
      "env": {
        "PYTHONPATH": "/absolute/path/to/devhive"
      }
    }
  }
}
```

Replace `/absolute/path/to/devhive` with the full path to this directory.

## Workflow Options

DevHive supports two workflows depending on your MCP client's capabilities:

### 1. Manual Workflow (OpenCode, Cursor without sampling)

**Recommended for OpenCode users** - See [WORKFLOW_MANUAL.md](WORKFLOW_MANUAL.md) for detailed guide.

This workflow doesn't require MCP sampling support. You manually orchestrate the pipeline:

```python
# Step 1: Get next agent and prompts
get_next_step("my_project")

# Step 2: OpenCode sends prompts to LLM

# Step 3: Execute agent with LLM response
execute_explorer("my_project", "requirements", llm_response)

# Step 4: Repeat for all 8 agents
```

**Available Tools:**
- `get_next_step(project_name)` - Get next agent and prompts
- `execute_explorer(project_name, requirements, llm_response)`
- `execute_proposal(project_name, llm_response)`
- `execute_architect(project_name, llm_response)`
- `execute_task_planner(project_name, llm_response)`
- `execute_developer(project_name, llm_response)` - Writes code files
- `execute_qa(project_name, llm_response)` - Writes test files
- `execute_auditor(project_name, llm_response)`
- `execute_archivist(project_name)` - No LLM needed

**Pipeline Order:**
1. Explorer - Initial feature analysis
2. Proposal - Feature proposal and acceptance criteria
3. Architect - Technical architecture design
4. TaskPlanner - Break down into development tasks
5. Developer - Implement feature and write code files
6. QA - Generate tests and write test files
7. Auditor - Verify consistency and completeness
8. Archivist - Archive completed project

### 2. Automatic Workflow (Future - Requires Sampling)

**Note:** This requires MCP sampling support, not yet available in OpenCode.

```python
# One call runs entire pipeline
build_feature("Add CSV export", "my_project")
```

Currently, calling `build_feature()` will return an error message explaining that sampling is not supported and directing you to use the manual workflow.

## Available Tools

### Manual Workflow Tools (OpenCode Compatible)

#### `get_next_step(project_name: str)`

Returns the next agent to run and the complete prompts for the LLM.

**Input:**
```json
{
  "project_name": "my_project"
}
```

**Output:**
```json
{
  "status": "ready",
  "agent": "Explorer",
  "reason": "Need initial feature analysis",
  "system_prompt": "You are the Analyst...",
  "user_prompt": "Analyze: ...",
  "expected_keys": ["user_needs", "constraints", "dependencies", "risks"]
}
```

#### `execute_<agent>(project_name: str, llm_response: str)`

Executes a specific agent with the LLM's response.

**Input:**
```json
{
  "project_name": "my_project",
  "llm_response": "{\"user_needs\": \"...\", ...}"
}
```

**Output:**
```json
{
  "status": "success",
  "agent": "Explorer",
  "artifact_id": "exploration_1234567890",
  "message": "Explorer completed successfully."
}
```

### Utility Tools

#### `list_workspace_files(path: str = ".")`

Lists all files in the project workspace.

#### `read_workspace_file(path: str)`

Reads the contents of a file from the project workspace.

### Deprecated Tools

#### `build_feature(feature_request: str, project_name: str)` [DEPRECATED]

Requires MCP sampling support (not available in OpenCode). Returns error message directing to manual workflow.

## Documentation

- **[WORKFLOW_MANUAL.md](WORKFLOW_MANUAL.md)** - Complete manual workflow guide with examples
- **[AGENTS.md](AGENTS.md)** - Developer guide and code style guidelines
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical implementation details

## Example: Quick Start with OpenCode

```python
# 1. Initialize and get first agent
result = get_next_step("csv_export")
# Returns: Explorer agent with prompts

# 2. Send prompts to LLM (OpenCode does this automatically)
# LLM returns: {"user_needs": "...", "constraints": [], ...}

# 3. Execute Explorer
result = execute_explorer(
    "csv_export",
    "Add CSV export functionality",
    '{"user_needs": "Export data as CSV", "constraints": [], "dependencies": ["csv library"], "risks": []}'
)
# Returns: Success with artifact_id

# 4. Continue to next agent
result = get_next_step("csv_export")
# Returns: Proposal agent with prompts

# ... repeat for all 8 agents ...
```

## Troubleshooting

### "Sampling not supported" Error

If you see this error from `build_feature()`, you're using an MCP client without sampling support (like OpenCode). Use the manual workflow instead - see [WORKFLOW_MANUAL.md](WORKFLOW_MANUAL.md).

### "Invalid response" or "Missing required keys"

The LLM response didn't include all required fields. Check the `expected_keys` from `get_next_step()` and ensure your LLM response includes them all.

### Files Not Being Written

Ensure you're using the correct `execute_*` tool and that the LLM response includes a `files` array with `path` and `content` for each file.

## Project Structure

```
devhive/
├── devhive/
│   ├── agents/          # 8 specialized agents
│   ├── core/            # Core infrastructure
│   │   ├── llm.py              # LLM wrapper (requires sampling)
│   │   ├── prompt_builder.py   # Prompt generation
│   │   ├── project_state_manager.py
│   │   └── artifact_manager.py
│   ├── utils/           # Utilities
│   │   ├── filesystem.py
│   │   └── validation.py       # Response validation
│   └── server.py        # MCP server with all tools
├── WORKFLOW_MANUAL.md   # Manual workflow guide
├── AGENTS.md           # Developer guide
└── README_MCP.md       # This file
```

## Getting Help

- See [WORKFLOW_MANUAL.md](WORKFLOW_MANUAL.md) for step-by-step instructions
- See [AGENTS.md](AGENTS.md) for development guidelines
- Report issues on GitHub (if available)

## License

[Your license here]
