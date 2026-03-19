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
        recommendations = ["explorer_tool"]
        reason = "The feature request has not been analyzed yet. We need to understand requirements first."
        
    elif not state.proposal:
        status = "proposal_missing"
        recommendations = ["proposal_tool"]
        reason = "Analysis is done. We need a concrete product proposal now."
        
    elif not state.architecture:
        status = "architecture_missing"
        recommendations = ["architect_tool"]
        reason = "Product proposal is ready. We need a technical architecture design."
        
    elif not state.tasks:
        status = "tasks_missing"
        recommendations = ["scrum_tool"]
        reason = "Architecture is defined. We need to break it down into actionable tasks."
        
    elif not state.implementation:
        status = "implementation_missing"
        recommendations = ["developer_tool"]
        reason = "Tasks are ready. We need an implementation plan and code structure."
        
    elif not state.testing:
        status = "testing_missing"
        recommendations = ["qa_tool"]
        reason = "Implementation plan is ready. We need a testing strategy."
        
    elif not state.verification:
        status = "verification_missing"
        recommendations = ["auditor_tool"]
        reason = "Testing strategy is ready. We need a final audit/verification before archiving."
        
    else:
        # Check verification results for feedback loop
        has_issues = False
        issues_list = []
        
        if not state.verification.architecture_consistency:
            has_issues = True
            issues_list.append("Architecture inconsistency detected")
            
        if state.verification.missing_pieces:
            has_issues = True
            issues_list.append(f"Missing pieces: {', '.join(state.verification.missing_pieces)}")
            
        if state.verification.security_risks:
            has_issues = True
            issues_list.append(f"Security risks: {', '.join(state.verification.security_risks)}")

        if has_issues:
            status = "verification_failed"
            # Loop back to implementation to fix issues
            recommendations = ["developer_tool"] 
            reason = f"Verification failed. Issues found: {'; '.join(issues_list)}. Rerunning implementation to fix."
        else:
            status = "ready_to_archive"
            recommendations = ["archivist_tool"]
            reason = "All steps are complete and verified. The project is ready to be archived."

    return {
        "project_status": status,
        "recommended_next_roles": recommendations,
        "reason": reason,
        "project_state_summary": get_project_summary(state),
        "available_roles": [
            "explorer_tool",
            "proposal_tool",
            "architect_tool",
            "scrum_tool",
            "developer_tool",
            "qa_tool",
            "auditor_tool",
            "archivist_tool"
        ]
    }
