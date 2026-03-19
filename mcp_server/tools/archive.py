from typing import Dict, Any, List
from mcp_server.schemas.project_models import ProjectState, HistoryEntry
from mcp_server.memory.archive_store import ArchiveStore
import time
import hashlib

# Initialize store
store = ArchiveStore()

def archive_feature(project_state: Dict[str, Any], project_summary: str) -> Dict[str, Any]:
    """
    Archivist Tool: Archives the project and marks it as complete.
    """
    try:
        state = ProjectState(**project_state)
    except Exception as e:
        return {"error": f"Invalid state: {str(e)}"}
    
    # 1. Mark as archived
    state.archived = True
    
    # 2. Add History
    state.history.append(HistoryEntry(
        role="Archivist",
        action="archive_feature",
        summary="Project archived.",
        timestamp=time.time()
    ))
    
    # 3. Generate ID and Save
    feature_id = hashlib.md5(f"{state.feature_request}{time.time()}".encode()).hexdigest()
    
    archive_data = {
        "id": feature_id,
        "summary": project_summary,
        "final_state": state.model_dump()
    }
    
    store.save(feature_id, archive_data)
    
    return {
        "status": "archived",
        "feature_id": feature_id,
        "final_state": state.model_dump(),
        "message": "Project successfully archived."
    }
