"""
Task Queue Manager for parallel task execution.

Manages task lifecycle: pending → in_progress → completed/failed
"""

import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class TaskQueue:
    """
    Manages task queue and tracks execution status.
    
    Task lifecycle:
    1. pending: Task is waiting to be executed
    2. in_progress: Task is currently being executed by a developer
    3. completed: Task finished successfully
    4. failed: Task execution failed
    """
    
    def __init__(self, tasks: List[Dict[str, Any]]):
        """
        Initialize task queue with task list.
        
        Args:
            tasks: List of task dictionaries
        """
        self.pending: Dict[str, Dict[str, Any]] = {
            task["id"]: task for task in tasks
        }
        self.in_progress: Dict[str, Dict[str, Any]] = {}
        self.completed: Dict[str, Dict[str, Any]] = {}
        self.failed: Dict[str, Dict[str, Any]] = {}
        
        # Track metadata
        self.task_metadata: Dict[str, Dict[str, Any]] = {}
        for task in tasks:
            self.task_metadata[task["id"]] = {
                "created_at": datetime.now().isoformat(),
                "started_at": None,
                "completed_at": None,
                "developer_id": None,
                "error": None
            }
    
    def get_next_tasks(self, count: int, available_task_ids: Optional[Set[str]] = None) -> List[Dict[str, Any]]:
        """
        Get next N tasks from the pending queue.
        
        Args:
            count: Number of tasks to retrieve
            available_task_ids: Optional set of task IDs that are ready (dependencies satisfied)
        
        Returns:
            List of task objects (up to count)
        """
        if available_task_ids:
            # Filter pending tasks to only those available
            available_pending = [
                task for task_id, task in self.pending.items()
                if task_id in available_task_ids
            ]
        else:
            available_pending = list(self.pending.values())
        
        # Return up to count tasks
        tasks_to_return = available_pending[:count]
        logger.info(f"Retrieved {len(tasks_to_return)} tasks from queue (requested: {count})")
        return tasks_to_return
    
    def mark_in_progress(self, task_id: str, developer_id: str):
        """
        Mark task as in progress.
        
        Args:
            task_id: The task ID
            developer_id: The developer agent handling this task
        """
        if task_id not in self.pending:
            logger.warning(f"Task {task_id} not found in pending queue")
            return
        
        # Move from pending to in_progress
        task = self.pending.pop(task_id)
        self.in_progress[task_id] = task
        
        # Update metadata
        self.task_metadata[task_id]["started_at"] = datetime.now().isoformat()
        self.task_metadata[task_id]["developer_id"] = developer_id
        
        logger.info(f"Task {task_id} marked as in_progress (developer: {developer_id})")
    
    def mark_completed(self, task_id: str, result: Dict[str, Any]):
        """
        Mark task as completed successfully.
        
        Args:
            task_id: The task ID
            result: The result data from the developer (artifact, files, etc.)
        """
        if task_id not in self.in_progress:
            logger.warning(f"Task {task_id} not found in in_progress queue")
            return
        
        # Move from in_progress to completed
        task = self.in_progress.pop(task_id)
        task["result"] = result
        self.completed[task_id] = task
        
        # Update metadata
        self.task_metadata[task_id]["completed_at"] = datetime.now().isoformat()
        
        logger.info(f"Task {task_id} marked as completed")
    
    def mark_failed(self, task_id: str, error: str):
        """
        Mark task as failed.
        
        Args:
            task_id: The task ID
            error: Error message describing the failure
        """
        # Task could be in pending or in_progress
        if task_id in self.in_progress:
            task = self.in_progress.pop(task_id)
        elif task_id in self.pending:
            task = self.pending.pop(task_id)
        else:
            logger.warning(f"Task {task_id} not found in any queue")
            return
        
        task["error"] = error
        self.failed[task_id] = task
        
        # Update metadata
        self.task_metadata[task_id]["completed_at"] = datetime.now().isoformat()
        self.task_metadata[task_id]["error"] = error
        
        logger.error(f"Task {task_id} marked as failed: {error}")
    
    def is_empty(self) -> bool:
        """
        Check if all tasks are complete (either completed or failed).
        
        Returns:
            True if no pending or in_progress tasks remain
        """
        return len(self.pending) == 0 and len(self.in_progress) == 0
    
    def all_completed(self) -> bool:
        """
        Check if all tasks completed successfully (no failures).
        
        Returns:
            True if all tasks are in completed state
        """
        total_tasks = len(self.task_metadata)
        return len(self.completed) == total_tasks
    
    def has_failures(self) -> bool:
        """Check if any tasks failed."""
        return len(self.failed) > 0
    
    def get_completed_task_ids(self) -> Set[str]:
        """Get set of completed task IDs (for dependency checking)."""
        return set(self.completed.keys())
    
    def get_failed_task_ids(self) -> Set[str]:
        """Get set of failed task IDs."""
        return set(self.failed.keys())
    
    def get_task_status(self, task_id: str) -> Optional[str]:
        """
        Get current status of a task.
        
        Args:
            task_id: The task ID
        
        Returns:
            One of: "pending", "in_progress", "completed", "failed", or None if not found
        """
        if task_id in self.pending:
            return "pending"
        elif task_id in self.in_progress:
            return "in_progress"
        elif task_id in self.completed:
            return "completed"
        elif task_id in self.failed:
            return "failed"
        return None
    
    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get result of a completed task.
        
        Args:
            task_id: The task ID
        
        Returns:
            Result dict if task is completed, None otherwise
        """
        task = self.completed.get(task_id)
        if task:
            return task.get("result")
        return None
    
    def retry_failed_task(self, task_id: str) -> bool:
        """
        Move a failed task back to pending for retry.
        
        Args:
            task_id: The task ID to retry
        
        Returns:
            True if task was moved, False if task not found in failed queue
        """
        if task_id not in self.failed:
            logger.warning(f"Task {task_id} not found in failed queue, cannot retry")
            return False
        
        # Move from failed back to pending
        task = self.failed.pop(task_id)
        
        # Clean up error info
        if "error" in task:
            del task["error"]
        
        self.pending[task_id] = task
        
        # Reset metadata
        self.task_metadata[task_id]["completed_at"] = None
        self.task_metadata[task_id]["error"] = None
        self.task_metadata[task_id]["developer_id"] = None
        
        logger.info(f"Task {task_id} moved from failed to pending for retry")
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get queue statistics.
        
        Returns:
            Dict with counts and percentages
        """
        total = len(self.task_metadata)
        
        stats = {
            "total_tasks": total,
            "pending": len(self.pending),
            "in_progress": len(self.in_progress),
            "completed": len(self.completed),
            "failed": len(self.failed),
            "completion_rate": (len(self.completed) / total * 100) if total > 0 else 0,
            "failure_rate": (len(self.failed) / total * 100) if total > 0 else 0
        }
        
        return stats
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get detailed summary of queue state.
        
        Returns:
            Dict with task IDs in each state and metadata
        """
        return {
            "statistics": self.get_statistics(),
            "pending_task_ids": list(self.pending.keys()),
            "in_progress_task_ids": list(self.in_progress.keys()),
            "completed_task_ids": list(self.completed.keys()),
            "failed_task_ids": list(self.failed.keys()),
            "task_metadata": self.task_metadata,
            "is_empty": self.is_empty(),
            "all_completed": self.all_completed(),
            "has_failures": self.has_failures()
        }
    
    def get_execution_time(self, task_id: str) -> Optional[float]:
        """
        Calculate execution time for a task in seconds.
        
        Args:
            task_id: The task ID
        
        Returns:
            Execution time in seconds, or None if not yet completed
        """
        metadata = self.task_metadata.get(task_id)
        if not metadata:
            return None
        
        started = metadata.get("started_at")
        completed = metadata.get("completed_at")
        
        if not started or not completed:
            return None
        
        start_time = datetime.fromisoformat(started)
        end_time = datetime.fromisoformat(completed)
        
        return (end_time - start_time).total_seconds()
