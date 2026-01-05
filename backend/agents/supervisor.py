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
    
    SYSTEM_PROMPT_TEMPLATE = """You are a Supervisor Agent that DEEPLY ANALYZES documents and creates detailed extraction plans.

Available downstream nodes: {available_nodes}
Planning style: {planning_style} | Optimization: {optimization_level}
{supervisor_instructions}

YOUR PRIMARY JOB: When a document is uploaded, you MUST:

1. **ANALYZE THE DOCUMENT THOROUGHLY**
   - Read and understand the ENTIRE document content provided
   - Identify the document TYPE (invoice, contract, resume, report, form, academic paper, etc.)
   - List ALL the key sections and their purposes
   - Identify ALL entities (people, organizations, dates, amounts, items)

2. **CREATE A DETAILED EXTRACTION PLAN**
   Based on your analysis, specify EXACTLY what should be extracted:
   
   For the Transformer Agent, provide:
   - Document type detected
   - Recommended columns/fields to extract
   - Specific data points found in the document
   - Structure recommendation (what should be rows vs columns)
   - Any special handling needed

3. **EXAMPLE OUTPUT FORMAT**:
   ```
   DOCUMENT ANALYSIS:
   - Type: [Invoice/Contract/Resume/Report/etc.]
   - Sections found: [list main sections]
   - Key entities: [people, companies, dates, amounts found]
   
   EXTRACTION INSTRUCTIONS FOR TRANSFORMER:
   - Recommended columns: [Column1, Column2, Column3, ...]
   - Each row should represent: [line item / entry / record / etc.]
   - Special notes: [any specific handling needed]
   
   KEY DATA IDENTIFIED:
   - [List specific data points you found that should be extracted]
   ```

Be SPECIFIC and DETAILED. The transformer relies on your analysis to know what to extract."""

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

