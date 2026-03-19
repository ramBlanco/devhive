from typing import List, Dict, Any
from ..core.agent_interface import BaseAgent
from ..core.context import SharedContext

class Orchestrator:
    """
    Manages the execution workflow of the agent team.
    
    The orchestrator is responsible for:
    1. Initializing the shared context.
    2. Invoking agents in the correct sequence.
    3. Passing context between agents.
    4. Collecting and returning the final result.
    """

    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents

    def run(self, initial_request: str) -> Dict[str, Any]:
        """
        Execute the agent pipeline for a given request.
        
        Args:
            initial_request: The user's request string.
            
        Returns:
            The final context state containing all agent outputs.
        """
        # Initialize context with the request
        context = SharedContext({"request": initial_request})
        
        print(f"--- Orchestrator started for request: '{initial_request}' ---")

        for agent in self.agents:
            try:
                print(f"-> Invoking agent: {agent.name}")
                
                # Get current context as a dictionary for the agent
                current_context_dict = context.to_dict()
                
                # Run agent logic
                result = agent.run(current_context_dict)
                
                # Update shared context with result
                if result:
                    context.update(result)
                    
            except Exception as e:
                print(f"Error in agent {agent.name}: {str(e)}")
                # In a real system, we might retry or fail gracefully here
                context.set("error", str(e))
                break
                
        print("--- Orchestrator finished ---")
        return context.to_dict()
