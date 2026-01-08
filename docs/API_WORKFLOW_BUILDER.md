# Workflow Builder API

AI-powered endpoints for generating and improving workflows from natural language.

## Build Workflow from Chat

Generate a workflow configuration from natural language description.

### Endpoint

```
POST /api/workflow/build
```

### Request Body

```typescript
{
  message: string;                    // Natural language description
  conversation_history?: Array<{      // Optional: Previous messages
    role: "user" | "assistant";
    content: string;
  }>;
}
```

### Example Request

```json
{
  "message": "I want to extract data from a PDF invoice and convert it to a spreadsheet",
  "conversation_history": [
    {
      "role": "user",
      "content": "I need to process invoices"
    },
    {
      "role": "assistant",
      "content": "I can help you create a workflow for that..."
    }
  ]
}
```

### Response

```json
{
  "workflow": {
    "nodes": [
      {
        "id": "node-1",
        "type": "upload",
        "position": { "x": 100, "y": 100 },
        "data": {
          "nodeType": "upload",
          "label": "Upload Invoice"
        }
      },
      {
        "id": "node-2",
        "type": "supervisor",
        "position": { "x": 300, "y": 100 },
        "data": {
          "nodeType": "supervisor",
          "label": "Supervisor"
        }
      }
    ],
    "edges": [
      {
        "id": "edge-1",
        "source": "node-1",
        "target": "node-2"
      }
    ]
  },
  "explanation": "This workflow will process your invoice PDF..."
}
```

### Status Codes

- `200 OK` - Workflow generated successfully
- `400 Bad Request` - Invalid request data
- `500 Internal Server Error` - Generation error

### Notes

- The AI analyzes the user's request and generates appropriate node types
- Generated workflows can be saved and executed immediately
- Conversation history helps maintain context across multiple requests

---

## Improve Workflow

Get AI suggestions to improve an existing workflow.

### Endpoint

```
POST /api/workflow/improve
```

### Request Body

```typescript
{
  workflow: {                         // Current workflow
    nodes: Array<any>;
    edges: Array<any>;
    name?: string;
  };
  feedback?: string;                  // Optional: User feedback
}
```

### Example Request

```json
{
  "workflow": {
    "nodes": [
      {
        "id": "node-1",
        "type": "prompt",
        "data": { "nodeType": "prompt" }
      }
    ],
    "edges": []
  },
  "feedback": "This workflow is too slow"
}
```

### Response

```json
{
  "suggestions": [
    {
      "type": "add_node",
      "description": "Add a semantic search node to improve context",
      "workflow": {
        "nodes": [...],
        "edges": [...]
      }
    },
    {
      "type": "optimize",
      "description": "Use a smaller model for the sampler node",
      "settings": {
        "node_id": "node-3",
        "model": "small"
      }
    }
  ],
  "explanation": "These improvements will make your workflow faster..."
}
```

### Status Codes

- `200 OK` - Suggestions generated successfully
- `400 Bad Request` - Invalid request data
- `500 Internal Server Error` - Generation error

---

## List Example Workflows

Get a list of available example workflows.

### Endpoint

```
GET /api/workflow/examples
```

### Response

```json
{
  "examples": [
    {
      "id": "pdf-to-excel",
      "name": "PDF to Excel Conversion",
      "description": "Extract data from PDF invoices and convert to spreadsheet",
      "category": "data-extraction"
    },
    {
      "id": "document-qa",
      "name": "Document Q&A",
      "description": "Ask questions about uploaded documents",
      "category": "qa"
    }
  ]
}
```

### Status Codes

- `200 OK` - Success

---

## Get Example Workflow

Retrieve a specific example workflow configuration.

### Endpoint

```
GET /api/workflow/examples/{example_id}
```

### Path Parameters

- `example_id` (string, required): Example workflow identifier

### Response

```json
{
  "id": "pdf-to-excel",
  "name": "PDF to Excel Conversion",
  "description": "Extract data from PDF invoices and convert to spreadsheet",
  "workflow": {
    "nodes": [
      {
        "id": "node-1",
        "type": "upload",
        "position": { "x": 100, "y": 100 },
        "data": {
          "nodeType": "upload",
          "label": "Upload PDF"
        }
      }
    ],
    "edges": []
  },
  "instructions": "1. Upload a PDF invoice\n2. The workflow will extract data...",
  "category": "data-extraction"
}
```

### Status Codes

- `200 OK` - Success
- `404 Not Found` - Example not found
- `500 Internal Server Error` - Server error

### Notes

- Example workflows can be loaded directly into the workflow builder
- They serve as templates for common use cases
- Users can modify examples to fit their needs

---

## AI Workflow Generation Details

### How It Works

1. **Analysis**: The AI analyzes the user's natural language request
2. **Node Selection**: Determines which agent nodes are needed
3. **Graph Construction**: Creates appropriate node connections
4. **Configuration**: Sets default settings for each node
5. **Validation**: Ensures the workflow is executable

### Supported Use Cases

- **Document Processing**: PDF extraction, text analysis
- **Data Extraction**: Structured data from unstructured sources
- **Content Generation**: Text synthesis, image generation
- **Question Answering**: Document Q&A, knowledge base queries
- **Data Transformation**: Format conversion, data cleaning

### Best Practices

- Be specific about your requirements
- Mention file types if processing documents
- Specify output format (text, spreadsheet, image)
- Provide context about the domain (legal, audit, etc.)

