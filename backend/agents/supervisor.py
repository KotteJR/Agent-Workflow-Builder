"""
Supervisor Agent - Analyzes workflow graph and optimizes execution plans.

The Supervisor understands the downstream nodes and creates an optimized
execution plan based on the query and available tools.

Supports Auto-RAG mode: automatically retrieves relevant context before planning.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from agents.base import BaseAgent, AgentResult
from models import LLMClientProtocol

# Get workflow logger
logger = logging.getLogger("workflow")

# Import retrieval module (pgvector or file-based)
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL:
    import retrieval_pgvector as retrieval_module
else:
    import retrieval as retrieval_module


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
        logger.info("=" * 50)
        logger.info("SUPERVISOR: Starting workflow analysis")
        logger.info("=" * 50)
        
        settings = settings or {}
        planning_style = settings.get("planningStyle", "optimized")
        optimization_level = settings.get("optimizationLevel", "basic")
        supervisor_prompt = settings.get("supervisorPrompt", "")
        auto_rag = settings.get("autoRAG", False)
        
        logger.debug(f"Planning style: {planning_style}, Optimization: {optimization_level}")
        logger.debug(f"Auto-RAG enabled: {auto_rag}")
        
        # Auto-RAG: Automatically retrieve relevant context before planning
        auto_rag_context = ""
        auto_rag_results = []
        if auto_rag:
            try:
                logger.info("[SUPERVISOR AUTO-RAG] Searching knowledge base...")
                # Use async version if pgvector, sync version if file-based
                if DATABASE_URL:
                    # pgvector: use async version directly
                    search_results = await retrieval_module.semantic_search_pg(
                        query=user_message,
                        top_k=5,
                        knowledge_base=None,  # Use active knowledge base
                        rerank=True,
                    )
                else:
                    # File-based: use sync version
                    search_results = retrieval_module.semantic_search(
                        query=user_message,
                        top_k=5,
                        rerank=True,
                    )
                
                if search_results:
                    auto_rag_results = search_results
                    context_snippets = []
                    for result in search_results:
                        title = result.get("title", "Unknown")
                        snippet = result.get("snippet", "")[:1000]
                        score = result.get("score", 0)
                        context_snippets.append(f"[{title}] (relevance: {score}%)\n{snippet}")
                    
                    auto_rag_context = "\n\n---\nRELEVANT KNOWLEDGE BASE CONTEXT:\n" + "\n\n".join(context_snippets)
                    logger.info(f"[SUPERVISOR AUTO-RAG] Found {len(search_results)} relevant documents")
                else:
                    logger.info("[SUPERVISOR AUTO-RAG] No relevant documents found")
            except Exception as e:
                logger.warning(f"[SUPERVISOR AUTO-RAG] Search failed: {e}")
        
        # Get downstream nodes from context
        downstream_nodes = context.get("downstream_nodes", [])
        logger.info(f"Downstream nodes available: {downstream_nodes}")
        
        # Format as a clear list for the LLM
        if downstream_nodes:
            available_nodes = "\n".join([f"- {node}" for node in downstream_nodes])
        else:
            available_nodes = "- (no specific nodes detected)"
        
        # Check if there's uploaded content - if so, use GPT-4 for deep analysis
        has_uploaded_content = bool(context.get("uploaded_file_content"))
        logger.debug(f"Has uploaded content: {has_uploaded_content}")
        
        # Add supervisor instructions if provided
        supervisor_instructions = ""
        if supervisor_prompt:
            supervisor_instructions = f"\nAdditional instructions from user:\n{supervisor_prompt}\n"
            logger.debug(f"Custom supervisor prompt provided")
        
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
        
        # Add Auto-RAG context if available
        if auto_rag_context:
            full_user_message = full_user_message + auto_rag_context
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_user_message},
        ]
        
        # Use GPT-4 when analyzing documents for better understanding
        actual_model = "gpt-4o" if has_uploaded_content else (model or "gpt-4o-mini")
        logger.debug(f"Using model: {actual_model}")
        
        # More tokens for document analysis
        max_tokens = 1500 if has_uploaded_content else 600
        
        response = await self._chat(
            messages=messages,
            model=actual_model,
            temperature=0.2,
            max_tokens=max_tokens,
        )
        
        plan = response.strip()
        
        logger.info("SUPERVISOR PLAN:")
        logger.info("-" * 40)
        # Log first 500 chars of plan
        for line in plan[:500].split('\n'):
            logger.info(f"  {line}")
        if len(plan) > 500:
            logger.info("  [... truncated ...]")
        logger.info("-" * 40)
        
        # Build context updates
        context_updates = {
            "supervisor_plan": plan,
            "supervisor_guidance": plan,
        }
        
        # Include Auto-RAG results if available
        if auto_rag_results:
            context_updates["semantic_results"] = auto_rag_results
            context_updates["context_snippets"] = [
                f"[{r.get('title', 'Unknown')}] {r.get('snippet', '')[:500]}"
                for r in auto_rag_results
            ]
            context_updates["auto_rag_used"] = True
        
        return AgentResult(
            agent=self.agent_id,
            model=actual_model,
            action="analyze_and_plan",
            content=plan,
            metadata={
                "planning_style": planning_style,
                "optimization_level": optimization_level,
                "analyzed_document": has_uploaded_content,
                "auto_rag": auto_rag,
                "auto_rag_results": len(auto_rag_results) if auto_rag_results else 0,
            },
            context_updates=context_updates,
        )

