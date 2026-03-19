from typing import Dict, Any, List
from mcp_server.schemas.project_models import ProjectState, TaskContent, HistoryEntry
import time

def task_breakdown(project_state: Dict[str, Any], epics: List[str], tasks: List[Dict[str, Any]], estimated_complexity: str) -> Dict[str, Any]:
    """
    Scrum Master Tool: Breaks down the project into actionable tasks.
    """
    try:
        state = ProjectState(**project_state)
    except Exception as e:
        return {"error": f"Invalid state: {str(e)}"}

    content = TaskContent(
        epics=epics,
        tasks=tasks,
        estimated_complexity=estimated_complexity
    )
    
    state.tasks = content
    state.history.append(HistoryEntry(
        role="Scrum Master",
        action="task_breakdown",
        summary=f"Created {len(tasks)} tasks. Complexity: {estimated_complexity}",
        timestamp=time.time()
    ))
    
    return state.model_dump()
