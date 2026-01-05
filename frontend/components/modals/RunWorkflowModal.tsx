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
                    {!result ? (
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

                            {isRunning && runningAgents.size > 0 && (
                                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                                    <p className="text-sm text-blue-600 font-medium">
                                        Running: {Array.from(runningAgents).join(", ")}
                                    </p>
                                </div>
                            )}
                        </div>
                    ) : (
                        <ResultDisplay result={result} />
                    )}
                </div>

                <div className="p-4 border-t border-gray-200 flex gap-3 justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                        Close
                    </button>
                    {!result && (
                        <button
                            onClick={onRun}
                            disabled={isRunning || !query.trim()}
                            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isRunning ? "Running..." : "Run"}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
});

const ResultDisplay = memo(function ResultDisplay({
    result,
}: {
    result: WorkflowExecutionResult;
}) {
    return (
        <div className="space-y-4">
            <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Result:</h3>
                <div className="p-4 bg-gray-50 rounded-xl whitespace-pre-wrap text-sm">
                    {result.answer}
                </div>
            </div>

            {result.tool_outputs?.docs && result.tool_outputs.docs.length > 0 && (
                <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Sources:</h3>
                    <div className="space-y-2">
                        {result.tool_outputs.docs.map((doc, i) => (
                            <div key={i} className="p-2 bg-gray-50 rounded-lg text-xs">
                                <span className="font-medium">
                                    [{i + 1}] {doc.title}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {result.tool_outputs?.images && result.tool_outputs.images.length > 0 && (
                <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Generated Images:</h3>
                    <div className="space-y-2">
                        {result.tool_outputs.images.map((img, i) => (
                            <img
                                key={i}
                                src={img.url}
                                alt={img.prompt}
                                className="w-full max-w-md rounded-lg"
                            />
                        ))}
                    </div>
                </div>
            )}

            <p className="text-xs text-gray-500">Completed in {result.latency_ms}ms</p>
        </div>
    );
});

