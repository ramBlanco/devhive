import json
from mcp.server.fastmcp import Context
from mcp_server.agents.base_agent import BaseAgent

class ArchivistAgent(BaseAgent):
    role = "Archivist"
    async def execute(self, ctx: Context, **kwargs) -> str:
        state = self.state_manager.get_state()
        state["status"] = "completed"
        if "artifacts" not in state: state["artifacts"] = {}
        state["artifacts"]["archive"] = "archived"
        self.state_manager.update_state(state)
        return "Project Archived Successfully"
