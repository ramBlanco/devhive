from typing import Any, Dict
from ..core.agent_interface import BaseAgent

class ExplorerAgent(BaseAgent):
    """
    The ExplorerAgent analyzes the initial request.
    
    It identifies relevant components, required capabilities, and
    provides a structured analysis for the Architect.
    """

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Ensure we have a request string
        request = context.get("request", "") or "No Request"
        
        # Simulated AI logic:
        # In a real system, this would call an LLM with a prompt like:
        # "Analyze this request: {request} and list relevant files..."
        
        print(f"[Explorer] Analyzing request: '{request}'")
        
        # MVP Mock Logic: infer relevant files based on keywords
        relevant_files = []
        if "csv" in request.lower():
            relevant_files.append("utils/csv_helper.py")
        if "dashboard" in request.lower():
            relevant_files.append("views/dashboard.py")
            
        analysis = {
            "summary": f"Request to '{request}' requires changes to dashboard and data export modules.",
            "relevant_files": relevant_files,
            "complexity": "Medium",
            "required_capabilities": ["Data Handling", "UI Update"]
        }
        
        return {"explorer": analysis}
