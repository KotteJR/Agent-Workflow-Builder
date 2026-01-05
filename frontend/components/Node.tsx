"use client";

import { memo, useCallback } from "react";
import { Handle, Position, NodeProps, useReactFlow } from "@xyflow/react";
import { NODE_TYPES, NodeSettings } from "@/lib/nodes";
import { HiXMark, HiCog6Tooth } from "react-icons/hi2";
import type { WorkflowNodeData, WorkflowNode } from "@/lib/types";

export const WorkflowNode = memo(({ id, data, selected }: NodeProps<WorkflowNode>) => {
    const { deleteElements } = useReactFlow();
    const nodeConfig = NODE_TYPES.find((n) => n.id === data.nodeType);

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
            if (data.onSettingsClick) {
                data.onSettingsClick(id);
            }
        },
        [data, id]
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
                    bg-white rounded-lg shadow-sm border-2 min-w-[220px]
                    transition-all duration-200
                    ${selected ? "border-blue-400 shadow-lg" : "border-gray-200"}
                    hover:shadow-md hover:border-gray-300
                    ${hasSettings ? "cursor-pointer" : ""}
                `}
                onDoubleClick={hasSettings ? handleSettingsClick : undefined}
            >
                {/* Header - Drag Handle */}
                <div className="drag-handle cursor-grab active:cursor-grabbing px-4 py-3 border-gray-100 flex items-center gap-3">
                    <div
                        className={`w-9 h-9 rounded-lg ${nodeConfig.color} flex items-center justify-center flex-shrink-0 border`}
                    >
                        <Icon className="w-5 h-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-gray-900 truncate">
                            {nodeConfig.label}
                        </div>
                        <div className="text-xs text-gray-500 capitalize">{nodeConfig.category}</div>
                    </div>
                </div>
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
