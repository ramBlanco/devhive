from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAgent(ABC):
    """
    Abstract Base Class for all agents in the DevHive system.
    
    This ensures all agents (Explorer, Architect, Implementer) follow
    a consistent interface, making the system extensible.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent with a name and optional configuration.
        
        Args:
            name: The identifier for this agent.
            config: Optional configuration dictionary (e.g., LLM model, temperature).
        """
        self.name = name
        self.config = config or {}

    @abstractmethod
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's logic based on the provided context.
        
        Args:
            context: The shared context dictionary containing previous agents' outputs.
            
        Returns:
            A dictionary containing the agent's specific output to be merged into the context.
        """
        pass
