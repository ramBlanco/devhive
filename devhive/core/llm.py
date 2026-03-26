import json
import logging
import re
from mcp.server.fastmcp import Context

logger = logging.getLogger(__name__)

class LLM:
    """
    Universal LLM wrapper for MCP.
    Uses the model currently selected in the MCP client (OpenCode, Claude Desktop, etc).
    """

    @staticmethod
    async def generate(ctx: Context, system_prompt: str, user_prompt: str, max_tokens: int = 2000):
        """
        Generate text using FastMCP's built-in sampling request.
        """
        
        # Combine system and user prompt into messages
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        messages = [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": full_prompt
                }
            }
        ]

        logger.info("LLM call starting via FastMCP request_sampling")

        try:
            # FastMCP official method: request_sampling from context
            result = await ctx.request_sampling(
                messages=messages,
                max_tokens=max_tokens
            )
            
            # Extract text from result
            text = LLM._extract_text(result)
            
            logger.info("LLM response received successfully")
            return text
            
        except AttributeError as e:
            logger.error(f"ctx.request_sampling not available: {e}")
            raise RuntimeError(
                "LLM call failed: FastMCP context does not support request_sampling. "
                "Make sure you're using FastMCP correctly and the MCP client supports sampling."
            )
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise RuntimeError(f"LLM call failed: {e}")

    # ------------------------------------------------

    @staticmethod
    def _extract_text(response):
        """Extract text from various MCP response formats"""
        
        # Handle SamplingResult/CreateMessageResult objects
        if hasattr(response, "content"):
            content = response.content
            
            # Content is a list of content blocks
            if isinstance(content, list):
                text_parts = []
                for block in content:
                    if hasattr(block, "text"):
                        text_parts.append(block.text)
                    elif isinstance(block, dict) and "text" in block:
                        text_parts.append(block["text"])
                return "".join(text_parts)
            
            # Content is a single object with text
            if hasattr(content, "text"):
                return content.text
            
            # Content is a dict
            if isinstance(content, dict) and "text" in content:
                return content["text"]
        
        # Fallback: convert to string
        return str(response)

    # ------------------------------------------------

    @staticmethod
    def parse_json(text: str):
        """Parse JSON from LLM response, handling markdown code blocks"""
        
        if not text:
            return {}

        # Remove markdown code blocks
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*", "", text)
        text = text.strip()

        try:
            return json.loads(text)
        except Exception as e:
            logger.warning(f"Failed to parse JSON from LLM: {e}")
            return {"raw_response": text}

    # ------------------------------------------------

    @staticmethod
    async def generate_json(ctx, system_prompt: str, user_prompt: str):
        """Generate and parse JSON response from LLM"""
        
        text = await LLM.generate(ctx, system_prompt, user_prompt)
        
        ctx.info(f"LLM RAW RESPONSE:\n{text}")
        
        return LLM.parse_json(text)