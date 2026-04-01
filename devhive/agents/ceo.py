import json
from typing import Dict, Any
from mcp.server.fastmcp import Context
from devhive.agents.base_agent import BaseAgent
from devhive.core.project_state_manager import ProjectStateManager

class CEOAgent(BaseAgent):
    role = "CEO"
    
    def get_next_agent_deterministic(self) -> Dict[str, Any]:
        """
        Determine next agent to run based on dynamic workflow_plan from the state.
        
        Returns:
            Dict with 'agent' (role name) and 'reason' (explanation)
        """
        state = self.state_manager.get_state()
        artifacts = state.get("artifacts", {})
        
        # If the CEO hasn't planned the workflow yet, run the CEO.
        if artifacts.get("workflow_plan") is None:
            return {
                "agent": "CEO",
                "reason": "Need initial workflow planning based on requirements"
            }
            
        # Get the workflow plan created by the CEO
        try:
            plan_id = artifacts.get("workflow_plan")
            plan_data = self.artifact_manager.load_artifact(plan_id)
            workflow_plan = plan_data.get("workflow_plan", [])
            # Fallback if workflow_plan is malformed
            if not workflow_plan:
                workflow_plan = ["Explorer", "Developer", "QA", "Archivist"]
        except Exception:
            # Fallback if something is broken
            workflow_plan = ["Explorer", "Developer", "QA", "Archivist"]
            
        # Map agent names to artifact keys
        mapping = {
            "Explorer": "exploration",
            "Proposal": "proposal",
            "Architect": "architecture",
            "TaskPlanner": "tasks",
            "Developer": "implementation",
            "QA": "tests",
            "Auditor": "verification",
            "Archivist": "archive"
        }
        
        # Iterate over the plan and find the first incomplete agent
        for agent in workflow_plan:
            artifact_key = mapping.get(agent)
            
            if artifact_key == "implementation":
                # Special iterative Developer logic
                if artifacts.get("implementation") is None:
                    dev_progress = state.get("developer_progress", {})
                    pending_tasks = dev_progress.get("pending_tasks", [])
                    completed_tasks = dev_progress.get("completed_tasks", [])
                    
                    if not dev_progress or pending_tasks:
                        task_count = len(pending_tasks) if pending_tasks else "tasks"
                        return {
                            "agent": "Developer",
                            "reason": f"Need to execute {task_count} pending tasks sequentially"
                        }
                    elif not pending_tasks and completed_tasks:
                        # Implementation is complete based on tasks
                        continue
                    else:
                        return {
                            "agent": "Developer",
                            "reason": "Ready for implementation"
                        }
                continue
                
            if artifacts.get(artifact_key) is None:
                return {
                    "agent": agent,
                    "reason": f"Next agent in workflow plan: {agent}"
                }
        
        # All done
        return {
            "agent": "Complete",
            "reason": "All pipeline stages in the workflow plan have finished, project is complete"
        }
    
    async def execute(self, ctx: Context, **kwargs) -> Dict[str, Any]:
        """
        CEO Agent execution logic is handled by TaskOrchestrator in the new task-based workflow.
        This legacy method is not used.
        """
        pass
