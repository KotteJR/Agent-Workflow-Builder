"""
Formatting Agent - Formats outputs to specific formats.

Converts content to various output formats like JSON, XML, Markdown,
HTML, CSV, or YAML.
"""

from typing import Any, Dict, List, Optional

from agents.base import BaseAgent, AgentResult
from models import LLMClientProtocol


class FormattingAgent(BaseAgent):
    """
    Formatting Agent that converts content to specific formats.
    
    Capabilities:
    - Converts to JSON, XML, Markdown, HTML, CSV, YAML
    - Preserves data structure and meaning
    - Handles various input types
    - Creates well-formed output
    """
    
    agent_id = "formatting"
    display_name = "Formatting Agent"
    default_model = "small"
    
    SYSTEM_PROMPT_TEMPLATE = """You are a Formatting Agent. Your task is to convert the provided content into {output_format} format.

OUTPUT FORMAT: {output_format}

REQUIREMENTS:
- Convert the content to valid {output_format}
- Preserve all important information
- Create well-structured, properly formatted output
- Follow {output_format} syntax rules exactly
- If the content is text, structure it appropriately for the format

Output ONLY the formatted content, no explanations."""

    FORMAT_HINTS = {
        "json": "Use proper JSON syntax with double quotes. Structure as an object with meaningful keys.",
        "xml": "Use proper XML tags. Include a root element and properly nest child elements.",
        "markdown": "Use headers, lists, bold, italic, and code blocks as appropriate.",
        "html": "Use semantic HTML5 elements. Include proper tags and structure.",
        "csv": "Use comma-separated values with headers in the first row.",
        "yaml": "Use proper YAML indentation. Use meaningful keys and proper data types.",
    }

    async def execute(
        self,
        user_message: str,
        context: Dict[str, Any],
        settings: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
    ) -> AgentResult:
        """
        Format content to the specified format.
        
        Args:
            user_message: Original query (for context)
            context: Contains 'input_content' to format
            settings: Contains 'outputFormat'
            model: Model to use
            
        Returns:
            AgentResult with formatted content
        """
        settings = settings or {}
        output_format = settings.get("outputFormat", "json")
        
        # Get content to format from context
        content_to_format = context.get("input_content")
        if not content_to_format:
            content_to_format = context.get("final_answer")
        if not content_to_format:
            snippets = context.get("context_snippets", [])
            content_to_format = "\n\n".join(snippets) if snippets else ""
        
        if not content_to_format:
            return AgentResult(
                agent=self.agent_id,
                model=model or "gpt-4o-mini",
                action="format",
                content="No content available to format.",
                success=False,
                metadata={"error": "No input content"},
            )
        
        format_hint = self.FORMAT_HINTS.get(output_format, "")
        
        system_prompt = self._build_system_prompt(
            self.SYSTEM_PROMPT_TEMPLATE,
            output_format=output_format.upper(),
        )
        
        if format_hint:
            system_prompt += f"\n\nFormat hint: {format_hint}"
        
        user_prompt = f"""Content to format:
{content_to_format}

Convert this content to {output_format.upper()} format."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        formatted = await self._chat(
            messages=messages,
            model=model or "gpt-4o-mini",
            temperature=0.1,
            max_tokens=2000,
        )
        
        # Clean up response (remove markdown code blocks if present)
        if formatted.startswith("```"):
            lines = formatted.split("\n")
            # Remove first and last lines if they're code block markers
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            formatted = "\n".join(lines)
        
        return AgentResult(
            agent=self.agent_id,
            model=model or "gpt-4o-mini",
            action="format",
            content=formatted,
            metadata={
                "output_format": output_format,
                "original_length": len(content_to_format),
                "formatted_length": len(formatted),
            },
            context_updates={
                "formatted_content": formatted,
                "input_content": formatted,  # Pass formatted content to next node
            },
        )

