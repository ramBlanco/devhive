import json
from typing import Dict, Any
from mcp.server.fastmcp import Context
from devhive.agents.base_agent import BaseAgent

class DeveloperAgent(BaseAgent):
    role = "Developer"
    
    def write_files(self, data: Dict[str, Any]) -> list[str]:
        """Write implementation files to disk. Returns list of file paths."""
        files = data.get("files", [])
        from devhive.utils.filesystem import write_file
        file_paths = []
        for f in files:
            if isinstance(f, dict) and "path" in f and "content" in f:
                write_file(f["path"], f["content"])
                file_paths.append(f["path"])
        return file_paths
    
    async def execute(self, ctx: Context, **kwargs) -> str:
        context = self.get_context()
        sys_prompt = "You are the Developer. Output JSON only."
        user_prompt = f"""Implement the feature.
Context: {json.dumps(context, default=str)}
Return JSON with keys: implementation_strategy, file_structure, pseudocode, files (list of {{path, content}})."""
        
        resp = await self._call_llm(ctx, sys_prompt, user_prompt, max_tokens=4000)
        data = self._parse_json(resp)
        
        # Write files (using extracted method)
        file_paths = self.write_files(data)
        self.state_manager.add_files(file_paths)
        return self.save_artifact("implementation", data)
    
    def generate_summary(self, data: Dict[str, Any]) -> str:
        """Generate executive summary for Developer agent."""
        if data.get("iterative_execution"):
            tasks_count = data.get("total_tasks_completed", 0)
            return f"Completed iterative implementation of {tasks_count} tasks."
            
        files_count = len(data.get("files", []))
        strategy = data.get("implementation_strategy", "N/A")
        # Truncate if too long
        if len(strategy) > 80:
            strategy = strategy[:80] + "..."
        return (
            f"Implemented {files_count} files using strategy: {strategy}"
        )
