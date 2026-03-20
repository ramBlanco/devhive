import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List

from mcp.server.fastmcp import FastMCP, Context
from mcp_server.core.project_state_manager import ProjectStateManager
from mcp_server.core.prompt_builder import PromptBuilder
from mcp_server.utils.validation import ResponseValidator
from mcp_server.utils.filesystem import list_files, read_file, write_file
from mcp_server.agents import (
    ExplorerAgent, ProposalAgent, ArchitectAgent, TaskAgent,
    DeveloperAgent, QAAgent, AuditorAgent, ArchivistAgent, CEOAgent
)

# Add project root to path for imports to work correctly
sys.path.append(str(Path(__file__).resolve().parents[1]))

mcp = FastMCP("DevHive Dynamic Organization")

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Agents
def get_agent(role: str, project_name: str):
    if role == "Explorer": return ExplorerAgent(project_name)
    if role == "Proposal": return ProposalAgent(project_name)
    if role == "Architect": return ArchitectAgent(project_name)
    if role == "TaskPlanner": return TaskAgent(project_name)
    if role == "Developer": return DeveloperAgent(project_name)
    if role == "QA": return QAAgent(project_name)
    if role == "Auditor": return AuditorAgent(project_name)
    if role == "Archivist": return ArchivistAgent(project_name)
    if role == "CEO": return CEOAgent(project_name)
    raise ValueError(f"Unknown role: {role}")

def _parse_json_response(text: str) -> Dict[str, Any]:
    """Helper to parse JSON from LLM response, handling markdown code blocks"""
    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        raise ValueError(f"Invalid JSON response: {e}")

# ============================================================================
# MANUAL WORKFLOW TOOLS (OpenCode Compatible - No Sampling Required)
# ============================================================================

@mcp.tool()
def get_next_step(project_name: str) -> str:
    """
    Returns the next agent to run and the prompts to send to LLM.
    
    This tool determines which agent should execute next based on the current
    project state. It returns the complete system and user prompts that should
    be sent to the LLM.
    
    Args:
        project_name: Project identifier
    
    Returns:
        JSON string with:
        - agent: The agent role name (Explorer, Proposal, etc.)
        - reason: Why this agent needs to run
        - system_prompt: System prompt to send to LLM
        - user_prompt: User prompt to send to LLM  
        - status: Current status (ready, complete, or error)
        - expected_keys: List of keys the LLM response should contain
    """
    try:
        # Initialize project if needed
        state_manager = ProjectStateManager(project_name)
        ceo = CEOAgent(project_name)
        
        # Get next agent (deterministic, no LLM)
        decision = ceo.get_next_agent_deterministic()
        agent_role = decision["agent"]
        
        # Check if complete
        if agent_role == "Complete":
            return json.dumps({
                "status": "complete",
                "message": "All pipeline stages finished, project is complete",
                "agent": "Complete"
            }, indent=2)
        
        # Get agent instance to access context
        agent = get_agent(agent_role, project_name)
        context = agent.get_context()
        
        # Build prompts using PromptBuilder
        # For Explorer, we need to check if requirements are in kwargs
        if agent_role == "Explorer":
            # Requirements should be provided when executing Explorer
            prompts = PromptBuilder.build_prompts(agent_role, context, requirements="[Requirements will be provided when executing]")
        else:
            prompts = PromptBuilder.build_prompts(agent_role, context)
        
        # Get expected keys for validation
        expected_keys = ResponseValidator.get_expected_keys(agent_role)
        
        return json.dumps({
            "status": "ready",
            "agent": agent_role,
            "reason": decision["reason"],
            "system_prompt": prompts["system_prompt"],
            "user_prompt": prompts["user_prompt"],
            "expected_keys": expected_keys,
            "context_summary": {
                "project_name": context.get("project_name"),
                "current_stage": context.get("current_stage"),
                "files_count": context.get("files_generated_summary", 0)
            }
        }, indent=2)
        
    except Exception as e:
        logger.error(f"get_next_step failed: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, indent=2)

@mcp.tool()
def execute_explorer(project_name: str, requirements: str, llm_response: str) -> str:
    """
    Execute Explorer agent with LLM-generated response.
    
    The Explorer agent performs initial feature analysis.
    
    Args:
        project_name: Project identifier
        requirements: Original feature request/requirements
        llm_response: JSON response from LLM (can be markdown-wrapped)
    
    Returns:
        JSON with status, artifact_id, and message
    """
    try:
        agent = ExplorerAgent(project_name)
        
        # Parse and validate response
        data = _parse_json_response(llm_response)
        valid, error_msg = ResponseValidator.validate_explorer(data)
        
        if not valid:
            return json.dumps({
                "status": "error",
                "message": f"Invalid response: {error_msg}",
                "expected_keys": ResponseValidator.get_expected_keys("Explorer")
            }, indent=2)
        
        # Save artifact
        artifact_id = agent.save_artifact("exploration", data)
        
        return json.dumps({
            "status": "success",
            "agent": "Explorer",
            "artifact_id": artifact_id,
            "message": "Explorer completed successfully. Call get_next_step() to continue."
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Explorer execution failed: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, indent=2)

@mcp.tool()
def execute_proposal(project_name: str, llm_response: str) -> str:
    """
    Execute Proposal agent with LLM-generated response.
    
    The Proposal agent creates a feature proposal based on exploration.
    
    Args:
        project_name: Project identifier
        llm_response: JSON response from LLM (can be markdown-wrapped)
    
    Returns:
        JSON with status, artifact_id, and message
    """
    try:
        agent = ProposalAgent(project_name)
        
        # Parse and validate response
        data = _parse_json_response(llm_response)
        valid, error_msg = ResponseValidator.validate_proposal(data)
        
        if not valid:
            return json.dumps({
                "status": "error",
                "message": f"Invalid response: {error_msg}",
                "expected_keys": ResponseValidator.get_expected_keys("Proposal")
            }, indent=2)
        
        # Save artifact
        artifact_id = agent.save_artifact("proposal", data)
        
        return json.dumps({
            "status": "success",
            "agent": "Proposal",
            "artifact_id": artifact_id,
            "message": "Proposal completed successfully. Call get_next_step() to continue."
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Proposal execution failed: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, indent=2)

@mcp.tool()
def execute_architect(project_name: str, llm_response: str) -> str:
    """
    Execute Architect agent with LLM-generated response.
    
    The Architect agent designs the technical architecture.
    
    Args:
        project_name: Project identifier
        llm_response: JSON response from LLM (can be markdown-wrapped)
    
    Returns:
        JSON with status, artifact_id, and message
    """
    try:
        agent = ArchitectAgent(project_name)
        
        # Parse and validate response
        data = _parse_json_response(llm_response)
        valid, error_msg = ResponseValidator.validate_architect(data)
        
        if not valid:
            return json.dumps({
                "status": "error",
                "message": f"Invalid response: {error_msg}",
                "expected_keys": ResponseValidator.get_expected_keys("Architect")
            }, indent=2)
        
        # Save artifact
        artifact_id = agent.save_artifact("architecture", data)
        
        return json.dumps({
            "status": "success",
            "agent": "Architect",
            "artifact_id": artifact_id,
            "message": "Architect completed successfully. Call get_next_step() to continue."
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Architect execution failed: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, indent=2)

@mcp.tool()
def execute_task_planner(project_name: str, llm_response: str) -> str:
    """
    Execute TaskPlanner agent with LLM-generated response.
    
    The TaskPlanner agent breaks down the feature into development tasks.
    
    Args:
        project_name: Project identifier
        llm_response: JSON response from LLM (can be markdown-wrapped)
    
    Returns:
        JSON with status, artifact_id, and message
    """
    try:
        agent = TaskAgent(project_name)
        
        # Parse and validate response
        data = _parse_json_response(llm_response)
        valid, error_msg = ResponseValidator.validate_task_planner(data)
        
        if not valid:
            return json.dumps({
                "status": "error",
                "message": f"Invalid response: {error_msg}",
                "expected_keys": ResponseValidator.get_expected_keys("TaskPlanner")
            }, indent=2)
        
        # Save artifact
        artifact_id = agent.save_artifact("tasks", data)
        
        return json.dumps({
            "status": "success",
            "agent": "TaskPlanner",
            "artifact_id": artifact_id,
            "message": "TaskPlanner completed successfully. Call get_next_step() to continue."
        }, indent=2)
        
    except Exception as e:
        logger.error(f"TaskPlanner execution failed: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, indent=2)

@mcp.tool()
def execute_developer(project_name: str, llm_response: str) -> str:
    """
    Execute Developer agent with LLM-generated response.
    
    The Developer agent implements the feature and writes code files.
    
    Args:
        project_name: Project identifier
        llm_response: JSON response from LLM (can be markdown-wrapped)
    
    Returns:
        JSON with status, artifact_id, files written, and message
    """
    try:
        agent = DeveloperAgent(project_name)
        
        # Parse and validate response
        data = _parse_json_response(llm_response)
        valid, error_msg = ResponseValidator.validate_developer(data)
        
        if not valid:
            return json.dumps({
                "status": "error",
                "message": f"Invalid response: {error_msg}",
                "expected_keys": ResponseValidator.get_expected_keys("Developer")
            }, indent=2)
        
        # Write files
        files = data.get("files", [])
        file_paths = []
        for f in files:
            if isinstance(f, dict) and "path" in f and "content" in f:
                write_file(f["path"], f["content"])
                file_paths.append(f["path"])
        
        agent.state_manager.add_files(file_paths)
        
        # Save artifact
        artifact_id = agent.save_artifact("implementation", data)
        
        return json.dumps({
            "status": "success",
            "agent": "Developer",
            "artifact_id": artifact_id,
            "files_written": file_paths,
            "message": f"Developer completed successfully. Wrote {len(file_paths)} files. Call get_next_step() to continue."
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Developer execution failed: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, indent=2)

@mcp.tool()
def execute_qa(project_name: str, llm_response: str) -> str:
    """
    Execute QA agent with LLM-generated response.
    
    The QA agent generates tests and writes test files.
    
    Args:
        project_name: Project identifier
        llm_response: JSON response from LLM (can be markdown-wrapped)
    
    Returns:
        JSON with status, artifact_id, test files written, and message
    """
    try:
        agent = QAAgent(project_name)
        
        # Parse and validate response
        data = _parse_json_response(llm_response)
        valid, error_msg = ResponseValidator.validate_qa(data)
        
        if not valid:
            return json.dumps({
                "status": "error",
                "message": f"Invalid response: {error_msg}",
                "expected_keys": ResponseValidator.get_expected_keys("QA")
            }, indent=2)
        
        # Write test files
        files = data.get("files", [])
        file_paths = []
        for f in files:
            if isinstance(f, dict) and "path" in f and "content" in f:
                write_file(f["path"], f["content"])
                file_paths.append(f["path"])
        
        agent.state_manager.add_files(file_paths)
        
        # Save artifact
        artifact_id = agent.save_artifact("tests", data)
        
        return json.dumps({
            "status": "success",
            "agent": "QA",
            "artifact_id": artifact_id,
            "test_files_written": file_paths,
            "message": f"QA completed successfully. Wrote {len(file_paths)} test files. Call get_next_step() to continue."
        }, indent=2)
        
    except Exception as e:
        logger.error(f"QA execution failed: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, indent=2)

@mcp.tool()
def execute_auditor(project_name: str, llm_response: str) -> str:
    """
    Execute Auditor agent with LLM-generated response.
    
    The Auditor agent verifies project consistency and completeness.
    
    Args:
        project_name: Project identifier
        llm_response: JSON response from LLM (can be markdown-wrapped)
    
    Returns:
        JSON with status, artifact_id, and message
    """
    try:
        agent = AuditorAgent(project_name)
        
        # Parse and validate response
        data = _parse_json_response(llm_response)
        valid, error_msg = ResponseValidator.validate_auditor(data)
        
        if not valid:
            return json.dumps({
                "status": "error",
                "message": f"Invalid response: {error_msg}",
                "expected_keys": ResponseValidator.get_expected_keys("Auditor")
            }, indent=2)
        
        # Save artifact
        artifact_id = agent.save_artifact("verification", data)
        
        return json.dumps({
            "status": "success",
            "agent": "Auditor",
            "artifact_id": artifact_id,
            "architecture_consistent": data.get("architecture_consistency"),
            "message": "Auditor completed successfully. Call get_next_step() to continue."
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Auditor execution failed: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, indent=2)

@mcp.tool()
def execute_archivist(project_name: str) -> str:
    """
    Execute Archivist agent to archive the completed project.
    
    The Archivist agent marks the project as complete. No LLM needed.
    
    Args:
        project_name: Project identifier
    
    Returns:
        JSON with status and message
    """
    try:
        agent = ArchivistAgent(project_name)
        
        # Archivist doesn't need LLM, just updates state
        state = agent.state_manager.get_state()
        state["status"] = "completed"
        if "artifacts" not in state: 
            state["artifacts"] = {}
        state["artifacts"]["archive"] = "archived"
        agent.state_manager.update_state(state)
        
        return json.dumps({
            "status": "success",
            "agent": "Archivist",
            "message": "Project archived successfully. Pipeline complete!"
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Archivist execution failed: {e}")
        return json.dumps({
            "status": "error",
            "message": str(e)
        }, indent=2)

# ============================================================================
# DEPRECATED TOOL (Requires Sampling Support)
# ============================================================================

@mcp.tool()
async def build_feature(feature_request: str, project_name: str, ctx: Context) -> str:
    """
    [DEPRECATED - Requires sampling support not available in OpenCode]
    
    This tool requires MCP client sampling support which is not yet available.
    
    Use manual workflow instead:
    1. Call get_next_step(project_name)
    2. Send prompts to LLM
    3. Call execute_<agent>(project_name, llm_response)
    4. Repeat until Archivist completes
    
    This tool is kept for future compatibility when sampling is supported.
    """
    return json.dumps({
        "error": "Sampling not supported",
        "message": "This tool requires MCP sampling support. Use manual workflow with get_next_step() and execute_* tools instead.",
        "workflow": [
            "1. Call get_next_step(project_name)",
            "2. Send returned prompts to LLM",
            "3. Call execute_<agent>(project_name, llm_response)",
            "4. Repeat steps 1-3 until complete"
        ],
        "example": {
            "step_1": "get_next_step('my_project')",
            "step_2": "# OpenCode sends prompts to LLM",
            "step_3": "execute_explorer('my_project', 'feature request', '{...llm response...}')",
            "step_4": "# Repeat"
        }
    }, indent=2)

# ============================================================================
# UTILITY TOOLS
# ============================================================================

@mcp.tool()
def list_workspace_files(path: str = ".") -> List[str]:
    """Lists files in the project workspace."""
    return list_files(path)

@mcp.tool()
def read_workspace_file(path: str) -> str:
    """Reads a file from the project workspace."""
    return read_file(path)

def main():
    mcp.run()

if __name__ == "__main__":
    main()
