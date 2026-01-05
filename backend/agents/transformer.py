"""
Transformer Agent - Transforms data from one format to another.

Converts data between different formats while preserving structure
and meaning.
"""

from typing import Any, Dict, List, Optional

from agents.base import BaseAgent, AgentResult
from models import LLMClientProtocol


class TransformerAgent(BaseAgent):
    """
    Transformer Agent that converts between formats.
    
    Capabilities:
    - Converts between JSON, XML, CSV, Markdown, etc.
    - Preserves data structure and relationships
    - Handles nested data
    - Validates output format
    """
    
    agent_id = "transformer"
    display_name = "Transformer Agent"
    default_model = "small"
    
    SYSTEM_PROMPT_TEMPLATE = """You are a Data Transformer Agent. Your task is to convert data from {from_format} format to {to_format} format.

SOURCE FORMAT: {from_format}
TARGET FORMAT: {to_format}

REQUIREMENTS:
- Convert the data structure accurately
- Preserve all data values and relationships
- Handle nested structures appropriately
- Create valid {to_format} output
- If source format is unclear, infer the structure

Output ONLY the transformed data in {to_format} format, no explanations."""

    async def execute(
        self,
        user_message: str,
        context: Dict[str, Any],
        settings: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
    ) -> AgentResult:
        """
        Transform data from one format to another.
        
        Args:
            user_message: Original query (for context)
            context: Contains 'input_content' to transform
            settings: Contains 'fromFormat' and 'toFormat'
            model: Model to use
            
        Returns:
            AgentResult with transformed data
        """
        settings = settings or {}
        from_format = settings.get("fromFormat", "json")
        to_format = settings.get("toFormat", "xml")
        
        # Get content to transform from context
        content_to_transform = context.get("input_content")
        if not content_to_transform:
            content_to_transform = context.get("final_answer")
        if not content_to_transform:
            snippets = context.get("context_snippets", [])
            content_to_transform = "\n\n".join(snippets) if snippets else ""
        
        if not content_to_transform:
            return AgentResult(
                agent=self.agent_id,
                model=model or "gpt-4o-mini",
                action="transform",
                content="No content available to transform.",
                success=False,
                metadata={"error": "No input content"},
            )
        
        system_prompt = self._build_system_prompt(
            self.SYSTEM_PROMPT_TEMPLATE,
            from_format=from_format.upper(),
            to_format=to_format.upper(),
        )
        
        user_prompt = f"""Source data ({from_format}):
{content_to_transform}

Transform this to {to_format} format."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        transformed = await self._chat(
            messages=messages,
            model=model or "gpt-4o-mini",
            temperature=0.1,
            max_tokens=2000,
        )
        
        # Clean up response (remove markdown code blocks if present)
        if transformed.startswith("```"):
            lines = transformed.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            transformed = "\n".join(lines)
        
        return AgentResult(
            agent=self.agent_id,
            model=model or "gpt-4o-mini",
            action="transform",
            content=transformed,
            metadata={
                "from_format": from_format,
                "to_format": to_format,
                "original_length": len(content_to_transform),
                "transformed_length": len(transformed),
            },
            context_updates={
                "transformed_content": transformed,
                "input_content": transformed,  # Pass transformed content to next node
            },
        )

