"""
Task-based pipeline orchestrator.
Manages agent sequence and returns Task launch instructions for OpenCode.
"""

import json
import logging
from typing import Dict, Any, Optional

from devhive.core.project_state_manager import ProjectStateManager
from devhive.core.artifact_manager import ArtifactManager
from devhive.core.prompt_builder import PromptBuilder
from devhive.core.context_router import ContextRouter
from devhive.core.memory_store import MemoryStore
from devhive.agents.ceo import CEOAgent
from devhive.utils.validation import ResponseValidator

logger = logging.getLogger(__name__)


class TaskOrchestrator:
    """
    Orchestrates the DevHive pipeline using Task-based execution.
    
    This class is a thin wrapper around existing components that:
    - Determines next agent using CEO's deterministic logic
    - Builds prompts using PromptBuilder
    - Validates responses using ResponseValidator
    - Saves artifacts using ArtifactManager
    - Returns structured envelopes for OpenCode
    """
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.state_manager = ProjectStateManager(project_name)
        self.artifact_manager = ArtifactManager(project_name)
        self.memory_store = MemoryStore(project_name)
        self.context_router = ContextRouter(
            self.state_manager, 
            self.artifact_manager,
            self.memory_store  # Enable hybrid TF-IDF retrieval
        )
        self.ceo = CEOAgent(project_name)
        
    def get_next_task(self, requirements: Optional[str] = None) -> Dict[str, Any]:
        """
        Returns Task launch instructions for the next agent.
        
        Args:
            requirements: Optional requirements (only needed for Explorer)
        
        Returns:
            {
                "status": "pending" | "complete",
                "agent": "Explorer" | "Proposal" | ...,
                "system_prompt": "...",
                "user_prompt": "...",
                "task_description": "Short description for Task tool",
                "expected_keys": [...],  # For validation help
                "context": {...}  # Minimal context for debugging
            }
        """
        # Use CEO's deterministic logic to get next agent
        next_decision = self.ceo.get_next_agent_deterministic()
        next_agent = next_decision.get("agent")
        
        if not next_agent:
             return {
                "status": "error",
                "message": "CEO agent failed to determine next step"
             }

        # Check if pipeline is complete
        if next_agent == "Complete":
            return {
                "status": "complete",
                "message": "All pipeline stages finished",
                "reason": next_decision.get("reason")
            }
        
        # Get context for this agent from ContextRouter
        context = self.context_router.get_context(next_agent)
        
        # Build prompts using existing PromptBuilder
        try:
            prompts = PromptBuilder.build_prompts(
                agent_role=next_agent,
                context=context,
                requirements=requirements  # Only used by Explorer
            )
        except Exception as e:
            logger.error(f"Failed to build prompts for {next_agent}: {e}")
            return {
                "status": "error",
                "message": f"Failed to build prompts: {str(e)}"
            }
        
        # Get expected keys for validation help
        expected_keys = ResponseValidator.get_expected_keys(next_agent)
        
        # Store prompts in memory database
        self.memory_store.store_memory(
            chunk_type="system_prompt",
            content=prompts["system_prompt"],
            agent_name=next_agent,
            metadata={"requirements": requirements}
        )
        self.memory_store.store_memory(
            chunk_type="user_prompt",
            content=prompts["user_prompt"],
            agent_name=next_agent,
            metadata={"context_keys": list(context.keys())}
        )
        
        return {
            "status": "pending",
            "agent": next_agent,
            "reason": next_decision.get("reason"),
            "system_prompt": prompts["system_prompt"],
            "user_prompt": prompts["user_prompt"],
            "task_description": f"Execute DevHive {next_agent} agent",
            "expected_keys": expected_keys,
            "context": {
                "project": self.project_name,
                "stage": self.state_manager.get_state().get("stage"),
                "artifacts_present": [k for k, v in context.get("artifacts", {}).items() if v is not None]
            }
        }
    
    def submit_result(self, agent_name: str, llm_response: str) -> Dict[str, Any]:
        """
        Process agent result, validate, save artifact, and return structured envelope.
        
        Args:
            agent_name: Name of agent that produced result (Explorer, Proposal, etc.)
            llm_response: Raw LLM response (JSON string)
        
        Returns:
            {
                "status": "success" | "error",
                "message": "...",
                "artifact_id": "...",
                "executive_summary": "...",
                "next_agent": "..." | None,
                "agent_completed": "..."
            }
        """
        # Parse JSON response
        try:
            data = json.loads(llm_response)
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "message": f"Invalid JSON response: {str(e)}",
                "expected_keys": ResponseValidator.get_expected_keys(agent_name)
            }
        
        # Validate response using existing validator
        is_valid, error_msg = self._validate_response(agent_name, data)
        
        if not is_valid:
            return {
                "status": "error",
                "message": error_msg,
                "expected_keys": ResponseValidator.get_expected_keys(agent_name)
            }
        
        # Save artifact
        try:
            artifact_id = self._save_artifact(agent_name, data)
        except Exception as e:
            logger.error(f"Failed to save artifact for {agent_name}: {e}")
            return {
                "status": "error",
                "message": f"Failed to save artifact: {str(e)}"
            }
        
        # Update state
        artifact_key = self._get_artifact_key(agent_name)
        self.state_manager.update_artifact(artifact_key, artifact_id)
        
        # Handle side effects for agents that write files
        if agent_name == "Developer":
            from devhive.agents.developer import DeveloperAgent
            agent = DeveloperAgent(self.project_name)
            file_paths = agent.write_files(data)
            self.state_manager.add_files(file_paths)
        elif agent_name == "QA":
            from devhive.agents.qa import QAAgent
            agent = QAAgent(self.project_name)
            file_paths = agent.write_test_files(data)
            self.state_manager.add_files(file_paths)
        elif agent_name == "Explorer":
            if "new_guidelines_content" in data:
                from devhive.utils.filesystem import write_file
                write_file("GUIDELINES.md", data["new_guidelines_content"])
        
        # Generate executive summary
        summary = self._generate_summary(agent_name, data)
        
        # Store agent response and artifact in memory database
        self.memory_store.store_memory(
            chunk_type="agent_response",
            content=llm_response,
            agent_name=agent_name,
            step_name=artifact_key,
            metadata={"artifact_id": artifact_id, "summary": summary}
        )
        self.memory_store.store_memory(
            chunk_type="artifact",
            content=json.dumps(data, indent=2),
            agent_name=agent_name,
            step_name=artifact_key,
            metadata={"artifact_id": artifact_id}
        )
        
        # Get next agent
        next_decision = self.ceo.get_next_agent_deterministic()
        next_agent = next_decision.get("agent")
        
        return {
            "status": "success",
            "message": f"{agent_name} completed successfully",
            "agent_completed": agent_name,
            "artifact_id": artifact_id,
            "executive_summary": summary,
            "next_agent": next_agent if next_agent != "Complete" else None,
            "next_reason": next_decision.get("reason") if next_agent != "Complete" else None
        }
    
    def _validate_response(self, agent_name: str, response: Dict[str, Any]) -> tuple[bool, str]:
        """Validate response using appropriate validator method."""
        validators = {
            "Explorer": ResponseValidator.validate_explorer,
            "Proposal": ResponseValidator.validate_proposal,
            "Architect": ResponseValidator.validate_architect,
            "TaskPlanner": ResponseValidator.validate_task_planner,
            "Developer": ResponseValidator.validate_developer,
            "QA": ResponseValidator.validate_qa,
            "Auditor": ResponseValidator.validate_auditor,
            "Archivist": lambda x: (True, "")  # Archivist doesn't need validation
        }
        
        validator_func = validators.get(agent_name)
        if not validator_func:
            return False, f"Unknown agent: {agent_name}"
        
        return validator_func(response)
    
    def _save_artifact(self, agent_name: str, data: Dict[str, Any]) -> str:
        """Save artifact and return its ID."""
        artifact_key = self._get_artifact_key(agent_name)
        return self.artifact_manager.save_artifact(artifact_key, data)
    
    def _get_artifact_key(self, agent_name: str) -> str:
        """Map agent name to artifact key used in state."""
        mapping = {
            "Explorer": "exploration",
            "Proposal": "proposal",
            "Architect": "architecture",
            "TaskPlanner": "tasks",
            "Developer": "implementation",
            "QA": "tests",
            "Auditor": "verification",
            "Archivist": "archive"
        }
        return mapping.get(agent_name, agent_name.lower())
    
    def _generate_summary(self, agent_name: str, data: Dict[str, Any]) -> str:
        """
        Generate 1-3 sentence executive summary of agent's work.
        
        This is a default implementation. Individual agents can override
        via their generate_summary() method for more specific summaries.
        """
        summaries = {
            "Explorer": self._summarize_explorer,
            "Proposal": self._summarize_proposal,
            "Architect": self._summarize_architect,
            "TaskPlanner": self._summarize_task_planner,
            "Developer": self._summarize_developer,
            "QA": self._summarize_qa,
            "Auditor": self._summarize_auditor,
            "Archivist": self._summarize_archivist
        }
        
        summarizer = summaries.get(agent_name, lambda x: f"{agent_name} completed successfully.")
        return summarizer(data)
    
    def _summarize_explorer(self, data: Dict[str, Any]) -> str:
        """Generate summary for Explorer agent."""
        constraints_count = len(data.get("constraints", []))
        deps_count = len(data.get("dependencies", []))
        base_summary = (
            f"Analyzed requirements and identified {constraints_count} constraints "
            f"and {deps_count} dependencies. Key user need: {data.get('user_needs', 'N/A')[:80]}..."
        )
        
        extra_info = []
        if "new_guidelines_content" in data:
            extra_info.append("Created GUIDELINES.md with best practices.")
        if "clarification_question" in data:
            extra_info.append(f"QUESTION FOR USER: {data['clarification_question']}")
            
        if extra_info:
            return f"{base_summary} {' '.join(extra_info)}"
        return base_summary
    
    def _summarize_proposal(self, data: Dict[str, Any]) -> str:
        """Generate summary for Proposal agent."""
        criteria_count = len(data.get("acceptance_criteria", []))
        return (
            f"Created feature proposal with {criteria_count} acceptance criteria. "
            f"Feature: {data.get('feature_description', 'N/A')[:80]}..."
        )
    
    def _summarize_architect(self, data: Dict[str, Any]) -> str:
        """Generate summary for Architect agent."""
        components_count = len(data.get("components", []))
        apis_count = len(data.get("apis", []))
        return (
            f"Designed architecture using {data.get('architecture_pattern', 'N/A')} pattern "
            f"with {components_count} components and {apis_count} APIs."
        )
    
    def _summarize_task_planner(self, data: Dict[str, Any]) -> str:
        """Generate summary for TaskPlanner agent."""
        epics_count = len(data.get("epics", []))
        tasks_count = len(data.get("tasks", []))
        complexity = data.get("estimated_complexity", "unknown")
        return (
            f"Created task breakdown with {epics_count} epics and {tasks_count} tasks. "
            f"Estimated complexity: {complexity}."
        )
    
    def _summarize_developer(self, data: Dict[str, Any]) -> str:
        """Generate summary for Developer agent."""
        files_count = len(data.get("files", []))
        return (
            f"Implemented {files_count} files using strategy: "
            f"{data.get('implementation_strategy', 'N/A')[:80]}..."
        )
    
    def _summarize_qa(self, data: Dict[str, Any]) -> str:
        """Generate summary for QA agent."""
        tests_count = len(data.get("unit_tests", []))
        files_count = len(data.get("files", []))
        return (
            f"Generated {tests_count} unit tests across {files_count} test files. "
            f"Strategy: {data.get('test_strategy', 'N/A')[:60]}..."
        )
    
    def _summarize_auditor(self, data: Dict[str, Any]) -> str:
        """Generate summary for Auditor agent."""
        consistent = data.get("architecture_consistency", False)
        missing_count = len(data.get("missing_pieces", []))
        risks_count = len(data.get("security_risks", []))
        status = "consistent" if consistent else "inconsistent"
        return (
            f"Architecture is {status}. Found {missing_count} missing pieces "
            f"and {risks_count} security risks."
        )
    
    def _summarize_archivist(self, data: Dict[str, Any]) -> str:
        """Generate summary for Archivist agent."""
        return "Project archived successfully. All artifacts saved and pipeline complete."
