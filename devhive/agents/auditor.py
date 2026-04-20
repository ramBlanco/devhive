import json
from typing import Dict, Any
from mcp.server.fastmcp import Context
from devhive.agents.base_agent import BaseAgent

class AuditorAgent(BaseAgent):
    role = "Auditor"
    async def execute(self, ctx: Context, **kwargs) -> str:
        context = self.get_context()
        sys_prompt = "You are the Auditor. Output JSON only."
        user_prompt = f"""Verify the project.
Context: {json.dumps(context, default=str)}
Return JSON with keys: architecture_consistency (bool), missing_pieces (list), security_risks (list)."""
        
        resp = await self._call_llm(ctx, sys_prompt, user_prompt)
        data = self._parse_json(resp)
        return self.save_artifact("verification", data)
    
