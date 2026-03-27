from typing import Dict, Any, Optional, List
from devhive.core.project_state_manager import ProjectStateManager
from devhive.core.artifact_manager import ArtifactManager

class ContextRouter:
    """
    Manages which agents receive what information.
    Loads summaries and specific data to minimize context window usage.
    
    **HYBRID MODE (Option B):**
    - Auto-injects relevant context via TF-IDF retrieval
    - Agents can also use devhive_search_memory for deeper queries
    """
    def __init__(
        self, 
        project_state_manager: ProjectStateManager, 
        artifact_manager: ArtifactManager,
        memory_store=None  # Optional: MemoryStore for TF-IDF retrieval
    ):
        self.state_manager = project_state_manager
        self.artifact_manager = artifact_manager
        self.memory_store = memory_store

    def get_project_guidelines(self) -> str:
        """Retrieves project guidelines if available."""
        try:
            from devhive.utils.filesystem import read_file
            return read_file("GUIDELINES.md")
        except Exception:
            return "Guidelines not found."

    def get_agent_skills(self, agent_role: str) -> Dict[str, str]:
        """Retrieves global skills and role-specific skills from the package."""
        skills = {}
        try:
            from pathlib import Path
            import logging
            skills_dir = Path(__file__).parent.parent / "skills"
            
            paths_to_check = [skills_dir / "global"]
            if agent_role:
                paths_to_check.append(skills_dir / agent_role.lower())
                
            for path in paths_to_check:
                if path.exists() and path.is_dir():
                    for md_file in path.glob("*.md"):
                        try:
                            with open(md_file, "r", encoding="utf-8") as f:
                                skills[f"{path.name}/{md_file.stem}"] = f.read()
                        except Exception as inner_e:
                            logging.warning(f"Failed to read skill file {md_file}: {inner_e}")
        except Exception as e:
            import logging
            logging.warning(f"Failed to load agent skills: {e}")
        return skills

    def get_context(self, agent_role: str) -> Dict[str, Any]:
        state = self.state_manager.get_state()
        
        # Base context: Project info and stage
        base_context = {
            "project_name": state["project"],
            "current_stage": state["stage"],
            "files_generated_summary": len(state.get("files_generated", [])),
            "agent_skills": self.get_agent_skills(agent_role),
        }

        # Role-specific context loading
        if agent_role == "CEO":
            # CEO needs summarized state of all artifacts
            summaries = {}
            for step, artifact_id in state["artifacts"].items():
                if artifact_id:
                    summaries[step] = self.artifact_manager.load_summary(artifact_id)
                else:
                    summaries[step] = "Not Started"
            base_context["artifacts_summary"] = summaries
            base_context["project_status"] = state.get("status", "unknown")
            return base_context

        elif agent_role == "Explorer":
            # Explorer needs user request (assumed passed separately or stored)
            # and potentially existing constraints/dependencies if iterating
            base_context["project_guidelines"] = self.get_project_guidelines()
            return base_context

        elif agent_role == "Proposal":
            # Proposal needs Explorer artifact
            explorer_id = state["artifacts"].get("exploration")
            if explorer_id:
                base_context["exploration_artifact"] = self.artifact_manager.load_artifact(explorer_id)
            else:
                base_context["exploration_artifact"] = "Missing"
            return base_context

        elif agent_role == "Architect":
            # Architect needs Proposal artifact
            proposal_id = state["artifacts"].get("proposal")
            if proposal_id:
                base_context["proposal_artifact"] = self.artifact_manager.load_artifact(proposal_id)
            else:
                base_context["proposal_artifact"] = "Missing"
            return base_context

        elif agent_role == "TaskPlanner": # Scrum Master
            # Task Planner needs Architecture artifact
            arch_id = state["artifacts"].get("architecture")
            if arch_id:
                base_context["architecture_artifact"] = self.artifact_manager.load_artifact(arch_id)
            else:
                base_context["architecture_artifact"] = "Missing"
            return base_context

        elif agent_role == "Developer": # Implementation
            # Developer needs Architecture + Tasks
            arch_id = state["artifacts"].get("architecture")
            tasks_id = state["artifacts"].get("tasks")
            
            # Dynamic Workflow: If architecture/tasks are missing (skipped), provide earlier artifacts
            if arch_id:
                base_context["architecture_artifact"] = self.artifact_manager.load_artifact(arch_id)
            if tasks_id:
                base_context["tasks_artifact"] = self.artifact_manager.load_artifact(tasks_id)
            
            # Fallback for simpler workflows
            if not arch_id or not tasks_id:
                explorer_id = state["artifacts"].get("exploration")
                proposal_id = state["artifacts"].get("proposal")
                if explorer_id:
                     base_context["exploration_artifact"] = self.artifact_manager.load_artifact(explorer_id)
                if proposal_id:
                     base_context["proposal_artifact"] = self.artifact_manager.load_artifact(proposal_id)
            
            # Should also know existing files
            base_context["existing_files"] = state.get("files_generated", [])
            base_context["project_guidelines"] = self.get_project_guidelines()
            return base_context

        elif agent_role == "QA":
            # QA needs Implementation Plan (or just code access) + Architecture
            impl_id = state["artifacts"].get("implementation")
            arch_id = state["artifacts"].get("architecture")
            
            if impl_id:
                base_context["implementation_artifact"] = self.artifact_manager.load_artifact(impl_id)
            
            if arch_id:
                base_context["architecture_artifact"] = self.artifact_manager.load_summary(arch_id)
            else:
                # Fallback: Use exploration/proposal as spec for tests
                explorer_id = state["artifacts"].get("exploration")
                proposal_id = state["artifacts"].get("proposal")
                if explorer_id:
                     base_context["exploration_artifact"] = self.artifact_manager.load_artifact(explorer_id)
                if proposal_id:
                     base_context["proposal_artifact"] = self.artifact_manager.load_artifact(proposal_id)
            
            base_context["files_to_test"] = state.get("files_generated", [])
            return base_context

        elif agent_role == "Auditor":
            # Auditor needs everything (summarized) + Final Implementation details
            summaries = {}
            for step, artifact_id in state["artifacts"].items():
                if artifact_id:
                    summaries[step] = self.artifact_manager.load_summary(artifact_id)
            base_context["project_history"] = summaries
            return base_context

        elif agent_role == "Archivist":
            # Archivist needs final state
            base_context["final_state"] = state
            return base_context

        return base_context
    
    def _enhance_with_tfidf(
        self, 
        base_context: Dict[str, Any], 
        agent_role: str,
        query_hints: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        HYBRID MODE: Enhance context with TF-IDF retrieved memories.
        
        Args:
            base_context: Base context from traditional routing
            agent_role: Agent requesting context
            query_hints: Optional query terms to guide retrieval
        
        Returns:
            Enhanced context with relevant memory chunks
        """
        if not self.memory_store:
            return base_context  # No memory store available
        
        # Build query based on agent role and hints
        query_terms = query_hints or []
        
        # Add role-specific queries
        role_queries = {
            "Developer": ["implementation", "architecture", "tasks", "code structure"],
            "QA": ["tests", "validation", "implementation", "requirements"],
            "Auditor": ["verification", "consistency", "architecture", "security"],
            "Proposal": ["requirements", "constraints", "dependencies"],
            "Architect": ["design", "architecture", "components", "proposal"],
            "TaskPlanner": ["tasks", "architecture", "planning", "breakdown"]
        }
        
        query_terms.extend(role_queries.get(agent_role, []))
        query = " ".join(query_terms)
        
        # Retrieve top relevant chunks
        try:
            relevant_memories = self.memory_store.search_memory(
                query=query,
                top_k=3,  # Limit to top 3 to avoid context bloat
                chunk_types=["artifact", "agent_response"]  # Focus on substantive content
            )
            
            # Add to context under "relevant_memories" key
            if relevant_memories:
                base_context["relevant_memories"] = [
                    {
                        "source": f"{m['agent_name']} - {m['step_name']}",
                        "content_preview": m["content"][:200] + "...",
                        "relevance": round(m["relevance_score"], 2)
                    }
                    for m in relevant_memories
                ]
        except Exception as e:
            # Fail gracefully if TF-IDF retrieval fails
            import logging
            logging.warning(f"TF-IDF retrieval failed for {agent_role}: {e}")
        
        return base_context
