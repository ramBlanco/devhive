from typing import Dict, Any, List
from mcp_server.schemas.project_models import ProjectState, HistoryEntry
from mcp_server.memory.archive_store import ArchiveStore
from mcp_server.utils.filesystem import append_file, list_files
import time
import hashlib
import json
import datetime

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

    # 4. Append to feature_archive.json
    # Note: Using direct file access for the archive log at project root, bypassing workspace sandbox for this specific file
    from pathlib import Path
    
    archive_path = Path("feature_archive.json").resolve()
    
    existing_data = []
    if archive_path.exists():
        try:
            with open(archive_path, "r") as f:
                existing_data = json.load(f)
        except:
            pass
            
    if not isinstance(existing_data, list):
        existing_data = []
        
    # Generate entry
    generated_files = list_files()
    agents_used = list(set([h.role for h in state.history]))

    archive_entry = {
        "project": state.feature_request,
        "agents_used": agents_used,
        "files_generated": len(generated_files),
        "timestamp": datetime.datetime.now().isoformat(),
        "status": "completed",
        "feature_id": feature_id
    }
    
    existing_data.append(archive_entry)
    
    with open(archive_path, "w") as f:
        json.dump(existing_data, f, indent=2)
    
    return {
        "status": "archived",
        "feature_id": feature_id,
        "final_state": state.model_dump(),
        "message": "Project successfully archived."
    }
