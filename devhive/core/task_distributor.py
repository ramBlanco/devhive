"""
Task Distributor for parallel developer orchestration.

Coordinates multiple developer agents working on independent tasks.
"""

import json
import logging
from typing import Dict, Any, List, Optional

from mcp.server.fastmcp import Context
from devhive.agents.base_agent import BaseAgent
from devhive.agents.parallel_developer import ParallelDeveloperAgent
from devhive.core.dependency_manager import DependencyManager
from devhive.core.task_queue import TaskQueue

logger = logging.getLogger(__name__)


class TaskDistributor(BaseAgent):
    """
    Orchestrates parallel developer agents to execute tasks concurrently.
    
    Responsibilities:
    - Analyze task dependencies
    - Spawn developer agents dynamically (up to 5)
    - Distribute tasks to available developers
    - Track progress and handle failures
    - Aggregate results for QA stage
    """
    
    role = "TaskDistributor"
    
    def __init__(self, project_name: str):
        super().__init__(project_name)
        self.max_developers = 5
        self.active_developers: Dict[str, ParallelDeveloperAgent] = {}
        self.dependency_manager: Optional[DependencyManager] = None
        self.task_queue: Optional[TaskQueue] = None
    
    async def execute(self, ctx: Context, **kwargs) -> str:
        """
        Main execution method for task distribution.
        
        This method coordinates the parallel development workflow:
        1. Load tasks from TaskPlanner artifact
        2. Build dependency graph
        3. Distribute tasks to developers based on dependencies
        4. Execute developers (in OpenCode workflow, this is sequential but tracks parallel capability)
        5. Aggregate results
        
        Args:
            ctx: MCP context
            **kwargs: Additional arguments
        
        Returns:
            Artifact ID for aggregated implementation
        """
        logger.info("TaskDistributor: Starting parallel development workflow")
        
        # Step 1: Load tasks from TaskPlanner
        tasks = self._load_tasks()
        
        if not tasks:
            raise ValueError("No tasks found from TaskPlanner. Cannot proceed with development.")
        
        logger.info(f"TaskDistributor: Loaded {len(tasks)} tasks for distribution")
        
        # Step 2: Initialize dependency manager and task queue
        self.dependency_manager = DependencyManager(tasks)
        self.task_queue = TaskQueue(tasks)
        
        # Log dependency statistics
        dep_stats = self.dependency_manager.get_statistics()
        logger.info(f"Dependency analysis: {dep_stats}")
        
        # Check for circular dependencies
        if dep_stats.get("has_circular_deps"):
            raise ValueError(
                "Circular dependencies detected in task graph. "
                "Please fix task dependencies in TaskPlanner."
            )
        
        # Step 3: Execute tasks with dependency management
        results = await self._execute_tasks_with_dependencies(ctx)
        
        # Step 4: Aggregate results
        aggregated_artifact = self._aggregate_results(results)
        
        # Step 5: Save aggregated artifact
        artifact_id = self.save_artifact("implementation", aggregated_artifact)
        
        logger.info(f"TaskDistributor: Completed all tasks, saved artifact {artifact_id}")
        
        return artifact_id
    
    def _load_tasks(self) -> List[Dict[str, Any]]:
        """Load tasks from TaskPlanner artifact."""
        state = self.state_manager.get_state()
        tasks_artifact_id = state.get("artifacts", {}).get("tasks")
        
        if not tasks_artifact_id:
            raise ValueError("TaskPlanner artifact not found. Run TaskPlanner first.")
        
        tasks_data = self.artifact_manager.load_artifact(tasks_artifact_id)
        tasks = tasks_data.get("tasks", [])
        
        # Ensure all tasks have IDs
        for i, task in enumerate(tasks):
            if "id" not in task:
                task["id"] = f"task_{i + 1}"
        
        return tasks
    
    async def _execute_tasks_with_dependencies(self, ctx: Context) -> Dict[str, Any]:
        """
        Execute tasks respecting dependencies.
        
        In a true async environment, this would spawn tasks in parallel.
        In OpenCode's manual workflow, we simulate this by:
        1. Identifying which tasks can run in parallel (dependencies satisfied)
        2. Executing them sequentially but tracking them as "parallel batch"
        3. Moving to next batch when current batch completes
        
        Args:
            ctx: MCP context
        
        Returns:
            Dict mapping task_id -> result
        """
        results = {}
        batch_number = 1
        
        while not self.task_queue.is_empty():
            # Get tasks ready for execution (dependencies satisfied)
            completed_ids = self.task_queue.get_completed_task_ids()
            ready_tasks = self.dependency_manager.get_ready_tasks(completed_ids)
            
            if not ready_tasks:
                # Check if we have tasks in progress or failures
                if self.task_queue.has_failures():
                    failed_ids = self.task_queue.get_failed_task_ids()
                    raise ValueError(
                        f"Some tasks failed: {failed_ids}. "
                        f"Cannot proceed due to dependency requirements."
                    )
                
                # No ready tasks but queue not empty - something is wrong
                queue_stats = self.task_queue.get_statistics()
                raise ValueError(
                    f"Deadlock detected: {queue_stats['pending']} tasks pending "
                    f"but none have satisfied dependencies."
                )
            
            # Limit to max parallel developers
            tasks_to_execute = ready_tasks[:self.max_developers]
            
            logger.info(
                f"Batch {batch_number}: Executing {len(tasks_to_execute)} tasks in parallel "
                f"(ready: {len(ready_tasks)}, max_workers: {self.max_developers})"
            )
            
            # Execute batch
            batch_results = await self._execute_task_batch(tasks_to_execute, ctx)
            results.update(batch_results)
            
            batch_number += 1
        
        logger.info(f"All tasks completed in {batch_number - 1} batches")
        return results
    
    async def _execute_task_batch(
        self, 
        tasks: List[Dict[str, Any]], 
        ctx: Context
    ) -> Dict[str, Any]:
        """
        Execute a batch of tasks that can run in parallel.
        
        Args:
            tasks: List of tasks to execute
            ctx: MCP context
        
        Returns:
            Dict mapping task_id -> result
        """
        batch_results = {}
        
        for task in tasks:
            task_id = task["id"]
            
            # Mark task as in progress
            self.task_queue.mark_in_progress(task_id, f"dev_{task_id}")
            
            try:
                # Spawn developer agent
                developer = self._spawn_developer(task)
                
                # Execute developer
                logger.info(f"Executing developer for task {task_id}")
                artifact_id = await developer.execute(ctx)
                
                # Load result
                result_data = self.artifact_manager.load_artifact(artifact_id)
                
                # Mark task as completed
                self.task_queue.mark_completed(task_id, result_data)
                batch_results[task_id] = result_data
                
                logger.info(f"Task {task_id} completed successfully")
                
            except Exception as e:
                logger.error(f"Task {task_id} failed: {e}")
                self.task_queue.mark_failed(task_id, str(e))
                
                # Decide whether to continue or fail entire workflow
                # For now, we fail fast
                raise ValueError(
                    f"Task {task_id} failed: {e}. "
                    f"Stopping parallel development workflow."
                )
        
        return batch_results
    
    def _spawn_developer(self, task: Dict[str, Any]) -> ParallelDeveloperAgent:
        """
        Create a new parallel developer agent instance.
        
        Args:
            task: Task dictionary
        
        Returns:
            ParallelDeveloperAgent instance
        """
        dev_id = f"dev_{task['id']}"
        
        developer = ParallelDeveloperAgent(
            project_name=self.project_name,
            developer_id=dev_id,
            task=task
        )
        
        self.active_developers[dev_id] = developer
        
        logger.info(f"Spawned {dev_id} for task: {task.get('name')}")
        
        return developer
    
    def _aggregate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate results from all developers into a single implementation artifact.
        
        Args:
            results: Dict mapping task_id -> task result
        
        Returns:
            Aggregated artifact data
        """
        all_files = []
        all_strategies = []
        all_file_structures = []
        
        for task_id, result in results.items():
            # Collect files from each developer
            files = result.get("files", [])
            all_files.extend(files)
            
            # Collect strategies
            strategy = result.get("implementation_strategy")
            if strategy:
                all_strategies.append(f"Task {task_id}: {strategy}")
            
            # Collect file structures
            file_structure = result.get("file_structure", [])
            all_file_structures.extend(file_structure)
        
        # Remove duplicate file paths from file_structure
        all_file_structures = list(set(all_file_structures))
        
        # Build aggregated artifact
        aggregated = {
            "implementation_strategy": "\n\n".join(all_strategies),
            "file_structure": all_file_structures,
            "files": all_files,
            "parallel_execution": True,
            "total_tasks": len(results),
            "task_results": {
                task_id: {
                    "files_created": len(result.get("files", [])),
                    "strategy": result.get("implementation_strategy", "")[:100]
                }
                for task_id, result in results.items()
            }
        }
        
        logger.info(
            f"Aggregated {len(all_files)} files from {len(results)} tasks"
        )
        
        return aggregated
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of task distribution.
        
        Returns:
            Status dict with queue state and developer info
        """
        if not self.task_queue:
            return {"status": "not_started"}
        
        queue_summary = self.task_queue.get_summary()
        
        return {
            "status": "in_progress" if not self.task_queue.is_empty() else "completed",
            "queue": queue_summary,
            "active_developers": list(self.active_developers.keys()),
            "max_developers": self.max_developers
        }
    
    def generate_summary(self, data: Dict[str, Any]) -> str:
        """Generate executive summary for TaskDistributor."""
        total_tasks = data.get("total_tasks", 0)
        total_files = len(data.get("files", []))
        
        return (
            f"Distributed {total_tasks} tasks across parallel developers. "
            f"Total implementation: {total_files} files."
        )
