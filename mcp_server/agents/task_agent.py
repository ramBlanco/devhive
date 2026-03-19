import json
from mcp.server.fastmcp import Context
from mcp_server.agents.base_agent import BaseAgent

class TaskAgent(BaseAgent):
    role = "TaskPlanner"
    async def execute(self, ctx: Context, **kwargs) -> str:
        context = self.get_context()
        sys_prompt = "You are the Scrum Master. Output JSON only."
        user_prompt = f"""Break down tasks.
Context: {json.dumps(context, default=str)}
Return JSON with keys: epics, tasks (list of dicts), estimated_complexity."""
        
        resp = await self._call_llm(ctx, sys_prompt, user_prompt)
        data = self._parse_json(resp)
        return self.save_artifact("tasks", data)
