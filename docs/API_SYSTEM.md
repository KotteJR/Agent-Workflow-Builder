# System API

System-level endpoints for health checks and provider information.

## Health Check

Check if the API is running and healthy.

### Endpoint

```
GET /api/health
```

### Response

```json
{
  "status": "healthy",
  "document_count": 14
}
```

### Response Fields

- `status` (string): Always "healthy" if endpoint responds
- `document_count` (number): Number of documents in active knowledge base

### Status Codes

- `200 OK` - Service is healthy
- `500 Internal Server Error` - Service error

### Use Cases

- Load balancer health checks
- Monitoring and alerting
- Service discovery

---

## Provider Info

Get information about the current LLM and image generation provider configuration.

### Endpoint

```
GET /api/provider
```

### Response

```json
{
  "provider": "openai",
  "small_model": "gpt-4o-mini",
  "large_model": "gpt-4o",
  "image_provider": "gemini"
}
```

### Response Fields

- `provider` (string): LLM provider ("openai", "anthropic", "ollama")
- `small_model` (string): Model used for small tasks
- `large_model` (string): Model used for large/complex tasks
- `image_provider` (string): Image generation provider ("dalle", "gemini")

### Status Codes

- `200 OK` - Success
- `500 Internal Server Error` - Server error

### Example Responses

**OpenAI:**
```json
{
  "provider": "openai",
  "small_model": "gpt-4o-mini",
  "large_model": "gpt-4o",
  "image_provider": "dalle"
}
```

**Ollama:**
```json
{
  "provider": "ollama",
  "small_model": "llama3.1:8b",
  "large_model": "llama3.1:8b",
  "image_provider": "gemini"
}
```

**Anthropic:**
```json
{
  "provider": "anthropic",
  "small_model": "claude-3-haiku-20240307",
  "large_model": "claude-3-5-sonnet-20241022",
  "image_provider": "gemini"
}
```

### Notes

- Configuration is loaded from environment variables
- Changes require server restart
- Use this endpoint to verify configuration before executing workflows

---

## API Documentation

Interactive API documentation is available at:

```
http://localhost:8000/docs
```

This provides:
- Swagger UI interface
- Interactive endpoint testing
- Request/response schemas
- Authentication configuration (if added)

### Alternative Documentation

ReDoc documentation is available at:

```
http://localhost:8000/redoc
```

---

## Server Configuration

### Default Settings

- **Host**: `0.0.0.0` (all interfaces)
- **Port**: `8000`
- **Reload**: Enabled in development mode

### Environment Variables

See `backend/config.py` for all configuration options:

```bash
# Server
HOST=0.0.0.0
PORT=8000

# LLM Provider
LLM_PROVIDER=openai

# Models
SMALL_MODEL=gpt-4o-mini
LARGE_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small

# Image Generation
IMAGE_PROVIDER=gemini
GOOGLE_API_KEY=your-key

# API Keys
OPENAI_API_KEY=your-key
OPENAI_BASE_URL=https://api.openai.com/v1
```

---

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error message here"
}
```

### Common Errors

**400 Bad Request:**
```json
{
  "detail": "Invalid knowledge base. Must be 'legal' or 'audit'"
}
```

**404 Not Found:**
```json
{
  "detail": "Workflow not found"
}
```

**403 Forbidden:**
```json
{
  "detail": "Workflow does not belong to user"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

### Error Logging

- Errors are logged to console with stack traces
- Check server logs for detailed error information
- Production should implement proper error tracking

---

## CORS Configuration

CORS is configured to allow all origins in development:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production Recommendation:**
```python
allow_origins=["https://yourdomain.com"]
```

---

## Rate Limiting

Currently, there are no rate limits implemented. Consider adding rate limiting for production:

- Per-IP rate limiting
- Per-user rate limiting
- Endpoint-specific limits
- Token-based throttling

---

## Monitoring

### Recommended Metrics

- Request count per endpoint
- Response times
- Error rates
- Workflow execution times
- LLM API usage/costs

### Logging

- All requests are logged by Uvicorn
- Workflow execution logs are in `workflow_logger.py`
- Check console output for detailed logs

---

## Security Considerations

### Current State

- No authentication required
- No rate limiting
- CORS allows all origins
- API keys stored in environment variables

### Production Recommendations

1. **Authentication**: Implement JWT or API key authentication
2. **Rate Limiting**: Add rate limiting middleware
3. **CORS**: Restrict allowed origins
4. **Input Validation**: Already handled by Pydantic
5. **Error Messages**: Sanitize error messages (don't expose internals)
6. **HTTPS**: Use HTTPS in production
7. **API Keys**: Store in secure vault, not in code

