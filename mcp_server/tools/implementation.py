from typing import Dict, Any, List
from mcp_server.schemas.project_models import ProjectState, ImplementationContent, HistoryEntry
import time

def implementation_plan(project_state: Dict[str, Any], implementation_strategy: str, file_structure: str, pseudocode: str) -> Dict[str, Any]:
    """
    Developer Tool: Plans the implementation details.
    """
    try:
        state = ProjectState(**project_state)
    except Exception as e:
        return {"error": f"Invalid state: {str(e)}"}

    content = ImplementationContent(
        implementation_strategy=implementation_strategy,
        file_structure=file_structure,
        pseudocode=pseudocode
    )
    
    state.implementation = content
    state.history.append(HistoryEntry(
        role="Developer",
        action="implementation_plan",
        summary="Defined implementation plan and file structure.",
        timestamp=time.time()
    ))
    
    return state.model_dump()
