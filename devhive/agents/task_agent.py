import json
from typing import Dict, Any
from mcp.server.fastmcp import Context
from devhive.agents.base_agent import BaseAgent

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
    
    def generate_summary(self, data: Dict[str, Any]) -> str:
        """Generate executive summary for TaskPlanner agent."""
        tasks_count = len(data.get("tasks", []))
        complexity = data.get("estimated_complexity", "N/A")
        epics_count = len(data.get("epics", [])) if isinstance(data.get("epics"), list) else 0
        return (
            f"Created {tasks_count} tasks across {epics_count} epics. "
            f"Complexity: {complexity}"
        )
