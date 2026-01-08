# PostgreSQL with pgvector Setup on Railway

This guide explains how to set up persistent vector storage using PostgreSQL with pgvector on Railway.

## Why pgvector?

- **Persistent Storage**: Embeddings survive redeploys
- **Fast Similarity Search**: pgvector is optimized for vector operations
- **Scalable**: PostgreSQL handles large datasets efficiently
- **Shared State**: Multiple instances can share the same embeddings

## Setup Steps

### 1. Add PostgreSQL Database on Railway

1. Go to your Railway project dashboard
2. Click **"+ New"** → **"Database"** → **"PostgreSQL"**
3. Wait for the database to provision
4. Railway automatically creates `DATABASE_URL` variable

### 2. Link Database to Backend Service

1. Click on your backend service
2. Go to **Variables** tab
3. Click **"+ Add Variable"** → **"Reference"**
4. Select the PostgreSQL service
5. Choose `DATABASE_URL`
6. The variable will be automatically injected

### 3. Enable pgvector Extension

Railway's PostgreSQL supports pgvector. On first startup, the app will run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

This is handled automatically by `retrieval_pgvector.py`.

### 4. Update Your Code to Use pgvector

In `main.py`, change the import:

```python
# Before (file-based)
import retrieval

# After (PostgreSQL)
import retrieval_pgvector as retrieval
```

Or modify `retrieval.py` to auto-detect:

```python
import os
if os.environ.get("DATABASE_URL"):
    from retrieval_pgvector import *
else:
    # Use file-based storage
    pass
```

### 5. Redeploy

Push the changes and Railway will redeploy with PostgreSQL support.

## Database Schema

The pgvector module creates this table:

```sql
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    knowledge_base TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT,
    embedding vector(1536),  -- OpenAI embedding dimension
    content_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast similarity search
CREATE INDEX documents_embedding_idx 
ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

## How It Works

### Document Syncing
On startup, the app:
1. Creates tables and enables pgvector
2. Syncs documents from `documents/legal/` and `documents/audit/` folders
3. Generates embeddings for new/changed documents
4. Stores embeddings in PostgreSQL

### Semantic Search
When you search:
1. Query embedding is generated
2. pgvector finds nearest neighbors using IVFFlat index
3. Results are optionally reranked using LLM
4. Top-K results returned with similarity scores

### Fallback Behavior
If `DATABASE_URL` is not set:
- Falls back to file-based storage (`retrieval.py`)
- Uses JSON cache files for embeddings
- Works exactly like before

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes (for pgvector) |
| `OPENAI_API_KEY` | For generating embeddings | Yes |

## Monitoring

Check document counts:
```bash
curl https://your-app.up.railway.app/api/health
```

Response includes document count from PostgreSQL.

## Troubleshooting

### "asyncpg not found"
```bash
pip install asyncpg
```

### "vector type not found"
pgvector extension not enabled. Run manually:
```sql
CREATE EXTENSION vector;
```

### Slow initial sync
First sync embeds all documents. Subsequent syncs only embed changed files (tracked by content hash).

## Cost Considerations

Railway PostgreSQL pricing:
- **Starter**: Free tier with 500MB storage
- **Pro**: $5/month + usage

For most use cases, the free tier is sufficient for storing embeddings.

