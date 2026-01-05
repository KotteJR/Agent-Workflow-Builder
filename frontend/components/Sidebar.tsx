"use client";

import { useState } from "react";
import { NODE_TYPES } from "@/lib/nodes";
import { HiChevronLeft, HiChevronRight } from "react-icons/hi2";

type SidebarProps = {
    onDragStart: (nodeType: string, e: React.DragEvent) => void;
};

export function Sidebar({ onDragStart }: SidebarProps) {
    const [isExpanded, setIsExpanded] = useState(true);

    return (
        <div
            className={`
                absolute right-6 top-6 bottom-6
                bg-white rounded-2xl shadow-xl border border-gray-200
                flex flex-col overflow-visible transition-all duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1.0)] z-20
                ${isExpanded ? 'w-80' : 'w-20'}
            `}
        >
            {/* Toggle Button */}
            <div className="absolute left-0 top-1/2 transform -translate-x-1/2 z-30">
                <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="bg-white border border-gray-200 rounded-full w-8 h-8 flex items-center justify-center text-gray-500 shadow-md hover:text-gray-800 hover:scale-110 hover:shadow-lg transition-all active:scale-95"
                >
                    {isExpanded ? <HiChevronRight className="w-4 h-4" /> : <HiChevronLeft className="w-4 h-4" />}
                </button>
            </div>

            {/* Inner Container for content overflow */}
            <div className="flex-1 overflow-hidden flex flex-col w-full rounded-2xl">
                {/* Node List */}
                <div className={`flex-1 overflow-y-auto overflow-x-hidden p-3 ${isExpanded ? 'space-y-4' : 'space-y-3'}`}>
                    {NODE_TYPES.map((node) => {
                        const Icon = node.icon;

                        if (!isExpanded) {
                            // Collapsed View - Icon Only
                            return (
                                <div
                                    key={node.id}
                                    draggable={!node.comingSoon}
                                    onDragStart={node.comingSoon ? undefined : (e) => onDragStart(node.id, e)}
                                    title={node.comingSoon ? `${node.label} - Coming Soon` : node.label}
                                    className={`
                                        flex items-center justify-center
                                        w-14 h-14 bg-white rounded-xl border border-gray-200 shadow-sm
                                        transition-all duration-600 mx-auto flex-shrink-0
                                        animate-in fade-in zoom-in-95 duration-600 fill-mode-both delay-75
                                        ${node.comingSoon 
                                            ? "opacity-50 cursor-not-allowed" 
                                            : "cursor-grab active:cursor-grabbing hover:border-blue-400 hover:shadow-md hover:scale-105 hover:bg-blue-50"
                                        }
                                    `}
                                >
                                    <div className={`w-10 h-10 rounded-lg ${node.color} flex items-center justify-center ${node.comingSoon ? "opacity-50" : ""}`}>
                                        <Icon className="w-6 h-6" />
                                    </div>
                                </div>
                            );
                        }

                        // Expanded View - Full Card
                        return (
                            <div
                                key={node.id}
                                className={`
                                    group
                                    bg-slate-50 rounded-xl p-3 border border-gray-200
                                    transition-all duration-500
                                    animate-in fade-in slide-in-from-right-4 duration-500 fill-mode-both
                                    ${node.comingSoon 
                                        ? "opacity-60" 
                                        : "hover:border-gray-300 hover:shadow-md hover:bg-white"
                                    }
                                `}
                            >
                                {/* The Node Visual - Matches Canvas Node */}
                                <div
                                    draggable={!node.comingSoon}
                                    onDragStart={node.comingSoon ? undefined : (e) => onDragStart(node.id, e)}
                                    className={`
                                        bg-white rounded-lg shadow-sm border border-gray-200
                                        mb-3 overflow-hidden transition-all duration-200 relative
                                        ${node.comingSoon 
                                            ? "opacity-50 cursor-not-allowed" 
                                            : "cursor-grab active:cursor-grabbing hover:shadow-md hover:border-blue-400"
                                        }
                                    `}
                                >
                                    {node.comingSoon && (
                                        <div className="absolute top-2 right-2 bg-amber-100 text-amber-700 text-[10px] font-bold px-2 py-0.5 rounded-full z-10">
                                            COMING SOON
                                        </div>
                                    )}
                                    <div className="px-4 py-3 flex items-center gap-3">
                                        <div className={`w-10 h-10 rounded-lg ${node.color} flex items-center justify-center flex-shrink-0 border shadow-sm ${node.comingSoon ? "opacity-50" : ""}`}>
                                            <Icon className="w-6 h-6" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <div className="text-sm font-bold text-gray-800 truncate">
                                                {node.label}
                                            </div>
                                            <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">
                                                {node.category}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Description */}
                                <div className="px-1">
                                    <p className="text-xs text-gray-500 leading-relaxed font-medium">
                                        {node.description}
                                    </p>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
