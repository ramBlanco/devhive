import json
from typing import Dict, Any
from mcp.server.fastmcp import Context
from devhive.agents.base_agent import BaseAgent
from devhive.core.project_state_manager import ProjectStateManager

class CEOAgent(BaseAgent):
    role = "CEO"
    
    def get_next_agent_deterministic(self) -> Dict[str, Any]:
        """
        Determine next agent to run based on current state (no LLM needed).
        This is a rule-based decision making process following the strict pipeline sequence.
        
        Pipeline order:
        1. Explorer
        2. Proposal
        3. Architect
        4. TaskPlanner
        5. Developer
        6. QA
        7. Auditor
        8. Archivist
        
        Returns:
            Dict with 'agent' (role name) and 'reason' (explanation)
        """
        state = self.state_manager.get_state()
        artifacts = state.get("artifacts", {})
        
        # Check each stage in order
        if artifacts.get("exploration") is None:
            return {
                "agent": "Explorer",
                "reason": "Need initial feature analysis and exploration"
            }
            
        # Determine complexity from exploration artifact
        complexity = "high" # Default to high safety
        try:
            expl_id = artifacts.get("exploration")
            if expl_id:
                expl_data = self.artifact_manager.load_artifact(expl_id)
                complexity = expl_data.get("complexity", "high").lower()
        except Exception:
            pass # Fallback to high complexity on error
        
        # Dynamic Routing based on Complexity
        # Low: Explorer -> Developer -> QA -> Archivist
        # Medium: Explorer -> Proposal -> Developer -> QA -> Archivist
        # High: Full Suite
        
        if artifacts.get("proposal") is None:
            if complexity == "low":
                pass # Skip Proposal
            else:
                return {
                    "agent": "Proposal",
                    "reason": "Exploration complete, need feature proposal"
                }
        
        if artifacts.get("architecture") is None:
            if complexity in ["low", "medium"]:
                pass # Skip Architecture
            else:
                return {
                    "agent": "Architect",
                    "reason": "Proposal complete, need technical architecture design"
                }
        
        if artifacts.get("tasks") is None:
            if complexity in ["low", "medium"]:
                pass # Skip Task Planning
            else:
                return {
                    "agent": "TaskPlanner",
                    "reason": "Architecture complete, need task breakdown"
                }
        
        if artifacts.get("implementation") is None:
            return {
                "agent": "Developer",
                "reason": "Ready for implementation"
            }
        
        if artifacts.get("tests") is None:
            return {
                "agent": "QA",
                "reason": "Implementation complete, need tests"
            }
        
        if artifacts.get("verification") is None:
            if complexity in ["low", "medium"]:
                pass # Skip Auditor
            else:
                return {
                    "agent": "Auditor",
                    "reason": "Tests complete, need final verification"
                }
        
        if artifacts.get("archive") is None:
            return {
                "agent": "Archivist",
                "reason": "All stages complete, ready to archive project"
            }
        
        # All done
        return {
            "agent": "Complete",
            "reason": "All pipeline stages finished, project is complete"
        }
    
    async def execute(self, ctx: Context, **kwargs) -> Dict[str, Any]:
        """
        Original LLM-based decision making (requires sampling support).
        Currently not used in manual workflow.
        """
        state_manager = ProjectStateManager(self.project_name)
        state = state_manager.get_state()

        context = {
            "project_status": state.get('status'),
            "artifacts_summary": state.get("artifacts", {})
        }

        sys_prompt = """
        You are the CEO orchestrating an AI software development pipeline.

        The pipeline is strictly sequential:

        1 Explorer
        2 Proposal
        3 Architect
        4 TaskPlanner
        5 Developer
        6 QA
        7 Auditor
        8 Archivist

        Rules:

        - NEVER return Wait unless the pipeline is finished
        - ALWAYS select the next missing role
        - Each role produces an artifact

        Explorer → exploration
        Proposal → proposal
        Architect → architecture
        TaskPlanner → tasks
        Developer → implementation
        QA → tests
        Auditor → verification
        Archivist → archived

        Return JSON only:
        { "decision": "Run <Role>", "reason": "..." }
        """
        user_prompt = f"""Decide next step.

Project: {context.get('project_name')}
Status: {context.get('project_status')}
Stage: {context.get('stage')}
Artifacts: {json.dumps(context.get('artifacts_summary', {}), indent=2)}

Available Roles: Explorer, Proposal, Architect, TaskPlanner, Developer, QA, Auditor, Archivist.
Return JSON: {{ "decision": "Run <Role>", "reason": "..." }}
If finished, "Run Archivist".
If stage is "initialization", "Run Explorer"
"""
        resp = await self._call_llm(ctx, sys_prompt, user_prompt)
        return self._parse_json(resp)
