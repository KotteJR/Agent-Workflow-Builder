"""
Supervisor Agent - Analyzes workflow graph and optimizes execution plans.

The Supervisor understands the downstream nodes and creates an optimized
execution plan based on the query and available tools.
"""

import json
from typing import Any, Dict, List, Optional

from agents.base import BaseAgent, AgentResult
from models import LLMClientProtocol


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent that analyzes queries and plans execution.
    
    Capabilities:
    - Analyzes user queries to understand intent
    - Examines downstream nodes to plan execution
    - Provides search guidance for semantic search
    - Identifies parallel execution opportunities
    """
    
    agent_id = "supervisor"
    display_name = "Supervisor Agent"
    default_model = "small"
    
    SYSTEM_PROMPT_TEMPLATE = """You are a Supervisor Agent analyzing a user's request to plan and guide workflow execution.

Available downstream nodes in this workflow:
{available_nodes}

Your planning style: {planning_style}
Optimization level: {optimization_level}
{supervisor_instructions}

TASK TYPE DETECTION:
- FILE TRANSFORMATION: If the request involves converting, transforming, or extracting data from files (PDF, CSV, etc.), focus on guiding the transformation process.
- ANALYSIS/SEARCH: If the request involves answering questions or finding information, provide search guidance.

For FILE TRANSFORMATION tasks:
- Provide clear instructions on what to extract or convert
- Specify the desired output format and structure
- Describe what columns/fields should be created

For ANALYSIS/SEARCH tasks:
- Provide search guidance for finding relevant information
- Recommend which nodes to use

OUTPUT: Provide a clear, actionable plan that guides downstream agents. Be specific about what should be done with the content."""

    async def execute(
        self,
        user_message: str,
        context: Dict[str, Any],
        settings: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
    ) -> AgentResult:
        """
        Analyze the query and create an execution plan.
        
        Args:
            user_message: User's query
            context: Contains 'downstream_nodes' list of available nodes
            settings: Contains 'planningStyle' and 'optimizationLevel'
            model: Model to use
            
        Returns:
            AgentResult with execution plan
        """
        settings = settings or {}
        planning_style = settings.get("planningStyle", "optimized")
        optimization_level = settings.get("optimizationLevel", "basic")
        supervisor_prompt = settings.get("supervisorPrompt", "")
        
        # Get downstream nodes from context
        downstream_nodes = context.get("downstream_nodes", [])
        available_nodes = ", ".join(downstream_nodes) if downstream_nodes else "semantic_search, synthesis"
        
        # Add supervisor instructions if provided
        supervisor_instructions = ""
        if supervisor_prompt:
            supervisor_instructions = f"\nAdditional instructions from user:\n{supervisor_prompt}\n"
        
        system_prompt = self._build_system_prompt(
            self.SYSTEM_PROMPT_TEMPLATE,
            available_nodes=available_nodes,
            planning_style=planning_style,
            optimization_level=optimization_level,
            supervisor_instructions=supervisor_instructions,
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        
        response = await self._chat(
            messages=messages,
            model=model or "gpt-4o-mini",
            temperature=0.2,
            max_tokens=600,
        )
        
        # The supervisor now outputs guidance text, not JSON
        # This guidance is passed to downstream agents
        plan = response.strip()
        
        return AgentResult(
            agent=self.agent_id,
            model=model or "gpt-4o-mini",
            action="plan",
            content=plan,
            metadata={
                "planning_style": planning_style,
                "optimization_level": optimization_level,
            },
            context_updates={
                "supervisor_plan": plan,
                "supervisor_guidance": plan,  # Pass to transformer and other agents
            },
        )

