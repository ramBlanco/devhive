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
python3 -m mcp_server.server
```

This starts the server on stdio, ready to be connected to an MCP client like Claude Desktop or Cursor.

## Connecting to Claude Desktop

To use this with Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "devhive": {
      "command": "python3",
      "args": [
        "-m",
        "mcp_server.server"
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

## Available Tools

### `build_feature`

Executes the internal AI development team pipeline.

**Input Schema:**
```json
{
  "feature_request": "string"
}
```

**Example Usage:**
```json
{
  "feature_request": "Add CSV export to dashboard"
}
```

**Output:**
Returns a structured JSON object containing:
- `analysis` (from Explorer Agent)
- `architecture` (from Architect Agent)
- `implementation_plan` (from Implementer Agent)
