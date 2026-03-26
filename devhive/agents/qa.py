import json
from typing import Dict, Any
from mcp.server.fastmcp import Context
from devhive.agents.base_agent import BaseAgent

class QAAgent(BaseAgent):
    role = "QA"
    
    def write_test_files(self, data: Dict[str, Any]) -> list[str]:
        """Write test files to disk. Returns list of file paths."""
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
        sys_prompt = "You are QA. Output JSON only."
        user_prompt = f"""Generate tests.
Context: {json.dumps(context, default=str)}
Return JSON with keys: test_strategy, unit_tests, validation_plan, files (list of {{path, content}})."""
        
        resp = await self._call_llm(ctx, sys_prompt, user_prompt)
        data = self._parse_json(resp)
        
        # Write test files (using extracted method)
        file_paths = self.write_test_files(data)
        self.state_manager.add_files(file_paths)
        return self.save_artifact("tests", data)
    
    def generate_summary(self, data: Dict[str, Any]) -> str:
        """Generate executive summary for QA agent."""
        tests_count = len(data.get("unit_tests", []))
        files_count = len(data.get("files", []))
        strategy = data.get("test_strategy", "N/A")
        # Truncate if too long
        if len(strategy) > 60:
            strategy = strategy[:60] + "..."
        return (
            f"Generated {tests_count} unit tests across {files_count} test files. "
            f"Strategy: {strategy}"
        )
