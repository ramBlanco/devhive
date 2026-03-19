from typing import Dict, Any, List
from mcp_server.schemas.project_models import ProjectState, VerificationContent, HistoryEntry
import time

def verification_report(project_state: Dict[str, Any], architecture_consistency: bool, missing_pieces: List[str], security_risks: List[str]) -> Dict[str, Any]:
    """
    Auditor Tool: Verifies the project for risks and consistency.
    """
    try:
        state = ProjectState(**project_state)
    except Exception as e:
        return {"error": f"Invalid state: {str(e)}"}

    content = VerificationContent(
        architecture_consistency=architecture_consistency,
        missing_pieces=missing_pieces,
        security_risks=security_risks
    )
    
    state.verification = content
    state.history.append(HistoryEntry(
        role="Auditor",
        action="verification_report",
        summary=f"Audit complete. Consistent: {architecture_consistency}.",
        timestamp=time.time()
    ))
    
    return state.model_dump()
