"""
Dependency Manager for parallel task execution.

Manages task dependencies using a hybrid approach:
1. Explicit dependencies from TaskPlanner (depends_on field)
2. Automatic inference based on file analysis
"""

import logging
from typing import Dict, List, Set, Any, Optional

logger = logging.getLogger(__name__)


class DependencyManager:
    """
    Manages task dependencies and determines execution order.
    
    Features:
    - Build dependency graph from task list
    - Detect circular dependencies
    - Infer dependencies from file relationships
    - Return tasks ready for parallel execution
    """
    
    def __init__(self, tasks: List[Dict[str, Any]]):
        """
        Initialize dependency manager with task list.
        
        Args:
            tasks: List of task dicts with structure:
                {
                    "id": "task_1",
                    "name": "Create models",
                    "description": "...",
                    "depends_on": ["task_0"],  # Optional
                    "files_involved": ["models/user.py"]  # Optional
                }
        """
        self.tasks = {task["id"]: task for task in tasks}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.file_creators: Dict[str, str] = {}  # file_path -> task_id
        
        self._build_dependency_graph()
        self._infer_file_dependencies()
        
        # Validate no circular dependencies
        if self.has_circular_dependencies():
            logger.warning("Circular dependencies detected in task graph!")
    
    def _build_dependency_graph(self):
        """Build explicit dependency graph from task definitions."""
        for task_id, task in self.tasks.items():
            # Initialize with explicit dependencies
            deps = task.get("depends_on", [])
            self.dependency_graph[task_id] = set(deps) if deps else set()
            
            # Track which files this task creates
            files = task.get("files_involved", [])
            for file_path in files:
                # Assume first task to mention a file creates it
                if file_path not in self.file_creators:
                    self.file_creators[file_path] = task_id
    
    def _infer_file_dependencies(self):
        """
        Automatically infer dependencies based on file relationships.
        
        Logic:
        - If task B uses/modifies files that task A creates → B depends on A
        - Common patterns: imports, file modifications, shared resources
        """
        for task_id, task in self.tasks.items():
            files_used = task.get("files_involved", [])
            
            for file_path in files_used:
                # Check if another task creates this file
                creator_task_id = self.file_creators.get(file_path)
                
                if creator_task_id and creator_task_id != task_id:
                    # Inferred dependency: this task depends on the creator
                    self.dependency_graph[task_id].add(creator_task_id)
                    logger.info(
                        f"Inferred dependency: {task_id} depends on {creator_task_id} "
                        f"(file: {file_path})"
                    )
            
            # Additional inference: check for common file patterns
            self._infer_from_file_patterns(task_id, files_used)
    
    def _infer_from_file_patterns(self, task_id: str, files: List[str]):
        """
        Infer dependencies from file naming patterns.
        
        Examples:
        - If task creates 'models/user.py', tasks using 'api/user_routes.py' likely depend on it
        - If task creates 'services/auth.py', tests in 'tests/test_auth.py' depend on it
        """
        task_name = self.tasks[task_id].get("name", "").lower()
        
        for other_task_id, other_task in self.tasks.items():
            if other_task_id == task_id:
                continue
                
            other_files = other_task.get("files_involved", [])
            other_name = other_task.get("name", "").lower()
            
            # Pattern 1: Test files depend on implementation files
            if "test" in other_name and "test" not in task_name:
                # Check for matching module names
                for file_path in files:
                    module_name = self._extract_module_name(file_path)
                    for other_file in other_files:
                        if module_name in other_file:
                            self.dependency_graph[other_task_id].add(task_id)
                            logger.info(
                                f"Inferred test dependency: {other_task_id} depends on {task_id}"
                            )
            
            # Pattern 2: API routes depend on models/services
            if any(keyword in task_name for keyword in ["model", "schema", "service"]):
                if any(keyword in other_name for keyword in ["api", "route", "endpoint"]):
                    self.dependency_graph[other_task_id].add(task_id)
                    logger.info(
                        f"Inferred API dependency: {other_task_id} depends on {task_id}"
                    )
    
    def _extract_module_name(self, file_path: str) -> str:
        """Extract module name from file path (e.g., 'models/user.py' -> 'user')"""
        # Remove extension and directory
        parts = file_path.replace("\\", "/").split("/")
        filename = parts[-1]
        module = filename.split(".")[0]
        return module
    
    def get_ready_tasks(self, completed_task_ids: Set[str]) -> List[Dict[str, Any]]:
        """
        Get tasks that are ready to execute (all dependencies satisfied).
        
        Args:
            completed_task_ids: Set of task IDs that have been completed
        
        Returns:
            List of task objects ready for execution
        """
        ready_tasks = []
        
        for task_id, task in self.tasks.items():
            # Skip already completed tasks
            if task_id in completed_task_ids:
                continue
            
            # Check if all dependencies are satisfied
            dependencies = self.dependency_graph.get(task_id, set())
            
            if dependencies.issubset(completed_task_ids):
                ready_tasks.append(task)
        
        logger.info(f"Found {len(ready_tasks)} tasks ready for execution")
        return ready_tasks
    
    def has_circular_dependencies(self) -> bool:
        """
        Detect circular dependencies using DFS.
        
        Returns:
            True if circular dependencies exist, False otherwise
        """
        visited = set()
        rec_stack = set()
        
        def dfs(node: str) -> bool:
            """Depth-first search to detect cycles."""
            visited.add(node)
            rec_stack.add(node)
            
            # Check all dependencies
            for neighbor in self.dependency_graph.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Back edge found - circular dependency
                    logger.error(f"Circular dependency detected: {node} -> {neighbor}")
                    return True
            
            rec_stack.remove(node)
            return False
        
        # Check all tasks
        for task_id in self.tasks:
            if task_id not in visited:
                if dfs(task_id):
                    return True
        
        return False
    
    def get_dependency_chain(self, task_id: str) -> List[str]:
        """
        Get the full dependency chain for a task (topologically sorted).
        
        Args:
            task_id: The task ID to get dependencies for
        
        Returns:
            List of task IDs in execution order (dependencies first)
        """
        chain = []
        visited = set()
        
        def dfs(node: str):
            if node in visited:
                return
            visited.add(node)
            
            # Visit dependencies first
            for dep in self.dependency_graph.get(node, set()):
                dfs(dep)
            
            chain.append(node)
        
        dfs(task_id)
        return chain
    
    def get_all_dependencies(self, task_id: str) -> Set[str]:
        """
        Get all direct and transitive dependencies for a task.
        
        Args:
            task_id: The task ID
        
        Returns:
            Set of all dependency task IDs
        """
        all_deps = set()
        
        def collect_deps(node: str):
            for dep in self.dependency_graph.get(node, set()):
                if dep not in all_deps:
                    all_deps.add(dep)
                    collect_deps(dep)
        
        collect_deps(task_id)
        return all_deps
    
    def validate_dependency_exists(self, task_id: str) -> bool:
        """Check if a task ID exists in the dependency graph."""
        return task_id in self.tasks
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task object by ID."""
        return self.tasks.get(task_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the dependency graph.
        
        Returns:
            Dict with stats: total tasks, tasks with dependencies, etc.
        """
        total_tasks = len(self.tasks)
        tasks_with_deps = sum(1 for deps in self.dependency_graph.values() if deps)
        total_deps = sum(len(deps) for deps in self.dependency_graph.values())
        
        # Find tasks with no dependencies (can start immediately)
        independent_tasks = [
            task_id for task_id, deps in self.dependency_graph.items() 
            if not deps
        ]
        
        return {
            "total_tasks": total_tasks,
            "tasks_with_dependencies": tasks_with_deps,
            "total_dependency_edges": total_deps,
            "independent_tasks": len(independent_tasks),
            "independent_task_ids": independent_tasks,
            "has_circular_deps": self.has_circular_dependencies()
        }
