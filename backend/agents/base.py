"""
Base agent class that all agents inherit from.
Provides common functionality and interface definition.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from models import LLMClientProtocol


@dataclass
class AgentResult:
    """Result returned by an agent execution."""
    
    agent: str  # Agent identifier
    model: str  # Model used
    action: str  # Action performed
    content: str  # Main output content
    success: bool = True  # Whether execution succeeded
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional data
    context_updates: Dict[str, Any] = field(default_factory=dict)  # Updates to execution context


class BaseAgent(ABC):
    """
    Base class for all workflow agents.
    
    Each agent represents a node in the workflow graph and performs
    a specific task in the multi-agent pipeline.
    """
    
    # Agent identifier - must match node type in frontend
    agent_id: str = "base"
    
    # Display name for logging/tracing
    display_name: str = "Base Agent"
    
    # Default model to use (can be overridden per-call)
    default_model: str = "small"  # "small" or "large"
    
    def __init__(self, llm_client: LLMClientProtocol):
        """
        Initialize the agent with an LLM client.
        
        Args:
            llm_client: The LLM client to use for completions
        """
        self.llm = llm_client
    
    @abstractmethod
    async def execute(
        self,
        user_message: str,
        context: Dict[str, Any],
        settings: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
    ) -> AgentResult:
        """
        Execute the agent's task.
        
        Args:
            user_message: The original user query
            context: Execution context with results from previous nodes
            settings: Node-specific settings from frontend
            model: Model to use (overrides default)
            
        Returns:
            AgentResult with the execution results
        """
        pass
    
    async def _chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> str:
        """
        Helper method to call the LLM.
        
        Args:
            messages: Chat messages
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        return await self.llm.chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    
    def _build_system_prompt(self, template: str, **kwargs) -> str:
        """
        Build a system prompt from a template.
        
        Args:
            template: String template with {placeholders}
            **kwargs: Values to fill in placeholders
            
        Returns:
            Formatted system prompt
        """
        return template.format(**kwargs)


