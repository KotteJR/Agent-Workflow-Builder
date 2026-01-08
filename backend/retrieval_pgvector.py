"""
PostgreSQL with pgvector for vector storage and semantic search.

This module provides persistent vector storage using PostgreSQL with the pgvector extension.
Use this instead of retrieval.py for production deployments on Railway.

Setup:
1. Add PostgreSQL database on Railway
2. Set DATABASE_URL environment variable
3. Run initialize_database() on startup to create tables and enable pgvector
"""

import asyncio
import hashlib
import json
import os
from typing import Any, Dict, List, Optional

import numpy as np

from config import config
from models import get_llm_client, get_embedding_client

# Database URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Connection pool
_pool = None

# Current active knowledge base
_active_knowledge_base: str = "legal"


async def get_pool():
    """Get or create the database connection pool."""
    global _pool
    if _pool is None:
        import asyncpg
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    return _pool


async def initialize_database():
    """Create tables and enable pgvector extension."""
    if not DATABASE_URL:
        print("[PGVECTOR] DATABASE_URL not set, skipping database initialization")
        return False
    
    try:
        import asyncpg
    except ImportError:
        print("[PGVECTOR] asyncpg not installed. Install with: pip install asyncpg")
        return False
    
    pool = await get_pool()
    
    # First, detect embedding dimension by generating a test embedding
    embedding_client = get_embedding_client()
    test_embedding = embedding_client.embed_texts(["test"])[0]
    embedding_dim = len(test_embedding)
    print(f"[PGVECTOR] Detected embedding dimension: {embedding_dim}")
    
    async with pool.acquire() as conn:
        # Enable pgvector extension
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Check if table exists and has correct dimension
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'documents'
            )
        """)
        
        if table_exists:
            # Check current dimension
            current_dim = await conn.fetchval("""
                SELECT atttypmod FROM pg_attribute 
                WHERE attrelid = 'documents'::regclass 
                AND attname = 'embedding'
            """)
            
            # atttypmod for vector stores dimension + 4
            if current_dim and (current_dim - 4) != embedding_dim:
                print(f"[PGVECTOR] Dimension mismatch (current: {current_dim - 4}, needed: {embedding_dim}). Recreating table...")
                await conn.execute("DROP TABLE IF EXISTS documents CASCADE;")
                table_exists = False
        
        if not table_exists:
            # Create documents table with correct vector dimension
            await conn.execute(f"""
                CREATE TABLE documents (
                    id TEXT PRIMARY KEY,
                    knowledge_base TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT,
                    embedding vector({embedding_dim}),
                    content_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create index for fast similarity search
            await conn.execute(f"""
                CREATE INDEX documents_embedding_idx 
                ON documents USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            """)
            
            # Create index for knowledge base filtering
            await conn.execute("""
                CREATE INDEX documents_kb_idx ON documents(knowledge_base);
            """)
            
            print(f"[PGVECTOR] Created documents table with {embedding_dim}-dimensional vectors")
        
        print("[PGVECTOR] Database initialized successfully")
        return True


async def upsert_document(
    doc_id: str,
    knowledge_base: str,
    title: str,
    content: str,
    source: str = "",
) -> bool:
    """Insert or update a document with its embedding."""
    if not DATABASE_URL:
        return False
    
    pool = await get_pool()
    
    # Compute content hash
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    
    async with pool.acquire() as conn:
        # Check if document exists and content unchanged
        existing = await conn.fetchrow(
            "SELECT content_hash FROM documents WHERE id = $1",
            doc_id
        )
        
        if existing and existing["content_hash"] == content_hash:
            # Content unchanged, skip re-embedding
            return True
        
        # Generate embedding
        embedding_client = get_embedding_client()
        embeddings = embedding_client.embed_texts([content])
        embedding = embeddings[0]
        
        # Convert to string format for pgvector
        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
        
        # Upsert document
        await conn.execute("""
            INSERT INTO documents (id, knowledge_base, title, content, source, embedding, content_hash, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6::vector, $7, CURRENT_TIMESTAMP)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                content = EXCLUDED.content,
                source = EXCLUDED.source,
                embedding = EXCLUDED.embedding,
                content_hash = EXCLUDED.content_hash,
                updated_at = CURRENT_TIMESTAMP
        """, doc_id, knowledge_base, title, content, source, embedding_str, content_hash)
        
        return True


async def semantic_search_pg(
    query: str,
    top_k: int = 5,
    knowledge_base: Optional[str] = None,
    rerank: bool = True,
) -> List[Dict[str, Any]]:
    """
    Perform semantic search using pgvector.
    
    Args:
        query: Search query
        top_k: Number of results to return
        knowledge_base: Which knowledge base to search
        rerank: Whether to use LLM reranking
        
    Returns:
        List of matching documents with scores
    """
    if not DATABASE_URL:
        return []
    
    kb = knowledge_base or _active_knowledge_base
    pool = await get_pool()
    
    # Generate query embedding
    embedding_client = get_embedding_client()
    query_embedding = embedding_client.embed_texts([query])[0]
    query_embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
    
    # Fetch initial candidates (get more if reranking)
    initial_k = top_k * 3 if rerank else top_k
    
    async with pool.acquire() as conn:
        # Use cosine similarity (1 - cosine distance)
        rows = await conn.fetch("""
            SELECT 
                id, title, content, source,
                1 - (embedding <=> $1::vector) as similarity
            FROM documents
            WHERE knowledge_base = $2
            ORDER BY embedding <=> $1::vector
            LIMIT $3
        """, query_embedding_str, kb, initial_k)
    
    if not rows:
        return []
    
    # Convert to list of dicts
    candidates = [
        {
            "id": row["id"],
            "title": row["title"],
            "content": row["content"],
            "source": row["source"],
            "similarity": float(row["similarity"]),
        }
        for row in rows
    ]
    
    if rerank and len(candidates) > 1:
        try:
            reranked = await _rerank_with_llm_async(query, candidates, top_k)
            return reranked
        except Exception as e:
            print(f"[PGVECTOR] Reranking failed: {e}")
    
    # Return semantic results
    return [
        {
            "title": doc["title"],
            "snippet": doc["content"],
            "score": round(doc["similarity"] * 100, 1),
            "score_type": "semantic",
            "knowledge_base": kb,
        }
        for doc in candidates[:top_k]
    ]


async def _rerank_with_llm_async(query: str, candidates: List[Dict], top_k: int) -> List[Dict[str, Any]]:
    """Use LLM to rerank candidates based on relevance."""
    docs_text = ""
    for i, item in enumerate(candidates):
        snippet = item["content"][:2000] + "..." if len(item["content"]) > 2000 else item["content"]
        docs_text += f"\n[DOC {i+1}] {item['title']}\n{snippet}\n"
    
    rerank_prompt = f"""You are a document relevance scorer. Score each document's relevance to the query.

Query: {query}

Documents:
{docs_text}

For each document, output a JSON array with objects containing:
- "doc_id": the document number (1-indexed integer)
- "relevance_score": an INTEGER from 0 to 100

Output ONLY a valid JSON array, no explanation."""
    
    llm_client = get_llm_client()
    content = await llm_client.chat(
        model=config.SMALL_MODEL,
        messages=[{"role": "user", "content": rerank_prompt}],
        temperature=0.0,
        max_tokens=500,
    )
    
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    
    rankings = json.loads(content)
    
    # Create reranked output
    reranked_results = []
    for rank_item in rankings:
        doc_idx = rank_item["doc_id"] - 1
        if 0 <= doc_idx < len(candidates):
            item = candidates[doc_idx]
            relevance = rank_item["relevance_score"]
            if relevance <= 1.0:
                relevance = relevance * 100
            reranked_results.append({
                "title": item["title"],
                "snippet": item["content"],
                "score": round(relevance, 1),
                "semantic_score": round(item["similarity"] * 100, 1),
                "score_type": "reranked",
            })
    
    reranked_results.sort(key=lambda x: x["score"], reverse=True)
    return reranked_results[:top_k]


async def get_document_count_pg(knowledge_base: Optional[str] = None) -> int:
    """Return the number of documents in the database."""
    if not DATABASE_URL:
        return 0
    
    kb = knowledge_base or _active_knowledge_base
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        result = await conn.fetchval(
            "SELECT COUNT(*) FROM documents WHERE knowledge_base = $1",
            kb
        )
        return result or 0


async def get_all_document_counts_pg() -> Dict[str, int]:
    """Return document counts for all knowledge bases."""
    if not DATABASE_URL:
        return {}
    
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT knowledge_base, COUNT(*) as count 
            FROM documents 
            GROUP BY knowledge_base
        """)
        return {row["knowledge_base"]: row["count"] for row in rows}


async def sync_documents_to_db(knowledge_base: str = "legal") -> int:
    """
    Sync documents from local files to PostgreSQL.
    Call this on startup to ensure database has latest documents.
    """
    if not DATABASE_URL:
        print("[PGVECTOR] DATABASE_URL not set, skipping sync")
        return 0
    
    from pathlib import Path
    
    docs_dir = config.get_documents_dir(knowledge_base)
    if not docs_dir.exists():
        return 0
    
    count = 0
    for filepath in sorted(docs_dir.iterdir()):
        if filepath.is_dir():
            continue
        
        if filepath.suffix == ".md":
            content = filepath.read_text(encoding="utf-8")
        elif filepath.suffix == ".pdf":
            try:
                from pypdf import PdfReader
                reader = PdfReader(filepath)
                content = "\n\n".join(page.extract_text() or "" for page in reader.pages)
            except Exception:
                continue
        elif filepath.suffix == ".txt":
            content = filepath.read_text(encoding="utf-8")
        else:
            continue
        
        if not content.strip():
            continue
        
        # Extract title
        title = filepath.stem.replace("_", " ").replace("-", " ").title()
        lines = content.strip().split("\n")
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break
        
        doc_id = f"doc_{knowledge_base}_{filepath.stem}"
        
        success = await upsert_document(
            doc_id=doc_id,
            knowledge_base=knowledge_base,
            title=title,
            content=content,
            source=filepath.name,
        )
        
        if success:
            count += 1
            print(f"[PGVECTOR] Synced: {filepath.name}")
    
    print(f"[PGVECTOR] Synced {count} documents to {knowledge_base}")
    return count


def set_active_knowledge_base(knowledge_base: str) -> None:
    """Set the active knowledge base for semantic search."""
    global _active_knowledge_base
    if knowledge_base in ["legal", "audit"]:
        _active_knowledge_base = knowledge_base


def get_active_knowledge_base() -> str:
    """Get the currently active knowledge base."""
    return _active_knowledge_base


# Synchronous wrappers for compatibility with existing code
def semantic_search(query: str, top_k: int = 5, rerank: bool = True, knowledge_base: Optional[str] = None) -> List[Dict[str, Any]]:
    """Synchronous wrapper for semantic_search_pg."""
    if not DATABASE_URL:
        # Fallback to file-based retrieval
        from retrieval import semantic_search as file_semantic_search
        return file_semantic_search(query, top_k, rerank, knowledge_base)
    
    return asyncio.run(semantic_search_pg(query, top_k, knowledge_base, rerank))


def get_document_count(knowledge_base: Optional[str] = None) -> int:
    """Synchronous wrapper for get_document_count_pg."""
    if not DATABASE_URL:
        from retrieval import get_document_count as file_get_count
        return file_get_count(knowledge_base)
    return asyncio.run(get_document_count_pg(knowledge_base))


def get_all_document_counts() -> Dict[str, int]:
    """Synchronous wrapper for get_all_document_counts_pg."""
    if not DATABASE_URL:
        from retrieval import get_all_document_counts as file_get_counts
        return file_get_counts()
    return asyncio.run(get_all_document_counts_pg())


def initialize_vector_store(force: bool = False, knowledge_base: Optional[str] = None) -> None:
    """Initialize the vector store - either pgvector or file-based."""
    if DATABASE_URL:
        # Use PostgreSQL
        asyncio.run(initialize_database())
        if knowledge_base:
            asyncio.run(sync_documents_to_db(knowledge_base))
        else:
            asyncio.run(sync_documents_to_db("legal"))
            asyncio.run(sync_documents_to_db("audit"))
    else:
        # Fallback to file-based
        from retrieval import initialize_vector_store as file_init
        file_init(force, knowledge_base)

