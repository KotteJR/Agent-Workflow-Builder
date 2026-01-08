# API Reference

Complete API documentation for the Workflow Builder backend.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Response Format

### Success Response

Most endpoints return JSON:

```json
{
  "status": "success",
  "data": { ... }
}
```

### Error Response

```json
{
  "detail": "Error message"
}
```

### Streaming Response

Workflow execution uses Server-Sent Events (SSE):

```
event: agent_start
data: {"agent": "node-1", "status": "working"}

event: agent_complete
data: {"agent": "node-1", "step": {...}}

event: done
data: {"answer": "...", "trace": {...}}
```

## Endpoint Categories

1. [Workflow Execution](./API_WORKFLOW_EXECUTION.md) - Execute workflows with SSE streaming
2. [Workflow Management](./API_WORKFLOW_MANAGEMENT.md) - Save, load, delete workflows
3. [Workflow Builder](./API_WORKFLOW_BUILDER.md) - AI-powered workflow generation
4. [Knowledge Base](./API_KNOWLEDGE_BASE.md) - Document management and search
5. [System](./API_SYSTEM.md) - Health checks and provider info

## Common Status Codes

- `200 OK` - Success
- `400 Bad Request` - Invalid request data
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Rate Limiting

Currently, there are no rate limits. Consider implementing rate limiting for production use.

## CORS

CORS is enabled for all origins. Configure in `main.py` for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

