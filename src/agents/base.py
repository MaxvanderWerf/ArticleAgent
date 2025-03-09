"""
Base Agent class for the Agentic Writer System.
Defines the common interface and functionality for all agents.
"""

from typing import Dict, Optional, TYPE_CHECKING, Any
import time
from datetime import datetime

# This avoids circular imports
if TYPE_CHECKING:
    from src.agentic_system import AgenticSystem

class Agent:
    """
    Base class for all agents in the system.
    
    Attributes:
        name: The name of the agent
        system: Reference to the parent AgenticSystem
    """
    
    def __init__(self, name: str, system: 'AgenticSystem'):
        """
        Initialize a new agent.
        
        Args:
            name: The name of the agent
            system: Reference to the parent AgenticSystem
        """
        self.name = name
        self.system = system
    
    def log(self, message: str):
        """
        Log a message from this agent with timestamp.
        
        Args:
            message: The message to log
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{self.name}] {message}")
    
    def act(self, task: str, context: Optional[Dict] = None) -> Dict:
        """
        Perform the agent's primary action.
        
        Args:
            task: Description of the task to perform
            context: Optional context information
            
        Returns:
            Dictionary containing the results of the action
        """
        raise NotImplementedError("Subclasses must implement the act method") 