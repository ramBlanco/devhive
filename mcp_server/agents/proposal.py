import json
from typing import Dict, Any
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
    
    def generate_summary(self, data: Dict[str, Any]) -> str:
        """Generate executive summary for Proposal agent."""
        criteria_count = len(data.get("acceptance_criteria", []))
        feature_desc = data.get("feature_description", "N/A")
        # Truncate if too long
        if len(feature_desc) > 80:
            feature_desc = feature_desc[:80] + "..."
        return (
            f"Created feature proposal with {criteria_count} acceptance criteria. "
            f"Feature: {feature_desc}"
        )
