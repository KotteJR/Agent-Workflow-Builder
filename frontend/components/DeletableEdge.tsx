"use client";

import { BaseEdge, EdgeLabelRenderer, EdgeProps, getSmoothStepPath, useReactFlow } from "@xyflow/react";
import { HiXMark } from "react-icons/hi2";

export default function DeletableEdge({
    id,
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
    style = {},
    markerEnd,
}: EdgeProps) {
    const { deleteElements } = useReactFlow();
    
    // Use smooth step path for straight lines with rounded corners
    const [edgePath, labelX, labelY] = getSmoothStepPath({
        sourceX,
        sourceY,
        sourcePosition,
        targetX,
        targetY,
        targetPosition,
        borderRadius: 8,
    });

    return (
        <>
            <BaseEdge path={edgePath} markerEnd={markerEnd} style={style} />
            <EdgeLabelRenderer>
                <div
                    style={{
                        position: 'absolute',
                        transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
                        pointerEvents: 'all',
                    }}
                    className="nodrag nopan opacity-0 hover:opacity-100 transition-opacity"
                >
                    <button
                        className="w-5 h-5 bg-white border border-gray-300 text-gray-400 hover:text-red-500 hover:border-red-300 hover:bg-red-50 rounded-full flex items-center justify-center shadow-sm cursor-pointer transition-all"
                        onClick={() => deleteElements({ edges: [{ id }] })}
                        title="Delete connection"
                    >
                        <HiXMark className="w-3 h-3" />
                    </button>
                </div>
            </EdgeLabelRenderer>
        </>
    );
}
