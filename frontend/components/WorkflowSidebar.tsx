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
} from "react-icons/hi2";
import { listWorkflows, deleteWorkflow, type WorkflowListItem } from "@/lib/api";

type WorkflowSidebarProps = {
    isChatOpen: boolean;
    onToggleChat: () => void;
    onNewWorkflow: () => void;
    onLoadWorkflow: (workflowId: string) => void;
    onSaveWorkflow: () => void;
    onRunWorkflow: () => void;
    isRunning?: boolean;
    currentWorkflowId?: string | null;
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
}: WorkflowSidebarProps) {
    const [isExpanded, setIsExpanded] = useState(false);
    const [showLoadModal, setShowLoadModal] = useState(false);
    const [workflows, setWorkflows] = useState<WorkflowListItem[]>([]);
    const [loadingWorkflows, setLoadingWorkflows] = useState(false);

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

                    {/* Spacer */}
                    <div className="flex-1" />

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
        </>
    );
}
