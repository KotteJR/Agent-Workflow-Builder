"""
Synthesis Agent - Synthesizes final answer from multiple sources.

Combines information from semantic search, tool outputs, and candidate
answers into a coherent, well-structured final response.
"""

from typing import Any, Dict, List, Optional

from agents.base import BaseAgent, AgentResult
from models import LLMClientProtocol


class SynthesisAgent(BaseAgent):
    """
    Synthesis Agent that creates the final answer.
    
    Capabilities:
    - Synthesizes information from multiple sources
    - Handles citations and formatting
    - Respects word limits
    - Adapts to different content types (text, images, etc.)
    """
    
    agent_id = "synthesis"
    display_name = "Synthesis Agent"
    default_model = "large"
    
    SYSTEM_PROMPT_TEMPLATE = """Synthesize a clear, informative answer from the available context, candidates, and tool outputs.

{tool_context}

INSTRUCTIONS:
- Create a clear, well-structured answer that directly addresses the question
- Use information from the candidates and sources - focus on the most relevant information
- Maximum words: {max_words}
- Include key facts, numbers, and details that directly answer the question
- Be concise but complete - avoid unnecessary elaboration
- Structure your answer with CLEAR, DISTINCT PARAGRAPHS
- IMPORTANT: Cite sources using [1], [2], [3] notation inline in your response
- Place source citations immediately after the relevant information
- If an image was generated, mention "See the image/diagram below"
- Focus on answering the question directly

{source_list}

Your answer should clearly and directly address the user's question."""

    SYSTEM_PROMPT_IMAGE_ONLY = """You are responding to an image generation request.

{tool_context}

Write a brief response (1-2 sentences) acknowledging the image was created. 
Reference what was generated. Example: "I've created a diagram showing [description]. See it below."
Do NOT make up details not in the image prompt."""

    async def execute(
        self,
        user_message: str,
        context: Dict[str, Any],
        settings: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
    ) -> AgentResult:
        """
        Synthesize the final answer.
        
        Args:
            user_message: User's query
            context: Contains 'candidates', 'context_snippets', 'tool_outputs'
            settings: Contains 'maxWords'
            model: Model to use (should be large model)
            
        Returns:
            AgentResult with final synthesized answer
        """
        settings = settings or {}
        max_words = settings.get("maxWords", 500)
        
        # Get context data
        candidates = context.get("candidates", [])
        snippets = context.get("context_snippets", [])
        tool_outputs = context.get("tool_outputs", {})
        docs = context.get("docs", [])
        
        # Check what was generated
        has_images = bool(tool_outputs.get("images"))
        has_docs = bool(docs)
        has_web = bool(tool_outputs.get("web_results"))
        
        # Build tool context
        tool_context_parts = []
        
        if has_images:
            img = tool_outputs["images"][0]
            tool_context_parts.append(
                f"IMAGE GENERATED: '{img.get('prompt', '')}' - The image will be displayed below your response."
            )
        
        if tool_outputs.get("calculations"):
            for calc in tool_outputs["calculations"]:
                if calc.get("success"):
                    tool_context_parts.append(f"CALCULATION: {calc['expression']} = {calc['result']}")
                else:
                    tool_context_parts.append(f"CALCULATION ERROR: {calc.get('error')}")
        
        if has_web:
            tool_context_parts.append(f"WEB SEARCH: Found {len(tool_outputs['web_results'])} results")
        
        tool_context = "\n".join(tool_context_parts) if tool_context_parts else ""
        
        # Choose appropriate prompt based on content type
        if has_images and not has_docs and not has_web:
            # Image-only response
            system_prompt = self._build_system_prompt(
                self.SYSTEM_PROMPT_IMAGE_ONLY,
                tool_context=tool_context,
            )
        else:
            # Mixed or text-based response
            source_list = ""
            if docs:
                source_list = "\n\nAvailable Sources (use [1], [2], etc. to cite):\n"
                for i, doc in enumerate(docs):
                    source_list += f"[{i+1}] {doc.get('title', 'Unknown')}\n"
            
            system_prompt = self._build_system_prompt(
                self.SYSTEM_PROMPT_TEMPLATE,
                tool_context=tool_context,
                max_words=max_words,
                source_list=source_list,
            )
        
        # Build user prompt
        snippet_text = "\n\n".join([
            f"[Source {i+1}]\n{snippet}" for i, snippet in enumerate(snippets)
        ]) if snippets else "No document context"
        
        candidates_text = "\n\n".join([
            f"Candidate {i+1}: {c}" for i, c in enumerate(candidates)
        ]) if candidates else "No candidates"
        
        user_prompt = f"""Question: {user_message}

Retrieved Documents and Context:
{snippet_text}

Candidate Answers (synthesize the best parts):
{candidates_text}

Create a clear, concise answer that combines the best insights from the sources."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        final_answer = await self._chat(
            messages=messages,
            model=model or "gpt-4o",
            temperature=0.3,
            max_tokens=max(800, max_words * 2),
        )
        
        return AgentResult(
            agent=self.agent_id,
            model=model or "gpt-4o",
            action="synthesize",
            content=final_answer,
            metadata={
                "max_words": max_words,
                "has_images": has_images,
                "has_docs": has_docs,
                "num_candidates": len(candidates),
            },
            context_updates={
                "final_answer": final_answer,
            },
        )

