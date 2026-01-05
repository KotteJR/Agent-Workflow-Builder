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
    
    SYSTEM_PROMPT_TEMPLATE = """You are a Supervisor Agent that understands workflows and analyzes documents.

WORKFLOW CONTEXT:
- Downstream nodes: {available_nodes}
- Planning style: {planning_style} | Optimization: {optimization_level}
{supervisor_instructions}

AUTOMATIC WORKFLOW UNDERSTANDING:
Based on the downstream nodes, automatically determine what to do:
- If TRANSFORMER + SPREADSHEET are present → Extract document data into structured table format
- If TRANSFORMER alone → Convert document to specified format
- If SYNTHESIS is present → Summarize and synthesize information
- If SEMANTIC_SEARCH is present → Prepare for knowledge retrieval

YOUR JOB:
1. **UNDERSTAND THE WORKFLOW** - What nodes come after you? What's the end goal?
2. **ANALYZE THE DOCUMENT** - What type? What data is inside?
3. **CREATE EXTRACTION PLAN** - Guide downstream agents on what to extract

For SPREADSHEET workflows (most common):
Analyze the document and provide:
- Document type detected
- ALL data that should become columns
- What each row should represent
- Specific entities/values found

OUTPUT FORMAT:
DOCUMENT TYPE: [Invoice/Contract/Resume/Report/Academic Paper/etc.]
TARGET OUTPUT: [Based on workflow - spreadsheet/summary/etc.]

KEY DATA FOUND:
- [List all extractable data points you identified]

EXTRACTION PLAN FOR TRANSFORMER:
- Columns: [Column1, Column2, Column3, ...]  
- Rows: [What each row represents]
- Structure: [Any special organization needed]

Be specific - list actual data you found in the document."""

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
        available_nodes = ", ".join(downstream_nodes) if downstream_nodes else "transformer, spreadsheet"
        
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

