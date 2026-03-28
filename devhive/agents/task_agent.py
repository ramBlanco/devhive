import json
from typing import Dict, Any
from mcp.server.fastmcp import Context
from devhive.agents.base_agent import BaseAgent

class TaskAgent(BaseAgent):
    role = "TaskPlanner"
    async def execute(self, ctx: Context, **kwargs) -> str:
        context = self.get_context()
        sys_prompt = "You are the Scrum Master. Output JSON only."
        user_prompt = f"""Break down the feature into development tasks with dependency information.

Context: {json.dumps(context, default=str)}

IMPORTANT: For parallel development, structure each task with:
- id: Unique task identifier (e.g., "task_1", "task_2")
- name: Clear task name
- description: Detailed description of what needs to be done
- depends_on: List of task IDs this task depends on (empty list if no dependencies)
- estimated_tokens: Rough estimate of complexity (low: <1000, medium: 1000-2500, high: >2500)
- files_involved: List of file paths this task will create or modify

Guidelines for task breakdown:
1. Keep tasks focused (2-4 files per task maximum)
2. Clearly identify dependencies (e.g., API routes depend on models)
3. Tasks without dependencies can be executed in parallel
4. Group related functionality into epics

Return JSON with keys:
- epics: List of high-level epics/themes
- tasks: List of task objects with structure described above
- estimated_complexity: Overall project complexity (low/medium/high)

Example:
{{
  "epics": ["Backend Models", "API Layer", "Frontend Components"],
  "tasks": [
    {{
      "id": "task_1",
      "name": "Create database models",
      "description": "Define User and Post models with SQLAlchemy",
      "depends_on": [],
      "estimated_tokens": 1500,
      "files_involved": ["models/user.py", "models/post.py"]
    }},
    {{
      "id": "task_2",
      "name": "Create API endpoints",
      "description": "Build REST API for users and posts",
      "depends_on": ["task_1"],
      "estimated_tokens": 2000,
      "files_involved": ["api/routes.py", "api/schemas.py"]
    }}
  ],
  "estimated_complexity": "medium"
}}"""
        
        resp = await self._call_llm(ctx, sys_prompt, user_prompt)
        data = self._parse_json(resp)
        return self.save_artifact("tasks", data)
    
    def generate_summary(self, data: Dict[str, Any]) -> str:
        """Generate executive summary for TaskPlanner agent."""
        tasks_count = len(data.get("tasks", []))
        complexity = data.get("estimated_complexity", "N/A")
        epics_count = len(data.get("epics", [])) if isinstance(data.get("epics"), list) else 0
        
        # Count tasks with dependencies for parallel execution insight
        tasks_with_deps = sum(
            1 for task in data.get("tasks", [])
            if task.get("depends_on") and len(task["depends_on"]) > 0
        )
        parallel_capable = tasks_count - tasks_with_deps
        
        return (
            f"Created {tasks_count} tasks across {epics_count} epics. "
            f"Complexity: {complexity}. "
            f"{parallel_capable} tasks can run in parallel."
        )
