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
    
    SYSTEM_PROMPT_TEMPLATE = """You are a Supervisor Agent analyzing a user's question to plan workflow execution.

Available downstream nodes in this workflow:
{available_nodes}

Your planning style: {planning_style}
Optimization level: {optimization_level}

Analyze the user's question and provide:
1. A brief execution plan (how to answer the question using available nodes)
2. Search guidance: What specific topics, concepts, or keywords should be searched
3. Node recommendations: Which nodes should be activated and in what order

Respond in JSON format:
{{
    "plan": "Brief plan for answering the question",
    "search_guidance": "Specific topics, concepts, or keywords to search for",
    "recommended_nodes": ["node1", "node2"],
    "parallel_opportunities": ["nodes that can run in parallel"],
    "reasoning": "Why this plan is optimal"
}}"""

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
        
        # Get downstream nodes from context
        downstream_nodes = context.get("downstream_nodes", [])
        available_nodes = ", ".join(downstream_nodes) if downstream_nodes else "semantic_search, synthesis"
        
        system_prompt = self._build_system_prompt(
            self.SYSTEM_PROMPT_TEMPLATE,
            available_nodes=available_nodes,
            planning_style=planning_style,
            optimization_level=optimization_level,
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        
        response = await self._chat(
            messages=messages,
            model=model or "gpt-4o-mini",
            temperature=0.1,
            max_tokens=400,
        )
        
        # Parse JSON response
        try:
            parsed = json.loads(response)
            plan = parsed.get("plan", response)
            search_guidance = parsed.get("search_guidance", user_message)
            recommended_nodes = parsed.get("recommended_nodes", [])
            parallel_opportunities = parsed.get("parallel_opportunities", [])
            reasoning = parsed.get("reasoning", "")
        except json.JSONDecodeError:
            plan = response
            search_guidance = user_message
            recommended_nodes = []
            parallel_opportunities = []
            reasoning = ""
        
        return AgentResult(
            agent=self.agent_id,
            model=model or "gpt-4o-mini",
            action="plan",
            content=plan,
            metadata={
                "search_guidance": search_guidance,
                "recommended_nodes": recommended_nodes,
                "parallel_opportunities": parallel_opportunities,
                "reasoning": reasoning,
                "planning_style": planning_style,
                "optimization_level": optimization_level,
            },
            context_updates={
                "supervisor_plan": plan,
                "search_guidance": search_guidance,
                "recommended_nodes": recommended_nodes,
            },
        )

