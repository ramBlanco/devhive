import time
from typing import Dict, Any, List
from mcp_server.schemas.project_models import ProjectState, HistoryEntry

def update_project_history(state: ProjectState, role: str, action: str, summary: str) -> ProjectState:
    """Helper to append a history entry."""
    entry = HistoryEntry(
        role=role,
        action=action,
        summary=summary,
        timestamp=time.time()
    )
    state.history.append(entry)
    return state

def get_project_summary(state: ProjectState) -> str:
    """Generates a concise summary of the project state for context."""
    summary = f"Project: {state.feature_request}\n"
    summary += f"Archived: {state.archived}\n"
    summary += "Status:\n"
    summary += f"- Analysis: {'Done' if state.analysis else 'Pending'}\n"
    summary += f"- Proposal: {'Done' if state.proposal else 'Pending'}\n"
    summary += f"- Architecture: {'Done' if state.architecture else 'Pending'}\n"
    summary += f"- Tasks: {'Done' if state.tasks else 'Pending'}\n"
    summary += f"- Implementation: {'Done' if state.implementation else 'Pending'}\n"
    summary += f"- Testing: {'Done' if state.testing else 'Pending'}\n"
    summary += f"- Verification: {'Done' if state.verification else 'Pending'}\n"
    
    if state.history:
        summary += "\nLast Action: " + state.history[-1].summary
        
    return summary
