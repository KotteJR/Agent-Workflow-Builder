"""
Workflow Builder API

FastAPI application providing endpoints for:
- Workflow execution with SSE streaming
- Workflow storage (save/load/delete)
- Workflow builder AI assistant
- Document management
"""

import json
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from config import config
from workflow_executor import execute_workflow
from workflows import (
    create_workflow,
    get_workflow,
    save_workflow,
    list_workflows,
    delete_workflow,
)
from workflow_builder_llm import (
    build_workflow_from_chat,
    suggest_workflow_improvements,
    get_example_workflow,
    list_example_workflows,
)
import retrieval


# =============================================================================
# FastAPI App Setup
# =============================================================================

app = FastAPI(
    title="Workflow Builder API",
    description="Multi-agent workflow builder with graph-based execution",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Startup Events
# =============================================================================

@app.on_event("startup")
def startup_event():
    """Initialize services on startup."""
    print(f"[STARTUP] LLM Provider: {config.LLM_PROVIDER}")
    print(f"[STARTUP] Models: {config.get_model_config()}")
    
    # Initialize vector stores for both knowledge bases
    try:
        retrieval.initialize_vector_store()
        counts = retrieval.get_all_document_counts()
        print(f"[STARTUP] Vector stores initialized: Legal={counts.get('legal', 0)}, Audit={counts.get('audit', 0)} documents")
    except Exception as e:
        print(f"[STARTUP] Warning: Could not initialize vector store: {e}")


# =============================================================================
# Request/Response Models
# =============================================================================

class WorkflowExecuteRequest(BaseModel):
    message: str
    workflow_nodes: List[Dict[str, Any]]
    workflow_edges: Optional[List[Dict[str, str]]] = []
    knowledge_base: Optional[str] = "legal"


class KnowledgeBaseRequest(BaseModel):
    knowledge_base: str


class WorkflowSaveRequest(BaseModel):
    workflow_id: Optional[str] = None
    name: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, str]]


class WorkflowBuildRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = None


class WorkflowImproveRequest(BaseModel):
    workflow: Dict[str, Any]
    feedback: Optional[str] = None


# =============================================================================
# Workflow Execution Endpoints
# =============================================================================

@app.get("/api/knowledge-base")
async def get_knowledge_base_info():
    """Get information about available knowledge bases."""
    counts = retrieval.get_all_document_counts()
    return {
        "active": retrieval.get_active_knowledge_base(),
        "available": [
            {"id": "legal", "name": "Legal", "document_count": counts.get("legal", 0)},
            {"id": "audit", "name": "Audit", "document_count": counts.get("audit", 0)},
        ]
    }


@app.post("/api/knowledge-base/switch")
async def switch_knowledge_base(req: KnowledgeBaseRequest):
    """Switch the active knowledge base."""
    if req.knowledge_base not in ["legal", "audit"]:
        raise HTTPException(status_code=400, detail="Invalid knowledge base. Must be 'legal' or 'audit'")
    
    retrieval.set_active_knowledge_base(req.knowledge_base)
    return {"active": req.knowledge_base, "message": f"Switched to {req.knowledge_base} knowledge base"}


@app.post("/api/workflow/execute")
async def api_execute_workflow(req: WorkflowExecuteRequest):
    """
    Execute a workflow with SSE streaming.
    
    The workflow is defined by nodes and edges from the frontend.
    Results are streamed as Server-Sent Events.
    """
    # Set knowledge base for this execution if specified
    if req.knowledge_base:
        retrieval.set_active_knowledge_base(req.knowledge_base)
    
    return StreamingResponse(
        execute_workflow(
            user_message=req.message,
            workflow_nodes=req.workflow_nodes,
            workflow_edges=req.workflow_edges or [],
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# =============================================================================
# Workflow Storage Endpoints
# =============================================================================

@app.get("/api/workflows")
async def api_list_workflows(user_id: str = "default"):
    """List all saved workflows for a user."""
    workflows = list_workflows(user_id=user_id)
    return {"workflows": workflows}


@app.get("/api/workflows/{workflow_id}")
async def api_get_workflow(workflow_id: str, user_id: str = "default"):
    """Get a specific workflow by ID."""
    workflow = get_workflow(workflow_id, user_id=user_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@app.post("/api/workflows")
async def api_save_workflow(req: WorkflowSaveRequest, user_id: str = "default"):
    """Save or update a workflow."""
    try:
        workflow = save_workflow(
            workflow_id=req.workflow_id,
            name=req.name,
            nodes=req.nodes,
            edges=req.edges,
            user_id=user_id,
        )
        return workflow
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@app.delete("/api/workflows/{workflow_id}")
async def api_delete_workflow(workflow_id: str, user_id: str = "default"):
    """Delete a workflow."""
    success = delete_workflow(workflow_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"success": True}


# =============================================================================
# Workflow Builder AI Endpoints
# =============================================================================

@app.post("/api/workflow/build")
async def api_build_workflow(req: WorkflowBuildRequest):
    """
    Use AI to build a workflow from natural language description.
    
    The user describes what they want and the AI generates
    the appropriate workflow configuration.
    """
    result = await build_workflow_from_chat(
        user_message=req.message,
        conversation_history=req.conversation_history,
    )
    return result


@app.post("/api/workflow/improve")
async def api_improve_workflow(req: WorkflowImproveRequest):
    """
    Get AI suggestions to improve an existing workflow.
    """
    result = await suggest_workflow_improvements(
        current_workflow=req.workflow,
        user_feedback=req.feedback,
    )
    return result


@app.get("/api/workflow/examples")
async def api_list_examples():
    """List available example workflows."""
    return {"examples": list_example_workflows()}


@app.get("/api/workflow/examples/{example_id}")
async def api_get_example(example_id: str):
    """Get a specific example workflow."""
    example = get_example_workflow(example_id)
    if not example:
        raise HTTPException(status_code=404, detail="Example not found")
    return example


# =============================================================================
# Provider Info Endpoint
# =============================================================================

@app.get("/api/provider")
async def api_provider_info():
    """Get current LLM provider information."""
    model_config = config.get_model_config()
    return {
        "provider": config.LLM_PROVIDER,
        "small_model": model_config["small"],
        "large_model": model_config["large"],
        "image_provider": config.IMAGE_PROVIDER,
    }


@app.get("/api/health")
async def api_health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "document_count": retrieval.get_document_count(),
    }


@app.get("/api/ocr-status")
async def api_ocr_status():
    """Check OCR dependencies status."""
    import subprocess
    import os
    
    status = {
        "tesseract": {"installed": False, "version": None, "error": None},
        "poppler": {"installed": False, "path": None, "error": None},
        "pdf2image": {"installed": False, "error": None},
        "pytesseract": {"installed": False, "error": None},
        "tessdata_prefix": os.environ.get("TESSDATA_PREFIX", "NOT SET"),
    }
    
    # Check Tesseract
    try:
        result = subprocess.run(["tesseract", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            status["tesseract"]["installed"] = True
            status["tesseract"]["version"] = result.stdout.split("\n")[0]
        else:
            status["tesseract"]["error"] = result.stderr
    except Exception as e:
        status["tesseract"]["error"] = str(e)
    
    # Check Poppler (pdftoppm)
    try:
        result = subprocess.run(["which", "pdftoppm"], capture_output=True, text=True)
        if result.returncode == 0:
            status["poppler"]["installed"] = True
            status["poppler"]["path"] = result.stdout.strip()
        else:
            status["poppler"]["error"] = "pdftoppm not found"
    except Exception as e:
        status["poppler"]["error"] = str(e)
    
    # Check pdf2image Python package
    try:
        from pdf2image import convert_from_bytes
        status["pdf2image"]["installed"] = True
    except ImportError as e:
        status["pdf2image"]["error"] = str(e)
    
    # Check pytesseract Python package
    try:
        import pytesseract
        status["pytesseract"]["installed"] = True
        # Try to get tesseract command
        try:
            status["pytesseract"]["tesseract_cmd"] = pytesseract.pytesseract.tesseract_cmd
        except:
            pass
    except ImportError as e:
        status["pytesseract"]["error"] = str(e)
    
    # Check if tessdata directory exists
    tessdata_path = os.environ.get("TESSDATA_PREFIX", "/usr/share/tesseract-ocr/5/tessdata")
    if os.path.exists(tessdata_path):
        try:
            files = os.listdir(tessdata_path)
            status["tessdata_files"] = [f for f in files if f.endswith(".traineddata")]
        except Exception as e:
            status["tessdata_files"] = f"Error listing: {e}"
    else:
        status["tessdata_files"] = f"Directory not found: {tessdata_path}"
    
    # Overall status
    status["ocr_ready"] = all([
        status["tesseract"]["installed"],
        status["poppler"]["installed"],
        status["pdf2image"]["installed"],
        status["pytesseract"]["installed"],
    ])
    
    return status


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
    )


