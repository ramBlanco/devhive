from typing import Dict, Any, List
from mcp_server.schemas.project_models import ProjectState, ArchitectureContent, HistoryEntry
import time

def architecture_design(project_state: Dict[str, Any], architecture_pattern: str, components: List[str], data_models: List[Dict[str, Any]], apis: List[str]) -> Dict[str, Any]:
    """
    Tech Lead Tool: Designs the technical architecture.
    """
    try:
        state = ProjectState(**project_state)
    except Exception as e:
        return {"error": f"Invalid state: {str(e)}"}

    content = ArchitectureContent(
        architecture_pattern=architecture_pattern,
        components=components,
        data_models=data_models,
        apis=apis
    )
    
    state.architecture = content
    state.history.append(HistoryEntry(
        role="Tech Lead",
        action="architecture_design",
        summary=f"Designed architecture using {architecture_pattern}",
        timestamp=time.time()
    ))
    
    return state.model_dump()
