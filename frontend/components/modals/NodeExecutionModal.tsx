"use client";

import { memo } from "react";
import { HiXMark } from "react-icons/hi2";
import type { AgentStep } from "@/lib/types";

interface NodeExecutionModalProps {
    isOpen: boolean;
    onClose: () => void;
    nodeId: string;
    nodeLabel: string;
    step?: AgentStep;
    executionTime?: number;
}

export const NodeExecutionModal = memo(function NodeExecutionModal({
    isOpen,
    onClose,
    nodeId,
    nodeLabel,
    step,
    executionTime,
}: NodeExecutionModalProps) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
            <div
                className="bg-white rounded-xl shadow-2xl max-w-2xl w-full mx-4 max-h-[80vh] flex flex-col"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
                    <div>
                        <h2 className="text-lg font-semibold text-gray-900">Execution Details</h2>
                        <p className="text-sm text-gray-500 mt-1">{nodeLabel}</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                        <HiXMark className="w-5 h-5 text-gray-500" />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
                    {step ? (
                        <>
                            <div>
                                <h3 className="text-sm font-medium text-gray-700 mb-2">Status:</h3>
                                <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                                    <span className="text-sm text-gray-900">
                                        {step.excluded ? "Excluded" : "Executing"}
                                    </span>
                                </div>
                            </div>

                            <div>
                                <h3 className="text-sm font-medium text-gray-700 mb-2">Agent:</h3>
                                <div className="p-3 bg-gray-50 rounded-lg text-sm text-gray-900">
                                    {step.agent}
                                </div>
                            </div>

                            {step.model && (
                                <div>
                                    <h3 className="text-sm font-medium text-gray-700 mb-2">Model:</h3>
                                    <div className="p-3 bg-gray-50 rounded-lg text-sm text-gray-900">
                                        {step.model}
                                    </div>
                                </div>
                            )}

                            {step.action && (
                                <div>
                                    <h3 className="text-sm font-medium text-gray-700 mb-2">Action:</h3>
                                    <div className="p-3 bg-gray-50 rounded-lg text-sm text-gray-900">
                                        {step.action}
                                    </div>
                                </div>
                            )}

                            {step.content && (
                                <div>
                                    <h3 className="text-sm font-medium text-gray-700 mb-2">Output:</h3>
                                    <div className="p-4 bg-gray-50 rounded-lg text-sm text-gray-900 whitespace-pre-wrap max-h-96 overflow-y-auto">
                                        {step.content}
                                    </div>
                                </div>
                            )}

                            {executionTime !== undefined && (
                                <div>
                                    <h3 className="text-sm font-medium text-gray-700 mb-2">Execution Time:</h3>
                                    <div className="p-3 bg-gray-50 rounded-lg text-sm text-gray-900">
                                        {executionTime.toFixed(2)}ms
                                    </div>
                                </div>
                            )}

                            {step.excluded && (
                                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                                    <p className="text-sm text-yellow-800">
                                        This node was excluded from execution.
                                    </p>
                                </div>
                            )}
                        </>
                    ) : (
                        <div className="text-center py-8">
                            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                            <p className="text-sm text-gray-500">Waiting for execution data...</p>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors text-sm font-medium"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
});





