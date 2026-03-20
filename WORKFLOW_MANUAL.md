# DevHive Manual Workflow Guide

**For OpenCode and other MCP clients without sampling support**

This guide explains how to use DevHive's AI development team through manual step-by-step execution.

## Overview

DevHive orchestrates an AI development team through 8 specialized agents in a sequential pipeline:

```
Explorer → Proposal → Architect → TaskPlanner → Developer → QA → Auditor → Archivist
```

Since OpenCode doesn't yet support MCP sampling (automatic LLM calls), you'll manually:
1. Get prompts from DevHive
2. Send them to your LLM
3. Return the response back to DevHive
4. Repeat for each agent

## Quick Start

### 1. Start Your Project

Call `get_next_step()` with your project name:

```python
get_next_step("my_csv_exporter")
```

**Response:**
```json
{
  "status": "ready",
  "agent": "Explorer",
  "reason": "Need initial feature analysis and exploration",
  "system_prompt": "You are the Analyst (Explorer). Output JSON only.",
  "user_prompt": "Analyze the following feature request: ...",
  "expected_keys": ["user_needs", "constraints", "dependencies", "risks"]
}
```

### 2. Send Prompts to LLM

OpenCode automatically sends the `system_prompt` and `user_prompt` to your selected LLM.

The LLM responds with JSON (the structure you need is in `expected_keys`).

### 3. Execute the Agent

Call the appropriate `execute_*` tool with the LLM's response:

```python
execute_explorer(
    "my_csv_exporter",
    "Add CSV export to analytics dashboard",
    '{"user_needs": "Users need to export data in CSV format", ...}'
)
```

**Response:**
```json
{
  "status": "success",
  "agent": "Explorer",
  "artifact_id": "exploration_1710875432",
  "message": "Explorer completed successfully. Call get_next_step() to continue."
}
```

### 4. Continue to Next Agent

Call `get_next_step()` again:

```python
get_next_step("my_csv_exporter")
```

Returns prompts for the next agent (Proposal).

### 5. Repeat Until Complete

Continue the cycle until `get_next_step()` returns:

```json
{
  "status": "complete",
  "message": "All pipeline stages finished, project is complete"
}
```

---

## Complete Agent Pipeline

### 1. Explorer Agent

**Purpose:** Initial feature analysis

**Call:**
```python
get_next_step("project_name")
# Returns Explorer prompts

execute_explorer("project_name", "feature requirements", llm_response)
```

**Expected LLM Response Structure:**
```json
{
  "user_needs": "Description of what users need",
  "constraints": ["Technical constraints", "Business constraints"],
  "dependencies": ["Required libraries", "External services"],
  "risks": ["Potential issues", "Challenges"]
}
```

---

### 2. Proposal Agent

**Purpose:** Create feature proposal

**Call:**
```python
get_next_step("project_name")
# Returns Proposal prompts

execute_proposal("project_name", llm_response)
```

**Expected LLM Response Structure:**
```json
{
  "feature_description": "Detailed feature description",
  "user_value": "Value provided to users",
  "acceptance_criteria": ["Criterion 1", "Criterion 2"],
  "scope": "What's in and out of scope"
}
```

---

### 3. Architect Agent

**Purpose:** Design technical architecture

**Call:**
```python
get_next_step("project_name")
# Returns Architect prompts

execute_architect("project_name", llm_response)
```

**Expected LLM Response Structure:**
```json
{
  "architecture_pattern": "MVC / Microservices / etc.",
  "components": ["Component1", "Component2"],
  "data_models": ["Model1", "Model2"],
  "apis": ["API endpoint specifications"]
}
```

---

### 4. TaskPlanner Agent

**Purpose:** Break down into development tasks

**Call:**
```python
get_next_step("project_name")
# Returns TaskPlanner prompts

execute_task_planner("project_name", llm_response)
```

**Expected LLM Response Structure:**
```json
{
  "epics": ["Epic 1", "Epic 2"],
  "tasks": [
    {"name": "Task 1", "description": "Details"},
    {"name": "Task 2", "description": "Details"}
  ],
  "estimated_complexity": "low/medium/high"
}
```

---

### 5. Developer Agent

**Purpose:** Implement the feature and write code files

**Call:**
```python
get_next_step("project_name")
# Returns Developer prompts

execute_developer("project_name", llm_response)
```

**Expected LLM Response Structure:**
```json
{
  "implementation_strategy": "High-level strategy",
  "file_structure": ["file1.py", "file2.py"],
  "pseudocode": "Brief implementation notes",
  "files": [
    {
      "path": "src/services/csv_generator.py",
      "content": "actual Python code here"
    }
  ]
}
```

**Note:** This agent **writes actual files** to the workspace!

---

### 6. QA Agent

**Purpose:** Generate tests and write test files

**Call:**
```python
get_next_step("project_name")
# Returns QA prompts

execute_qa("project_name", llm_response)
```

**Expected LLM Response Structure:**
```json
{
  "test_strategy": "Overall testing approach",
  "unit_tests": ["test_csv_generation", "test_export"],
  "validation_plan": "How to validate the feature",
  "files": [
    {
      "path": "tests/test_csv_generator.py",
      "content": "actual test code here"
    }
  ]
}
```

**Note:** This agent **writes actual test files** to the workspace!

---

### 7. Auditor Agent

**Purpose:** Verify project consistency and completeness

**Call:**
```python
get_next_step("project_name")
# Returns Auditor prompts

execute_auditor("project_name", llm_response)
```

**Expected LLM Response Structure:**
```json
{
  "architecture_consistency": true,
  "missing_pieces": ["List of missing components"],
  "security_risks": ["Potential security issues"]
}
```

---

### 8. Archivist Agent

**Purpose:** Archive completed project

**Call:**
```python
get_next_step("project_name")
# Returns Archivist info (no LLM needed)

execute_archivist("project_name")
```

**Note:** No LLM response needed! This agent just marks the project complete.

---

## Error Handling

### Validation Errors

If the LLM response doesn't match the expected structure, you'll get:

```json
{
  "status": "error",
  "message": "Invalid response: Missing required keys: user_needs, constraints",
  "expected_keys": ["user_needs", "constraints", "dependencies", "risks"]
}
```

**Solution:** Fix the LLM response to include all required keys and retry the same `execute_*` call.

### JSON Parsing Errors

If the response isn't valid JSON:

```json
{
  "status": "error",
  "message": "Invalid JSON response: Expecting value: line 1 column 1 (char 0)"
}
```

**Solution:** Ensure the LLM response is valid JSON. DevHive can handle markdown code blocks:

```markdown
```json
{"user_needs": "..."}
```
```

### File Writing Errors

If Developer or QA agents fail to write files:

```json
{
  "status": "error",
  "message": "Access denied: Path is outside workspace root"
}
```

**Solution:** Ensure file paths are relative and within the project workspace.

---

## Tips & Best Practices

### 1. Keep Track of Your Project State

You can check the current state anytime:

```python
read_workspace_file("project_name/project_state.json")
```

### 2. Inspect Generated Files

```python
list_workspace_files("project_name")
read_workspace_file("project_name/src/file.py")
```

### 3. Artifacts Are Saved Automatically

Each agent saves its output as an artifact:
- Location: `project_name/artifacts/`
- Format: `<step_name>_<timestamp>.json`
- Also includes summary: `<artifact_id>_summary.json`

### 4. Pipeline is Strictly Sequential

You must complete agents in order:
1. Explorer
2. Proposal
3. Architect
4. TaskPlanner
5. Developer
6. QA
7. Auditor
8. Archivist

You cannot skip agents. `get_next_step()` enforces this order.

### 5. LLM Responses Can Include Extra Keys

The validation only checks for **required** keys. The LLM can include additional information.

### 6. Developer and QA Write Real Files

When Developer and QA execute, they write actual code/test files to disk. Make sure:
- File paths are valid
- Content is properly formatted
- You review generated code before running it

---

## Troubleshooting

### "Missing required keys" Error

**Problem:** LLM didn't include all required keys in response.

**Solution:** Check the `expected_keys` from `get_next_step()` and ensure LLM includes them all.

### "Invalid JSON response" Error

**Problem:** LLM response isn't valid JSON.

**Solution:** 
- Ensure LLM outputs JSON only
- Remove any extra text before/after JSON
- Markdown code blocks are OK (DevHive handles them)

### "Agent already completed" or Wrong Agent

**Problem:** Trying to execute an agent that's already done or out of order.

**Solution:** Always call `get_next_step()` first to see which agent should run next.

### Files Not Being Written

**Problem:** Developer/QA execution succeeds but no files appear.

**Solution:**
- Check the `files_written` field in the response
- Verify files are in the workspace: `list_workspace_files("project_name")`
- Ensure `files` array in LLM response has correct `path` and `content` fields

### Project State Issues

**Problem:** Project state seems corrupted or incorrect.

**Solution:**
- Check state file: `read_workspace_file("project_name/project_state.json")`
- If needed, delete project directory and start over
- State is automatically initialized on first `get_next_step()` call

---

## Example: Complete Walkthrough

Let's build a CSV export feature:

```python
# Step 1: Start project
get_next_step("csv_export")
# Agent: Explorer

# Step 2: Execute Explorer
execute_explorer(
    "csv_export",
    "Add CSV export to dashboard",
    '{"user_needs": "Users need CSV export", "constraints": [], "dependencies": ["csv library"], "risks": []}'
)
# Success!

# Step 3: Continue
get_next_step("csv_export")
# Agent: Proposal

# Step 4: Execute Proposal
execute_proposal(
    "csv_export",
    '{"feature_description": "CSV export button", "user_value": "Data portability", "acceptance_criteria": ["Button visible"], "scope": "Basic CSV only"}'
)
# Success!

# Step 5: Continue
get_next_step("csv_export")
# Agent: Architect

# ... continue through all 8 agents ...

# Step N: Final step
get_next_step("csv_export")
# Agent: Archivist

execute_archivist("csv_export")
# Success! Project complete!

# Step N+1: Verify completion
get_next_step("csv_export")
# {"status": "complete", "message": "All pipeline stages finished"}
```

---

## Advanced Usage

### Multiple Projects

You can run multiple projects simultaneously. Each project is isolated by name:

```python
get_next_step("project_a")  # Independent
get_next_step("project_b")  # Independent
```

### Inspecting Artifacts

Each agent creates detailed artifacts you can inspect:

```python
# List all artifacts
list_workspace_files("project_name/artifacts")

# Read specific artifact
read_workspace_file("project_name/artifacts/exploration_1234567890.json")

# Read summary (lighter weight)
read_workspace_file("project_name/artifacts/exploration_1234567890_summary.json")
```

### Custom Requirements for Explorer

The Explorer agent needs the feature requirements. Provide them when executing:

```python
execute_explorer(
    "project_name",
    "Detailed feature requirements go here...",
    llm_response
)
```

---

## Migration to Automatic Mode

When OpenCode adds sampling support, you can switch to the automatic `build_feature()` tool:

```python
# Future: When sampling is supported
build_feature("Add CSV export", "project_name")
# Runs entire pipeline automatically!
```

Until then, use the manual workflow described in this guide.

---

## Getting Help

- **AGENTS.md** - Code style guidelines for developers
- **README_MCP.md** - MCP server setup and configuration
- **Project Issues** - Report bugs or request features

---

## Summary

Manual workflow in 3 steps:

1. **Get prompts**: `get_next_step(project_name)`
2. **Get LLM response**: OpenCode handles this
3. **Execute agent**: `execute_<agent>(project_name, llm_response)`

Repeat until complete. Each agent validates its input and saves artifacts automatically.

Happy building! 🚀
