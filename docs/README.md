# Documentation Index

Complete documentation for the Workflow Builder project.

## 📚 Documentation Files

### Main Documentation

- **[README.md](../README.md)** - Project overview, architecture, setup guide

### API Documentation

- **[API_REFERENCE.md](./API_REFERENCE.md)** - Complete API reference overview
- **[API_WORKFLOW_EXECUTION.md](./API_WORKFLOW_EXECUTION.md)** - Workflow execution endpoints with SSE streaming
- **[API_WORKFLOW_MANAGEMENT.md](./API_WORKFLOW_MANAGEMENT.md)** - Save, load, delete workflows
- **[API_WORKFLOW_BUILDER.md](./API_WORKFLOW_BUILDER.md)** - AI-powered workflow generation
- **[API_KNOWLEDGE_BASE.md](./API_KNOWLEDGE_BASE.md)** - Knowledge base and document management
- **[API_SYSTEM.md](./API_SYSTEM.md)** - System endpoints (health, provider info)

## 🚀 Quick Start

1. Read the [main README](../README.md) for project overview
2. Check [API_REFERENCE.md](./API_REFERENCE.md) for API overview
3. Review specific API docs for your use case

## 📖 Documentation Structure

```
docs/
├── README.md                    # This file
├── API_REFERENCE.md             # API overview
├── API_WORKFLOW_EXECUTION.md    # Execution endpoints
├── API_WORKFLOW_MANAGEMENT.md   # Storage endpoints
├── API_WORKFLOW_BUILDER.md      # AI builder endpoints
├── API_KNOWLEDGE_BASE.md        # Knowledge base endpoints
└── API_SYSTEM.md                # System endpoints
```

## 🔍 Finding Information

### By Use Case

**Execute a workflow:**
- [API_WORKFLOW_EXECUTION.md](./API_WORKFLOW_EXECUTION.md)

**Save/load workflows:**
- [API_WORKFLOW_MANAGEMENT.md](./API_WORKFLOW_MANAGEMENT.md)

**Generate workflows with AI:**
- [API_WORKFLOW_BUILDER.md](./API_WORKFLOW_BUILDER.md)

**Manage documents:**
- [API_KNOWLEDGE_BASE.md](./API_KNOWLEDGE_BASE.md)

**Check system status:**
- [API_SYSTEM.md](./API_SYSTEM.md)

### By Endpoint

All endpoints are documented with:
- HTTP method and path
- Request/response formats
- Status codes
- Example requests
- Notes and best practices

## 📝 API Endpoints Summary

### Workflow Execution
- `POST /api/workflow/execute` - Execute workflow with SSE

### Workflow Management
- `GET /api/workflows` - List workflows
- `GET /api/workflows/{id}` - Get workflow
- `POST /api/workflows` - Save workflow
- `DELETE /api/workflows/{id}` - Delete workflow

### Workflow Builder
- `POST /api/workflow/build` - Generate workflow from chat
- `POST /api/workflow/improve` - Improve existing workflow
- `GET /api/workflow/examples` - List examples
- `GET /api/workflow/examples/{id}` - Get example

### Knowledge Base
- `GET /api/knowledge-base` - Get KB info
- `POST /api/knowledge-base/switch` - Switch KB

### System
- `GET /api/health` - Health check
- `GET /api/provider` - Provider info

## 🔗 Interactive Documentation

For interactive API testing, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📞 Support

For questions or issues:
1. Check the relevant documentation file
2. Review the main [README.md](../README.md)
3. Check server logs for errors
4. Review workflow execution logs

