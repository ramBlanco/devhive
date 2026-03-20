import json
import logging
from typing import Dict, Any, Optional
from mcp.types import SamplingMessage, TextContent
from mcp.server.fastmcp import Context
from mcp_server.core.project_state_manager import ProjectStateManager
from mcp_server.core.artifact_manager import ArtifactManager
from mcp_server.core.context_router import ContextRouter
from mcp_server.core.llm import LLM

logger = logging.getLogger(__name__)

class BaseAgent:
    role: str = "Base"

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.state_manager = ProjectStateManager(project_name)
        self.artifact_manager = ArtifactManager(project_name)
        self.context_router = ContextRouter(self.state_manager, self.artifact_manager)

    def get_context(self) -> Dict[str, Any]:
        return self.context_router.get_context(self.role)

    def save_artifact(self, step_name: str, content: Dict[str, Any]) -> str:
        aid = self.artifact_manager.save_artifact(step_name, content)
        self.state_manager.update_artifact(step_name, aid)
        return aid

    async def _call_llm(self, ctx: Context, system_prompt: str, user_prompt: str, max_tokens: int = 2000)-> str:
        decision = await LLM.generate_json(
            ctx,
            system_prompt,
            user_prompt
        )
        return json.dumps(decision)


    async def _call_llm_old(self, ctx: Context, system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
        """Helper to call LLM via Sampling."""
        try:
            messages = [
                {"role": "user", "content": { "type": "text", "text": f"{system_prompt}\n\n{user_prompt}" }}
            ]
            
            # Using create_message which is standard
            if hasattr(ctx.session, 'create_message'):
                try:
                    result = await ctx.session.create_message(
                        messages=messages,
                        max_tokens=max_tokens,
                        system_prompt=system_prompt
                    )
                except:
                    # Retry with just user prompt if system prompt arg fails
                    result = await ctx.session.create_message(
                        messages=messages,
                        max_tokens=max_tokens
                    )

                if hasattr(result, 'content') and hasattr(result.content, 'text'):
                    return result.content.text
                return str(result)
            
            # Fallback
            if hasattr(ctx.session, 'sample'):
                 return str(await ctx.session.sample(messages=messages, max_tokens=max_tokens))
            
            return '{"error": "No sampling capability found on session"}'

        except Exception as e:
            logger.error(f"LLM Call failed: {e}")
            return json.dumps({"error": str(e)})

    def _parse_json(self, text: str) -> Dict[str, Any]:
        """ Robust JSON parser """
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        try:
            return json.loads(text)
        except:
            return {"raw_text": text}

    async def execute(self, ctx: Context, **kwargs) -> Any:
        raise NotImplementedError
