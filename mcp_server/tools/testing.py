from typing import Dict, Any, List
from mcp_server.schemas.project_models import ProjectState, TestingContent, HistoryEntry
import time

def testing_strategy(project_state: Dict[str, Any], test_strategy: str, unit_tests: List[str], validation_plan: str) -> Dict[str, Any]:
    """
    QA Tool: Defines the testing strategy.
    """
    try:
        state = ProjectState(**project_state)
    except Exception as e:
        return {"error": f"Invalid state: {str(e)}"}

    content = TestingContent(
        test_strategy=test_strategy,
        unit_tests=unit_tests,
        validation_plan=validation_plan
    )
    
    state.testing = content
    state.history.append(HistoryEntry(
        role="QA",
        action="testing_strategy",
        summary=f"Defined {len(unit_tests)} unit tests and strategy.",
        timestamp=time.time()
    ))
    
    return state.model_dump()
