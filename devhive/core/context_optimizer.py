"""
Context optimization utilities for parallel development.

Provides aggressive summarization and filtering of context to prevent
token limit errors when spawning parallel developer agents.
"""

import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logger.warning("tiktoken not available, using fallback token estimation")


class ContextOptimizer:
    """Optimizes context for parallel developer agents to prevent token limits."""
    
    def __init__(self, model: str = "gpt-4"):
        """
        Initialize the optimizer.
        
        Args:
            model: Model name for tokenization (default: gpt-4)
        """
        self.model = model
        self.encoding = None
        
        if TIKTOKEN_AVAILABLE:
            try:
                self.encoding = tiktoken.encoding_for_model(model)
            except KeyError:
                # Fallback to cl100k_base for unknown models
                self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        if self.encoding:
            return len(self.encoding.encode(text))
        else:
            # Fallback: ~4 chars per token on average
            return len(text) // 4
    
    def truncate_text(self, text: str, max_chars: int) -> str:
        """
        Truncate text to maximum character count.
        
        Args:
            text: Text to truncate
            max_chars: Maximum characters
            
        Returns:
            Truncated text with ellipsis if needed
        """
        if not text:
            return ""
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "..."
    
    def summarize_exploration(self, exploration: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggressively summarize exploration artifact.
        
        Keeps only:
        - user_needs (truncated to 200 chars)
        - Top 3 constraints
        - Top 3 dependencies (names only)
        
        Args:
            exploration: Full exploration artifact
            
        Returns:
            Summarized exploration
        """
        if not exploration:
            return {}
        
        summarized = {}
        
        # User needs - truncated
        if "user_needs" in exploration:
            summarized["user_needs"] = self.truncate_text(
                exploration["user_needs"], 200
            )
        
        # Top 3 constraints
        if "constraints" in exploration:
            constraints = exploration["constraints"]
            if isinstance(constraints, list):
                summarized["constraints"] = constraints[:3]
            else:
                summarized["constraints"] = self.truncate_text(str(constraints), 150)
        
        # Top 3 dependencies (names only)
        if "dependencies" in exploration:
            deps = exploration["dependencies"]
            if isinstance(deps, list):
                summarized["dependencies"] = [
                    dep.get("name", str(dep)) if isinstance(dep, dict) else str(dep)
                    for dep in deps[:3]
                ]
            else:
                summarized["dependencies"] = self.truncate_text(str(deps), 100)
        
        return summarized
    
    def summarize_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggressively summarize proposal artifact.
        
        Keeps only:
        - feature_description (truncated to 200 chars)
        - Top 3 acceptance_criteria
        - implementation_approach (truncated to 150 chars)
        
        Args:
            proposal: Full proposal artifact
            
        Returns:
            Summarized proposal
        """
        if not proposal:
            return {}
        
        summarized = {}
        
        # Feature description - truncated
        if "feature_description" in proposal:
            summarized["feature_description"] = self.truncate_text(
                proposal["feature_description"], 200
            )
        
        # Top 3 acceptance criteria
        if "acceptance_criteria" in proposal:
            criteria = proposal["acceptance_criteria"]
            if isinstance(criteria, list):
                summarized["acceptance_criteria"] = [
                    self.truncate_text(str(c), 100) for c in criteria[:3]
                ]
            else:
                summarized["acceptance_criteria"] = self.truncate_text(str(criteria), 150)
        
        # Implementation approach - truncated
        if "implementation_approach" in proposal:
            summarized["implementation_approach"] = self.truncate_text(
                proposal["implementation_approach"], 150
            )
        
        return summarized
    
    def summarize_architecture(
        self, 
        architecture: Dict[str, Any],
        task_files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Summarize architecture artifact, filtering to task-relevant components.
        
        Keeps only:
        - pattern (full)
        - components that match task files (if provided)
        - data_flow (truncated to 200 chars)
        
        Args:
            architecture: Full architecture artifact
            task_files: List of files this task will modify (for filtering)
            
        Returns:
            Summarized architecture
        """
        if not architecture:
            return {}
        
        summarized = {}
        
        # Pattern - keep full
        if "pattern" in architecture:
            summarized["pattern"] = architecture["pattern"]
        
        # Components - filter by task files if provided
        if "components" in architecture:
            components = architecture["components"]
            if isinstance(components, list) and task_files:
                # Filter components whose files overlap with task files
                relevant_components = []
                for comp in components:
                    if isinstance(comp, dict):
                        comp_files = comp.get("files", [])
                        if any(tf in str(comp_files) for tf in task_files):
                            # Keep only name and purpose
                            relevant_components.append({
                                "name": comp.get("name", ""),
                                "purpose": self.truncate_text(comp.get("purpose", ""), 100)
                            })
                summarized["components"] = relevant_components[:5]  # Max 5
            elif isinstance(components, list):
                # No task files - keep top 3 components with minimal info
                summarized["components"] = [
                    {
                        "name": comp.get("name", "") if isinstance(comp, dict) else str(comp),
                        "purpose": self.truncate_text(
                            comp.get("purpose", "") if isinstance(comp, dict) else "", 80
                        )
                    }
                    for comp in components[:3]
                ]
        
        # Data flow - truncated
        if "data_flow" in architecture:
            summarized["data_flow"] = self.truncate_text(
                str(architecture["data_flow"]), 200
            )
        
        return summarized
    
    def filter_dependency_outputs(
        self, 
        dependency_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Filter dependency outputs to remove file contents.
        
        Keeps only:
        - File paths
        - Function/class signatures (if available)
        - Removes full file contents
        
        Args:
            dependency_outputs: Full dependency outputs from other developers
            
        Returns:
            Filtered dependency outputs
        """
        if not dependency_outputs:
            return {}
        
        filtered = {}
        
        for task_id, output in dependency_outputs.items():
            if not isinstance(output, dict):
                filtered[task_id] = str(output)
                continue
            
            task_filtered = {}
            
            # Keep files list (paths only)
            if "files" in output:
                files = output["files"]
                if isinstance(files, list):
                    task_filtered["files"] = [
                        f.get("path", str(f)) if isinstance(f, dict) else str(f)
                        for f in files
                    ]
                else:
                    task_filtered["files"] = str(files)
            
            # Keep summary/description if present
            if "summary" in output:
                task_filtered["summary"] = self.truncate_text(output["summary"], 150)
            
            if "description" in output:
                task_filtered["description"] = self.truncate_text(output["description"], 150)
            
            # Extract function/class names if in implementation_details
            if "implementation_details" in output:
                details = output["implementation_details"]
                if isinstance(details, str):
                    # Simple extraction - look for common patterns
                    task_filtered["exports"] = self.truncate_text(details, 100)
            
            filtered[task_id] = task_filtered
        
        return filtered
    
    def estimate_context_size(self, context: Dict[str, Any]) -> Dict[str, int]:
        """
        Estimate token size of context components.
        
        Args:
            context: Full context dictionary
            
        Returns:
            Dictionary mapping component names to estimated token counts
        """
        sizes = {}
        
        for key, value in context.items():
            if value is None:
                sizes[key] = 0
            else:
                text = json.dumps(value, default=str)
                sizes[key] = self.estimate_tokens(text)
        
        sizes["total"] = sum(sizes.values())
        
        return sizes
    
    def optimize_full_context(
        self,
        context: Dict[str, Any],
        task_files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Apply all optimizations to a full context dictionary.
        
        Args:
            context: Full context from ParallelDeveloperAgent
            task_files: Files this task will modify
            
        Returns:
            Optimized context
        """
        optimized = {}
        
        # Optimize each component
        if "exploration" in context and context["exploration"]:
            optimized["exploration"] = self.summarize_exploration(context["exploration"])
        
        if "proposal" in context and context["proposal"]:
            optimized["proposal"] = self.summarize_proposal(context["proposal"])
        
        if "architecture" in context and context["architecture"]:
            optimized["architecture"] = self.summarize_architecture(
                context["architecture"], task_files
            )
        
        if "dependency_outputs" in context and context["dependency_outputs"]:
            optimized["dependency_outputs"] = self.filter_dependency_outputs(
                context["dependency_outputs"]
            )
        
        # Pass through other fields as-is (they should already be minimal)
        for key in ["task_description", "task_id", "files_to_modify"]:
            if key in context:
                optimized[key] = context[key]
        
        return optimized
    
    def log_optimization_stats(
        self,
        original_context: Dict[str, Any],
        optimized_context: Dict[str, Any]
    ) -> None:
        """
        Log statistics about context optimization.
        
        Args:
            original_context: Original context before optimization
            optimized_context: Context after optimization
        """
        original_sizes = self.estimate_context_size(original_context)
        optimized_sizes = self.estimate_context_size(optimized_context)
        
        reduction_pct = (
            100 * (1 - optimized_sizes["total"] / original_sizes["total"])
            if original_sizes["total"] > 0 else 0
        )
        
        logger.info(
            f"Context optimization: {original_sizes['total']} → "
            f"{optimized_sizes['total']} tokens ({reduction_pct:.1f}% reduction)"
        )
        
        # Log component-wise breakdown
        for key in original_sizes:
            if key != "total" and key in optimized_sizes:
                logger.debug(
                    f"  {key}: {original_sizes[key]} → {optimized_sizes[key]} tokens"
                )
