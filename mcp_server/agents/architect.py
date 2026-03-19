import json
from mcp.server.fastmcp import Context
from mcp_server.agents.base_agent import BaseAgent

class ArchitectAgent(BaseAgent):
    role = "Architect"
    async def execute(self, ctx: Context, **kwargs) -> str:
        context = self.get_context()
        sys_prompt = "You are the Tech Lead. Output JSON only."
        user_prompt = f"""Design architecture.
Context: {json.dumps(context, default=str)}
Return JSON with keys: architecture_pattern, components, data_models, apis."""
        
        resp = await self._call_llm(ctx, sys_prompt, user_prompt)
        data = self._parse_json(resp)
        return self.save_artifact("architecture", data)
