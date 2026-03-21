import json
from typing import Dict, Any
from mcp.server.fastmcp import Context
from mcp_server.agents.base_agent import BaseAgent

class ExplorerAgent(BaseAgent):
    role = "Explorer"
    
    async def execute(self, ctx: Context, **kwargs) -> str:
        requirements = kwargs.get("requirements", "")
        context = self.get_context()
        sys_prompt = """
        You are the Analyst (Explorer). Remember always read AGENTS.md or GUIDELINES.md if exists. 
        
        Output JSON only.
        """
        user_prompt = f"""Analyze: {requirements}
Context: {json.dumps(context, default=str)}
Return JSON with keys: user_needs, constraints, dependencies, risks."""
        
        resp = await self._call_llm(ctx, sys_prompt, user_prompt)
        data = self._parse_json(resp)
        return self.save_artifact("exploration", data)
    
    def generate_summary(self, data: Dict[str, Any]) -> str:
        """Generate executive summary for Explorer agent."""
        constraints_count = len(data.get("constraints", []))
        deps_count = len(data.get("dependencies", []))
        user_needs = data.get("user_needs", "N/A")
        # Truncate user_needs if too long
        if len(user_needs) > 80:
            user_needs = user_needs[:80] + "..."
        return (
            f"Analyzed requirements and identified {constraints_count} constraints "
            f"and {deps_count} dependencies. Key user need: {user_needs}"
        )
