"use client";

import { memo, useCallback, useMemo, useState } from "react";
import { HiXMark, HiDocumentArrowDown, HiClipboardDocument, HiTableCells, HiCodeBracket, HiDocumentText, HiChevronDown, HiChevronUp } from "react-icons/hi2";
import type { NodeOutputData, SourceDocument } from "@/lib/types";

interface OutputViewModalProps {
    isOpen: boolean;
    onClose: () => void;
    nodeId: string;
    nodeType: string;
    outputData?: NodeOutputData;
}

// Source document modal component
const SourceModal = memo(function SourceModal({ 
    source, 
    onClose 
}: { 
    source: SourceDocument; 
    onClose: () => void;
}) {
    return (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-[110]">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl mx-4 max-h-[80vh] overflow-hidden flex flex-col">
                <div className="p-4 border-b border-gray-200 flex items-center justify-between bg-gradient-to-r from-blue-50 to-indigo-50">
                    <div>
                        <h3 className="font-semibold text-gray-900">{source.title}</h3>
                        {source.score !== undefined && (
                            <span className="text-xs text-blue-600 font-medium">
                                {Math.round(source.score * 100)}% relevance
                            </span>
                        )}
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-white/50 rounded-lg transition-colors"
                    >
                        <HiXMark className="w-5 h-5 text-gray-500" />
                    </button>
                </div>
                <div className="flex-1 overflow-auto p-4">
                    <div className="prose prose-sm max-w-none">
                        <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed bg-gray-50 p-4 rounded-lg border border-gray-200">
                            {source.snippet}
                        </pre>
                    </div>
                </div>
                <div className="p-3 border-t border-gray-200 flex justify-end bg-gray-50">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
});

// Sources section component
const SourcesSection = memo(function SourcesSection({ 
    sources 
}: { 
    sources: SourceDocument[];
}) {
    const [isExpanded, setIsExpanded] = useState(true);
    const [selectedSource, setSelectedSource] = useState<SourceDocument | null>(null);

    if (!sources || sources.length === 0) return null;

    return (
        <>
            <div className="mt-6 border-t border-gray-200 pt-4">
                <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="flex items-center justify-between w-full text-left group"
                >
                    <div className="flex items-center gap-2">
                        <HiDocumentText className="w-5 h-5 text-blue-600" />
                        <h3 className="font-semibold text-gray-900">
                            Sources ({sources.length})
                        </h3>
                    </div>
                    <div className="flex items-center gap-1 text-sm text-gray-500 group-hover:text-gray-700">
                        {isExpanded ? (
                            <>
                                <span>Hide</span>
                                <HiChevronUp className="w-4 h-4" />
                            </>
                        ) : (
                            <>
                                <span>Show</span>
                                <HiChevronDown className="w-4 h-4" />
                            </>
                        )}
                    </div>
                </button>

                {isExpanded && (
                    <div className="mt-3 space-y-2">
                        {sources.map((source, index) => {
                            const relevancePercent = source.score !== undefined 
                                ? Math.round(source.score * 100) 
                                : null;
                            
                            // Color based on relevance
                            const getRelevanceColor = (percent: number | null) => {
                                if (percent === null) return "bg-gray-100 text-gray-600";
                                if (percent >= 80) return "bg-green-100 text-green-700";
                                if (percent >= 60) return "bg-blue-100 text-blue-700";
                                if (percent >= 40) return "bg-yellow-100 text-yellow-700";
                                return "bg-orange-100 text-orange-700";
                            };

                            return (
                                <button
                                    key={index}
                                    onClick={() => setSelectedSource(source)}
                                    className="w-full text-left p-3 bg-gray-50 hover:bg-blue-50 rounded-lg border border-gray-200 hover:border-blue-300 transition-all group"
                                >
                                    <div className="flex items-start justify-between gap-3">
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="font-medium text-gray-900 truncate">
                                                    {source.title}
                                                </span>
                                            </div>
                                            <p className="text-sm text-gray-600 line-clamp-2">
                                                {source.snippet.substring(0, 150)}...
                                            </p>
                                        </div>
                                        <div className="flex flex-col items-end gap-1">
                                            {relevancePercent !== null && (
                                                <span className={`px-2 py-1 text-xs font-semibold rounded-full whitespace-nowrap ${getRelevanceColor(relevancePercent)}`}>
                                                    {relevancePercent}%
                                                </span>
                                            )}
                                            <span className="text-xs text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity">
                                                View →
                                            </span>
                                        </div>
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Source detail modal */}
            {selectedSource && (
                <SourceModal 
                    source={selectedSource} 
                    onClose={() => setSelectedSource(null)} 
                />
            )}
        </>
    );
});

// Parse CSV content into rows and columns
function parseCSV(content: string): string[][] {
    const rows: string[][] = [];
    const lines = content.split('\n');
    
    for (const line of lines) {
        if (!line.trim()) continue;
        
        const row: string[] = [];
        let current = '';
        let inQuotes = false;
        
        for (let i = 0; i < line.length; i++) {
            const char = line[i];
            
            if (char === '"') {
                if (inQuotes && line[i + 1] === '"') {
                    current += '"';
                    i++;
                } else {
                    inQuotes = !inQuotes;
                }
            } else if (char === ',' && !inQuotes) {
                row.push(current.trim());
                current = '';
            } else {
                current += char;
            }
        }
        row.push(current.trim());
        rows.push(row);
    }
    
    return rows;
}

export const OutputViewModal = memo(function OutputViewModal({
    isOpen,
    onClose,
    nodeId,
    nodeType,
    outputData,
}: OutputViewModalProps) {
    const [viewMode, setViewMode] = useState<'table' | 'raw'>('table');
    
    if (!isOpen) return null;

    const hasImages = outputData?.images && outputData.images.length > 0;
    const isSpreadsheet = nodeType === "spreadsheet" || outputData?.format === "csv" || outputData?.format === "spreadsheet";

    // Parse CSV data for table view
    const parsedData = useMemo(() => {
        if (!isSpreadsheet || !outputData?.content) return null;
        try {
            return parseCSV(outputData.content);
        } catch {
            return null;
        }
    }, [isSpreadsheet, outputData?.content]);

    const handleDownload = useCallback(() => {
        if (!outputData?.content) return;
        
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
    }, [outputData, isSpreadsheet]);

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
                                {/* View mode toggle for spreadsheets */}
                                {isSpreadsheet && parsedData && (
                                    <div className="flex items-center bg-gray-100 rounded-lg p-0.5 mr-2">
                                        <button
                                            onClick={() => setViewMode('table')}
                                            className={`px-2.5 py-1 text-sm rounded-md transition-colors flex items-center gap-1 ${
                                                viewMode === 'table'
                                                    ? 'bg-white shadow-sm text-gray-900'
                                                    : 'text-gray-600 hover:text-gray-900'
                                            }`}
                                            title="Table view"
                                        >
                                            <HiTableCells className="w-4 h-4" />
                                            Table
                                        </button>
                                        <button
                                            onClick={() => setViewMode('raw')}
                                            className={`px-2.5 py-1 text-sm rounded-md transition-colors flex items-center gap-1 ${
                                                viewMode === 'raw'
                                                    ? 'bg-white shadow-sm text-gray-900'
                                                    : 'text-gray-600 hover:text-gray-900'
                                            }`}
                                            title="Raw CSV"
                                        >
                                            <HiCodeBracket className="w-4 h-4" />
                                            Raw
                                        </button>
                                    </div>
                                )}
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
                                    Download {isSpreadsheet ? "CSV" : ""}
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
                            
                            {/* Sources section for images too */}
                            {outputData.sources && outputData.sources.length > 0 && (
                                <SourcesSection sources={outputData.sources} />
                            )}
                        </div>
                    )}
                    
                    {/* Display text content if no images */}
                    {!hasImages && outputData?.content ? (
                        <div className="relative">
                            {/* Format indicator */}
                            <div className="absolute top-2 right-2 px-2 py-1 bg-gray-100 rounded text-xs text-gray-600 uppercase z-10">
                                {outputData.format || "text"}
                            </div>
                            
                            {/* Table view for spreadsheets */}
                            {isSpreadsheet && parsedData && viewMode === 'table' ? (
                                <div className="border border-gray-200 rounded-lg overflow-hidden">
                                    <div className="overflow-auto max-h-[60vh]">
                                        <table className="w-full text-sm">
                                            <thead className="bg-gradient-to-b from-gray-50 to-gray-100 sticky top-0">
                                                {parsedData.length > 0 && (
                                                    <tr>
                                                        {parsedData[0].map((header, idx) => (
                                                            <th
                                                                key={idx}
                                                                className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200 whitespace-nowrap"
                                                            >
                                                                {header.replace(/^"|"$/g, '')}
                                                            </th>
                                                        ))}
                                                    </tr>
                                                )}
                                            </thead>
                                            <tbody className="bg-white divide-y divide-gray-100">
                                                {parsedData.slice(1).map((row, rowIdx) => (
                                                    <tr
                                                        key={rowIdx}
                                                        className="hover:bg-blue-50/50 transition-colors"
                                                    >
                                                        {row.map((cell, cellIdx) => (
                                                            <td
                                                                key={cellIdx}
                                                                className="px-4 py-2.5 text-gray-700 border-b border-gray-50"
                                                            >
                                                                <div className="max-w-md truncate" title={cell.replace(/^"|"$/g, '')}>
                                                                    {cell.replace(/^"|"$/g, '')}
                                                                </div>
                                                            </td>
                                                        ))}
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            ) : (
                                /* Raw text view */
                                <pre className="p-4 bg-gray-50 rounded-lg text-sm font-mono whitespace-pre-wrap overflow-x-auto border border-gray-200">
                                    {outputData.content}
                                </pre>
                            )}
                            
                            {/* Stats */}
                            <div className="mt-2 text-xs text-gray-500">
                                {outputData.content.length.toLocaleString()} characters
                                {isSpreadsheet && parsedData && (
                                    <span className="ml-2">
                                        • {parsedData.length} rows × {parsedData[0]?.length || 0} columns
                                    </span>
                                )}
                            </div>

                            {/* Sources section */}
                            {outputData.sources && outputData.sources.length > 0 && (
                                <SourcesSection sources={outputData.sources} />
                            )}
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

