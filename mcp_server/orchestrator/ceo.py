from typing import Dict, Any, List
from mcp_server.schemas.project_models import ProjectState
from mcp_server.orchestrator.project_state import get_project_summary

def ceo_decision_logic(project_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes the project state and recommends the next best action.
    """
    
    # Simple validation - ensure we have a valid state structure
    try:
        state = ProjectState(**project_state)
    except Exception as e:
        return {
            "error": f"Invalid project state: {str(e)}",
            "recommended_next_roles": ["explorer_analysis"], # Fallback
            "reason": "Could not parse state, assuming start of project."
        }

    recommendations = []
    reason = ""
    status = "in_progress"

    if state.archived:
        status = "completed"
        reason = "Project is already archived."
        recommendations = []
    
    elif not state.analysis:
        status = "analysis_missing"
        recommendations = ["explorer_analysis"]
        reason = "The feature request has not been analyzed yet. We need to understand requirements first."
        
    elif not state.proposal:
        status = "proposal_missing"
        recommendations = ["product_proposal"]
        reason = "Analysis is done. We need a concrete product proposal now."
        
    elif not state.architecture:
        status = "architecture_missing"
        recommendations = ["architecture_design"]
        reason = "Product proposal is ready. We need a technical architecture design."
        
    elif not state.tasks:
        status = "tasks_missing"
        recommendations = ["task_breakdown"]
        reason = "Architecture is defined. We need to break it down into actionable tasks."
        
    elif not state.implementation:
        status = "implementation_missing"
        recommendations = ["implementation_plan"]
        reason = "Tasks are ready. We need an implementation plan and code structure."
        
    elif not state.testing:
        status = "testing_missing"
        recommendations = ["testing_strategy"]
        reason = "Implementation plan is ready. We need a testing strategy."
        
    elif not state.verification:
        status = "verification_missing"
        recommendations = ["verification_report"]
        reason = "Testing strategy is ready. We need a final audit/verification before archiving."
        
    else:
        status = "ready_to_archive"
        recommendations = ["archive_feature"]
        reason = "All steps are complete. The project is ready to be archived."

    return {
        "project_status": status,
        "recommended_next_roles": recommendations,
        "reason": reason,
        "project_state_summary": get_project_summary(state),
        "available_roles": [
            "explorer_analysis",
            "product_proposal",
            "architecture_design",
            "task_breakdown",
            "implementation_plan",
            "testing_strategy",
            "verification_report",
            "archive_feature"
        ]
    }
