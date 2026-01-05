"use client";

import { memo } from "react";
import type { WorkflowExecutionResult, ToolOutputs } from "@/lib/types";

interface RunWorkflowModalProps {
    isOpen: boolean;
    query: string;
    onQueryChange: (query: string) => void;
    isRunning: boolean;
    runningAgents: Set<string>;
    result: WorkflowExecutionResult | null;
    onRun: () => void;
    onClose: () => void;
}

export const RunWorkflowModal = memo(function RunWorkflowModal({
    isOpen,
    query,
    onQueryChange,
    isRunning,
    runningAgents,
    result,
    onRun,
    onClose,
}: RunWorkflowModalProps) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100]">
            <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl mx-4 max-h-[80vh] overflow-hidden flex flex-col">
                <div className="p-4 border-b border-gray-200">
                    <h2 className="text-lg font-semibold text-gray-900">Run Workflow</h2>
                </div>

                <div className="p-4 flex-1 overflow-y-auto">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Enter your query:
                        </label>
                        <textarea
                            value={query}
                            onChange={(e) => onQueryChange(e.target.value)}
                            placeholder="What would you like to know?"
                            rows={3}
                            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                            disabled={isRunning}
                        />

                        {isRunning && (
                            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                                <p className="text-sm text-blue-600 font-medium">
                                    Workflow is running... Check the canvas for execution progress.
                                </p>
                            </div>
                        )}
                    </div>
                </div>

                <div className="p-4 border-t border-gray-200 flex gap-3 justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                        disabled={isRunning}
                    >
                        Close
                    </button>
                    <button
                        onClick={onRun}
                        disabled={isRunning || !query.trim()}
                        className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isRunning ? "Running..." : "Run"}
                    </button>
                </div>
            </div>
        </div>
    );
});



