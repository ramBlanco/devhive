from typing import Dict, Any, List
from mcp_server.schemas.project_models import ProjectState, ProposalContent, HistoryEntry
import time

def product_proposal(project_state: Dict[str, Any], feature_description: str, user_value: str, acceptance_criteria: List[str], scope: str) -> Dict[str, Any]:
    """
    Product Manager Tool: Creates a structured product proposal based on analysis.
    """
    try:
        state = ProjectState(**project_state)
    except Exception as e:
        return {"error": f"Invalid state: {str(e)}"}
        
    content = ProposalContent(
        feature_description=feature_description,
        user_value=user_value,
        acceptance_criteria=acceptance_criteria,
        scope=scope
    )
    
    state.proposal = content
    state.history.append(HistoryEntry(
        role="Product Manager",
        action="product_proposal",
        summary=f"Defined proposal: {feature_description[:30]}...",
        timestamp=time.time()
    ))
    
    return state.model_dump()
