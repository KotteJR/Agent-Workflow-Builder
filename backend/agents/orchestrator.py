"""
Tool Orchestrator Agent - Intelligently selects which tools to execute.

Uses semantic search results and context to make informed decisions
about which tools are needed to answer the query.
"""

import json
import re
import logging
from typing import Any, Dict, List, Optional

from agents.base import BaseAgent, AgentResult
from models import LLMClientProtocol

# Get workflow logger
logger = logging.getLogger("workflow")


class OrchestratorAgent(BaseAgent):
    """
    Tool Orchestrator Agent that decides which tools to use.
    
    Capabilities:
    - Analyzes semantic search results for context
    - Decides which tools are necessary
    - Provides instructions for tool execution
    - Follows conservative approach (defaults to no tools if not needed)
    """
    
    agent_id = "orchestrator"
    display_name = "Tool Orchestrator"
    default_model = "large"
    
    SYSTEM_PROMPT_TEMPLATE = """You are a Tool Orchestrator Agent. You have access to semantic search results from the knowledge base.

Available tools (beyond semantic search): {available_tools}

Tool Selection Strategy: {tool_selection_strategy}
Maximum Tools to Use: {max_tools}

IMPORTANT: Only use tools when they are ABSOLUTELY necessary. Default to using NO tools if semantic search already provides sufficient context.

Decision criteria:
- **web_search**: ONLY use if the question requires CURRENT/REAL-TIME information (e.g., "What's the weather today?", "Latest news about X"). Do NOT use for general knowledge questions.
- **image_generator**: ONLY use if the user explicitly asks for an image, diagram, or visual (e.g., "Show me a diagram", "Create an image").

If semantic search results are relevant and sufficient, set tools_to_execute to [] (empty array).

ONLY CHOOSE ONE PATH; DO NOT USE VERBALIZED SAMPLING NODE OR SYNTHESIS IF IMAGE GENERATION IS SELECTED!!! OR VISE VERSA!!!

Output a JSON object with:
{{
  "tools_to_execute": [],
  "image_prompt": "detailed prompt for image generation" (only if image_generator selected),
  "image_type": "diagram" | "photo" | "artistic" | "cartoon" | "illustration" (only if image_generator selected),
  "reasoning": "brief explanation of why tools were chosen or why none were needed"
}}"""

    async def execute(
        self,
        user_message: str,
        context: Dict[str, Any],
        settings: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
    ) -> AgentResult:
        """
        Decide which tools to execute based on context.
        
        Args:
            user_message: User's query
            context: Contains 'semantic_results' from semantic search
            settings: Contains 'toolSelectionStrategy' and 'maxTools'
            model: Model to use
            
        Returns:
            AgentResult with tool decisions
        """
        logger.info("=" * 50)
        logger.info("ORCHESTRATOR: Starting tool selection")
        logger.info("=" * 50)
        
        settings = settings or {}
        tool_strategy = settings.get("toolSelectionStrategy", "balanced")
        max_tools = settings.get("maxTools", 3)
        
        logger.debug(f"Tool strategy: {tool_strategy}, Max tools: {max_tools}")
        
        # Get semantic results from context
        semantic_results = context.get("semantic_results", [])
        logger.debug(f"Semantic results count: {len(semantic_results)}")
        
        # Build context text
        if semantic_results:
            context_text = "\n".join([
                f"[{i+1}] {item.get('title', 'Unknown')}: {item.get('snippet', '')[:200]}..."
                for i, item in enumerate(semantic_results[:3])
            ])
        else:
            context_text = "No relevant documents found in knowledge base."
        
        # Get available tools from context
        available_tools = context.get("available_tools", [])
        tools_list = ", ".join(available_tools) if available_tools else "none"
        
        logger.info(f"Available tools in workflow: {available_tools}")
        
        system_prompt = self._build_system_prompt(
            self.SYSTEM_PROMPT_TEMPLATE,
            available_tools=tools_list,
            tool_selection_strategy=tool_strategy,
            max_tools=max_tools,
        )
        
        user_prompt = f"""User Question: {user_message[:500]}

Semantic Search Results (from knowledge base):
{context_text}

Analyze:
1. Does the semantic search provide sufficient information to answer the question?
2. Does the question require CURRENT/REAL-TIME information?
3. Does the user explicitly request an image or visual?

Decide which tools to execute (if any) and provide instructions."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        logger.debug("Sending request to LLM for tool selection...")
        
        response = await self._chat(
            messages=messages,
            model=model or "gpt-4o-mini",
            temperature=0.3,
            max_tokens=300,
        )
        
        logger.debug(f"LLM Response: {response[:500]}...")
        
        # Parse JSON response
        try:
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                logger.debug(f"Parsed JSON: {parsed}")
            else:
                parsed = json.loads(response)
        except json.JSONDecodeError as e:
            # Conservative fallback - no tools
            logger.warning(f"Failed to parse orchestrator response: {e}")
            logger.warning(f"Raw response: {response}")
            parsed = {
                "tools_to_execute": [],
                "reasoning": "Failed to parse response, defaulting to no additional tools",
            }
        
        tools_to_execute = parsed.get("tools_to_execute", [])
        reasoning = parsed.get("reasoning", "")
        image_prompt = parsed.get("image_prompt", user_message)
        image_type = parsed.get("image_type", "photo")
        
        # Log the critical decision
        logger.info("=" * 50)
        logger.info(f"ORCHESTRATOR DECISION:")
        logger.info(f"  Tools selected: {tools_to_execute}")
        logger.info(f"  Reasoning: {reasoning}")
        if "image_generator" in tools_to_execute:
            logger.info(f"  Image prompt: {image_prompt[:100]}...")
            logger.info(f"  Image type: {image_type}")
        logger.info("=" * 50)
        
        # Warn if multiple conflicting paths might be selected
        if "image_generator" in tools_to_execute and len(tools_to_execute) > 1:
            logger.warning("⚠️  Multiple tools selected including image_generator!")
            logger.warning("   This may cause branch conflicts!")
        
        return AgentResult(
            agent=self.agent_id,
            model=model or "gpt-4o-mini",
            action="orchestrate",
            content=f"Decided to use: {', '.join(tools_to_execute) or 'no additional tools'}",
            metadata={
                "tools_to_execute": tools_to_execute,
                "reasoning": reasoning,
                "image_prompt": image_prompt,
                "image_type": image_type,
                "tool_selection_strategy": tool_strategy,
                "max_tools": max_tools,
            },
            context_updates={
                "tools_to_execute": tools_to_execute,
                "orchestrator_result": {
                    "tools_to_execute": tools_to_execute,
                    "image_prompt": image_prompt,
                    "image_type": image_type,
                    "reasoning": reasoning,
                },
            },
        )


