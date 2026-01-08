# Workflow Execution API

Endpoints for executing workflows with real-time streaming.

## Execute Workflow

Execute a workflow and stream results via Server-Sent Events (SSE).

### Endpoint

```
POST /api/workflow/execute
```

### Request Body

```typescript
{
  message: string;                    // User query/prompt
  workflow_nodes: Array<{             // Workflow node definitions
    id: string;
    type: string;
    position: { x: number; y: number };
    data: {
      nodeType: string;
      label: string;
      settings?: object;
      promptText?: string;            // For prompt nodes
      uploadedFiles?: Array<{         // For upload nodes
        name: string;
        size: number;
        type: string;
        content?: string;              // Base64 encoded or text
      }>;
    };
  }>;
  workflow_edges?: Array<{            // Optional: workflow connections
    id: string;
    source: string;                   // Source node ID
    target: string;                   // Target node ID
  }>;
  knowledge_base?: string;            // Optional: "legal" or "audit" (default: "legal")
}
```

### Example Request

```json
{
  "message": "What are the 7 HACCP principles?",
  "workflow_nodes": [
    {
      "id": "node-1",
      "type": "prompt",
      "position": { "x": 100, "y": 100 },
      "data": {
        "nodeType": "prompt",
        "label": "Prompt",
        "promptText": "What are the 7 HACCP principles?"
      }
    },
    {
      "id": "node-2",
      "type": "supervisor",
      "position": { "x": 300, "y": 100 },
      "data": {
        "nodeType": "supervisor",
        "label": "Supervisor",
        "settings": {
          "planningStyle": "detailed",
          "optimizationLevel": "basic"
        }
      }
    }
  ],
  "workflow_edges": [
    {
      "id": "edge-1",
      "source": "node-1",
      "target": "node-2"
    }
  ],
  "knowledge_base": "legal"
}
```

### Response

**Content-Type:** `text/event-stream`

**Events:**

#### 1. `agent_start`

Fired when an agent begins execution:

```
event: agent_start
data: {"agent": "node-2", "status": "working"}
```

#### 2. `agent_complete`

Fired when an agent completes:

```
event: agent_complete
data: {
  "agent": "node-2",
  "step": {
    "agent": "supervisor",
    "model": "gpt-4o-mini",
    "action": "analyze_and_plan",
    "content": "QUERY ANALYSIS: ...",
    "metadata": { ... }
  }
}
```

**Step Object:**
```typescript
{
  agent: string;           // Agent identifier
  model: string;           // Model used
  action: string;         // Action performed
  content: string;        // Output content
  excluded?: boolean;      // True if node was excluded
  [key: string]: any;     // Additional metadata
}
```

#### 3. `done`

Fired when workflow execution completes:

```
event: done
data: {
  "answer": "Final answer text...",
  "tool_outputs": {
    "images": Array<{
      prompt: string;
      url: string;
      style: string;
      has_data: boolean;
    }>;
    "calculations": Array<any>;
    "web_results": Array<any>;
    "docs": Array<{
      title: string;
      snippet: string;
      score: number;
    }>;
  },
  "trace": {
    "steps": Array<Step>  // All execution steps
  },
  "latency_ms": number,
  "output_format": "text" | "spreadsheet"
}
```

#### 4. `error`

Fired on execution error:

```
event: error
data: {"message": "Error description"}
```

### Example Client Usage (JavaScript)

```javascript
const response = await fetch('/api/workflow/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'Generate a diagram of the 7 HACCP principles',
    workflow_nodes: [...],
    workflow_edges: [...]
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('event: ')) {
      const eventType = line.substring(7);
    } else if (line.startsWith('data: ')) {
      const data = JSON.parse(line.substring(6));
      // Handle event data
    }
  }
}
```

### Status Codes

- `200 OK` - Stream started successfully
- `400 Bad Request` - Invalid request data
- `500 Internal Server Error` - Execution error

### Notes

- The stream remains open until execution completes or errors
- Each event is separated by double newlines (`\n\n`)
- The `done` event signals completion
- If an `error` event occurs, the stream closes
- Execution time is included in the `done` event as `latency_ms`

### Workflow Execution Flow

1. **Input Processing**: Extract data from input nodes (prompt, upload)
2. **Topological Sort**: Determine execution order based on dependencies
3. **Agent Execution**: Execute agents in order, passing context between nodes
4. **Branch Routing**: Skip nodes whose dependencies weren't executed
5. **Output Generation**: Format final result based on output node type

### Node Execution States

- **EXECUTED**: Node completed successfully
- **EXCLUDED**: Node skipped (dependency not met or not selected)
- **SKIPPED**: Node skipped due to missing dependencies
- **ERROR**: Node execution failed

