"""
Parallel Developer Agent for independent task execution.

Each instance handles a single task with isolated context and state.
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from mcp.server.fastmcp import Context
from devhive.agents.base_agent import BaseAgent
from devhive.core.artifact_manager import ArtifactManager

logger = logging.getLogger(__name__)


class ParallelDeveloperAgent(BaseAgent):
    """
    Developer agent for parallel task execution.
    
    Features:
    - Isolated state per developer instance
    - Task-scoped context (only relevant information)
    - Access to shared artifacts (exploration, proposal, architecture)
    - Independent file writing with merge capability
    """
    
    role = "Developer"
    
    def __init__(self, project_name: str, developer_id: str, task: Dict[str, Any]):
        """
        Initialize parallel developer agent.
        
        Args:
            project_name: Project identifier
            developer_id: Unique developer ID (e.g., "dev_task_1")
            task: Task dictionary with id, name, description, dependencies, etc.
        """
        self.developer_id = developer_id
        self.task = task
        
        # Initialize base agent
        super().__init__(project_name)
        
        # Create developer-specific state directory
        self._init_developer_state()
        
        logger.info(f"Initialized {developer_id} for task: {task.get('name')}")
    
    def _init_developer_state(self):
        """Create isolated state directory for this developer."""
        from devhive.utils.filesystem import get_safe_path, write_file
        
        # Create developers directory
        dev_dir = f"{self.project_name}/developers"
        get_safe_path(dev_dir)
        
        # Create state file for this developer
        self.state_file = f"{dev_dir}/{self.developer_id}_state.json"
        
        try:
            from devhive.utils.filesystem import read_file
            read_file(self.state_file)
        except:
            # Initialize state
            initial_state = {
                "developer_id": self.developer_id,
                "task_id": self.task["id"],
                "task_name": self.task.get("name"),
                "status": "initialized",
                "files_created": [],
                "artifact_id": None
            }
            write_file(self.state_file, json.dumps(initial_state, indent=2))
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get task-scoped context for this developer.
        
        Context includes:
        - Shared artifacts (exploration, proposal, architecture) - READ ONLY
        - Current task details
        - Outputs from dependency tasks
        - Project guidelines
        
        Returns:
            Context dictionary optimized for this specific task
        """
        # Get shared artifacts (exploration, proposal, architecture, tasks)
        shared_context = self._get_shared_context()
        
        # Add task-specific context
        task_context = {
            "developer_id": self.developer_id,
            "task_id": self.task["id"],
            "task_name": self.task.get("name"),
            "task_description": self.task.get("description"),
            "files_to_create": self.task.get("files_involved", []),
            "estimated_tokens": self.task.get("estimated_tokens", "unknown")
        }
        
        # Add outputs from dependency tasks
        dependency_outputs = self._get_dependency_outputs()
        if dependency_outputs:
            task_context["dependency_outputs"] = dependency_outputs
        
        return {
            **shared_context,
            "current_task": task_context
        }
    
    def _get_shared_context(self) -> Dict[str, Any]:
        """
        Load shared artifacts that all developers can access.
        
        Returns:
            Dict with exploration, proposal, architecture, tasks artifacts
        """
        context = {
            "project_name": self.project_name,
            "current_stage": "parallel_development"
        }
        
        # Load shared artifacts
        state = self.state_manager.get_state()
        artifacts = state.get("artifacts", {})
        
        shared_artifact_keys = ["exploration", "proposal", "architecture", "tasks"]
        
        for key in shared_artifact_keys:
            artifact_id = artifacts.get(key)
            if artifact_id:
                try:
                    artifact_data = self.artifact_manager.load_artifact(artifact_id)
                    context[key] = artifact_data
                except Exception as e:
                    logger.warning(f"Could not load {key} artifact: {e}")
                    context[key] = None
        
        # Add project guidelines if available
        try:
            from devhive.utils.filesystem import read_file
            guidelines = read_file("GUIDELINES.md")
            context["project_guidelines"] = guidelines
        except:
            context["project_guidelines"] = "Guidelines not found."
        
        return context
    
    def _get_dependency_outputs(self) -> Optional[Dict[str, Any]]:
        """
        Load outputs from tasks that this task depends on.
        
        Returns:
            Dict mapping dependency task_id -> task result
        """
        depends_on = self.task.get("depends_on", [])
        if not depends_on:
            return None
        
        dependency_outputs = {}
        
        for dep_task_id in depends_on:
            # Try to load artifact from the dependent task's developer
            dep_dev_id = f"dev_{dep_task_id}"
            artifact_key = f"implementation_{dep_dev_id}"
            
            try:
                # Load from artifact manager
                artifact_id = self.state_manager.get_state().get("artifacts", {}).get(artifact_key)
                if artifact_id:
                    dep_artifact = self.artifact_manager.load_artifact(artifact_id)
                    dependency_outputs[dep_task_id] = {
                        "files": dep_artifact.get("files", []),
                        "implementation_strategy": dep_artifact.get("implementation_strategy"),
                        "file_structure": dep_artifact.get("file_structure", [])
                    }
                    logger.info(f"{self.developer_id}: Loaded output from dependency {dep_task_id}")
            except Exception as e:
                logger.warning(f"{self.developer_id}: Could not load dependency {dep_task_id}: {e}")
        
        return dependency_outputs if dependency_outputs else None
    
    async def execute(self, ctx: Context, **kwargs) -> str:
        """
        Execute this developer's specific task.
        
        Args:
            ctx: MCP context
            **kwargs: Additional arguments
        
        Returns:
            Artifact ID for the implementation
        """
        logger.info(f"{self.developer_id}: Starting execution of task {self.task['id']}")
        
        # Get task-scoped context
        context = self.get_context()
        
        # Check if context might exceed token limits
        estimated_tokens = self._estimate_context_size(context)
        logger.info(f"{self.developer_id}: Estimated context size: {estimated_tokens} tokens")
        
        if estimated_tokens > 3500:  # Leave buffer for max_tokens=4000
            logger.warning(f"{self.developer_id}: Context too large, attempting to reduce")
            return await self._handle_large_context(context, ctx)
        
        # Build prompts
        sys_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(context)
        
        # Call LLM
        try:
            resp = await self._call_llm(ctx, sys_prompt, user_prompt, max_tokens=4000)
            data = self._parse_json(resp)
        except Exception as e:
            logger.error(f"{self.developer_id}: LLM call failed: {e}")
            raise
        
        # Write files
        file_paths = self.write_files(data)
        
        # Update developer state
        self._update_developer_state("completed", file_paths, data)
        
        # Save artifact with developer-specific key
        artifact_id = self.save_artifact(f"implementation_{self.developer_id}", data)
        
        logger.info(f"{self.developer_id}: Completed task {self.task['id']}, wrote {len(file_paths)} files")
        
        return artifact_id
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for this developer."""
        return f"""You are {self.developer_id}, a specialized Developer agent.

CRITICAL CONSTRAINTS:
- You are working on ONE specific task only: "{self.task.get('name')}"
- Do NOT implement features outside your task scope
- Focus only on the files assigned to you: {self.task.get('files_involved', [])}
- If your task depends on other tasks, their outputs are provided in the context

Output JSON only with the required structure."""
    
    def _build_user_prompt(self, context: Dict[str, Any]) -> str:
        """Build user prompt with task-specific instructions."""
        task_info = context.get("current_task", {})
        
        prompt = f"""Implement the following task:

TASK: {task_info.get('task_name')}
DESCRIPTION: {task_info.get('task_description')}

FILES TO CREATE/MODIFY:
{json.dumps(task_info.get('files_to_create', []), indent=2)}

CONTEXT FROM PREVIOUS PIPELINE STAGES:
{json.dumps({k: v for k, v in context.items() if k != 'current_task'}, default=str, indent=2)}
"""
        
        # Add dependency outputs if available
        if task_info.get("dependency_outputs"):
            prompt += f"""

OUTPUTS FROM DEPENDENCY TASKS:
{json.dumps(task_info['dependency_outputs'], default=str, indent=2)}

NOTE: These files have already been created by other developers. You can reference/import them.
"""
        
        prompt += """

Return JSON with the following keys:
- implementation_strategy: High-level strategy for this specific task
- file_structure: List of files you will create/modify
- pseudocode: Brief implementation notes for this task
- files: List of file objects with 'path' and 'content' keys

IMPORTANT: Only implement THIS task. Do not create files outside your scope."""
        
        return prompt
    
    async def _handle_large_context(self, context: Dict[str, Any], ctx: Context) -> str:
        """
        Handle cases where context is too large.
        
        Strategy:
        1. Try to reduce context by summarizing large artifacts
        2. If still too large, attempt to split task
        3. If cannot split, return error with guidance
        
        Args:
            context: The full context
            ctx: MCP context
        
        Returns:
            Artifact ID or raises exception
        """
        logger.warning(f"{self.developer_id}: Attempting context reduction")
        
        # Strategy 1: Summarize large artifacts
        reduced_context = self._reduce_context(context)
        estimated = self._estimate_context_size(reduced_context)
        
        if estimated <= 3500:
            logger.info(f"{self.developer_id}: Context reduction successful ({estimated} tokens)")
            sys_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(reduced_context)
            
            resp = await self._call_llm(ctx, sys_prompt, user_prompt, max_tokens=4000)
            data = self._parse_json(resp)
            
            file_paths = self.write_files(data)
            self._update_developer_state("completed", file_paths, data)
            return self.save_artifact(f"implementation_{self.developer_id}", data)
        
        # Strategy 2: Try to split task by files
        files_involved = self.task.get("files_involved", [])
        if len(files_involved) > 3:
            error_msg = (
                f"Task {self.task['id']} is too large and involves {len(files_involved)} files. "
                f"Please re-run TaskPlanner with instruction to split this task into smaller subtasks "
                f"(e.g., 2-3 files per task)."
            )
            logger.error(f"{self.developer_id}: {error_msg}")
            raise ValueError(error_msg)
        
        # Strategy 3: Cannot proceed
        error_msg = (
            f"Task {self.task['id']} context exceeds token limits and cannot be split further. "
            f"Consider simplifying the task description or reducing the number of dependencies."
        )
        logger.error(f"{self.developer_id}: {error_msg}")
        raise ValueError(error_msg)
    
    def _reduce_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reduce context size by summarizing large artifacts.
        
        Args:
            context: Full context
        
        Returns:
            Reduced context
        """
        reduced = context.copy()
        
        # Summarize exploration
        if "exploration" in reduced and isinstance(reduced["exploration"], dict):
            exploration = reduced["exploration"]
            reduced["exploration"] = {
                "user_needs": exploration.get("user_needs", "")[:200],
                "constraints": exploration.get("constraints", [])[:3],
                "dependencies": exploration.get("dependencies", [])[:3]
            }
        
        # Summarize proposal
        if "proposal" in reduced and isinstance(reduced["proposal"], dict):
            proposal = reduced["proposal"]
            reduced["proposal"] = {
                "feature_description": proposal.get("feature_description", "")[:200],
                "acceptance_criteria": proposal.get("acceptance_criteria", [])[:3]
            }
        
        # Keep architecture as-is (usually concise)
        
        # Reduce dependency outputs to just file paths
        if "current_task" in reduced and "dependency_outputs" in reduced["current_task"]:
            dep_outputs = reduced["current_task"]["dependency_outputs"]
            for dep_id, dep_data in dep_outputs.items():
                if "files" in dep_data:
                    # Keep only file paths, not full content
                    dep_data["files"] = [
                        {"path": f.get("path")} for f in dep_data["files"]
                        if isinstance(f, dict) and "path" in f
                    ]
        
        return reduced
    
    def _estimate_context_size(self, context: Dict[str, Any]) -> int:
        """
        Rough estimate of context size in tokens.
        
        Uses approximation: 1 token ≈ 4 characters
        
        Args:
            context: Context dictionary
        
        Returns:
            Estimated token count
        """
        context_str = json.dumps(context, default=str)
        char_count = len(context_str)
        token_estimate = char_count // 4
        return token_estimate
    
    def _update_developer_state(self, status: str, file_paths: list, artifact_data: Dict):
        """Update developer-specific state file."""
        from devhive.utils.filesystem import write_file, read_file
        
        try:
            state = json.loads(read_file(self.state_file))
        except:
            state = {}
        
        state["status"] = status
        state["files_created"] = file_paths
        state["artifact_id"] = f"implementation_{self.developer_id}"
        
        write_file(self.state_file, json.dumps(state, indent=2))
    
    def generate_summary(self, data: Dict[str, Any]) -> str:
        """Generate executive summary for this developer's work."""
        files_count = len(data.get("files", []))
        task_name = self.task.get("name", "Unknown task")
        return f"{self.developer_id} completed '{task_name}' ({files_count} files)"
