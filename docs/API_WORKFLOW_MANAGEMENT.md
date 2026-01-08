# Workflow Management API

Endpoints for saving, loading, and managing workflows.

## List Workflows

Get all saved workflows for a user.

### Endpoint

```
GET /api/workflows?user_id=default
```

### Query Parameters

- `user_id` (string, optional): User identifier (default: "default")

### Response

```json
{
  "workflows": [
    {
      "id": "9d6709b9",
      "name": "PDF to Excel Conversion Workflow",
      "created_at": "2024-01-07T12:00:00Z",
      "updated_at": "2024-01-07T12:30:00Z",
      "node_count": 4,
      "edge_count": 3
    }
  ]
}
```

### Status Codes

- `200 OK` - Success
- `500 Internal Server Error` - Server error

---

## Get Workflow

Retrieve a specific workflow by ID.

### Endpoint

```
GET /api/workflows/{workflow_id}?user_id=default
```

### Path Parameters

- `workflow_id` (string, required): Workflow identifier

### Query Parameters

- `user_id` (string, optional): User identifier (default: "default")

### Response

```json
{
  "id": "9d6709b9",
  "name": "PDF to Excel Conversion Workflow",
  "user_id": "default",
  "nodes": [
    {
      "id": "node-1",
      "type": "prompt",
      "position": { "x": 100, "y": 100 },
      "data": {
        "nodeType": "prompt",
        "label": "Prompt"
      }
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "source": "node-1",
      "target": "node-2"
    }
  ],
  "created_at": "2024-01-07T12:00:00Z",
  "updated_at": "2024-01-07T12:30:00Z"
}
```

### Status Codes

- `200 OK` - Success
- `404 Not Found` - Workflow not found or doesn't belong to user
- `500 Internal Server Error` - Server error

---

## Save Workflow

Save or update a workflow.

### Endpoint

```
POST /api/workflows?user_id=default
```

### Query Parameters

- `user_id` (string, optional): User identifier (default: "default")

### Request Body

```typescript
{
  workflow_id?: string;     // Optional: ID for updating existing workflow
  name: string;            // Workflow name
  nodes: Array<{           // Workflow nodes
    id: string;
    type: string;
    position: { x: number; y: number };
    data: {
      nodeType: string;
      label: string;
      settings?: object;
      [key: string]: any;
    };
  }>;
  edges: Array<{           // Workflow edges
    id: string;
    source: string;
    target: string;
  }>;
}
```

### Example Request

```json
{
  "name": "My Workflow",
  "nodes": [
    {
      "id": "node-1",
      "type": "prompt",
      "position": { "x": 100, "y": 100 },
      "data": {
        "nodeType": "prompt",
        "label": "Prompt"
      }
    }
  ],
  "edges": []
}
```

### Response

```json
{
  "id": "9d6709b9",
  "name": "My Workflow",
  "user_id": "default",
  "nodes": [...],
  "edges": [...],
  "created_at": "2024-01-07T12:00:00Z",
  "updated_at": "2024-01-07T12:00:00Z"
}
```

### Status Codes

- `200 OK` - Workflow saved successfully
- `403 Forbidden` - Workflow doesn't belong to user (when updating)
- `400 Bad Request` - Invalid request data
- `500 Internal Server Error` - Server error

### Notes

- If `workflow_id` is provided and exists, the workflow is updated
- If `workflow_id` is not provided or doesn't exist, a new workflow is created
- Workflows are stored as JSON files in `backend/workflows/`
- Each workflow is isolated by `user_id`

---

## Delete Workflow

Delete a workflow.

### Endpoint

```
DELETE /api/workflows/{workflow_id}?user_id=default
```

### Path Parameters

- `workflow_id` (string, required): Workflow identifier

### Query Parameters

- `user_id` (string, optional): User identifier (default: "default")

### Response

```json
{
  "success": true
}
```

### Status Codes

- `200 OK` - Workflow deleted successfully
- `404 Not Found` - Workflow not found or doesn't belong to user
- `500 Internal Server Error` - Server error

### Notes

- Only workflows belonging to the specified `user_id` can be deleted
- Deletion is permanent (file is removed from disk)

---

## Workflow Storage

### Storage Location

Workflows are stored as JSON files in:
```
backend/workflows/{workflow_id}.json
```

### File Format

```json
{
  "id": "9d6709b9",
  "name": "Workflow Name",
  "user_id": "default",
  "nodes": [...],
  "edges": [...],
  "created_at": "2024-01-07T12:00:00Z",
  "updated_at": "2024-01-07T12:30:00Z"
}
```

### User Isolation

- Each workflow has a `user_id` field
- Users can only access workflows with their `user_id`
- This provides basic multi-tenancy support

### Backup

To backup workflows, copy the `backend/workflows/` directory.

