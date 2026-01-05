/**
 * Shared TypeScript types for the workflow builder frontend.
 */

import { Node, Edge } from "@xyflow/react";
import { NodeSettings } from "./nodes";

// =============================================================================
// Node Data Types
// =============================================================================

export interface WorkflowNodeData extends Record<string, unknown> {
    nodeType: string;
    label: string;
    settings?: NodeSettings;
    onSettingsClick?: (nodeId: string) => void;
    // Inline editing for input nodes
    promptText?: string; // For prompt node
    uploadedFiles?: Array<{ name: string; size: number; type: string; content?: string }>; // For upload node
    uploadInstruction?: string; // Custom instruction for uploaded files
    onDataChange?: (nodeId: string, data: Partial<WorkflowNodeData>) => void; // Callback to update node data
    // Execution state
    executionState?: NodeExecutionState;
    onExecutionClick?: (nodeId: string) => void; // Callback when clicking executing node
    // Output data (for output nodes)
    outputData?: NodeOutputData;
    onOutputClick?: (nodeId: string) => void; // Callback when clicking output node to view result
}

export type WorkflowNode = Node<WorkflowNodeData>;
export type WorkflowEdge = Edge;

// =============================================================================
// API Types
// =============================================================================

export interface ApiWorkflowNode {
    id: string;
    type: string;
    position: { x: number; y: number };
    data: {
        nodeType: string;
        label: string;
        settings?: NodeSettings;
        promptText?: string;
        uploadedFiles?: Array<{ name: string; size: number; type: string; content?: string }>;
        uploadInstruction?: string;
    };
}

export interface ApiWorkflowEdge {
    id: string;
    source: string;
    target: string;
}

export interface ApiWorkflow {
    id: string;
    name: string;
    nodes: ApiWorkflowNode[];
    edges: ApiWorkflowEdge[];
    created_at?: string;
    updated_at?: string;
}

export interface WorkflowListItem {
    id: string;
    name: string;
    created_at?: string;
    updated_at?: string;
    node_count: number;
    edge_count: number;
}

// =============================================================================
// Execution Types
// =============================================================================

export interface AgentStep {
    agent: string;
    model: string;
    action: string;
    content: string;
    excluded?: boolean;
    [key: string]: unknown;
}

export interface ToolOutputs {
    images: Array<{ prompt: string; url: string; style: string }>;
    calculations: Array<{ expression: string; result: unknown; success: boolean }>;
    web_results: Array<{ title: string; snippet: string; url: string }>;
    docs: Array<{ title: string; snippet: string; score: number }>;
}

export interface WorkflowExecutionResult {
    answer: string;
    tool_outputs: ToolOutputs;
    trace: { steps: AgentStep[] };
    latency_ms: number;
}

// =============================================================================
// UI State Types
// =============================================================================

export interface WorkflowState {
    id: string | null;
    name: string;
    isDirty: boolean;
}

// =============================================================================
// SSE Event Types
// =============================================================================

export type SSEEventType = "agent_start" | "agent_complete" | "done" | "error";

export interface SSEAgentStartData {
    agent: string;
    status: string;
}

export interface SSEAgentCompleteData {
    agent: string;
    step: AgentStep;
}

// =============================================================================
// Node Execution State
// =============================================================================

export interface NodeExecutionState {
    isExecuting: boolean;
    step?: AgentStep;
    startTime?: number;
}

export interface NodeOutputData {
    content: string;
    format?: "text" | "csv" | "json" | "spreadsheet";
    timestamp: number;
}

export interface SSEDoneData extends WorkflowExecutionResult {}

export interface SSEErrorData {
    message: string;
}

// =============================================================================
// Execution History Types
// =============================================================================

export interface ExecutionHistoryItem {
    id: string;
    timestamp: number;
    workflowName: string;
    query: string;
    result: WorkflowExecutionResult;
    nodeOutputs: Map<string, AgentStep>; // nodeId -> step output
    duration: number;
}

