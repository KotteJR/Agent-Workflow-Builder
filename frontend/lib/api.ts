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

export type { ApiWorkflow as Workflow, ApiWorkflowNode as WorkflowNode, ApiWorkflowEdge as WorkflowEdge };

export interface WorkflowBuildResult {
    explanation: string;
    workflow: ApiWorkflow | null;
    raw_response: string;
}

/**
 * Execute a workflow with SSE streaming.
 */
export async function executeWorkflow(
    message: string,
    nodes: ApiWorkflowNode[],
    edges: ApiWorkflowEdge[],
    onEvent: (event: string, data: unknown) => void
): Promise<void> {
    const response = await fetch(`${API_BASE}/api/workflow/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            message,
            workflow_nodes: nodes,
            workflow_edges: edges,
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

/**
 * Save a workflow to the backend.
 */
export async function saveWorkflow(
    name: string,
    nodes: ApiWorkflowNode[],
    edges: ApiWorkflowEdge[],
    workflowId?: string
): Promise<ApiWorkflow> {
    const response = await fetch(`${API_BASE}/api/workflows`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            workflow_id: workflowId,
            name,
            nodes,
            edges,
        }),
    });

    if (!response.ok) {
        throw new Error(`Save failed: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Load a workflow from the backend.
 */
export async function loadWorkflow(workflowId: string): Promise<ApiWorkflow> {
    const response = await fetch(`${API_BASE}/api/workflows/${workflowId}`);

    if (!response.ok) {
        throw new Error(`Load failed: ${response.statusText}`);
    }

    return response.json();
}

/**
 * List all workflows.
 */
export async function listWorkflows(): Promise<WorkflowListItem[]> {
    const response = await fetch(`${API_BASE}/api/workflows`);

    if (!response.ok) {
        throw new Error(`List failed: ${response.statusText}`);
    }

    const data = await response.json();
    return data.workflows;
}

/**
 * Delete a workflow.
 */
export async function deleteWorkflow(workflowId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/api/workflows/${workflowId}`, {
        method: "DELETE",
    });

    if (!response.ok) {
        throw new Error(`Delete failed: ${response.statusText}`);
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
