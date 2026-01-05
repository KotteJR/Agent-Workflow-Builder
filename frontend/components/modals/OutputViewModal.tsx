"use client";

import { memo, useCallback } from "react";
import { HiXMark, HiDocumentArrowDown, HiClipboardDocument } from "react-icons/hi2";
import type { NodeOutputData } from "@/lib/types";

interface OutputViewModalProps {
    isOpen: boolean;
    onClose: () => void;
    nodeId: string;
    nodeType: string;
    outputData?: NodeOutputData;
}

export const OutputViewModal = memo(function OutputViewModal({
    isOpen,
    onClose,
    nodeId,
    nodeType,
    outputData,
}: OutputViewModalProps) {
    if (!isOpen) return null;

    const handleDownload = useCallback(() => {
        if (!outputData?.content) return;
        
        const isSpreadsheet = nodeType === "spreadsheet" || outputData.format === "csv" || outputData.format === "spreadsheet";
        const extension = isSpreadsheet ? "csv" : "txt";
        const mimeType = isSpreadsheet ? "text/csv" : "text/plain";
        
        const blob = new Blob([outputData.content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `workflow_output_${Date.now()}.${extension}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, [outputData, nodeType]);

    const handleCopyToClipboard = useCallback(async () => {
        if (!outputData?.content) return;
        try {
            await navigator.clipboard.writeText(outputData.content);
            alert("Copied to clipboard!");
        } catch (err) {
            console.error("Failed to copy:", err);
        }
    }, [outputData]);

    const formatTimestamp = (ts: number) => {
        return new Date(ts).toLocaleString();
    };

    const title = nodeType === "spreadsheet" ? "Spreadsheet Output" : "Workflow Output";

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100]">
            <div className="bg-white rounded-2xl shadow-xl w-full max-w-4xl mx-4 max-h-[85vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                    <div>
                        <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
                        {outputData?.timestamp && (
                            <p className="text-xs text-gray-500">Generated: {formatTimestamp(outputData.timestamp)}</p>
                        )}
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={handleCopyToClipboard}
                            className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-1.5"
                            title="Copy to clipboard"
                        >
                            <HiClipboardDocument className="w-4 h-4" />
                            Copy
                        </button>
                        <button
                            onClick={handleDownload}
                            className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-1.5"
                        >
                            <HiDocumentArrowDown className="w-4 h-4" />
                            Download {nodeType === "spreadsheet" ? "CSV" : ""}
                        </button>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-gray-100 rounded-lg transition-colors ml-2"
                        >
                            <HiXMark className="w-5 h-5 text-gray-500" />
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-auto p-4">
                    {outputData?.content ? (
                        <div className="relative">
                            {/* Format indicator */}
                            <div className="absolute top-2 right-2 px-2 py-1 bg-gray-100 rounded text-xs text-gray-600 uppercase">
                                {outputData.format || "text"}
                            </div>
                            
                            {/* Output content */}
                            <pre className="p-4 bg-gray-50 rounded-lg text-sm font-mono whitespace-pre-wrap overflow-x-auto border border-gray-200">
                                {outputData.content}
                            </pre>
                            
                            {/* Stats */}
                            <div className="mt-2 text-xs text-gray-500">
                                {outputData.content.length.toLocaleString()} characters
                                {nodeType === "spreadsheet" && (
                                    <span className="ml-2">
                                        • {outputData.content.split("\n").length} rows
                                    </span>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-12 text-gray-500">
                            No output data available. Run the workflow to generate output.
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-gray-200 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
});

