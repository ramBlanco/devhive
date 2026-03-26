import json
from typing import Dict, Any
from mcp.server.fastmcp import Context
from devhive.agents.base_agent import BaseAgent

class ArchivistAgent(BaseAgent):
    role = "Archivist"
    async def execute(self, ctx: Context, **kwargs) -> str:
        state = self.state_manager.get_state()
        state["status"] = "completed"
        if "artifacts" not in state: state["artifacts"] = {}
        state["artifacts"]["archive"] = "archived"
        self.state_manager.update_state(state)
        return "Project Archived Successfully"
    
    def generate_summary(self, data: Dict[str, Any]) -> str:
        """Generate executive summary for Archivist agent."""
        # Archivist doesn't use structured data, just returns success message
        return "Project archived successfully. All artifacts and state preserved."
