import json
from mcp.server.fastmcp import Context
from mcp_server.agents.base_agent import BaseAgent

class DeveloperAgent(BaseAgent):
    role = "Developer"
    async def execute(self, ctx: Context, **kwargs) -> str:
        context = self.get_context()
        sys_prompt = "You are the Developer. Output JSON only."
        user_prompt = f"""Implement the feature.
Context: {json.dumps(context, default=str)}
Return JSON with keys: implementation_strategy, file_structure, pseudocode, files (list of {{path, content}})."""
        
        resp = await self._call_llm(ctx, sys_prompt, user_prompt, max_tokens=4000)
        data = self._parse_json(resp)
        
        # Write files
        files = data.get("files", [])
        from mcp_server.utils.filesystem import write_file
        file_paths = []
        for f in files:
            if isinstance(f, dict) and "path" in f and "content" in f:
                write_file(f["path"], f["content"])
                file_paths.append(f["path"])
            
        self.state_manager.add_files(file_paths)
        return self.save_artifact("implementation", data)
