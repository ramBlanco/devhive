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


class TestContextOptimizer:
    """Test context optimization for token limit prevention."""
    
    def test_summarize_exploration(self):
        """Test exploration artifact summarization."""
        from devhive.core.context_optimizer import ContextOptimizer
        
        optimizer = ContextOptimizer()
        
        exploration = {
            "user_needs": "A" * 500,  # Very long text
            "constraints": ["c1", "c2", "c3", "c4", "c5"],  # Many constraints
            "dependencies": ["d1", "d2", "d3", "d4"],  # Many dependencies
            "other_field": "should be removed"
        }
        
        summarized = optimizer.summarize_exploration(exploration)
        
        # Check truncation
        assert len(summarized["user_needs"]) <= 203  # 200 + "..."
        # Check top 3 only
        assert len(summarized["constraints"]) == 3
        assert len(summarized["dependencies"]) == 3
        # Check other fields removed
        assert "other_field" not in summarized
    
    def test_summarize_proposal(self):
        """Test proposal artifact summarization."""
        from devhive.core.context_optimizer import ContextOptimizer
        
        optimizer = ContextOptimizer()
        
        proposal = {
            "feature_description": "B" * 300,
            "acceptance_criteria": ["ac1", "ac2", "ac3", "ac4"],
            "implementation_approach": "C" * 200,
            "other_field": "should be removed"
        }
        
        summarized = optimizer.summarize_proposal(proposal)
        
        assert len(summarized["feature_description"]) <= 203
        assert len(summarized["acceptance_criteria"]) == 3
        assert len(summarized["implementation_approach"]) <= 153
        assert "other_field" not in summarized
    
    def test_summarize_architecture(self):
        """Test architecture summarization with task file filtering."""
        from devhive.core.context_optimizer import ContextOptimizer
        
        optimizer = ContextOptimizer()
        
        architecture = {
            "pattern": "MVC",
            "components": [
                {"name": "UserModel", "files": ["models/user.py"], "purpose": "A" * 100},
                {"name": "AuthAPI", "files": ["api/auth.py"], "purpose": "B" * 100},
                {"name": "Database", "files": ["db/connection.py"], "purpose": "C" * 100}
            ],
            "data_flow": "D" * 300
        }
        
        task_files = ["models/user.py"]
        summarized = optimizer.summarize_architecture(architecture, task_files)
        
        # Pattern should be kept
        assert summarized["pattern"] == "MVC"
        # Only relevant component (UserModel) should be kept
        assert len(summarized["components"]) == 1
        assert summarized["components"][0]["name"] == "UserModel"
        # Purpose should be truncated
        assert len(summarized["components"][0]["purpose"]) <= 103
        # Data flow truncated
        assert len(summarized["data_flow"]) <= 203
    
    def test_filter_dependency_outputs(self):
        """Test filtering dependency outputs to remove file contents."""
        from devhive.core.context_optimizer import ContextOptimizer
        
        optimizer = ContextOptimizer()
        
        dep_outputs = {
            "task_1": {
                "files": [
                    {"path": "models/user.py", "content": "class User: pass"},
                    {"path": "models/role.py", "content": "class Role: pass"}
                ],
                "summary": "A" * 200,
                "implementation_details": "B" * 300
            },
            "task_2": {
                "files": [{"path": "api/routes.py"}],
                "description": "C" * 200
            }
        }
        
        filtered = optimizer.filter_dependency_outputs(dep_outputs)
        
        # File contents should be removed
        assert "content" not in str(filtered["task_1"]["files"])
        # Paths should be kept
        assert any("models/user.py" in str(f) for f in filtered["task_1"]["files"])
        # Summary should be truncated
        assert len(filtered["task_1"]["summary"]) <= 153
        # Description truncated
        assert len(filtered["task_2"]["description"]) <= 153
    
    def test_estimate_tokens(self):
        """Test token estimation."""
        from devhive.core.context_optimizer import ContextOptimizer
        
        optimizer = ContextOptimizer()
        
        # Test with known text
        text = "Hello world! " * 100  # ~1300 characters
        tokens = optimizer.estimate_tokens(text)
        
        # Should be roughly 1300/4 = 325 tokens (may vary with tiktoken)
        assert 200 < tokens < 500  # Reasonable range
    
    def test_optimize_full_context(self):
        """Test full context optimization."""
        from devhive.core.context_optimizer import ContextOptimizer
        
        optimizer = ContextOptimizer()
        
        context = {
            "exploration": {
                "user_needs": "A" * 500,
                "constraints": ["c1", "c2", "c3", "c4"],
                "dependencies": ["d1", "d2", "d3"]
            },
            "proposal": {
                "feature_description": "B" * 300,
                "acceptance_criteria": ["ac1", "ac2", "ac3", "ac4"]
            },
            "architecture": {
                "pattern": "MVC",
                "components": [{"name": "Comp1", "files": ["test.py"]}]
            },
            "dependency_outputs": {
                "task_1": {
                    "files": [{"path": "test.py", "content": "code"}],
                    "summary": "Summary"
                }
            }
        }
        
        optimized = optimizer.optimize_full_context(context, task_files=["test.py"])
        
        # All components should be optimized
        assert len(optimized["exploration"]["user_needs"]) <= 203
        assert len(optimized["proposal"]["feature_description"]) <= 203
        assert "pattern" in optimized["architecture"]
        assert "content" not in str(optimized["dependency_outputs"])
    
    def test_context_size_reduction(self):
        """Test that optimization actually reduces context size."""
        from devhive.core.context_optimizer import ContextOptimizer
        
        optimizer = ContextOptimizer()
        
        # Create large context
        large_context = {
            "exploration": {"user_needs": "X" * 1000, "constraints": ["c"] * 20},
            "proposal": {"feature_description": "Y" * 1000, "acceptance_criteria": ["a"] * 20},
            "architecture": {"components": [{"name": f"C{i}", "purpose": "P" * 200} for i in range(10)]}
        }
        
        optimized = optimizer.optimize_full_context(large_context)
        
        # Calculate sizes
        original_size = optimizer.estimate_context_size(large_context)["total"]
        optimized_size = optimizer.estimate_context_size(optimized)["total"]
        
        # Optimized should be significantly smaller
        reduction_pct = 100 * (1 - optimized_size / original_size)
        assert reduction_pct > 50  # At least 50% reduction


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
