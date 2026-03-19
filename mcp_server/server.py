from typing import Dict, Any, List
from mcp.server.fastmcp import FastMCP, Context
from mcp_server.core.project_state_manager import ProjectStateManager
from mcp_server.agents import (
    ExplorerAgent, ProposalAgent, ArchitectAgent, TaskAgent,
    DeveloperAgent, QAAgent, AuditorAgent, ArchivistAgent, CEOAgent
)
from mcp_server.utils.filesystem import list_files, read_file
import sys
from pathlib import Path

# Add project root to path for imports to work correctly
sys.path.append(str(Path(__file__).resolve().parents[1]))

mcp = FastMCP("DevHive Dynamic Organization")

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

@mcp.tool()
async def build_feature(feature_request: str, project_name: str, ctx: Context) -> str:
    """
    Triggers the AI Development Team to build a feature.
    This orchestrates the entire process: Analysis -> Plan -> Code -> Test -> Archive.
    It runs in a loop, asking the CEO agent for decisions.
    """
    # 1. Initialize Project
    state_manager = ProjectStateManager(project_name)
    state = state_manager.get_state()
    
    # Simple check if new project
    if state["stage"] == "initialization":
        # we could verify if feature_request matches?
        pass

    ceo = CEOAgent(project_name)
    
    steps_log = []
    max_steps = 15 # Safety limit
    
    for i in range(max_steps):
        # CEO Decision
        # CEO execute returns dict with decision
        decision = await ceo.execute(ctx)
        
        # Parse decision - handle if it's a string (raw LLM output) or dict
        if isinstance(decision, str):
             # Try to parse if LLM returned string despite instructions
             import json
             try:
                 decision = json.loads(decision)
             except:
                 decision = {"decision": "Wait", "reason": f"Failed to parse CEO output: {decision}"}

        action = decision.get("decision", "Wait")
        reason = decision.get("reason", "No reason provided")
        
        steps_log.append(f"Step {i+1}: CEO decided '{action}' ({reason})")
        
        if isinstance(action, str) and action.startswith("Run "):
            role = action.split("Run ")[1].strip()
            
            # Special case for Archivist to stop loop
            if role == "Archivist":
                agent = get_agent("Archivist", project_name)
                res = await agent.execute(ctx)
                steps_log.append(f"Result: {res}")
                return "\n".join(steps_log)
            
            try:
                agent = get_agent(role, project_name)
                
                # Input mapping
                res = None
                if role == "Explorer":
                    # Pass the feature request
                    res = await agent.execute(ctx, requirements=feature_request)
                else:
                    # Others pull from context mainly
                    res = await agent.execute(ctx)
                    
                steps_log.append(f"Result: Success (Artifact ID: {res})")
                
            except Exception as e:
                steps_log.append(f"Result: Failed to run {role} ({str(e)})")
                # Don't break immediately, maybe CEO recovers? 
                # But typically retry logic is needed.
                # For now, let's break to avoid infinite loops of errors.
                break
        elif action == "Wait":
             steps_log.append("CEO decided to wait.")
             break
        else:
             steps_log.append(f"Unknown decision format: {action}")
             break
             
    return "\n".join(steps_log)

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
