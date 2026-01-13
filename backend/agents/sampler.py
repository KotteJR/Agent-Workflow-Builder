"""
Verbalized Sampling Agent - Generates diverse candidate answers.

Uses verbalized sampling to generate multiple diverse candidate answers
by exploring different reasoning paths and perspectives.
"""

from typing import Any, Dict, List, Optional

from agents.base import BaseAgent, AgentResult
from models import LLMClientProtocol


class SamplerAgent(BaseAgent):
    """
    Verbalized Sampling Agent that generates diverse candidates.
    
    Capabilities:
    - Generates multiple diverse candidate answers
    - Explores different reasoning paths
    - Considers various perspectives and approaches
    - Improves accuracy through diversity
    """
    
    agent_id = "sampler"
    display_name = "Verbalized Sampling"
    default_model = "small"
    
    SYSTEM_PROMPT_TEMPLATE = """Generate {num_responses} DIFFERENT candidate answers that explore different aspects and details of the prompt.

Each candidate should:
- Give me the {num_responses} most probable answers to the prompt.
- Be comprehensive and detailed (4-6 sentences minimum)
- Include specific facts, numbers, and details from the context
- Cover different relevant information from the provided documents
- Be well-structured and informative

Number each candidate as [1], [2], [3], etc.
Ground ALL information in the provided context.
Each candidate should be substantial enough to stand alone as a helpful answer."""

    async def execute(
        self,
        user_message: str,
        context: Dict[str, Any],
        settings: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
    ) -> AgentResult:
        """
        Generate diverse candidate answers.
        
        Args:
            user_message: User's query
            context: Contains 'context_snippets' from previous agents
            settings: Contains 'numResponses'
            model: Model to use
            
        Returns:
            AgentResult with candidate answers
        """
        settings = settings or {}
        num_responses = settings.get("numResponses", 5)
        
        # Get context snippets
        snippets = context.get("context_snippets", [])
        
        # If no real context, reduce candidates
        has_real_context = any(s for s in snippets if not s.startswith("[IMAGE]"))
        actual_candidates = num_responses if has_real_context else 2
        
        system_prompt = self._build_system_prompt(
            self.SYSTEM_PROMPT_TEMPLATE,
            num_responses=actual_candidates,
        )
        
        snippet_text = "\n- ".join(snippets) if snippets else "No context available"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Question: {user_message}\n\nContext:\n- {snippet_text}"},
        ]
        
        response = await self._chat(
            messages=messages,
            model=model or "gpt-4o-mini",
            temperature=0.7,
            max_tokens=1200,
        )
        
        # Parse candidates
        candidates = self._parse_candidates(response, actual_candidates)
        
        return AgentResult(
            agent=self.agent_id,
            model=model or "gpt-4o-mini",
            action="sample",
            content=f"Generated {len(candidates)} candidates",
            metadata={
                "num_candidates": len(candidates),
                "candidates": candidates,
                "candidates_preview": [c[:100] + "..." if len(c) > 100 else c for c in candidates],
            },
            context_updates={
                "candidates": candidates,
            },
        )
    
    def _parse_candidates(self, raw: str, expected: int) -> List[str]:
        """Parse numbered candidates from LLM response."""
        candidates = []
        current = []
        
        for line in raw.strip().split("\n"):
            is_new = False
            for i in range(1, expected + 2):
                if (line.strip().startswith(f"[{i}]") or 
                    line.strip().startswith(f"{i}.") or 
                    line.strip().startswith(f"{i})")):
                    if current:
                        candidates.append(" ".join(current).strip())
                    # Extract content after the number marker
                    content = line.split("]", 1)[-1].split(".", 1)[-1].split(")", 1)[-1].strip()
                    current = [content]
                    is_new = True
                    break
            if not is_new and current:
                current.append(line.strip())
        
        if current:
            candidates.append(" ".join(current).strip())
        
        candidates = [c for c in candidates if c.strip()]
        return candidates[:expected] if candidates else [raw.strip()]




