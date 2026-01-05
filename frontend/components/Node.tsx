"use client";

import { memo, useCallback, useState, useRef, useEffect } from "react";
import { Handle, Position, NodeProps, useReactFlow } from "@xyflow/react";
import { NODE_TYPES, NodeSettings } from "@/lib/nodes";
import { HiXMark, HiCog6Tooth, HiPaperClip, HiTrash, HiDocumentArrowDown, HiCheckCircle, HiEye } from "react-icons/hi2";
import type { WorkflowNodeData, NodeOutputData } from "@/lib/types";
import type { Node } from "@xyflow/react";

export const WorkflowNode = memo(({ id, data, selected }: NodeProps<Node>) => {
    const { deleteElements } = useReactFlow();
    const nodeData = data as WorkflowNodeData;
    const nodeConfig = NODE_TYPES.find((n) => n.id === nodeData.nodeType);

    const handleDelete = useCallback(
        (e: React.MouseEvent) => {
            e.stopPropagation();
            deleteElements({ nodes: [{ id }] });
        },
        [deleteElements, id]
    );

    const handleSettingsClick = useCallback(
        (e: React.MouseEvent) => {
            e.stopPropagation();
            e.preventDefault();
            if (nodeData.onSettingsClick) {
                nodeData.onSettingsClick(id);
            }
        },
        [nodeData, id]
    );

    if (!nodeConfig) return null;

    const Icon = nodeConfig.icon;
    const hasSettings = nodeConfig.hasSettings ?? false;

    return (
        <div className="relative group">
            {/* Delete Button - Visible on Hover/Selected */}
            <button
                className={`
                    absolute -top-2 -right-2 w-6 h-6 bg-white border border-gray-200
                    hover:text-red-500 hover:border-red-200 text-gray-400 rounded-full
                    flex items-center justify-center shadow-sm z-50
                    transition-all duration-200 scale-0 group-hover:scale-100 ${selected ? "scale-100" : ""}
                `}
                onClick={handleDelete}
            >
                <HiXMark className="w-4 h-4" />
            </button>

            {/* Settings Button - Only for nodes with settings */}
            {hasSettings && (
                <button
                    className={`
                        absolute -top-2 -left-2 w-6 h-6 bg-white border border-gray-200
                        hover:text-blue-500 hover:border-blue-200 text-gray-400 rounded-full
                        flex items-center justify-center shadow-sm z-50
                        transition-all duration-200 scale-0 group-hover:scale-100 ${selected ? "scale-100" : ""}
                    `}
                    onClick={handleSettingsClick}
                    title="Open settings"
                >
                    <HiCog6Tooth className="w-4 h-4" />
                </button>
            )}

            {/* Target Handle - Only if NOT 'input' */}
            {nodeConfig.category !== "input" && (
                <Handle
                    type="target"
                    position={Position.Left}
                    className="!w-3 !h-3 !bg-gray-400 !border-2 !border-white"
                />
            )}

            <div
                className={`
                    bg-white rounded-lg shadow-sm border-2 min-w-[220px] max-w-[320px]
                    transition-all duration-300 relative
                    ${selected ? "border-blue-400 shadow-lg" : "border-gray-200"}
                    hover:shadow-md hover:border-gray-300
                    ${hasSettings ? "cursor-pointer" : ""}
                    ${nodeData.executionState?.isExecuting ? "cursor-pointer border-blue-400" : ""}
                `}
                onDoubleClick={hasSettings ? handleSettingsClick : undefined}
                onClick={nodeData.executionState?.isExecuting && nodeData.onExecutionClick ? () => nodeData.onExecutionClick!(id) : undefined}
            >
                {/* Glowing effect when executing */}
                {nodeData.executionState?.isExecuting && (
                    <div 
                        className="absolute -inset-1 rounded-xl bg-blue-400/30 blur-md pointer-events-none animate-pulse"
                        style={{ animationDuration: '1.5s' }}
                    />
                )}
                {nodeData.executionState?.isExecuting && (
                    <div 
                        className="absolute -inset-0.5 rounded-lg bg-gradient-to-r from-blue-400 via-blue-500 to-blue-400 opacity-60 pointer-events-none animate-pulse"
                        style={{ animationDuration: '1s' }}
                    />
                )}
                {/* Header - Drag Handle */}
                <div className="drag-handle cursor-grab active:cursor-grabbing px-4 py-3 border-b border-gray-100 flex items-center gap-3 relative z-10">
                    <div
                        className={`w-9 h-9 rounded-lg ${nodeConfig.color} flex items-center justify-center flex-shrink-0 border relative`}
                    >
                        <Icon className="w-5 h-5" />
                        {/* Executing indicator dot */}
                        {nodeData.executionState?.isExecuting && (
                            <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full animate-pulse border-2 border-white" />
                        )}
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-gray-900 truncate flex items-center gap-2">
                            {nodeConfig.label}
                            {nodeData.executionState?.isExecuting && (
                                <span className="text-xs text-blue-600 font-normal animate-pulse">Executing...</span>
                            )}
                        </div>
                        <div className="text-xs text-gray-500 capitalize">{nodeConfig.category}</div>
                    </div>
                </div>

                {/* Inline Content Area */}
                {nodeData.nodeType === "prompt" && (
                    <PromptEditor
                        nodeId={id}
                        promptText={nodeData.promptText || ""}
                        onDataChange={nodeData.onDataChange}
                    />
                )}

                {nodeData.nodeType === "upload" && (
                    <UploadEditor
                        nodeId={id}
                        uploadedFiles={nodeData.uploadedFiles || []}
                        uploadInstruction={nodeData.uploadInstruction}
                        onDataChange={nodeData.onDataChange}
                    />
                )}

                {/* Output Node Content */}
                {(nodeData.nodeType === "response" || nodeData.nodeType === "spreadsheet") && (
                    <OutputViewer
                        nodeId={id}
                        nodeType={nodeData.nodeType}
                        outputData={nodeData.outputData}
                        onViewClick={nodeData.onOutputClick}
                    />
                )}
            </div>

            {/* Source Handle - Only if NOT 'output' */}
            {nodeConfig.category !== "output" && (
                <Handle
                    type="source"
                    position={Position.Right}
                    className="!w-3 !h-3 !bg-gray-400 !border-2 !border-white"
                />
            )}
        </div>
    );
});

WorkflowNode.displayName = "WorkflowNode";

// Prompt Editor Component
interface PromptEditorProps {
    nodeId: string;
    promptText: string;
    onDataChange?: (nodeId: string, data: Partial<WorkflowNodeData>) => void;
}

const PromptEditor = memo(({ nodeId, promptText, onDataChange }: PromptEditorProps) => {
    const [text, setText] = useState(promptText);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleChange = useCallback(
        (e: React.ChangeEvent<HTMLTextAreaElement>) => {
            const newText = e.target.value;
            setText(newText);
            onDataChange?.(nodeId, { promptText: newText });
        },
        [nodeId, onDataChange]
    );

    const handleFocus = useCallback((e: React.FocusEvent<HTMLTextAreaElement>) => {
        e.stopPropagation();
    }, []);

    return (
        <div className="px-4 py-3 border-t border-gray-100" onClick={(e) => e.stopPropagation()}>
            <textarea
                ref={textareaRef}
                value={text}
                onChange={handleChange}
                onFocus={handleFocus}
                placeholder="Enter your prompt here..."
                className="w-full min-h-[80px] max-h-[200px] px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                style={{ fieldSizing: "content" } as any}
            />
        </div>
    );
});

PromptEditor.displayName = "PromptEditor";

// Upload Editor Component
interface UploadEditorProps {
    nodeId: string;
    uploadedFiles: Array<{ name: string; size: number; type: string; content?: string }>;
    uploadInstruction?: string;
    onDataChange?: (nodeId: string, data: Partial<WorkflowNodeData>) => void;
}

const UploadEditor = memo(({ nodeId, uploadedFiles, uploadInstruction, onDataChange }: UploadEditorProps) => {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [instruction, setInstruction] = useState(uploadInstruction || "");
    
    // Sync with prop changes
    useEffect(() => {
        setInstruction(uploadInstruction || "");
    }, [uploadInstruction]);
    
    const handleInstructionChange = useCallback(
        (e: React.ChangeEvent<HTMLTextAreaElement>) => {
            const newInstruction = e.target.value;
            setInstruction(newInstruction);
            onDataChange?.(nodeId, { uploadInstruction: newInstruction });
        },
        [nodeId, onDataChange]
    );

    const formatFileSize = (bytes: number): string => {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    const handleFileSelect = useCallback(
        async (e: React.ChangeEvent<HTMLInputElement>) => {
            const files = Array.from(e.target.files || []);
            if (files.length === 0) return;

            const newFiles = await Promise.all(
                files.map(async (file) => {
                    let content: string | undefined;
                    
                    // For text-based files, read as text
                    if (file.type.startsWith("text/") || 
                        file.name.endsWith(".txt") || 
                        file.name.endsWith(".csv") || 
                        file.name.endsWith(".md")) {
                        try {
                            content = await file.text();
                        } catch (err) {
                            console.error("Failed to read text file:", err);
                        }
                    }
                    // For PDFs and other binary files, read as base64
                    else if (file.type === "application/pdf" || file.name.endsWith(".pdf")) {
                        try {
                            const arrayBuffer = await file.arrayBuffer();
                            const base64 = btoa(
                                new Uint8Array(arrayBuffer).reduce(
                                    (data, byte) => data + String.fromCharCode(byte),
                                    ''
                                )
                            );
                            content = `__PDF_BASE64__${base64}`;
                        } catch (err) {
                            console.error("Failed to read PDF file:", err);
                        }
                    }
                    // For Word docs, read as base64
                    else if (file.name.endsWith(".docx") || file.name.endsWith(".doc")) {
                        try {
                            const arrayBuffer = await file.arrayBuffer();
                            const base64 = btoa(
                                new Uint8Array(arrayBuffer).reduce(
                                    (data, byte) => data + String.fromCharCode(byte),
                                    ''
                                )
                            );
                            content = `__DOCX_BASE64__${base64}`;
                        } catch (err) {
                            console.error("Failed to read Word file:", err);
                        }
                    }
                    
                    return {
                        name: file.name,
                        size: file.size,
                        type: file.type,
                        content,
                    };
                })
            );

            const updatedFiles = [...uploadedFiles, ...newFiles];
            onDataChange?.(nodeId, { uploadedFiles: updatedFiles });
            
            // Reset input
            if (fileInputRef.current) {
                fileInputRef.current.value = "";
            }
        },
        [nodeId, uploadedFiles, onDataChange]
    );

    const handleRemoveFile = useCallback(
        (index: number) => {
            const updatedFiles = uploadedFiles.filter((_, i) => i !== index);
            onDataChange?.(nodeId, { uploadedFiles: updatedFiles });
        },
        [nodeId, uploadedFiles, onDataChange]
    );

    const handleClick = useCallback((e: React.MouseEvent) => {
        e.stopPropagation();
        fileInputRef.current?.click();
    }, []);

    return (
        <div className="px-4 py-3 border-t border-gray-100" onClick={(e) => e.stopPropagation()}>
            <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.txt,.csv,.md,.doc,.docx"
                onChange={handleFileSelect}
                className="hidden"
            />

            {/* Upload Button */}
            <button
                onClick={handleClick}
                className="w-full px-3 py-2 text-sm border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 hover:bg-blue-50 text-gray-600 hover:text-blue-600 transition-colors flex items-center justify-center gap-2"
            >
                <HiPaperClip className="w-4 h-4" />
                <span>Click to upload files</span>
            </button>

            {/* File List */}
            {uploadedFiles.length > 0 && (
                <div className="mt-2 space-y-1">
                    {uploadedFiles.map((file, index) => (
                        <div
                            key={index}
                            className="flex items-center gap-2 px-2 py-1.5 bg-gray-50 rounded text-xs"
                        >
                            <span className="flex-1 truncate text-gray-700">{file.name}</span>
                            <span className="text-gray-500">{formatFileSize(file.size)}</span>
                            <button
                                onClick={() => handleRemoveFile(index)}
                                className="p-1 hover:text-red-500 text-gray-400 transition-colors"
                            >
                                <HiTrash className="w-3 h-3" />
                            </button>
                        </div>
                    ))}
                </div>
            )}

            {/* Optional instructions for uploaded files */}
            {uploadedFiles.length > 0 && (
                <div className="mt-3">
                    <details className="group">
                        <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700 flex items-center gap-1">
                            <span className="group-open:rotate-90 transition-transform">▶</span>
                            Add custom instructions (optional)
                        </summary>
                        <textarea
                            value={instruction}
                            onChange={handleInstructionChange}
                            onFocus={(e) => e.stopPropagation()}
                            placeholder="Leave empty for automatic processing, or add specific instructions..."
                            className="mt-2 w-full min-h-[50px] max-h-[100px] px-3 py-2 text-xs border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                            style={{ fieldSizing: "content" } as any}
                        />
                    </details>
                </div>
            )}
        </div>
    );
});

UploadEditor.displayName = "UploadEditor";

// Output Viewer Component (for response and spreadsheet nodes)
interface OutputViewerProps {
    nodeId: string;
    nodeType: string;
    outputData?: NodeOutputData;
    onViewClick?: (nodeId: string) => void;
}

const OutputViewer = memo(({ nodeId, nodeType, outputData, onViewClick }: OutputViewerProps) => {
    const hasOutput = outputData && outputData.content;
    
    const handleViewClick = useCallback((e: React.MouseEvent) => {
        e.stopPropagation();
        onViewClick?.(nodeId);
    }, [nodeId, onViewClick]);

    const handleDownload = useCallback((e: React.MouseEvent) => {
        e.stopPropagation();
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

    return (
        <div className="px-4 py-3 border-t border-gray-100" onClick={(e) => e.stopPropagation()}>
            {hasOutput ? (
                <div className="space-y-2">
                    {/* Success indicator */}
                    <div className="flex items-center gap-2 text-green-600">
                        <HiCheckCircle className="w-4 h-4" />
                        <span className="text-xs font-medium">Output Ready</span>
                    </div>
                    
                    {/* Preview - first 100 chars */}
                    <div className="p-2 bg-gray-50 rounded text-xs text-gray-600 font-mono max-h-[60px] overflow-hidden">
                        {outputData.content.substring(0, 150)}{outputData.content.length > 150 ? "..." : ""}
                    </div>
                    
                    {/* Action buttons */}
                    <div className="flex gap-2">
                        <button
                            onClick={handleViewClick}
                            className="flex-1 px-3 py-1.5 text-xs bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors flex items-center justify-center gap-1.5"
                        >
                            <HiEye className="w-3.5 h-3.5" />
                            View Full Output
                        </button>
                        <button
                            onClick={handleDownload}
                            className="px-3 py-1.5 text-xs bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center gap-1.5"
                        >
                            <HiDocumentArrowDown className="w-3.5 h-3.5" />
                            {nodeType === "spreadsheet" ? "CSV" : "Download"}
                        </button>
                    </div>
                </div>
            ) : (
                <div className="text-center py-2 text-xs text-gray-400">
                    {nodeType === "spreadsheet" ? "Spreadsheet output will appear here" : "Output will appear here after execution"}
                </div>
            )}
        </div>
    );
});

OutputViewer.displayName = "OutputViewer";
