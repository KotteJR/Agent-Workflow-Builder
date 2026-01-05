"""
Summarization Agent - Summarizes long outputs and extracts key points.

Creates concise summaries while preserving essential information
and respecting configurable word limits.
"""

from typing import Any, Dict, List, Optional

from agents.base import BaseAgent, AgentResult
from models import LLMClientProtocol


class SummarizationAgent(BaseAgent):
    """
    Summarization Agent that condenses content.
    
    Capabilities:
    - Summarizes long text to specified word limit
    - Extracts key points and main ideas
    - Creates executive summaries
    - Preserves essential information
    """
    
    agent_id = "summarization"
    display_name = "Summarization Agent"
    default_model = "small"
    
    SYSTEM_PROMPT_TEMPLATE = """You are a Summarization Agent. Your task is to create a concise summary of the provided content.

REQUIREMENTS:
- Maximum words: {max_words}
- Preserve the most important information
- Extract key points and main ideas
- Maintain accuracy - don't add information not in the original
- Use clear, concise language
- Structure the summary logically

Create a focused summary that captures the essence of the content."""

    async def execute(
        self,
        user_message: str,
        context: Dict[str, Any],
        settings: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
    ) -> AgentResult:
        """
        Summarize the input content.
        
        Args:
            user_message: Original query (for context)
            context: Contains 'input_content' to summarize (or uses context_snippets)
            settings: Contains 'maxWords'
            model: Model to use
            
        Returns:
            AgentResult with summary
        """
        settings = settings or {}
        max_words = settings.get("maxWords", 100)
        
        # Get content to summarize from context
        # Priority: input_content > final_answer > context_snippets
        content_to_summarize = context.get("input_content")
        if not content_to_summarize:
            content_to_summarize = context.get("final_answer")
        if not content_to_summarize:
            snippets = context.get("context_snippets", [])
            content_to_summarize = "\n\n".join(snippets) if snippets else ""
        
        if not content_to_summarize:
            return AgentResult(
                agent=self.agent_id,
                model=model or "gpt-4o-mini",
                action="summarize",
                content="No content available to summarize.",
                success=False,
                metadata={"error": "No input content"},
            )
        
        system_prompt = self._build_system_prompt(
            self.SYSTEM_PROMPT_TEMPLATE,
            max_words=max_words,
        )
        
        user_prompt = f"""Original Query: {user_message}

Content to Summarize:
{content_to_summarize}

Create a summary in approximately {max_words} words or less."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        summary = await self._chat(
            messages=messages,
            model=model or "gpt-4o-mini",
            temperature=0.3,
            max_tokens=max(200, max_words * 2),
        )
        
        return AgentResult(
            agent=self.agent_id,
            model=model or "gpt-4o-mini",
            action="summarize",
            content=summary,
            metadata={
                "max_words": max_words,
                "original_length": len(content_to_summarize.split()),
                "summary_length": len(summary.split()),
            },
            context_updates={
                "summary": summary,
                "input_content": summary,  # Pass summary as input to next node
            },
        )

