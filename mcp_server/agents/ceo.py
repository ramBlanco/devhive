import json
from typing import Dict, Any
from mcp.server.fastmcp import Context
from mcp_server.agents.base_agent import BaseAgent

class CEOAgent(BaseAgent):
    role = "CEO"
    async def execute(self, ctx: Context, **kwargs) -> Dict[str, Any]:
        context = self.get_context()
        sys_prompt = "You are the CEO. Output JSON only."
        user_prompt = f"""Decide next step.
Project: {context.get('project_name')}
Status: {context.get('project_status')}
Artifacts: {json.dumps(context.get('artifacts_summary', {}), indent=2)}

Available Roles: Explorer, Proposal, Architect, TaskPlanner, Developer, QA, Auditor, Archivist.
Return JSON: {{ "decision": "Run <Role>", "reason": "..." }} or {{ "decision": "Wait", ... }}
If finished, "Run Archivist".
"""
        resp = await self._call_llm(ctx, sys_prompt, user_prompt)
        return self._parse_json(resp)
