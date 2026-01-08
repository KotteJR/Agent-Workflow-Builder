/**
 * API client for the workflow builder backend.
 */

import type {
    ApiWorkflow,
    ApiWorkflowNode,
    ApiWorkflowEdge,
    WorkflowListItem,
    WorkflowExecutionResult,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Log the API URL on load (helps debug Vercel vs localhost issues)
if (typeof window !== 'undefined') {
    console.log(`[API] Backend URL: ${API_BASE}`);
    console.log(`[API] Environment: ${process.env.NEXT_PUBLIC_API_URL ? 'Vercel/Production' : 'Localhost/Development'}`);
}

export type { 
    ApiWorkflow as Workflow, 
    ApiWorkflowNode as WorkflowNode, 
    ApiWorkflowEdge as WorkflowEdge,
    WorkflowListItem,
    WorkflowExecutionResult,
};

export interface WorkflowBuildResult {
    explanation: string;
    workflow: ApiWorkflow | null;
    raw_response: string;
}

export interface KnowledgeBaseInfo {
    active: string;
    available: Array<{
        id: string;
        name: string;
        document_count: number;
    }>;
}

/**
 * Get knowledge base information.
 */
export async function getKnowledgeBaseInfo(): Promise<KnowledgeBaseInfo> {
    const response = await fetch(`${API_BASE}/api/knowledge-base`);
    if (!response.ok) {
        throw new Error(`Failed to get knowledge base info: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Switch the active knowledge base.
 */
export async function switchKnowledgeBase(knowledgeBase: string): Promise<{ active: string; message: string }> {
    const response = await fetch(`${API_BASE}/api/knowledge-base/switch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ knowledge_base: knowledgeBase }),
    });
    if (!response.ok) {
        throw new Error(`Failed to switch knowledge base: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Execute a workflow with SSE streaming.
 */
export async function executeWorkflow(
    message: string,
    nodes: ApiWorkflowNode[],
    edges: ApiWorkflowEdge[],
    onEvent: (event: string, data: unknown) => void,
    knowledgeBase?: string
): Promise<void> {
    const response = await fetch(`${API_BASE}/api/workflow/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            message,
            workflow_nodes: nodes,
            workflow_edges: edges,
            knowledge_base: knowledgeBase,
        }),
    });

    if (!response.ok) {
        throw new Error(`Execution failed: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error("No response body");

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        // Process complete SSE messages
        const messages = buffer.split("\n\n");
        buffer = messages.pop() || ""; // Keep incomplete message in buffer

        for (const message of messages) {
            if (!message.trim()) continue;

            const lines = message.split("\n");
            let eventType = "";
            let data = "";

            for (const line of lines) {
                if (line.startsWith("event: ")) {
                    eventType = line.slice(7).trim();
                } else if (line.startsWith("data: ")) {
                    data = line.slice(6);
                }
            }

            if (eventType && data) {
                try {
                    const parsedData = JSON.parse(data);
                    onEvent(eventType, parsedData);
                } catch (e) {
                    console.error("Failed to parse SSE data:", e, data);
                }
            }
        }
    }
}

// ============ LOCAL STORAGE HELPERS ============
const LOCAL_STORAGE_KEY = "workflow_builder_workflows";

function getLocalWorkflows(): Record<string, ApiWorkflow> {
    if (typeof window === 'undefined') return {};
    try {
        const stored = localStorage.getItem(LOCAL_STORAGE_KEY);
        return stored ? JSON.parse(stored) : {};
    } catch {
        return {};
    }
}

function saveLocalWorkflow(workflow: ApiWorkflow): void {
    if (typeof window === 'undefined') return;
    try {
        const workflows = getLocalWorkflows();
        workflows[workflow.id] = workflow;
        localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(workflows));
        console.log(`[API] Saved workflow locally: ${workflow.name}`);
    } catch (e) {
        console.error("[API] Failed to save to localStorage:", e);
    }
}

function deleteLocalWorkflow(workflowId: string): void {
    if (typeof window === 'undefined') return;
    try {
        const workflows = getLocalWorkflows();
        delete workflows[workflowId];
        localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(workflows));
    } catch (e) {
        console.error("[API] Failed to delete from localStorage:", e);
    }
}

/**
 * Save a workflow to both localStorage and backend.
 */
export async function saveWorkflow(
    name: string,
    nodes: ApiWorkflowNode[],
    edges: ApiWorkflowEdge[],
    workflowId?: string
): Promise<ApiWorkflow> {
    // Generate ID if not provided
    const id = workflowId || crypto.randomUUID().slice(0, 8);
    const now = new Date().toISOString();
    
    // Create workflow object
    const workflow: ApiWorkflow = {
        id,
        name,
        nodes,
        edges,
        created_at: now,
        updated_at: now,
    };
    
    // Always save to localStorage first (works offline)
    saveLocalWorkflow(workflow);
    
    // Try to save to backend too
    try {
        const response = await fetch(`${API_BASE}/api/workflows`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                workflow_id: id,
                name,
                nodes,
                edges,
            }),
        });

        if (response.ok) {
            const backendWorkflow = await response.json();
            // Update local with backend response (has proper timestamps)
            saveLocalWorkflow(backendWorkflow);
            return backendWorkflow;
        }
    } catch (e) {
        console.warn("[API] Backend save failed, using local storage only:", e);
    }
    
    return workflow;
}

/**
 * Load a workflow from localStorage or backend.
 */
export async function loadWorkflow(workflowId: string): Promise<ApiWorkflow> {
    // Check localStorage first
    const localWorkflows = getLocalWorkflows();
    const localWorkflow = localWorkflows[workflowId];
    
    // Try backend
    try {
        const response = await fetch(`${API_BASE}/api/workflows/${workflowId}`);
        if (response.ok) {
            const backendWorkflow = await response.json();
            // Update local cache
            saveLocalWorkflow(backendWorkflow);
            return backendWorkflow;
        }
    } catch (e) {
        console.warn("[API] Backend load failed, using local storage:", e);
    }
    
    // Fall back to local
    if (localWorkflow) {
        return localWorkflow;
    }

    throw new Error(`Workflow not found: ${workflowId}`);
}

/**
 * List all workflows (merges localStorage + backend).
 */
export async function listWorkflows(): Promise<WorkflowListItem[]> {
    console.log(`[API] Listing workflows...`);
    
    // Get local workflows
    const localWorkflows = getLocalWorkflows();
    const localList: WorkflowListItem[] = Object.values(localWorkflows).map(w => ({
        id: w.id,
        name: w.name,
        node_count: w.nodes?.length || 0,
        edge_count: w.edges?.length || 0,
        updated_at: w.updated_at || w.created_at || new Date().toISOString(),
    }));
    
    // Try to get backend workflows
    let backendList: WorkflowListItem[] = [];
    try {
        const response = await fetch(`${API_BASE}/api/workflows`);
        if (response.ok) {
            const data = await response.json();
            backendList = data.workflows || [];
            console.log(`[API] Found ${backendList.length} workflows from backend`);
        }
    } catch (error) {
        console.warn(`[API] Backend unavailable, using local storage only`);
    }
    
    // Merge: backend takes priority, add local-only workflows
    const backendIds = new Set(backendList.map(w => w.id));
    const localOnly = localList.filter(w => !backendIds.has(w.id));
    const merged = [...backendList, ...localOnly];
    
    // Sort by updated_at descending
    merged.sort((a, b) => (b.updated_at || "").localeCompare(a.updated_at || ""));
    
    console.log(`[API] Total workflows: ${merged.length} (${backendList.length} backend, ${localOnly.length} local-only)`);
    return merged;
}

/**
 * Delete a workflow from both localStorage and backend.
 */
export async function deleteWorkflow(workflowId: string): Promise<void> {
    // Always delete from localStorage
    deleteLocalWorkflow(workflowId);
    
    // Try to delete from backend too
    try {
        const response = await fetch(`${API_BASE}/api/workflows/${workflowId}`, {
            method: "DELETE",
        });

        if (!response.ok && response.status !== 404) {
            console.warn(`[API] Backend delete failed: ${response.statusText}`);
        }
    } catch (e) {
        console.warn("[API] Backend delete failed:", e);
    }
}

/**
 * Build a workflow using AI.
 */
export async function buildWorkflowWithAI(
    message: string,
    conversationHistory?: Array<{ role: string; content: string }>
): Promise<WorkflowBuildResult> {
    const response = await fetch(`${API_BASE}/api/workflow/build`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            message,
            conversation_history: conversationHistory,
        }),
    });

    if (!response.ok) {
        throw new Error(`Build failed: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Get AI suggestions to improve a workflow.
 */
export async function improveWorkflowWithAI(
    workflow: ApiWorkflow,
    feedback?: string
): Promise<{ suggestions: string; improved_workflow: ApiWorkflow | null }> {
    const response = await fetch(`${API_BASE}/api/workflow/improve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            workflow,
            feedback,
        }),
    });

    if (!response.ok) {
        throw new Error(`Improve failed: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Get list of example workflows.
 */
export async function listExampleWorkflows(): Promise<
    Array<{ id: string; name: string; description: string }>
> {
    const response = await fetch(`${API_BASE}/api/workflow/examples`);

    if (!response.ok) {
        throw new Error(`List examples failed: ${response.statusText}`);
    }

    const data = await response.json();
    return data.examples;
}

/**
 * Load an example workflow.
 */
export async function loadExampleWorkflow(exampleId: string): Promise<ApiWorkflow> {
    const response = await fetch(`${API_BASE}/api/workflow/examples/${exampleId}`);

    if (!response.ok) {
        throw new Error(`Load example failed: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Get provider info.
 */
export async function getProviderInfo(): Promise<{
    provider: string;
    small_model: string;
    large_model: string;
    image_provider: string;
}> {
    const response = await fetch(`${API_BASE}/api/provider`);

    if (!response.ok) {
        throw new Error(`Get provider failed: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Health check.
 */
export async function healthCheck(): Promise<{ status: string; document_count: number }> {
    const response = await fetch(`${API_BASE}/api/health`);

    if (!response.ok) {
        throw new Error(`Health check failed: ${response.statusText}`);
    }

    return response.json();
}
