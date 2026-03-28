"""
Basic tests for parallel development components.

Run with: pytest tests/test_parallel_development.py
"""

import pytest
from devhive.core.dependency_manager import DependencyManager
from devhive.core.task_queue import TaskQueue


class TestDependencyManager:
    """Test dependency management functionality."""
    
    def test_basic_dependency_graph(self):
        """Test building a basic dependency graph."""
        tasks = [
            {
                "id": "task_1",
                "name": "Create models",
                "depends_on": [],
                "files_involved": ["models/user.py"]
            },
            {
                "id": "task_2",
                "name": "Create API",
                "depends_on": ["task_1"],
                "files_involved": ["api/routes.py"]
            }
        ]
        
        dm = DependencyManager(tasks)
        
        assert dm.dependency_graph["task_1"] == set()
        assert dm.dependency_graph["task_2"] == {"task_1"}
    
    def test_get_ready_tasks(self):
        """Test getting tasks ready for execution."""
        tasks = [
            {"id": "task_1", "name": "Task 1", "depends_on": []},
            {"id": "task_2", "name": "Task 2", "depends_on": ["task_1"]},
            {"id": "task_3", "name": "Task 3", "depends_on": []}
        ]
        
        dm = DependencyManager(tasks)
        
        # Initially, task_1 and task_3 are ready (no dependencies)
        ready = dm.get_ready_tasks(set())
        ready_ids = [t["id"] for t in ready]
        assert set(ready_ids) == {"task_1", "task_3"}
        
        # After task_1 completes, task_2 becomes ready
        ready = dm.get_ready_tasks({"task_1"})
        ready_ids = [t["id"] for t in ready]
        assert "task_2" in ready_ids
    
    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies."""
        tasks = [
            {"id": "task_1", "name": "Task 1", "depends_on": ["task_2"]},
            {"id": "task_2", "name": "Task 2", "depends_on": ["task_1"]}
        ]
        
        dm = DependencyManager(tasks)
        
        assert dm.has_circular_dependencies() == True
    
    def test_inferred_dependencies(self):
        """Test automatic file-based dependency inference."""
        tasks = [
            {
                "id": "task_1",
                "name": "Create models",
                "depends_on": [],
                "files_involved": ["models/user.py"]
            },
            {
                "id": "task_2",
                "name": "Create API",
                "depends_on": [],
                "files_involved": ["models/user.py", "api/routes.py"]
            }
        ]
        
        dm = DependencyManager(tasks)
        
        # task_2 should infer dependency on task_1 (both use models/user.py)
        assert "task_1" in dm.dependency_graph["task_2"]
    
    def test_dependency_statistics(self):
        """Test getting dependency statistics."""
        tasks = [
            {"id": "task_1", "name": "Task 1", "depends_on": []},
            {"id": "task_2", "name": "Task 2", "depends_on": ["task_1"]},
            {"id": "task_3", "name": "Task 3", "depends_on": ["task_1"]}
        ]
        
        dm = DependencyManager(tasks)
        stats = dm.get_statistics()
        
        assert stats["total_tasks"] == 3
        assert stats["tasks_with_dependencies"] == 2
        assert stats["independent_tasks"] == 1
        assert stats["has_circular_deps"] == False


class TestTaskQueue:
    """Test task queue functionality."""
    
    def test_queue_initialization(self):
        """Test initializing task queue."""
        tasks = [
            {"id": "task_1", "name": "Task 1"},
            {"id": "task_2", "name": "Task 2"}
        ]
        
        queue = TaskQueue(tasks)
        
        assert len(queue.pending) == 2
        assert len(queue.in_progress) == 0
        assert len(queue.completed) == 0
    
    def test_task_lifecycle(self):
        """Test task state transitions."""
        tasks = [{"id": "task_1", "name": "Task 1"}]
        queue = TaskQueue(tasks)
        
        # Initially pending
        assert queue.get_task_status("task_1") == "pending"
        
        # Mark in progress
        queue.mark_in_progress("task_1", "dev_task_1")
        assert queue.get_task_status("task_1") == "in_progress"
        
        # Mark completed
        queue.mark_completed("task_1", {"files": []})
        assert queue.get_task_status("task_1") == "completed"
    
    def test_task_failure(self):
        """Test task failure handling."""
        tasks = [{"id": "task_1", "name": "Task 1"}]
        queue = TaskQueue(tasks)
        
        queue.mark_in_progress("task_1", "dev_task_1")
        queue.mark_failed("task_1", "Test error")
        
        assert queue.get_task_status("task_1") == "failed"
        assert queue.has_failures() == True
    
    def test_retry_failed_task(self):
        """Test retrying a failed task."""
        tasks = [{"id": "task_1", "name": "Task 1"}]
        queue = TaskQueue(tasks)
        
        queue.mark_in_progress("task_1", "dev_task_1")
        queue.mark_failed("task_1", "Test error")
        
        # Retry the failed task
        success = queue.retry_failed_task("task_1")
        
        assert success == True
        assert queue.get_task_status("task_1") == "pending"
    
    def test_queue_statistics(self):
        """Test getting queue statistics."""
        tasks = [
            {"id": "task_1", "name": "Task 1"},
            {"id": "task_2", "name": "Task 2"},
            {"id": "task_3", "name": "Task 3"}
        ]
        
        queue = TaskQueue(tasks)
        
        queue.mark_in_progress("task_1", "dev_1")
        queue.mark_in_progress("task_2", "dev_2")
        queue.mark_completed("task_2", {})
        
        stats = queue.get_statistics()
        
        assert stats["total_tasks"] == 3
        assert stats["pending"] == 1
        assert stats["in_progress"] == 1
        assert stats["completed"] == 1
        assert stats["completion_rate"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
