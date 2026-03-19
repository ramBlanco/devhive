from typing import Dict, Any, List
from mcp_server.schemas.project_models import ProjectState, ImplementationContent, HistoryEntry, FileContent
from mcp_server.utils.filesystem import write_file
import time

def implementation_plan(project_state: Dict[str, Any], implementation_strategy: str, file_structure: str, pseudocode: str, files: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Developer Tool: Plans the implementation details and generates code.
    """
    try:
        state = ProjectState(**project_state)
    except Exception as e:
        return {"error": f"Invalid state: {str(e)}"}

    # Write files to disk
    try:
        for file_data in files:
            write_file(file_data["path"], file_data["content"])
    except Exception as e:
         return {"error": f"Failed to write files: {str(e)}"}

    file_objects = [FileContent(**f) for f in files]

    content = ImplementationContent(
        implementation_strategy=implementation_strategy,
        file_structure=file_structure,
        pseudocode=pseudocode,
        files=file_objects
    )
    
    state.implementation = content
    state.history.append(HistoryEntry(
        role="Developer",
        action="implementation_plan",
        summary=f"Implemented {len(files)} files.",
        timestamp=time.time()
    ))
    
    return state.model_dump()
