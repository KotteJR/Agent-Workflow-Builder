"""
Workflow storage and management.
Stores workflows as JSON files in a workflows/ folder.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import config


def _ensure_dir() -> None:
    """Ensure workflows directory exists."""
    config.WORKFLOWS_DIR.mkdir(parents=True, exist_ok=True)


def _get_workflow_path(workflow_id: str) -> Path:
    """Get the file path for a workflow."""
    return config.WORKFLOWS_DIR / f"{workflow_id}.json"


def create_workflow(
    name: str,
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, str]],
    user_id: str = "default",
) -> Dict[str, Any]:
    """Create a new workflow and return its metadata."""
    _ensure_dir()
    
    workflow_id = str(uuid.uuid4())[:8]
    now = datetime.utcnow().isoformat() + "Z"
    
    workflow = {
        "id": workflow_id,
        "name": name,
        "user_id": user_id,
        "nodes": nodes,
        "edges": edges,
        "created_at": now,
        "updated_at": now,
    }
    
    with open(_get_workflow_path(workflow_id), "w") as f:
        json.dump(workflow, f, indent=2)
    
    return workflow


def get_workflow(workflow_id: str, user_id: str = "default") -> Optional[Dict[str, Any]]:
    """Get a workflow by ID."""
    path = _get_workflow_path(workflow_id)
    if not path.exists():
        return None
    
    with open(path, "r") as f:
        workflow = json.load(f)
    
    # Check if workflow belongs to user
    if workflow.get("user_id") != user_id:
        return None
    
    return workflow


def save_workflow(
    workflow_id: Optional[str],
    name: str,
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, str]],
    user_id: str = "default",
) -> Dict[str, Any]:
    """Save or update a workflow."""
    _ensure_dir()
    
    now = datetime.utcnow().isoformat() + "Z"
    
    if workflow_id:
        # Update existing workflow
        path = _get_workflow_path(workflow_id)
        if path.exists():
            with open(path, "r") as f:
                workflow = json.load(f)
            
            # Check if workflow belongs to user
            if workflow.get("user_id") != user_id:
                raise ValueError("Workflow does not belong to user")
            
            workflow["name"] = name
            workflow["nodes"] = nodes
            workflow["edges"] = edges
            workflow["updated_at"] = now
            
            with open(path, "w") as f:
                json.dump(workflow, f, indent=2)
            
            return workflow
    
    # Create new workflow
    return create_workflow(name, nodes, edges, user_id)


def list_workflows(user_id: str = "default", limit: int = 50) -> List[Dict[str, Any]]:
    """List all workflows for a user, sorted by most recent first."""
    _ensure_dir()
    
    workflows = []
    for path in config.WORKFLOWS_DIR.glob("*.json"):
        try:
            with open(path, "r") as f:
                workflow = json.load(f)
            
            # Only include workflows for this user
            if workflow.get("user_id") == user_id:
                workflows.append({
                    "id": workflow["id"],
                    "name": workflow["name"],
                    "created_at": workflow.get("created_at"),
                    "updated_at": workflow.get("updated_at"),
                    "node_count": len(workflow.get("nodes", [])),
                    "edge_count": len(workflow.get("edges", [])),
                })
        except Exception:
            continue
    
    # Sort by updated_at descending
    workflows.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return workflows[:limit]


def delete_workflow(workflow_id: str, user_id: str = "default") -> bool:
    """Delete a workflow (only if it belongs to the user)."""
    path = _get_workflow_path(workflow_id)
    if not path.exists():
        return False
    
    # Check if workflow belongs to user
    with open(path, "r") as f:
        workflow = json.load(f)
    
    if workflow.get("user_id") != user_id:
        return False
    
    os.remove(path)
    return True


