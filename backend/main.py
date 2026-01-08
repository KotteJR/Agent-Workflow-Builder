"""
Workflow Builder API

FastAPI application providing endpoints for:
- Workflow execution with SSE streaming
- Workflow storage (save/load/delete)
- Workflow builder AI assistant
- Document management
"""

import json
from pathlib import Path
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
import os

# Use pgvector if DATABASE_URL is set, otherwise fallback to file-based
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL:
    print("[STARTUP] Using PostgreSQL with pgvector for vector storage")
    import retrieval_pgvector as retrieval
else:
    print("[STARTUP] Using file-based vector storage (no DATABASE_URL)")
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
async def startup_event():
    """Initialize services on startup."""
    print(f"[STARTUP] LLM Provider: {config.LLM_PROVIDER}")
    print(f"[STARTUP] Models: {config.get_model_config()}")
    
    # Initialize vector stores / database
    try:
        if DATABASE_URL:
            # Initialize PostgreSQL with pgvector
            import retrieval_pgvector
            success = await retrieval_pgvector.initialize_database()
            if success:
                counts = await retrieval_pgvector.get_all_document_counts_pg()
                print(f"[STARTUP] pgvector database initialized: Legal={counts.get('legal', 0)}, Audit={counts.get('audit', 0)} documents")
            else:
                print("[STARTUP] Warning: pgvector initialization failed")
        else:
            # Use file-based storage
            retrieval.initialize_vector_store()
            counts = retrieval.get_all_document_counts()
            print(f"[STARTUP] File-based vector store: Legal={counts.get('legal', 0)}, Audit={counts.get('audit', 0)} documents")
    except Exception as e:
        print(f"[STARTUP] Warning: Could not initialize vector store: {e}")
        import traceback
        traceback.print_exc()


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


class DocumentUploadRequest(BaseModel):
    title: str
    content: str
    knowledge_base: str = "legal"
    source: Optional[str] = None


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
# Document Management Endpoints (for pgvector)
# =============================================================================

@app.post("/api/documents")
async def api_upload_document(req: DocumentUploadRequest):
    """
    Upload a document to the knowledge base.
    Works with both pgvector (Railway) and file-based storage.
    """
    import hashlib
    
    if req.knowledge_base not in ["legal", "audit"]:
        raise HTTPException(status_code=400, detail="Invalid knowledge base. Must be 'legal' or 'audit'")
    
    # Generate document ID
    doc_id = f"doc_{req.knowledge_base}_{hashlib.md5(req.title.encode()).hexdigest()[:8]}"
    
    if DATABASE_URL:
        # Use pgvector
        import retrieval_pgvector
        import asyncio
        
        try:
            success = await retrieval_pgvector.upsert_document(
                doc_id=doc_id,
                knowledge_base=req.knowledge_base,
                title=req.title,
                content=req.content,
                source=req.source or req.title,
            )
            if success:
                return {"success": True, "document_id": doc_id, "message": "Document uploaded to database"}
            else:
                raise HTTPException(status_code=500, detail="Failed to upload document")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Save to file
        docs_dir = config.get_documents_dir(req.knowledge_base)
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        filename = req.title.replace(" ", "_").replace("/", "-") + ".md"
        filepath = docs_dir / filename
        filepath.write_text(f"# {req.title}\n\n{req.content}", encoding="utf-8")
        
        # Re-initialize vector store for this knowledge base
        retrieval.initialize_vector_store(force=True, knowledge_base=req.knowledge_base)
        
        return {"success": True, "document_id": doc_id, "message": "Document saved to file"}


@app.get("/api/documents")
async def api_list_documents(knowledge_base: str = "legal"):
    """List all documents in a knowledge base."""
    if knowledge_base not in ["legal", "audit"]:
        raise HTTPException(status_code=400, detail="Invalid knowledge base")
    
    if DATABASE_URL:
        import retrieval_pgvector
        pool = await retrieval_pgvector.get_pool()
        
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, title, source, 
                       LENGTH(content) as content_length,
                       created_at, updated_at
                FROM documents 
                WHERE knowledge_base = $1
                ORDER BY created_at DESC
            """, knowledge_base)
            
            return {
                "knowledge_base": knowledge_base,
                "documents": [
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "source": row["source"],
                        "content_length": row["content_length"],
                        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
                    }
                    for row in rows
                ]
            }
    else:
        # List from files
        docs_dir = config.get_documents_dir(knowledge_base)
        documents = []
        if docs_dir.exists():
            for f in sorted(docs_dir.iterdir()):
                if f.suffix in [".md", ".txt", ".pdf"]:
                    documents.append({
                        "id": f"doc_{knowledge_base}_{f.stem}",
                        "title": f.stem.replace("_", " ").title(),
                        "source": f.name,
                        "content_length": f.stat().st_size,
                    })
        return {"knowledge_base": knowledge_base, "documents": documents}


@app.delete("/api/documents/{doc_id}")
async def api_delete_document(doc_id: str):
    """Delete a document from the knowledge base."""
    if DATABASE_URL:
        import retrieval_pgvector
        pool = await retrieval_pgvector.get_pool()
        
        async with pool.acquire() as conn:
            result = await conn.execute("DELETE FROM documents WHERE id = $1", doc_id)
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="Document not found")
            return {"success": True, "message": f"Document {doc_id} deleted"}
    else:
        raise HTTPException(status_code=501, detail="Delete not supported for file-based storage")


@app.get("/api/database-status")
async def api_database_status():
    """Check database connection and pgvector status."""
    if not DATABASE_URL:
        return {
            "mode": "file-based",
            "database_url": None,
            "pgvector_enabled": False,
            "message": "Using file-based storage. Set DATABASE_URL to enable PostgreSQL."
        }
    
    try:
        import retrieval_pgvector
        pool = await retrieval_pgvector.get_pool()
        
        async with pool.acquire() as conn:
            # Check pgvector extension
            ext_result = await conn.fetchrow(
                "SELECT * FROM pg_extension WHERE extname = 'vector'"
            )
            
            # Get document counts
            counts = await conn.fetch("""
                SELECT knowledge_base, COUNT(*) as count 
                FROM documents 
                GROUP BY knowledge_base
            """)
            
            return {
                "mode": "pgvector",
                "database_url": DATABASE_URL[:50] + "..." if len(DATABASE_URL) > 50 else DATABASE_URL,
                "pgvector_enabled": ext_result is not None,
                "documents": {row["knowledge_base"]: row["count"] for row in counts},
                "status": "connected"
            }
    except Exception as e:
        return {
            "mode": "pgvector",
            "database_url": DATABASE_URL[:50] + "..." if len(DATABASE_URL) > 50 else DATABASE_URL,
            "pgvector_enabled": False,
            "status": "error",
            "error": str(e)
        }


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


