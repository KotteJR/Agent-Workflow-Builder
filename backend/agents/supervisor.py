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
    
    SYSTEM_PROMPT_TEMPLATE = """You are a Supervisor Agent that analyzes queries and plans workflow execution.

WORKFLOW STRUCTURE (nodes in this workflow):
{available_nodes}

Planning style: {planning_style} | Optimization: {optimization_level}
{supervisor_instructions}

YOUR JOB - Analyze the query and provide guidance for downstream nodes:

1. UNDERSTAND THE QUERY: What is the user asking for?
2. IDENTIFY THE GOAL: Based on the workflow nodes, what's the end goal?
   - If IMAGE_GENERATOR is present → User may want a visual/diagram
   - If SEMANTIC_SEARCH is present → Need to find relevant information from knowledge base
   - If SYNTHESIS is present → Need to generate a well-crafted text response
   - If TRANSFORMER + SPREADSHEET are present → Extract data into structured format
3. PROVIDE GUIDANCE: Give specific instructions for the downstream agents

OUTPUT FORMAT:
QUERY ANALYSIS: [What the user wants]
WORKFLOW PATH: [Which nodes should be activated based on the query]
GUIDANCE: [Specific instructions for downstream agents]

Be concise and focused on guiding the workflow execution."""

    async def execute(
        self,
        user_message: str,
        context: Dict[str, Any],
        settings: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
    ) -> AgentResult:
        """
        Analyze the query and uploaded documents, create an execution plan.
        
        Args:
            user_message: User's query (includes uploaded file content)
            context: Contains 'downstream_nodes', 'uploaded_file_content'
            settings: Contains 'planningStyle' and 'optimizationLevel'
            model: Model to use
            
        Returns:
            AgentResult with detailed extraction plan
        """
        settings = settings or {}
        planning_style = settings.get("planningStyle", "optimized")
        optimization_level = settings.get("optimizationLevel", "basic")
        supervisor_prompt = settings.get("supervisorPrompt", "")
        
        # Get downstream nodes from context
        downstream_nodes = context.get("downstream_nodes", [])
        # Format as a clear list for the LLM
        if downstream_nodes:
            available_nodes = "\n".join([f"- {node}" for node in downstream_nodes])
        else:
            available_nodes = "- (no specific nodes detected)"
        
        # Check if there's uploaded content - if so, use GPT-4 for deep analysis
        has_uploaded_content = bool(context.get("uploaded_file_content"))
        
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
        
        # Build user message with explicit document analysis request
        if has_uploaded_content:
            analysis_request = """IMPORTANT: A document has been uploaded. You MUST:
1. Read the ENTIRE document content below
2. Identify what type of document this is
3. List ALL the key data points, entities, and structures you find
4. Provide SPECIFIC extraction instructions for the transformer

"""
            full_user_message = analysis_request + user_message
        else:
            full_user_message = user_message
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_user_message},
        ]
        
        # Use GPT-4 when analyzing documents for better understanding
        actual_model = "gpt-4o" if has_uploaded_content else (model or "gpt-4o-mini")
        
        # More tokens for document analysis
        max_tokens = 1500 if has_uploaded_content else 600
        
        response = await self._chat(
            messages=messages,
            model=actual_model,
            temperature=0.2,
            max_tokens=max_tokens,
        )
        
        plan = response.strip()
        
        return AgentResult(
            agent=self.agent_id,
            model=actual_model,
            action="analyze_and_plan",
            content=plan,
            metadata={
                "planning_style": planning_style,
                "optimization_level": optimization_level,
                "analyzed_document": has_uploaded_content,
            },
            context_updates={
                "supervisor_plan": plan,
                "supervisor_guidance": plan,
            },
        )

