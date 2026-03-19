from typing import Any, Dict, Optional
from ..core.agent_interface import BaseAgent
from ..orchestrator.orchestrator import Orchestrator
from ..agents.explorer_agent import ExplorerAgent
from ..agents.architect_agent import ArchitectAgent
from ..agents.implementer_agent import ImplementerAgent

class DevTeamAgent:
    """
    Public interface for the DevHive system.
    
    This class is the entry point for external agents or users to interact
    with the development team. It encapsulates the complexity of the
    orchestrator and the individual agents.
    
    Usage:
        dev_team = DevTeamAgent()
        result = dev_team.build_feature("Add CSV export to dashboard")
    """
    
    def __init__(self, agent_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the DevTeamAgent with optional configuration.
        
        Args:
            agent_config: Configuration dictionary for the agents (e.g., LLM settings).
        """
        self.config = agent_config or {}
        
        # Instantiate the specialized agents
        # In a real system, we might load these dynamically or configure them
        # via dependency injection.
        self.explorer = ExplorerAgent("Explorer", self.config)
        self.architect = ArchitectAgent("Architect", self.config)
        self.implementer = ImplementerAgent("Implementer", self.config)
        
        # Configure the orchestrator pipeline
        self.orchestrator = Orchestrator([
            self.explorer,
            self.architect,
            self.implementer
        ])

    def build_feature(self, request: str) -> Dict[str, Any]:
        """
        Main entry point to request a feature implementation.
        
        Args:
            request: A natural language description of the feature request.
            
        Returns:
            A dictionary containing the full execution context, including:
            - The original request
            - Analysis from Explorer
            - Design from Architect
            - Implementation plan/code from Implementer
        """
        # Delegate execution to the orchestrator
        final_context = self.orchestrator.run(request)
        
        # Return the final result
        return final_context
