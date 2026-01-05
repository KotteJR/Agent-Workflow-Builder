"use client";

import { useCallback, useRef, useState, useMemo, MutableRefObject } from "react";
import {
  ReactFlow,
  Node,
  Edge,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  ReactFlowProvider,
  MarkerType,
  NodeTypes,
  BackgroundVariant,
    ReactFlowInstance,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { WorkflowNode } from "@/components/Node";
import { Sidebar } from "@/components/Sidebar";
import { AgentChat } from "@/components/AgentChat";
import { WorkflowSidebar } from "@/components/WorkflowSidebar";
import DeletableEdge from "@/components/DeletableEdge";
import { NodeSettingsPanel } from "@/components/NodeSettingsPanel";
import { SaveWorkflowModal } from "@/components/modals/SaveWorkflowModal";
import { NodeExecutionModal } from "@/components/modals/NodeExecutionModal";
import { NODE_TYPES, NodeSettings } from "@/lib/nodes";
import {
    saveWorkflow,
    loadWorkflow,
    executeWorkflow,
    type Workflow,
    type WorkflowNode as ApiWorkflowNode,
    type WorkflowEdge as ApiWorkflowEdge,
} from "@/lib/api";
import type { WorkflowNodeData, WorkflowExecutionResult, NodeExecutionState, AgentStep, NodeOutputData, ExecutionHistoryItem } from "@/lib/types";
import { OutputViewModal } from "@/components/modals/OutputViewModal";

// Memoize node types to prevent re-renders
const nodeTypes: NodeTypes = {
  workflow: WorkflowNode,
};

const edgeTypes = {
  deletable: DeletableEdge,
};

// Default edge options - memoized outside component
const defaultEdgeOptions = {
    animated: true,
    style: { strokeWidth: 2, stroke: "#60a5fa" },
    markerEnd: { type: MarkerType.ArrowClosed, color: "#60a5fa" },
    type: "deletable" as const,
};

// Double-click tracking
let lastNodeClick = 0;
let lastNodeId = "";

function FlowCanvas() {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
    const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

    // UI state
    const [isChatOpen, setIsChatOpen] = useState(true);
    const [settingsNodeId, setSettingsNodeId] = useState<string | null>(null);

    // Workflow state
    const [currentWorkflowId, setCurrentWorkflowId] = useState<string | null>(null);
    const [workflowName, setWorkflowName] = useState("Untitled Workflow");

    // Execution state
    const [isRunning, setIsRunning] = useState(false);
    const [nodeExecutionStates, setNodeExecutionStates] = useState<Map<string, NodeExecutionState>>(new Map());
    const [nodeExecutionSteps, setNodeExecutionSteps] = useState<Map<string, AgentStep>>(new Map());
    const [nodeExecutionTimes, setNodeExecutionTimes] = useState<Map<string, number>>(new Map());
    const [runResult, setRunResult] = useState<WorkflowExecutionResult | null>(null);
    const [executionHistory, setExecutionHistory] = useState<ExecutionHistoryItem[]>([]);
    // Ref to track steps during execution (avoids closure issues)
    const executionStepsRef = useRef<Map<string, AgentStep>>(new Map());

    // Node outputs state (stored on output nodes)
    const [nodeOutputs, setNodeOutputs] = useState<Map<string, NodeOutputData>>(new Map());
    
    // Knowledge base state
    const [knowledgeBase, setKnowledgeBase] = useState<string>("legal");

    // Modal state
    const [showSaveModal, setShowSaveModal] = useState(false);
    const [showNodeExecutionModal, setShowNodeExecutionModal] = useState(false);
    const [selectedExecutionNodeId, setSelectedExecutionNodeId] = useState<string | null>(null);
    const [showOutputModal, setShowOutputModal] = useState(false);
    const [selectedOutputNodeId, setSelectedOutputNodeId] = useState<string | null>(null);


    // Callbacks
    const handleNodeSettingsClick = useCallback((nodeId: string) => {
        setSettingsNodeId(nodeId);
    }, []);

    const handleDataChange = useCallback(
        (nodeId: string, data: Partial<WorkflowNodeData>) => {
            setNodes((nds) =>
                nds.map((node) =>
                    node.id === nodeId ? { ...node, data: { ...node.data, ...data } } : node
                )
            );
        },
        [setNodes]
    );

    const handleExecutionClick = useCallback((nodeId: string) => {
        setSelectedExecutionNodeId(nodeId);
        setShowNodeExecutionModal(true);
    }, []);

    const handleOutputClick = useCallback((nodeId: string) => {
        setSelectedOutputNodeId(nodeId);
        setShowOutputModal(true);
    }, []);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge({ ...params, type: "deletable" }, eds)),
    [setEdges]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const nodeType = event.dataTransfer.getData("application/reactflow");
      if (!nodeType || !reactFlowInstance) return;

      const nodeConfig = NODE_TYPES.find((n) => n.id === nodeType);
      if (!nodeConfig) return;

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const newNode: Node = {
        id: `${nodeType}-${Date.now()}`,
        type: "workflow",
        position,
        data: {
          nodeType,
          label: nodeConfig.label,
                    settings: nodeConfig.defaultSettings,
                    onSettingsClick: handleNodeSettingsClick,
                    onDataChange: handleDataChange,
                    promptText: nodeType === "prompt" ? "" : undefined,
                    uploadedFiles: nodeType === "upload" ? [] : undefined,
        },
        dragHandle: ".drag-handle",
      };

            setNodes((nds) => [...nds, newNode]);
    },
        [reactFlowInstance, setNodes, handleNodeSettingsClick, handleDataChange]
  );

  const onDragStart = useCallback((nodeType: string, event: React.DragEvent) => {
    event.dataTransfer.setData("application/reactflow", nodeType);
    event.dataTransfer.effectAllowed = "move";
  }, []);

    const handleSaveSettings = useCallback(
        (nodeId: string, settings: NodeSettings) => {
            setNodes((nds) =>
                nds.map((node) =>
                    node.id === nodeId ? { ...node, data: { ...node.data, settings } } : node
                )
            );
        },
        [setNodes]
    );

    const handleNodeClick = useCallback(
        (_: React.MouseEvent, node: Node) => {
            const nodeData = node.data as WorkflowNodeData;
            const nodeConfig = NODE_TYPES.find((n) => n.id === nodeData.nodeType);
            if (nodeConfig?.hasSettings) {
                const now = Date.now();
                // Detect double-click
                if (lastNodeClick && now - lastNodeClick < 300 && lastNodeId === node.id) {
                    handleNodeSettingsClick(node.id);
                }
                lastNodeClick = now;
                lastNodeId = node.id;
            }
        },
        [handleNodeSettingsClick]
    );

    // Workflow management
    const handleNewWorkflow = useCallback(() => {
        if (nodes.length > 0 && !confirm("Create a new workflow? Unsaved changes will be lost.")) {
            return;
        }
        setNodes([]);
        setEdges([]);
        setCurrentWorkflowId(null);
        setWorkflowName("Untitled Workflow");
    }, [nodes.length, setNodes, setEdges]);

    const handleSaveWorkflow = useCallback(() => {
        if (nodes.length === 0) {
            alert("Add some nodes before saving!");
            return;
        }
        setShowSaveModal(true);
    }, [nodes.length]);

    const confirmSaveWorkflow = useCallback(async () => {
        try {
            const workflowNodes: ApiWorkflowNode[] = nodes.map((node) => {
                const nodeData = node.data as WorkflowNodeData;
                return {
                    id: node.id,
                    type: node.type || "workflow",
                    position: node.position,
                    data: {
                        nodeType: nodeData.nodeType,
                        label: nodeData.label,
                        settings: nodeData.settings,
                        promptText: nodeData.promptText,
                        uploadedFiles: nodeData.uploadedFiles,
                    },
                };
            });

            const workflowEdges: ApiWorkflowEdge[] = edges.map((edge) => ({
                id: edge.id,
                source: edge.source,
                target: edge.target,
            }));

            const result = await saveWorkflow(
                workflowName,
                workflowNodes,
                workflowEdges,
                currentWorkflowId || undefined
            );

            setCurrentWorkflowId(result.id);
            setShowSaveModal(false);
            alert("Workflow saved successfully!");
        } catch (error) {
            console.error("Failed to save workflow:", error);
            alert("Failed to save workflow. Make sure the backend is running.");
        }
    }, [nodes, edges, workflowName, currentWorkflowId]);

    const handleLoadWorkflow = useCallback(
        async (workflowId: string) => {
            try {
                const workflow = await loadWorkflow(workflowId);

                const newNodes: Node[] = workflow.nodes.map((node) => {
                    const nodeData = node.data as any;
                    return {
                        id: node.id,
                        type: node.type || "workflow",
                        position: node.position,
                        data: {
                            nodeType: nodeData.nodeType,
                            label: nodeData.label,
                            settings: nodeData.settings,
                            onSettingsClick: handleNodeSettingsClick,
                            onDataChange: handleDataChange,
                            promptText: nodeData.promptText,
                            uploadedFiles: nodeData.uploadedFiles,
                        },
                        dragHandle: ".drag-handle",
                    };
                });

                const newEdges: Edge[] = workflow.edges.map((edge) => ({
                    id: edge.id,
                    source: edge.source,
                    target: edge.target,
                    type: "deletable",
                    animated: true,
                    style: { strokeWidth: 2, stroke: "#60a5fa" },
                    markerEnd: { type: MarkerType.ArrowClosed, color: "#60a5fa" },
                }));

                setNodes(newNodes);
                setEdges(newEdges);
                setCurrentWorkflowId(workflow.id);
                setWorkflowName(workflow.name);
            } catch (error) {
                console.error("Failed to load workflow:", error);
                alert("Failed to load workflow. Make sure the backend is running.");
            }
        },
        [handleNodeSettingsClick, handleDataChange, setNodes, setEdges]
    );

    const handleLoadFromChat = useCallback(
        (workflow: Workflow) => {
            const newNodes: Node[] = workflow.nodes.map((node) => {
                const nodeData = node.data as any;
                return {
                    id: node.id,
                    type: node.type || "workflow",
                    position: node.position,
                    data: {
                        nodeType: nodeData.nodeType,
                        label: nodeData.label,
                        settings: nodeData.settings,
                        onSettingsClick: handleNodeSettingsClick,
                        onDataChange: handleDataChange,
                        promptText: nodeData.promptText,
                        uploadedFiles: nodeData.uploadedFiles,
                    },
                    dragHandle: ".drag-handle",
                };
            });

            const newEdges: Edge[] = workflow.edges.map((edge) => ({
                id: edge.id,
                source: edge.source,
                target: edge.target,
                type: "deletable",
                animated: true,
                style: { strokeWidth: 2, stroke: "#60a5fa" },
                markerEnd: { type: MarkerType.ArrowClosed, color: "#60a5fa" },
            }));

            setNodes(newNodes);
            setEdges(newEdges);
            setCurrentWorkflowId(null);
            setWorkflowName(workflow.name || "AI Generated Workflow");
        },
        [handleNodeSettingsClick, handleDataChange, setNodes, setEdges]
    );

    // Execution - runs directly without modal, using prompt/upload node content
    const handleRunWorkflow = useCallback(async () => {
        if (nodes.length === 0) {
            alert("Add some nodes before running!");
            return;
        }

        // Find input nodes and extract query
        let query = "";
        let hasUpload = false;
        let uploadNode: Node | undefined;
        let hasSpreadsheet = false;
        let hasTransformer = false;
        
        // First pass: identify workflow structure
        for (const node of nodes) {
            const nodeData = node.data as WorkflowNodeData;
            if (nodeData.nodeType === "spreadsheet") hasSpreadsheet = true;
            if (nodeData.nodeType === "transformer") hasTransformer = true;
            if (nodeData.nodeType === "prompt") {
                query = nodeData.promptText || "";
            } else if (nodeData.nodeType === "upload") {
                hasUpload = true;
                uploadNode = node;
            }
        }
        
        // Determine query based on workflow structure if not provided
        if (hasUpload && uploadNode) {
            const uploadData = uploadNode.data as WorkflowNodeData;
            const fileCount = uploadData.uploadedFiles?.length || 0;
            if (fileCount > 0) {
                // Use custom instruction if provided
                if (uploadData.uploadInstruction && uploadData.uploadInstruction.trim()) {
                    query = uploadData.uploadInstruction;
                }
                // Otherwise, auto-detect based on workflow
                else if (hasSpreadsheet || hasTransformer) {
                    query = "Analyze the uploaded document and extract ALL data into a structured format. Identify the document type and extract every piece of meaningful information.";
                } else {
                    query = "Analyze the uploaded document and provide a comprehensive summary.";
                }
            }
        }

        if (!query && !hasUpload) {
            alert("Please enter a prompt in the Prompt node before running.");
            return;
        }

        if (hasUpload && uploadNode) {
            // Check if files are uploaded
            const uploadData = uploadNode.data as WorkflowNodeData;
            if (!uploadData?.uploadedFiles?.length) {
                alert("Please upload files in the Upload node before running.");
                return;
            }
        }

        setIsRunning(true);
        setNodeExecutionStates(new Map());
        setNodeExecutionSteps(new Map());
        setNodeExecutionTimes(new Map());
        setNodeOutputs(new Map()); // Clear previous outputs
        setRunResult(null);
        executionStepsRef.current = new Map(); // Clear ref

        try {
            const workflowNodes = nodes.map((node) => {
                const nodeData = node.data as WorkflowNodeData;
                return {
                    id: node.id,
                    type: node.type || "workflow",
                    position: node.position,
                    data: {
                        nodeType: nodeData.nodeType,
                        label: nodeData.label,
                        settings: nodeData.settings,
                        promptText: nodeData.promptText,
                        uploadedFiles: nodeData.uploadedFiles,
                        uploadInstruction: nodeData.uploadInstruction,
                    },
                };
            });

            const workflowEdges = edges.map((edge) => ({
                id: edge.id,
                source: edge.source,
                target: edge.target,
            }));

            await executeWorkflow(query, workflowNodes, workflowEdges, (event, data) => {
                if (event === "agent_start") {
                    const eventData = data as { agent: string; status?: string };
                    const nodeId = eventData.agent;
                    const startTime = Date.now();
                    
                    setNodeExecutionStates((prev) => {
                        const next = new Map(prev);
                        next.set(nodeId, {
                            isExecuting: true,
                            startTime,
                        });
                        return next;
                    });
                } else if (event === "agent_complete") {
                    const eventData = data as { agent: string; step?: AgentStep };
                    const nodeId = eventData.agent;
                    const step = eventData.step;
                    
                    setNodeExecutionStates((prev) => {
                        const next = new Map(prev);
                        const current = next.get(nodeId);
                        const executionTime = current?.startTime ? Date.now() - current.startTime : undefined;
                        
                        if (current) {
                            next.set(nodeId, {
                                ...current,
                                isExecuting: false,
                                step,
                            });
                        }
                        
                        // Store step and execution time separately
                        if (step) {
                            // Update ref immediately (no closure issues)
                            executionStepsRef.current.set(nodeId, step);
                            // Also update state for UI
                            setNodeExecutionSteps((prevSteps) => {
                                const nextSteps = new Map(prevSteps);
                                nextSteps.set(nodeId, step);
                                return nextSteps;
                            });
                        }
                        
                        if (executionTime !== undefined) {
                            setNodeExecutionTimes((prevTimes) => {
                                const nextTimes = new Map(prevTimes);
                                nextTimes.set(nodeId, executionTime);
                                return nextTimes;
                            });
                        }
                        
                        return next;
                    });
                } else if (event === "done") {
                    const result = data as WorkflowExecutionResult;
                    setRunResult(result);
                    setIsRunning(false);
                    
                    // Store output on output nodes (response, spreadsheet)
                    const outputContent = result.answer || "";
                    const isSpreadsheet = (result as any).output_format === "spreadsheet";
                    const hasImages = result.tool_outputs?.images?.length > 0;
                    
                    // Find output nodes and store the result
                    const newOutputs = new Map<string, NodeOutputData>();
                    for (const node of nodes) {
                        const nodeData = node.data as WorkflowNodeData;
                        if (nodeData.nodeType === "response" || nodeData.nodeType === "spreadsheet") {
                            newOutputs.set(node.id, {
                                content: outputContent,
                                format: hasImages ? "image" : (isSpreadsheet ? "spreadsheet" : "text"),
                                timestamp: Date.now(),
                                images: result.tool_outputs?.images,
                            });
                        }
                    }
                    setNodeOutputs(newOutputs);
                    
                    // Save to execution history (use ref for latest steps)
                    const historyItem: ExecutionHistoryItem = {
                        id: `exec-${Date.now()}`,
                        timestamp: Date.now(),
                        workflowName: workflowName,
                        query: query,
                        result: result,
                        nodeOutputs: new Map(executionStepsRef.current),
                        duration: result.latency_ms || 0,
                    };
                    setExecutionHistory((prev) => [historyItem, ...prev].slice(0, 50));
                    
                    // Clear execution states after a short delay
                    setTimeout(() => {
                        setNodeExecutionStates(new Map());
                    }, 2000);
                } else if (event === "error") {
                    const eventData = data as { message: string };
                    alert(`Workflow error: ${eventData.message}`);
                    setIsRunning(false);
                    setNodeExecutionStates(new Map());
                    setNodeExecutionSteps(new Map());
                    setNodeExecutionTimes(new Map());
                }
            }, knowledgeBase);
        } catch (error) {
            console.error("Failed to run workflow:", error);
            alert("Failed to run workflow. Make sure the backend is running.");
            setIsRunning(false);
        }
    }, [nodes, edges, workflowName, knowledgeBase]);

    // Memoized values
    const nodesWithSettings = useMemo(
        () =>
            nodes.map((node) => {
                const nodeData = node.data as WorkflowNodeData;
                const executionState = nodeExecutionStates.get(node.id);
                const outputData = nodeOutputs.get(node.id);
                return {
                    ...node,
                    data: {
                        ...nodeData,
                        onSettingsClick: handleNodeSettingsClick,
                        onDataChange: handleDataChange,
                        executionState,
                        onExecutionClick: handleExecutionClick,
                        outputData,
                        onOutputClick: handleOutputClick,
                    },
                };
            }),
        [nodes, handleNodeSettingsClick, handleDataChange, nodeExecutionStates, handleExecutionClick, nodeOutputs, handleOutputClick]
    );

    const selectedNode = useMemo(
        () => (settingsNodeId ? nodesWithSettings.find((n) => n.id === settingsNodeId) : null),
        [settingsNodeId, nodesWithSettings]
    );

  return (
    <div className="h-screen w-screen bg-white">
      <div className="absolute inset-0" ref={reactFlowWrapper}>
        <ReactFlow
                    nodes={nodesWithSettings}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onInit={setReactFlowInstance}
          onDrop={onDrop}
          onDragOver={onDragOver}
                    onNodeClick={handleNodeClick}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          fitView
          snapToGrid
          snapGrid={[15, 15]}
                    defaultEdgeOptions={defaultEdgeOptions}
          deleteKeyCode="Delete"
          style={{ backgroundColor: "#ffffff" }}
        >
          <Background
            color="#555555"
            bgColor="#ffffff"
            gap={20}
            size={3}
            variant={BackgroundVariant.Dots}
          />
          <Controls />
        </ReactFlow>
      </div>

            <WorkflowSidebar
                isChatOpen={isChatOpen}
                onToggleChat={() => setIsChatOpen((prev) => !prev)}
                onNewWorkflow={handleNewWorkflow}
                onLoadWorkflow={handleLoadWorkflow}
                onSaveWorkflow={handleSaveWorkflow}
                onRunWorkflow={handleRunWorkflow}
                isRunning={isRunning}
                currentWorkflowId={currentWorkflowId}
                executionHistory={executionHistory}
                knowledgeBase={knowledgeBase}
                onKnowledgeBaseChange={setKnowledgeBase}
            />

            {isChatOpen && (
                <AgentChat onClose={() => setIsChatOpen(false)} onLoadWorkflow={handleLoadFromChat} />
            )}

      <Sidebar onDragStart={onDragStart} />

            {selectedNode && (
                <NodeSettingsPanel
                    nodeId={selectedNode.id}
                    nodeType={(selectedNode.data as WorkflowNodeData).nodeType}
                    currentSettings={(selectedNode.data as WorkflowNodeData).settings}
                    onClose={() => setSettingsNodeId(null)}
                    onSave={(settings) => handleSaveSettings(selectedNode.id, settings)}
                />
            )}

            <SaveWorkflowModal
                isOpen={showSaveModal}
                workflowName={workflowName}
                onNameChange={setWorkflowName}
                onSave={confirmSaveWorkflow}
                onClose={() => setShowSaveModal(false)}
            />

            {selectedExecutionNodeId && (
                <NodeExecutionModal
                    isOpen={showNodeExecutionModal}
                    onClose={() => {
                        setShowNodeExecutionModal(false);
                        setSelectedExecutionNodeId(null);
                    }}
                    nodeId={selectedExecutionNodeId}
                    nodeLabel={(nodesWithSettings.find((n) => n.id === selectedExecutionNodeId)?.data as WorkflowNodeData)?.label || "Node"}
                    step={nodeExecutionSteps.get(selectedExecutionNodeId)}
                    executionTime={nodeExecutionTimes.get(selectedExecutionNodeId)}
                />
            )}

            {selectedOutputNodeId && (
                <OutputViewModal
                    isOpen={showOutputModal}
                    onClose={() => {
                        setShowOutputModal(false);
                        setSelectedOutputNodeId(null);
                    }}
                    nodeId={selectedOutputNodeId}
                    nodeType={(nodesWithSettings.find((n) => n.id === selectedOutputNodeId)?.data as WorkflowNodeData)?.nodeType || "response"}
                    outputData={nodeOutputs.get(selectedOutputNodeId)}
                />
            )}
    </div>
  );
}

export default function Page() {
  return (
    <ReactFlowProvider>
      <FlowCanvas />
    </ReactFlowProvider>
  );
}
