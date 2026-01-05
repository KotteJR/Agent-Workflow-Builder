"use client";

import { useCallback, useRef, useState, useMemo } from "react";
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
import { RunWorkflowModal } from "@/components/modals/RunWorkflowModal";
import { NODE_TYPES, NodeSettings } from "@/lib/nodes";
import {
    saveWorkflow,
    loadWorkflow,
    executeWorkflow,
    type Workflow,
    type WorkflowNode as ApiWorkflowNode,
    type WorkflowEdge as ApiWorkflowEdge,
} from "@/lib/api";
import type { WorkflowNodeData, WorkflowExecutionResult } from "@/lib/types";

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
    const [nodes, setNodes, onNodesChange] = useNodesState<Node<WorkflowNodeData>>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

    // UI state
    const [isChatOpen, setIsChatOpen] = useState(true);
    const [settingsNodeId, setSettingsNodeId] = useState<string | null>(null);

    // Workflow state
    const [currentWorkflowId, setCurrentWorkflowId] = useState<string | null>(null);
    const [workflowName, setWorkflowName] = useState("Untitled Workflow");

    // Execution state
    const [isRunning, setIsRunning] = useState(false);
    const [runningAgents, setRunningAgents] = useState<Set<string>>(new Set());
    const [runResult, setRunResult] = useState<WorkflowExecutionResult | null>(null);

    // Modal state
    const [showSaveModal, setShowSaveModal] = useState(false);
    const [showRunModal, setShowRunModal] = useState(false);
    const [runQuery, setRunQuery] = useState("");

    // Callbacks
    const handleNodeSettingsClick = useCallback((nodeId: string) => {
        setSettingsNodeId(nodeId);
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

            const newNode: Node<WorkflowNodeData> = {
        id: `${nodeType}-${Date.now()}`,
        type: "workflow",
        position,
        data: {
          nodeType,
          label: nodeConfig.label,
                    settings: nodeConfig.defaultSettings,
                    onSettingsClick: handleNodeSettingsClick,
        },
        dragHandle: ".drag-handle",
      };

            setNodes((nds) => [...nds, newNode]);
    },
        [reactFlowInstance, setNodes, handleNodeSettingsClick]
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
        (_: React.MouseEvent, node: Node<WorkflowNodeData>) => {
            const nodeConfig = NODE_TYPES.find((n) => n.id === node.data.nodeType);
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
            const workflowNodes: ApiWorkflowNode[] = nodes.map((node) => ({
                id: node.id,
                type: node.type || "workflow",
                position: node.position,
                data: {
                    nodeType: node.data.nodeType,
                    label: node.data.label,
                    settings: node.data.settings,
                },
            }));

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

                const newNodes: Node<WorkflowNodeData>[] = workflow.nodes.map((node) => ({
                    id: node.id,
                    type: node.type || "workflow",
                    position: node.position,
                    data: {
                        nodeType: node.data.nodeType,
                        label: node.data.label,
                        settings: node.data.settings,
                        onSettingsClick: handleNodeSettingsClick,
                    },
                    dragHandle: ".drag-handle",
                }));

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
        [handleNodeSettingsClick, setNodes, setEdges]
    );

    const handleLoadFromChat = useCallback(
        (workflow: Workflow) => {
            const newNodes: Node<WorkflowNodeData>[] = workflow.nodes.map((node) => ({
                id: node.id,
                type: node.type || "workflow",
                position: node.position,
                data: {
                    nodeType: node.data.nodeType,
                    label: node.data.label,
                    settings: node.data.settings,
                    onSettingsClick: handleNodeSettingsClick,
                },
                dragHandle: ".drag-handle",
            }));

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
        [handleNodeSettingsClick, setNodes, setEdges]
    );

    // Execution
    const handleRunWorkflow = useCallback(() => {
        if (nodes.length === 0) {
            alert("Add some nodes before running!");
            return;
        }
        setShowRunModal(true);
        setRunResult(null);
    }, [nodes.length]);

    const confirmRunWorkflow = useCallback(async () => {
        if (!runQuery.trim()) {
            alert("Please enter a query to run the workflow with.");
            return;
        }

        setIsRunning(true);
        setRunningAgents(new Set());
        setRunResult(null);

        try {
            const workflowNodes = nodes.map((node) => ({
                id: node.id,
                type: node.type || "workflow",
                position: node.position,
                data: {
                    nodeType: node.data.nodeType,
                    label: node.data.label,
                    settings: node.data.settings,
                },
            }));

            const workflowEdges = edges.map((edge) => ({
                id: edge.id,
                source: edge.source,
                target: edge.target,
            }));

            await executeWorkflow(runQuery, workflowNodes, workflowEdges, (event, data) => {
                if (event === "agent_start") {
                    const eventData = data as { agent: string };
                    setRunningAgents((prev) => new Set(prev).add(eventData.agent));
                } else if (event === "agent_complete") {
                    const eventData = data as { agent: string };
                    setRunningAgents((prev) => {
                        const next = new Set(prev);
                        next.delete(eventData.agent);
                        return next;
                    });
                } else if (event === "done") {
                    setRunResult(data as WorkflowExecutionResult);
                    setIsRunning(false);
                } else if (event === "error") {
                    const eventData = data as { message: string };
                    alert(`Workflow error: ${eventData.message}`);
                    setIsRunning(false);
                }
            });
        } catch (error) {
            console.error("Failed to run workflow:", error);
            alert("Failed to run workflow. Make sure the backend is running.");
            setIsRunning(false);
        }
    }, [nodes, edges, runQuery]);

    const handleCloseRunModal = useCallback(() => {
        setShowRunModal(false);
        setRunQuery("");
        setRunResult(null);
    }, []);

    // Memoized values
    const nodesWithSettings = useMemo(
        () =>
            nodes.map((node) => ({
                ...node,
                data: {
                    ...node.data,
                    onSettingsClick: handleNodeSettingsClick,
                },
            })),
        [nodes, handleNodeSettingsClick]
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
            />

            {isChatOpen && (
                <AgentChat onClose={() => setIsChatOpen(false)} onLoadWorkflow={handleLoadFromChat} />
            )}

      <Sidebar onDragStart={onDragStart} />

            {selectedNode && (
                <NodeSettingsPanel
                    nodeId={selectedNode.id}
                    nodeType={selectedNode.data.nodeType}
                    currentSettings={selectedNode.data.settings}
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

            <RunWorkflowModal
                isOpen={showRunModal}
                query={runQuery}
                onQueryChange={setRunQuery}
                isRunning={isRunning}
                runningAgents={runningAgents}
                result={runResult}
                onRun={confirmRunWorkflow}
                onClose={handleCloseRunModal}
            />
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
