"""
Semantic Search Agent - Searches knowledge base using vector embeddings.

Performs semantic search across documents and returns relevant results
with optional reranking for improved relevance.
"""

from typing import Any, Dict, List, Optional

from agents.base import BaseAgent, AgentResult
from models import LLMClientProtocol


class SemanticSearchAgent(BaseAgent):
    """
    Semantic Search Agent that queries the vector knowledge base.
    
    Capabilities:
    - Semantic similarity search using embeddings
    - Configurable top-k results
    - Optional LLM-based reranking
    - Combines system and user documents
    """
    
    agent_id = "semantic_search"
    display_name = "Semantic Search"
    default_model = "embedding"  # Uses embedding model, not LLM
    
    def __init__(self, llm_client: LLMClientProtocol, retrieval_module=None):
        """
        Initialize with LLM client and retrieval module.
        
        Args:
            llm_client: LLM client for reranking
            retrieval_module: Module with semantic_search function
        """
        super().__init__(llm_client)
        self.retrieval = retrieval_module
    
    async def execute(
        self,
        user_message: str,
        context: Dict[str, Any],
        settings: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
    ) -> AgentResult:
        """
        Perform semantic search on the knowledge base.
        
        Args:
            user_message: User's query (or search guidance from supervisor)
            context: Contains 'search_guidance' if supervisor ran first
            settings: Contains 'topK' and 'enableReranking'
            model: Not used for semantic search
            
        Returns:
            AgentResult with search results
        """
        settings = settings or {}
        top_k = settings.get("topK", 5)
        enable_reranking = settings.get("enableReranking", True)
        
        # Use search guidance from supervisor if available
        search_query = context.get("search_guidance", user_message)
        
        # Perform semantic search
        if self.retrieval:
            results = self.retrieval.semantic_search(
                query=search_query,
                top_k=top_k,
                rerank=enable_reranking,
            )
        else:
            # Fallback: return empty results if retrieval module not set
            results = []
        
        # Build context snippets
        context_snippets = []
        docs = []
        
        for item in results:
            snippet = f"[{item.get('title', 'Unknown')}] {item.get('snippet', '')}"
            context_snippets.append(snippet)
            docs.append({
                "title": item.get("title", "Unknown"),
                "snippet": item.get("snippet", "")[:500],
                "score": item.get("score"),
                "score_type": item.get("score_type", "semantic"),
            })
        
        return AgentResult(
            agent=self.agent_id,
            model="embedding",
            action="search",
            content=f"Found {len(results)} relevant documents",
            metadata={
                "num_results": len(results),
                "top_k": top_k,
                "reranked": enable_reranking and len(results) > 1,
                "docs": docs,
            },
            context_updates={
                "semantic_results": results,
                "context_snippets": context_snippets,
                "docs": docs,
            },
        )

