"use client";

import { useState, useEffect } from "react";
import {
    HiPlay,
    HiPause,
    HiStop,
    HiPlus,
    HiFolderOpen,
    HiChatBubbleLeftRight,
    HiInboxArrowDown,
    HiChevronRight,
    HiChevronLeft,
    HiXMark,
    HiTrash,
    HiClock,
    HiChevronDown,
    HiChevronUp,
} from "react-icons/hi2";
import { HiScale, HiClipboardDocumentCheck } from "react-icons/hi2";
import { listWorkflows, deleteWorkflow, switchKnowledgeBase, getKnowledgeBaseInfo, type WorkflowListItem } from "@/lib/api";
import type { ExecutionHistoryItem, AgentStep } from "@/lib/types";

type WorkflowSidebarProps = {
    isChatOpen: boolean;
    onToggleChat: () => void;
    onNewWorkflow: () => void;
    onLoadWorkflow: (workflowId: string) => void;
    onSaveWorkflow: () => void;
    onRunWorkflow: () => void;
    isRunning?: boolean;
    currentWorkflowId?: string | null;
    executionHistory?: ExecutionHistoryItem[];
    knowledgeBase?: string;
    onKnowledgeBaseChange?: (kb: string) => void;
};

export function WorkflowSidebar({
    isChatOpen,
    onToggleChat,
    onNewWorkflow,
    onLoadWorkflow,
    onSaveWorkflow,
    onRunWorkflow,
    isRunning = false,
    currentWorkflowId,
    executionHistory = [],
    knowledgeBase = "legal",
    onKnowledgeBaseChange,
}: WorkflowSidebarProps) {
    const [isExpanded, setIsExpanded] = useState(false);
    const [showLoadModal, setShowLoadModal] = useState(false);
    const [showHistoryModal, setShowHistoryModal] = useState(false);
    const [selectedHistoryItem, setSelectedHistoryItem] = useState<ExecutionHistoryItem | null>(null);
    const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
    const [workflows, setWorkflows] = useState<WorkflowListItem[]>([]);
    const [loadingWorkflows, setLoadingWorkflows] = useState(false);
    const [isSwitching, setIsSwitching] = useState(false);
    
    const handleKnowledgeBaseToggle = async () => {
        if (isSwitching) return;
        const newKb = knowledgeBase === "legal" ? "audit" : "legal";
        setIsSwitching(true);
        try {
            await switchKnowledgeBase(newKb);
            onKnowledgeBaseChange?.(newKb);
        } catch (error) {
            console.error("Failed to switch knowledge base:", error);
        } finally {
            setIsSwitching(false);
        }
    };

    const fetchWorkflows = async () => {
        setLoadingWorkflows(true);
        try {
            const data = await listWorkflows();
            setWorkflows(data);
        } catch (error) {
            console.error("Failed to fetch workflows:", error);
        } finally {
            setLoadingWorkflows(false);
        }
    };

    const handleOpenLoadModal = () => {
        setShowLoadModal(true);
        fetchWorkflows();
    };

    const handleLoadWorkflow = (workflowId: string) => {
        onLoadWorkflow(workflowId);
        setShowLoadModal(false);
    };

    const handleDeleteWorkflow = async (workflowId: string, e: React.MouseEvent) => {
        e.stopPropagation();
        if (!confirm("Are you sure you want to delete this workflow?")) return;
        
        try {
            await deleteWorkflow(workflowId);
            setWorkflows((prev) => prev.filter((w) => w.id !== workflowId));
        } catch (error) {
            console.error("Failed to delete workflow:", error);
        }
    };

    return (
        <>
        <div
            className={`
                absolute left-6 top-6 bottom-6
                bg-white rounded-2xl shadow-xl border border-gray-200
                flex flex-col z-20
                transition-all duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1.0)]
                ${isExpanded ? 'w-80' : 'w-20'}
            `}
        >
            {/* Logo */}
            <div className="p-3 flex items-center justify-center border-b border-gray-100">
                <img 
                    src="/thefuture-cats-main-logo-001.png.webp" 
                    alt="Logo" 
                    className={`transition-all duration-300 ${isExpanded ? 'h-10' : 'h-8'}`}
                />
            </div>
            {/* Inner container for overflow management */}
            <div className="flex-1 flex flex-col overflow-hidden w-full relative">
                {/* Workflow Actions */}
                <div className="pt-3 pb-3 border-b border-gray-100 flex flex-col gap-3">
                        <button
                            onClick={onNewWorkflow}
                            className="flex items-center justify-start p-0 text-blue-600 rounded-xl transition-all overflow-hidden relative group h-12 w-full"
                            title="New Workflow"
                        >
                        <div className="w-20 h-12 flex items-center justify-center flex-shrink-0">
                            <div className="w-10 h-10 flex items-center justify-center rounded-lg group-hover:bg-blue-100/50 transition-colors">
                                <HiPlus className="w-6 h-6 transition-transform duration-200 group-hover:scale-110" />
                            </div>
                        </div>
                        <span
                            className={`
                                text-sm font-semibold whitespace-nowrap transition-all duration-300 absolute left-16
                                ${isExpanded ? 'opacity-100 translate-x-4' : 'opacity-0 -translate-x-4 pointer-events-none'}
                            `}
                        >
                            New Workflow
                        </span>
                    </button>

                        <button
                            onClick={handleOpenLoadModal}
                            className="flex items-center justify-start p-0 text-gray-600 rounded-xl transition-all overflow-hidden relative group h-12 w-full"
                            title="Load Workflow"
                        >
                        <div className="w-20 h-12 flex items-center justify-center flex-shrink-0">
                            <div className="w-10 h-10 flex items-center justify-center rounded-lg group-hover:bg-gray-200/50 transition-colors">
                                <HiFolderOpen className="w-6 h-6 transition-transform duration-200 group-hover:scale-110" />
                            </div>
                        </div>
                        <span
                            className={`
                                text-sm font-semibold whitespace-nowrap transition-all duration-300 absolute left-16
                                ${isExpanded ? 'opacity-100 translate-x-4' : 'opacity-0 -translate-x-4 pointer-events-none'}
                            `}
                        >
                            Load Existing
                        </span>
                    </button>

                        <button
                            onClick={onSaveWorkflow}
                            className="flex items-center justify-start p-0 text-gray-600 rounded-xl transition-all overflow-hidden relative group h-12 w-full"
                            title="Save Workflow"
                        >
                        <div className="w-20 h-12 flex items-center justify-center flex-shrink-0">
                            <div className="w-10 h-10 flex items-center justify-center rounded-lg group-hover:bg-gray-200/50 transition-colors">
                                <HiInboxArrowDown className="w-6 h-6 transition-transform duration-200 group-hover:scale-110" />
                            </div>
                        </div>
                        <span
                            className={`
                                text-sm font-semibold whitespace-nowrap transition-all duration-300 absolute left-16
                                ${isExpanded ? 'opacity-100 translate-x-4' : 'opacity-0 -translate-x-4 pointer-events-none'}
                            `}
                        >
                            Save Progress
                        </span>
                    </button>
                </div>

                {/* History Section */}
                {executionHistory.length > 0 && (
                    <div className="pt-3 pb-3 border-t border-gray-100">
                        <button
                            onClick={() => setShowHistoryModal(true)}
                            className="flex items-center justify-start p-0 text-gray-600 rounded-xl transition-all overflow-hidden relative group h-12 w-full"
                            title="Execution History"
                        >
                            <div className="w-20 h-12 flex items-center justify-center flex-shrink-0">
                                <div className="w-10 h-10 flex items-center justify-center rounded-lg group-hover:bg-gray-200/50 transition-colors relative">
                                    <HiClock className="w-6 h-6 transition-transform duration-200 group-hover:scale-110" />
                                    <span className="absolute -top-1 -right-1 w-5 h-5 bg-blue-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                                        {executionHistory.length}
                                    </span>
                                </div>
                            </div>
                            <span
                                className={`
                                    text-sm font-semibold whitespace-nowrap transition-all duration-300 absolute left-16
                                    ${isExpanded ? 'opacity-100 translate-x-4' : 'opacity-0 -translate-x-4 pointer-events-none'}
                                `}
                            >
                                History ({executionHistory.length})
                            </span>
                        </button>
                    </div>
                )}

                {/* Spacer */}
                <div className="flex-1" />
                
                {/* Knowledge Base Toggle */}
                <div className="px-3 py-4 border-t border-gray-100">
                    <div className="flex flex-col items-center gap-2">
                        {/* Minimal pill toggle */}
                        <button
                            onClick={handleKnowledgeBaseToggle}
                            disabled={isSwitching}
                            className={`
                                relative flex items-center justify-center
                                w-12 h-12 rounded-full border-2 transition-all duration-300
                                ${isSwitching ? "opacity-50" : "hover:scale-105"}
                                ${knowledgeBase === "legal" 
                                    ? "bg-blue-50 border-blue-200 text-blue-600" 
                                    : "bg-emerald-50 border-emerald-200 text-emerald-600"
                                }
                            `}
                            title={`${knowledgeBase === "legal" ? "Legal" : "Audit"} · Click to switch`}
                        >
                            {knowledgeBase === "legal" ? (
                                <HiScale className="w-5 h-5" />
                            ) : (
                                <HiClipboardDocumentCheck className="w-5 h-5" />
                            )}
                            
                            {/* Small indicator dot */}
                            <span className={`
                                absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white
                                ${knowledgeBase === "legal" ? "bg-blue-500" : "bg-emerald-500"}
                            `} />
                        </button>
                        
                        {/* Label */}
                        <span className={`
                            text-[10px] font-semibold uppercase tracking-wider transition-colors duration-300
                            ${knowledgeBase === "legal" ? "text-blue-600" : "text-emerald-600"}
                        `}>
                            {knowledgeBase}
                        </span>
                    </div>
                </div>

                {/* Toggle Chat */}
                <div className="pt-3 pb-3 border-t border-gray-100">
                    <button
                        onClick={onToggleChat}
                        className={`
                            flex items-center justify-start p-0 w-full rounded-xl transition-all overflow-hidden relative group h-12
                            ${isChatOpen ? 'bg-purple-0 text-purple-600 hover:bg-purple-0' : 'text-gray-600 hover:bg-gray-0'}
                        `}
                        title="Toggle Assistant"
                    >
                        <div className="w-20 h-12 flex items-center justify-center flex-shrink-0">
                            <div className={`w-10 h-10 flex items-center justify-center rounded-lg transition-colors ${isChatOpen ? 'bg-purple-100' : 'group-hover:transparent'}`}>
                                <HiChatBubbleLeftRight className="w-6 h-6 transition-transform duration-200 group-hover:scale-110" />
                            </div>
                        </div>
                        <span
                            className={`
                                text-sm font-semibold whitespace-nowrap transition-all duration-300 absolute left-16
                                ${isExpanded ? 'opacity-100 translate-x-4' : 'opacity-0 -translate-x-4 pointer-events-none'}
                            `}
                        >
                            AI Assistant
                        </span>
                    </button>
                </div>

                {/* Controls */}
                <div className="p-3 border-t border-gray-100 bg-gray-50/50">
                    <div className={`flex gap-3 items-center py-2 h-14 ${isExpanded ? 'justify-center' : 'flex-col'}`}>
                            <button
                                onClick={onRunWorkflow}
                                disabled={isRunning}
                                className={`w-10 h-10 border rounded-full transition-all active:scale-95 flex items-center justify-center flex-shrink-0 group ${
                                    isRunning
                                        ? 'bg-gray-100 border-gray-300 text-gray-400 cursor-not-allowed'
                                        : 'bg-white border-gray-200 text-green-500 hover:shadow-lg hover:border-green-300 hover:text-green-600'
                                }`}
                                title="Run"
                            >
                            <HiPlay className="w-6 h-6 ml-0.5 group-hover:scale-110 transition-transform" />
                        </button>
                        {isExpanded && (
                            <>
                                <button className="w-10 h-10 bg-white border border-gray-200 text-amber-500 rounded-full hover:shadow-lg hover:border-amber-300 hover:text-amber-600 transition-all active:scale-95 flex items-center justify-center flex-shrink-0 group" title="Pause">
                                    <HiPause className="w-6 h-6 group-hover:scale-110 transition-transform" />
                                </button>
                                <button className="w-10 h-10 bg-white border border-gray-200 text-rose-500 rounded-full hover:shadow-lg hover:border-rose-300 hover:text-rose-600 transition-all active:scale-95 flex items-center justify-center flex-shrink-0 group" title="Stop">
                                    <HiStop className="w-6 h-6 group-hover:scale-110 transition-transform" />
                                </button>
                            </>
                        )}
                    </div>
                </div>
            </div>

                {/* Expand Toggle */}
            <div className="absolute right-0 top-1/2 transform translate-x-1/2 z-30">
                <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="bg-white border border-gray-200 rounded-full w-8 h-8 flex items-center justify-center text-gray-500 shadow-md hover:text-gray-800 hover:scale-110 hover:shadow-lg transition-all active:scale-95"
                >
                    {isExpanded ? <HiChevronLeft className="w-4 h-4" /> : <HiChevronRight className="w-4 h-4" />}
                </button>
            </div>
        </div>

            {/* Load Workflow Modal */}
            {showLoadModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100]">
                    <div className="bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 overflow-hidden">
                        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                            <h2 className="text-lg font-semibold text-gray-900">Load Workflow</h2>
                            <button
                                onClick={() => setShowLoadModal(false)}
                                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                            >
                                <HiXMark className="w-5 h-5 text-gray-500" />
                            </button>
                        </div>
                        
                        <div className="p-4 max-h-96 overflow-y-auto">
                            {loadingWorkflows ? (
                                <div className="text-center py-8 text-gray-500">Loading...</div>
                            ) : workflows.length === 0 ? (
                                <div className="text-center py-8 text-gray-500">
                                    No saved workflows found
                                </div>
                            ) : (
                                <div className="space-y-2">
                                    {workflows.map((workflow) => (
                                        <div
                                            key={workflow.id}
                                            onClick={() => handleLoadWorkflow(workflow.id)}
                                            className={`p-3 rounded-lg border cursor-pointer transition-all hover:border-blue-300 hover:bg-blue-50 ${
                                                workflow.id === currentWorkflowId
                                                    ? 'border-blue-500 bg-blue-50'
                                                    : 'border-gray-200'
                                            }`}
                                        >
                                            <div className="flex items-center justify-between">
                                                <div>
                                                    <h3 className="font-medium text-gray-900">{workflow.name}</h3>
                                                    <p className="text-xs text-gray-500 mt-1">
                                                        {workflow.node_count} nodes · {workflow.edge_count} connections
                                                    </p>
                                                </div>
                                                <button
                                                    onClick={(e) => handleDeleteWorkflow(workflow.id, e)}
                                                    className="p-2 hover:bg-red-100 rounded-lg transition-colors text-gray-400 hover:text-red-500"
                                                >
                                                    <HiTrash className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* History Modal */}
            {showHistoryModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100]">
                    <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl mx-4 max-h-[80vh] flex flex-col overflow-hidden">
                        <div className="p-4 border-b border-gray-200 flex items-center justify-between flex-shrink-0">
                            <h2 className="text-lg font-semibold text-gray-900">
                                {selectedHistoryItem ? "Execution Details" : "Execution History"}
                            </h2>
                            <button
                                onClick={() => {
                                    if (selectedHistoryItem) {
                                        setSelectedHistoryItem(null);
                                        setExpandedNodes(new Set());
                                    } else {
                                        setShowHistoryModal(false);
                                    }
                                }}
                                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                            >
                                <HiXMark className="w-5 h-5 text-gray-500" />
                            </button>
                        </div>
                        
                        <div className="flex-1 overflow-y-auto p-4 scrollbar-hide">
                            {selectedHistoryItem ? (
                                <HistoryDetailView 
                                    item={selectedHistoryItem} 
                                    expandedNodes={expandedNodes}
                                    setExpandedNodes={setExpandedNodes}
                                />
                            ) : (
                                <div className="space-y-2">
                                    {executionHistory.map((item) => (
                                        <div
                                            key={item.id}
                                            onClick={() => setSelectedHistoryItem(item)}
                                            className="p-4 rounded-lg border border-gray-200 cursor-pointer transition-all hover:border-blue-300 hover:bg-blue-50"
                                        >
                                            <div className="flex items-center justify-between">
                                                <div className="flex-1 min-w-0">
                                                    <h3 className="font-medium text-gray-900 truncate">{item.workflowName}</h3>
                                                    <p className="text-xs text-gray-500 mt-1 truncate">
                                                        {item.query.slice(0, 60)}{item.query.length > 60 ? "..." : ""}
                                                    </p>
                                                </div>
                                                <div className="text-right ml-4 flex-shrink-0">
                                                    <p className="text-xs text-gray-500">
                                                        {new Date(item.timestamp).toLocaleTimeString()}
                                                    </p>
                                                    <p className="text-xs text-blue-600 font-medium">
                                                        {(item.duration / 1000).toFixed(1)}s
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}

// History Detail View Component
function HistoryDetailView({ 
    item, 
    expandedNodes, 
    setExpandedNodes 
}: { 
    item: ExecutionHistoryItem;
    expandedNodes: Set<string>;
    setExpandedNodes: React.Dispatch<React.SetStateAction<Set<string>>>;
}) {
    const toggleNode = (nodeId: string) => {
        setExpandedNodes((prev) => {
            const next = new Set(prev);
            if (next.has(nodeId)) {
                next.delete(nodeId);
            } else {
                next.add(nodeId);
            }
            return next;
        });
    };

    // Convert Map entries to array for rendering
    const nodeEntries = Array.from(item.nodeOutputs.entries());

    return (
        <div className="space-y-4">
            {/* Summary */}
            <div className="p-4 bg-gray-50 rounded-lg">
                <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                        <span className="text-gray-500">Workflow:</span>
                        <span className="ml-2 font-medium text-gray-900">{item.workflowName}</span>
                    </div>
                    <div>
                        <span className="text-gray-500">Duration:</span>
                        <span className="ml-2 font-medium text-gray-900">{(item.duration / 1000).toFixed(2)}s</span>
                    </div>
                    <div className="col-span-2">
                        <span className="text-gray-500">Query:</span>
                        <p className="mt-1 text-gray-900 text-xs bg-white p-2 rounded border border-gray-200">
                            {item.query}
                        </p>
                    </div>
                </div>
            </div>

            {/* Node Outputs */}
            <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Node Outputs</h3>
                <div className="space-y-2">
                    {nodeEntries.map(([nodeId, step]) => (
                        <div key={nodeId} className="border border-gray-200 rounded-lg overflow-hidden">
                            <button
                                onClick={() => toggleNode(nodeId)}
                                className="w-full p-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
                            >
                                <div className="flex items-center gap-3">
                                    <div className={`w-2 h-2 rounded-full ${step.excluded ? 'bg-yellow-500' : 'bg-green-500'}`} />
                                    <span className="font-medium text-gray-900 text-sm">{step.agent}</span>
                                    <span className="text-xs text-gray-500 bg-gray-200 px-2 py-0.5 rounded">
                                        {step.action}
                                    </span>
                                </div>
                                {expandedNodes.has(nodeId) ? (
                                    <HiChevronUp className="w-4 h-4 text-gray-500" />
                                ) : (
                                    <HiChevronDown className="w-4 h-4 text-gray-500" />
                                )}
                            </button>
                            
                            {expandedNodes.has(nodeId) && (
                                <div className="p-3 border-t border-gray-200 bg-white">
                                    <div className="text-xs text-gray-500 mb-1">Model: {step.model}</div>
                                    <div className="text-sm text-gray-900 whitespace-pre-wrap bg-gray-50 p-3 rounded max-h-64 overflow-y-auto">
                                        {step.content || "No content"}
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Final Result */}
            <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Final Result</h3>
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg text-sm text-gray-900 whitespace-pre-wrap max-h-64 overflow-y-auto">
                    {item.result.answer || "No output"}
                </div>
            </div>
        </div>
    );
}
