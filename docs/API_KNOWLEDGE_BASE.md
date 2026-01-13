# Knowledge Base API

Endpoints for managing knowledge bases and document search.

## Get Knowledge Base Info

Get information about available knowledge bases and document counts.

### Endpoint

```
GET /api/knowledge-base
```

### Response

```json
{
  "active": "legal",
  "available": [
    {
      "id": "legal",
      "name": "Legal",
      "document_count": 14
    },
    {
      "id": "audit",
      "name": "Audit",
      "document_count": 0
    }
  ]
}
```

### Response Fields

- `active` (string): Currently active knowledge base ID
- `available` (array): List of available knowledge bases
  - `id` (string): Knowledge base identifier
  - `name` (string): Display name
  - `document_count` (number): Number of documents indexed

### Status Codes

- `200 OK` - Success
- `500 Internal Server Error` - Server error

---

## Switch Knowledge Base

Switch the active knowledge base for semantic search operations.

### Endpoint

```
POST /api/knowledge-base/switch
```

### Request Body

```typescript
{
  knowledge_base: "legal" | "audit";  // Knowledge base identifier
}
```

### Example Request

```json
{
  "knowledge_base": "audit"
}
```

### Response

```json
{
  "active": "audit",
  "message": "Switched to audit knowledge base"
}
```

### Status Codes

- `200 OK` - Knowledge base switched successfully
- `400 Bad Request` - Invalid knowledge base ID
- `500 Internal Server Error` - Server error

### Notes

- The active knowledge base affects all subsequent semantic search operations
- Switching is persistent for the current session
- Each knowledge base has its own document collection and embeddings

---

## Knowledge Base Structure

### Document Storage

Documents are stored in:
```
backend/documents/
├── legal/          # Legal documents
│   ├── *.md        # Markdown files
│   ├── *.pdf       # PDF files
│   └── *.txt       # Text files
└── audit/          # Audit documents
    ├── *.md
    ├── *.pdf
    └── *.txt
```

### Supported Formats

- **Markdown** (`.md`): Preferred format, supports formatting
- **PDF** (`.pdf`): Text extraction via PyPDF
- **Text** (`.txt`): Plain text files

### Document Indexing

Documents are automatically indexed on server startup:
1. Files are read from the knowledge base directory
2. Text is extracted (PDFs are parsed)
3. Documents are embedded using the configured embedding model
4. Embeddings are cached in `embeddings_cache_{knowledge_base}.json`

### Embedding Cache

Embeddings are cached to avoid recomputation:
- Cache file: `backend/embeddings_cache_{knowledge_base}.json`
- Cache is invalidated when documents change (hash-based)
- Cache format:
```json
{
  "documents_hash": "abc123...",
  "embeddings": [
    {
      "doc_id": "doc_legal_123",
      "embedding": [0.1, 0.2, ...]
    }
  ]
}
```

---

## Semantic Search

Semantic search is performed automatically by the `semantic_search` agent node during workflow execution. The search:

1. Embeds the user query
2. Computes similarity with all document embeddings
3. Returns top-k most relevant documents
4. Optionally reranks using LLM

### Search Parameters

Configured in the semantic search node settings:

```typescript
{
  topK: number;           // Number of results (default: 5)
  useReranking: boolean;   // Use LLM reranking (default: false)
  rerankTopK: number;     // Results to rerank (default: 10)
}
```

### Search Results Format

```typescript
{
  title: string;          // Document title
  snippet: string;        // Relevant text snippet
  score: number;          // Similarity score (0-1)
  source: string;         // Source filename
}
```

---

## Adding Documents

### Manual Addition

1. Place files in the appropriate knowledge base directory:
   - `backend/documents/legal/` for legal documents
   - `backend/documents/audit/` for audit documents

2. Restart the server to reindex

3. Documents are automatically:
   - Parsed and embedded
   - Added to the vector store
   - Available for semantic search

### Document Naming

- Use descriptive filenames (they become document titles)
- For Markdown files, the first `# Title` is used as the title
- Avoid special characters in filenames

### Best Practices

- **Markdown**: Preferred format, supports rich formatting
- **Structure**: Use headings to organize content
- **Size**: Keep documents under 100KB for best performance
- **Chunking**: Large documents are automatically chunked

---

## Current Knowledge Bases

### Legal Knowledge Base

Contains EU regulations and legal documents:
- Regulation (EC) No. 178/2002
- Regulation (EC) No. 1169/2011
- Regulation (EU) No. 1308/2013
- And more...

### Audit Knowledge Base

Currently empty. Add audit-related documents to:
```
backend/documents/audit/
```

---

## Troubleshooting

### Documents Not Appearing

1. Check file format (must be .md, .pdf, or .txt)
2. Verify files are in the correct directory
3. Check server logs for parsing errors
4. Clear embedding cache and restart

### Search Not Working

1. Verify knowledge base is active
2. Check that documents are indexed (see document count)
3. Ensure embeddings cache exists
4. Check server logs for errors

### Performance Issues

- Large documents may slow down indexing
- Consider splitting large documents
- Embedding cache speeds up subsequent startups
- Use reranking sparingly (it's expensive)



