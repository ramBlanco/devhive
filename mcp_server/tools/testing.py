from typing import Dict, Any, List
from mcp_server.schemas.project_models import ProjectState, TestingContent, HistoryEntry, FileContent
from mcp_server.utils.filesystem import write_file
import time

def testing_strategy(project_state: Dict[str, Any], test_strategy: str, unit_tests: List[str], validation_plan: str, test_files: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    QA Tool: Defines the testing strategy and generates test files.
    """
    try:
        state = ProjectState(**project_state)
    except Exception as e:
        return {"error": f"Invalid state: {str(e)}"}

    try:
        for file_data in test_files:
            write_file(file_data["path"], file_data["content"])
    except Exception as e:
         return {"error": f"Failed to write test files: {str(e)}"}

    file_objects = [FileContent(**f) for f in test_files]

    content = TestingContent(
        test_strategy=test_strategy,
        unit_tests=unit_tests,
        validation_plan=validation_plan,
        files=file_objects
    )
    
    state.testing = content
    state.history.append(HistoryEntry(
        role="QA",
        action="testing_strategy",
        summary=f"Defined {len(unit_tests)} unit tests and wrote {len(test_files)} test files.",
        timestamp=time.time()
    ))
    
    return state.model_dump()
