"use client";

import { memo, useCallback } from "react";
import { HiXMark, HiDocumentArrowDown, HiClipboardDocument, HiPhoto } from "react-icons/hi2";
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

    const hasImages = outputData?.images && outputData.images.length > 0;

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

    const handleDownloadImage = useCallback((imageUrl: string, index: number) => {
        const a = document.createElement("a");
        a.href = imageUrl;
        a.download = `generated_image_${Date.now()}_${index}.png`;
        a.target = "_blank";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }, []);

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

    const title = hasImages ? "Generated Image" : (nodeType === "spreadsheet" ? "Spreadsheet Output" : "Workflow Output");

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
                        {!hasImages && (
                            <>
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
                            </>
                        )}
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
                    {/* Display Images if present */}
                    {hasImages && (
                        <div className="space-y-6">
                            {outputData.images!.map((image, index) => (
                                <div key={index} className="space-y-3">
                                    {/* Image */}
                                    <div className="relative bg-gray-100 rounded-lg overflow-hidden">
                                        <img
                                            src={image.url}
                                            alt={image.prompt}
                                            className="w-full h-auto max-h-[60vh] object-contain"
                                            onError={(e) => {
                                                (e.target as HTMLImageElement).src = "https://placehold.co/512x512/1a1a2e/ff6b6b?text=Failed+to+load";
                                            }}
                                        />
                                    </div>
                                    
                                    {/* Image info */}
                                    <div className="flex items-center justify-between">
                                        <div className="text-sm text-gray-600">
                                            <span className="font-medium">Prompt:</span> {image.prompt}
                                        </div>
                                        <button
                                            onClick={() => handleDownloadImage(image.url, index)}
                                            className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-1.5"
                                        >
                                            <HiDocumentArrowDown className="w-4 h-4" />
                                            Download Image
                                        </button>
                                    </div>
                                    
                                    {/* Style badge */}
                                    <div className="flex gap-2">
                                        <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs">
                                            Style: {image.style}
                                        </span>
                                    </div>
                                </div>
                            ))}
                            
                            {/* Also show text response if present */}
                            {outputData.content && (
                                <div className="pt-4 border-t border-gray-200">
                                    <h3 className="text-sm font-medium text-gray-700 mb-2">Response:</h3>
                                    <p className="text-sm text-gray-600">{outputData.content}</p>
                                </div>
                            )}
                        </div>
                    )}
                    
                    {/* Display text content if no images */}
                    {!hasImages && outputData?.content ? (
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
                    ) : !hasImages && (
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

