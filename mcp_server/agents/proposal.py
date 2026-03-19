import json
from mcp.server.fastmcp import Context
from mcp_server.agents.base_agent import BaseAgent

class ProposalAgent(BaseAgent):
    role = "Proposal"
    async def execute(self, ctx: Context, **kwargs) -> str:
        context = self.get_context()
        sys_prompt = "You are the Product Manager. Output JSON only."
        user_prompt = f"""Create proposal based on exploration.
Context: {json.dumps(context, default=str)}
Return JSON with keys: feature_description, user_value, acceptance_criteria, scope."""
        
        resp = await self._call_llm(ctx, sys_prompt, user_prompt)
        data = self._parse_json(resp)
        return self.save_artifact("proposal", data)
