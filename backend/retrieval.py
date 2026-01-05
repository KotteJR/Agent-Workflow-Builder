"""
Vector store and semantic search with multi-provider support.

Provides semantic search over documents using embeddings from
OpenAI or Ollama with optional LLM-based reranking.
"""

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from config import config
from models import get_llm_client, get_embedding_client


# In-memory stores for each knowledge base: {"legal": [...], "audit": [...]}
_stores: Dict[str, List[Dict[str, Any]]] = {
    "legal": [],
    "audit": [],
}

# Current active knowledge base
_active_knowledge_base: str = "legal"


def _extract_title_from_content(content: str, filename: str) -> str:
    """Extract title from markdown heading or use filename."""
    lines = content.strip().split("\n")
    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()
    return filename.replace("_", " ").replace(".md", "").replace(".pdf", "").title()


def _read_pdf(filepath: Path) -> str:
    """Read text from a PDF file."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(filepath)
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n\n".join(text_parts)
    except ImportError:
        print(f"Warning: pypdf not installed, skipping {filepath}")
        return ""
    except Exception as e:
        print(f"Warning: Could not read PDF {filepath}: {e}")
        return ""


def _load_documents_from_folder(knowledge_base: str = "legal") -> List[Dict[str, str]]:
    """Load all documents from the specified knowledge base folder."""
    documents = []
    
    docs_dir = config.get_documents_dir(knowledge_base)
    if not docs_dir.exists():
        docs_dir.mkdir(parents=True, exist_ok=True)
        return documents
    
    for filepath in sorted(docs_dir.iterdir()):
        if filepath.is_dir():
            continue
        if filepath.suffix == ".md":
            content = filepath.read_text(encoding="utf-8")
        elif filepath.suffix == ".pdf":
            content = _read_pdf(filepath)
        elif filepath.suffix == ".txt":
            content = filepath.read_text(encoding="utf-8")
        else:
            continue
        
        if not content.strip():
            continue
        
        title = _extract_title_from_content(content, filepath.name)
        doc_id = f"doc_{knowledge_base}_{filepath.stem}"
        
        documents.append({
            "id": doc_id,
            "title": title,
            "content": content,
            "source": filepath.name,
        })
    
    return documents


def _compute_documents_hash(documents: List[Dict[str, str]]) -> str:
    """Compute a hash of all documents to detect changes."""
    content_str = json.dumps(
        [(d["id"], d["content"]) for d in documents],
        sort_keys=True
    )
    provider = config.LLM_PROVIDER
    model = config.EMBEDDING_MODEL if provider != "ollama" else config.OLLAMA_EMBEDDING_MODEL
    combined = f"{provider}:{model}:{content_str}"
    return hashlib.sha256(combined.encode()).hexdigest()


def _load_cache(knowledge_base: str = "legal") -> Optional[Dict[str, Any]]:
    """Load cached embeddings from disk for the specified knowledge base."""
    cache_path = config.get_embeddings_cache(knowledge_base)
    if not cache_path.exists():
        return None
    try:
        with open(cache_path, "r") as f:
            return json.load(f)
    except Exception:
        return None


def _save_cache(documents_hash: str, store_data: List[Dict[str, Any]], knowledge_base: str = "legal") -> None:
    """Save embeddings to disk cache for the specified knowledge base."""
    model = config.EMBEDDING_MODEL if config.LLM_PROVIDER != "ollama" else config.OLLAMA_EMBEDDING_MODEL
    cache_path = config.get_embeddings_cache(knowledge_base)
    cache_data = {
        "hash": documents_hash,
        "provider": config.LLM_PROVIDER,
        "embedding_model": model,
        "knowledge_base": knowledge_base,
        "documents": [
            {
                "id": item["id"],
                "title": item["title"],
                "content": item["content"],
                "embedding": item["embedding"].tolist() if isinstance(item["embedding"], np.ndarray) else item["embedding"],
            }
            for item in store_data
        ]
    }
    with open(cache_path, "w") as f:
        json.dump(cache_data, f)


def set_active_knowledge_base(knowledge_base: str) -> None:
    """Set the active knowledge base for semantic search."""
    global _active_knowledge_base
    if knowledge_base in ["legal", "audit"]:
        _active_knowledge_base = knowledge_base
        print(f"Switched to {knowledge_base} knowledge base")


def get_active_knowledge_base() -> str:
    """Get the currently active knowledge base."""
    return _active_knowledge_base


def initialize_vector_store(force: bool = False, knowledge_base: Optional[str] = None) -> None:
    """Build or rebuild the in-memory vector store. Uses cache if documents unchanged."""
    global _stores
    
    # If specific knowledge base specified, only initialize that one
    bases_to_init = [knowledge_base] if knowledge_base else ["legal", "audit"]
    
    for kb in bases_to_init:
        # Load documents from folder
        documents = _load_documents_from_folder(kb)
        
        if not documents:
            print(f"No documents found in {kb} documents folder.")
            _stores[kb] = []
            continue
        
        current_hash = _compute_documents_hash(documents)
        
        # Try to load from cache
        if not force:
            cache = _load_cache(kb)
            if cache and cache.get("hash") == current_hash:
                print(f"[{kb.upper()}] Loading {len(cache['documents'])} documents from cache...")
                _stores[kb] = [
                    {
                        "id": item["id"],
                        "title": item["title"],
                        "content": item["content"],
                        "embedding": np.array(item["embedding"], dtype=np.float32),
                    }
                    for item in cache["documents"]
                ]
                continue
        
        # Need to embed documents
        print(f"[{kb.upper()}] Embedding {len(documents)} documents...")
        
        embedding_client = get_embedding_client()
        contents = [doc["content"] for doc in documents]
        embeddings = embedding_client.embed_texts(contents)
        
        _stores[kb] = []
        for doc, emb in zip(documents, embeddings):
            _stores[kb].append({
                "id": doc["id"],
                "title": doc["title"],
                "content": doc["content"],
                "embedding": np.array(emb, dtype=np.float32),
            })
        
        # Save to cache
        _save_cache(current_hash, _stores[kb], kb)
        print(f"[{kb.upper()}] Cached embeddings for {len(_stores[kb])} documents.")


def semantic_search(
    query: str,
    top_k: int = 5,
    rerank: bool = True,
    knowledge_base: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Return the top-k documents with title, snippet, and similarity score.
    
    Args:
        query: Search query
        top_k: Number of results to return
        rerank: Whether to use LLM reranking
        knowledge_base: Which knowledge base to search (defaults to active)
        
    Returns:
        List of matching documents with scores
    """
    kb = knowledge_base or _active_knowledge_base
    store = _stores.get(kb, [])
    
    if not store:
        return []
    
    embedding_client = get_embedding_client()
    query_embedding = np.array(embedding_client.embed_texts([query])[0], dtype=np.float32)
    
    # Calculate cosine similarity
    scores = []
    for item in store:
        doc_emb = item["embedding"]
        sim = float(np.dot(query_embedding, doc_emb) / (np.linalg.norm(query_embedding) * np.linalg.norm(doc_emb)))
        scores.append((sim, item))
    
    scores.sort(key=lambda x: x[0], reverse=True)
    
    # Get initial candidates
    initial_k = min(top_k * 3, len(scores)) if rerank else top_k
    candidates = scores[:initial_k]
    
    if rerank and len(candidates) > 1:
        try:
            reranked = _rerank_with_llm(query, candidates, top_k)
            return reranked
        except Exception as e:
            print(f"[RERANK] Reranking failed: {e}, falling back to semantic scores")
    
    # Return semantic results
    output: List[Dict[str, Any]] = []
    for sim, item in candidates[:top_k]:
        output.append({
            "title": item["title"],
            "snippet": item["content"],
            "score": round(sim * 100, 1),
            "score_type": "semantic",
            "knowledge_base": kb,
        })
    return output


def _rerank_with_llm(query: str, candidates: List[tuple], top_k: int) -> List[Dict[str, Any]]:
    """Use LLM to rerank candidates based on relevance."""
    # Build prompt for reranking
    docs_text = ""
    for i, (sim, item) in enumerate(candidates):
        snippet = item["content"][:2000] + "..." if len(item["content"]) > 2000 else item["content"]
        docs_text += f"\n[DOC {i+1}] {item['title']}\n{snippet}\n"
    
    rerank_prompt = f"""You are a document relevance scorer. Score each document's relevance to the query.

Query: {query}

Documents:
{docs_text}

For each document, output a JSON array with objects containing:
- "doc_id": the document number (1-indexed integer)
- "relevance_score": an INTEGER from 0 to 100

Score criteria: topic match, specificity, information completeness, direct answer potential.
Output ONLY a valid JSON array, no explanation. Example: [{{"doc_id": 1, "relevance_score": 85}}]"""
    
    # Run reranking synchronously
    llm_client = get_llm_client()
    
    async def do_rerank():
        return await llm_client.chat(
            model=config.SMALL_MODEL,
            messages=[{"role": "user", "content": rerank_prompt}],
            temperature=0.0,
            max_tokens=500,
        )
    
    try:
        loop = asyncio.get_running_loop()
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, do_rerank())
            content = future.result()
    except RuntimeError:
        content = asyncio.run(do_rerank())
    
    content = content.strip()
    
    # Handle markdown code blocks
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    
    rankings = json.loads(content)
    
    # Check if LLM returned decimals
    max_score = max((r.get("relevance_score", 0) for r in rankings), default=0)
    is_decimal = max_score <= 1.0
    
    # Create reranked output
    reranked_results = []
    for rank_item in rankings:
        doc_idx = rank_item["doc_id"] - 1
        if 0 <= doc_idx < len(candidates):
            sim, item = candidates[doc_idx]
            relevance = rank_item["relevance_score"]
            if is_decimal:
                relevance = relevance * 100
            reranked_results.append({
                "title": item["title"],
                "snippet": item["content"],
                "score": round(relevance, 1),
                "semantic_score": round(sim * 100, 1),
                "score_type": "reranked",
            })
    
    reranked_results.sort(key=lambda x: x["score"], reverse=True)
    return reranked_results[:top_k]


def get_document_count(knowledge_base: Optional[str] = None) -> int:
    """Return the number of documents in the store."""
    kb = knowledge_base or _active_knowledge_base
    return len(_stores.get(kb, []))


def get_all_document_counts() -> Dict[str, int]:
    """Return document counts for all knowledge bases."""
    return {kb: len(store) for kb, store in _stores.items()}


