from typing import Dict, Any, List
from mcp_server.schemas.project_models import ProjectState, AnalysisContent, HistoryEntry
import time

def explorer_analysis(project_state: Dict[str, Any], user_needs: List[str], constraints: List[str], dependencies: List[str], risks: List[str]) -> Dict[str, Any]:
    """
    Analyst Tool: Records the analysis of user needs and constraints.
    """
    # 1. Parse current state
    try:
        state = ProjectState(**project_state)
    except Exception as e:
        return {"error": f"Invalid state: {str(e)}"}
    
    # 2. Create the content object from arguments
    content = AnalysisContent(
        user_needs=user_needs,
        constraints=constraints,
        dependencies=dependencies,
        risks=risks
    )
    
    # 3. Update State
    state.analysis = content
    
    # 4. Add History
    state.history.append(HistoryEntry(
        role="Analyst",
        action="explorer_analysis",
        summary=f"Completed analysis with {len(user_needs)} user needs identified.",
        timestamp=time.time()
    ))
    
    return state.model_dump()
