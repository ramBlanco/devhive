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
from devhive.core.context_optimizer import ContextOptimizer

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
        
        # Initialize context optimizer
        self.context_optimizer = ContextOptimizer()
        
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
        Load shared artifacts with aggressive optimization.
        
        Uses ContextOptimizer to minimize context size while preserving
        essential information. Developers can use memory search for additional details.
        
        Returns:
            Optimized dict with summarized artifacts
        """
        context = {
            "project_name": self.project_name,
            "current_stage": "parallel_development"
        }
        
        # Load shared artifacts
        state = self.state_manager.get_state()
        artifacts = state.get("artifacts", {})
        
        # Load artifacts (we'll optimize them before returning)
        raw_context = {}
        
        for key in ["exploration", "proposal", "architecture"]:
            artifact_id = artifacts.get(key)
            if artifact_id:
                try:
                    artifact_data = self.artifact_manager.load_artifact(artifact_id)
                    raw_context[key] = artifact_data
                except Exception as e:
                    logger.warning(f"Could not load {key} artifact: {e}")
                    raw_context[key] = None
            else:
                raw_context[key] = None
        
        # DON'T load full "tasks" artifact - developer only needs their own task
        # (Task details are provided in current_task context)
        
        # Optimize context using ContextOptimizer
        task_files = self.task.get("files_involved", [])
        optimized = self.context_optimizer.optimize_full_context(raw_context, task_files)
        
        # Log optimization stats
        self.context_optimizer.log_optimization_stats(raw_context, optimized)
        
        # Add optimized context
        context.update(optimized)
        
        # Add project guidelines (keep minimal)
        try:
            from devhive.utils.filesystem import read_file
            guidelines = read_file("GUIDELINES.md")
            # Truncate guidelines to 500 chars
            context["project_guidelines"] = self.context_optimizer.truncate_text(guidelines, 500)
        except:
            context["project_guidelines"] = "No guidelines available. Use memory search if needed."
        
        # Add note about memory search
        context["_memory_search_note"] = (
            "If you need additional context (e.g., detailed architecture, full exploration results), "
            "use the devhive_search_memory tool to query for specific information."
        )
        
        return context
    
    def _get_dependency_outputs(self) -> Optional[Dict[str, Any]]:
        """
        Load outputs from tasks that this task depends on.
        
        Applies optimization to remove file contents, keeping only paths/signatures.
        
        Returns:
            Optimized dict mapping dependency task_id -> task result
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
        
        # Optimize dependency outputs (remove file contents)
        if dependency_outputs:
            optimized = self.context_optimizer.filter_dependency_outputs(dependency_outputs)
            return optimized
        
        return None
    
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
        
        # Get task-scoped context (already optimized)
        context = self.get_context()
        
        # Estimate context size using optimizer (more accurate with tiktoken)
        context_sizes = self.context_optimizer.estimate_context_size(context)
        estimated_tokens = context_sizes["total"]
        
        logger.info(f"{self.developer_id}: Context size: {estimated_tokens} tokens")
        
        # Log component breakdown
        for key, size in context_sizes.items():
            if key != "total" and size > 0:
                logger.debug(f"  {key}: {size} tokens")
        
        if estimated_tokens > 3500:  # Leave buffer for max_tokens=4000
            logger.warning(f"{self.developer_id}: Context too large ({estimated_tokens} tokens), attempting auto-split")
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

CONTEXT OPTIMIZATION:
- The context provided has been optimized to reduce token usage
- If you need additional details (e.g., full architecture specs, detailed exploration results),
  you can use the devhive_search_memory tool to search project memory
- Example: devhive_search_memory(project_name="{self.project_name}", query="database schema design", top_k=3)

Output JSON only with the required structure."""
    
    def _build_user_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build user prompt with selective serialization.
        
        Only serialize essential fields instead of dumping entire context.
        """
        task_info = context.get("current_task", {})
        
        prompt = f"""Implement the following task:

TASK: {task_info.get('task_name')}
DESCRIPTION: {task_info.get('task_description')}

FILES TO CREATE/MODIFY:
{json.dumps(task_info.get('files_to_create', []), indent=2)}
"""
        
        # Add summarized shared context (already optimized)
        if context.get("exploration"):
            prompt += f"""

PROJECT REQUIREMENTS (Summarized):
{json.dumps(context['exploration'], indent=2)}
"""
        
        if context.get("proposal"):
            prompt += f"""

FEATURE PROPOSAL (Summarized):
{json.dumps(context['proposal'], indent=2)}
"""
        
        if context.get("architecture"):
            prompt += f"""

ARCHITECTURE (Relevant Components):
{json.dumps(context['architecture'], indent=2)}
"""
        
        # Add dependency outputs if available
        if task_info.get("dependency_outputs"):
            prompt += f"""

OUTPUTS FROM DEPENDENCY TASKS:
{json.dumps(task_info['dependency_outputs'], indent=2)}

NOTE: These files have already been created by other developers. You can reference/import them.
"""
        
        # Add guidelines if available
        if context.get("project_guidelines"):
            prompt += f"""

PROJECT GUIDELINES:
{context['project_guidelines']}
"""
        
        # Add memory search note
        if context.get("_memory_search_note"):
            prompt += f"""

ADDITIONAL CONTEXT:
{context['_memory_search_note']}
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
        Handle cases where context is too large even after optimization.
        
        Strategy:
        1. Context is already optimized by this point
        2. Attempt to auto-split task into smaller sub-tasks
        3. If cannot split, return detailed error with guidance
        
        Args:
            context: The optimized context (already reduced)
            ctx: MCP context
        
        Returns:
            Artifact ID or raises exception
        """
        logger.warning(f"{self.developer_id}: Context still too large after optimization")
        
        # Strategy 1: Try to auto-split task by files
        files_involved = self.task.get("files_involved", [])
        
        if len(files_involved) > 2:
            # Task has multiple files - can be split
            logger.info(f"{self.developer_id}: Attempting to auto-split task into sub-tasks")
            return await self._auto_split_task(files_involved, context, ctx)
        
        # Strategy 2: Check if we can further reduce context
        # (This is a last-resort - remove even more information)
        ultra_minimal_context = self._create_ultra_minimal_context(context)
        context_sizes = self.context_optimizer.estimate_context_size(ultra_minimal_context)
        estimated = context_sizes["total"]
        
        if estimated <= 3500:
            logger.info(f"{self.developer_id}: Ultra-minimal context worked ({estimated} tokens)")
            sys_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(ultra_minimal_context)
            
            resp = await self._call_llm(ctx, sys_prompt, user_prompt, max_tokens=4000)
            data = self._parse_json(resp)
            
            file_paths = self.write_files(data)
            self._update_developer_state("completed", file_paths, data)
            return self.save_artifact(f"implementation_{self.developer_id}", data)
        
        # Strategy 3: Cannot proceed - provide detailed error
        error_msg = (
            f"Task {self.task['id']} context exceeds token limits even after aggressive optimization.\n"
            f"Current context size: {estimated} tokens (limit: 3500)\n"
            f"Task involves {len(files_involved)} file(s): {files_involved}\n\n"
            f"Recommended actions:\n"
            f"1. Re-run TaskPlanner with instruction to create smaller tasks (1-2 files each)\n"
            f"2. Simplify the task description to reduce context\n"
            f"3. Reduce the number of task dependencies\n"
            f"4. Split complex files into smaller modules"
        )
        logger.error(f"{self.developer_id}: {error_msg}")
        raise ValueError(error_msg)
    
    async def _auto_split_task(
        self, 
        files_involved: list, 
        context: Dict[str, Any], 
        ctx: Context
    ) -> str:
        """
        Automatically split a task into smaller sub-tasks.
        
        Creates 2 file groups and processes them sequentially.
        
        Args:
            files_involved: List of files in the task
            context: Task context
            ctx: MCP context
            
        Returns:
            Combined artifact ID
        """
        logger.info(f"{self.developer_id}: Auto-splitting task with {len(files_involved)} files")
        
        # Split files into groups of 2
        mid_point = len(files_involved) // 2
        file_group_1 = files_involved[:mid_point]
        file_group_2 = files_involved[mid_point:]
        
        logger.info(f"{self.developer_id}: Group 1: {file_group_1}, Group 2: {file_group_2}")
        
        all_files = []
        combined_data = {
            "implementation_strategy": f"Auto-split task into {len(file_group_1) + len(file_group_2)} file groups",
            "file_structure": [],
            "pseudocode": "Task was auto-split due to token limits",
            "files": []
        }
        
        # Process each group
        for idx, file_group in enumerate([file_group_1, file_group_2], 1):
            logger.info(f"{self.developer_id}: Processing file group {idx}/{2}")
            
            # Create sub-task context with reduced file scope
            sub_context = context.copy()
            task_info = sub_context.get("current_task", {}).copy()
            task_info["files_to_create"] = file_group
            task_info["task_description"] = (
                f"{task_info.get('task_description', '')} "
                f"[Auto-split: Group {idx} - Files: {', '.join(file_group)}]"
            )
            sub_context["current_task"] = task_info
            
            # Build prompts for this group
            sys_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(sub_context)
            
            # Verify this group's context is small enough
            group_sizes = self.context_optimizer.estimate_context_size(sub_context)
            if group_sizes["total"] > 3500:
                error_msg = (
                    f"Even after auto-splitting, file group {idx} exceeds token limits "
                    f"({group_sizes['total']} tokens). Please manually split this task further."
                )
                logger.error(f"{self.developer_id}: {error_msg}")
                raise ValueError(error_msg)
            
            # Execute LLM call for this group
            resp = await self._call_llm(ctx, sys_prompt, user_prompt, max_tokens=4000)
            data = self._parse_json(resp)
            
            # Collect files from this group
            group_files = data.get("files", [])
            combined_data["files"].extend(group_files)
            combined_data["file_structure"].extend(data.get("file_structure", []))
            
            logger.info(f"{self.developer_id}: Group {idx} completed ({len(group_files)} files)")
        
        # Write all files
        file_paths = self.write_files(combined_data)
        
        # Update state
        self._update_developer_state("completed", file_paths, combined_data)
        
        # Save combined artifact
        artifact_id = self.save_artifact(f"implementation_{self.developer_id}", combined_data)
        
        logger.info(
            f"{self.developer_id}: Auto-split task completed successfully "
            f"({len(file_paths)} total files across {len([file_group_1, file_group_2])} groups)"
        )
        
        return artifact_id
    
    def _create_ultra_minimal_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create ultra-minimal context as last resort.
        
        Keeps only:
        - Task description
        - Files to create
        - Dependency file paths (no other dependency info)
        
        Args:
            context: Optimized context
            
        Returns:
            Ultra-minimal context
        """
        task_info = context.get("current_task", {})
        
        ultra_minimal = {
            "project_name": context.get("project_name"),
            "current_task": {
                "task_id": task_info.get("task_id"),
                "task_name": task_info.get("task_name"),
                "task_description": self.context_optimizer.truncate_text(
                    task_info.get("task_description", ""), 150
                ),
                "files_to_create": task_info.get("files_to_create", [])
            }
        }
        
        # Add only dependency file paths (absolute minimum)
        dep_outputs = task_info.get("dependency_outputs", {})
        if dep_outputs:
            minimal_deps = {}
            for dep_id, dep_data in dep_outputs.items():
                if isinstance(dep_data, dict) and "files" in dep_data:
                    # Just the file paths, nothing else
                    minimal_deps[dep_id] = {
                        "files": [f.get("path", str(f)) if isinstance(f, dict) else str(f) 
                                 for f in dep_data["files"]]
                    }
            ultra_minimal["current_task"]["dependency_outputs"] = minimal_deps
        
        # Add minimal note
        ultra_minimal["_note"] = (
            "Context minimized to prevent token limits. "
            f"Use devhive_search_memory(project_name='{context.get('project_name')}', query='...') "
            "to fetch additional details as needed."
        )
        
        return ultra_minimal
    
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
