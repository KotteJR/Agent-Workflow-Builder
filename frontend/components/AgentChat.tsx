"use client";

import { useState, useRef, useEffect } from "react";
import { HiPaperAirplane, HiXMark, HiSparkles, HiArrowPath } from "react-icons/hi2";
import { buildWorkflowWithAI, type Workflow } from "@/lib/api";

type Message = {
    role: "user" | "assistant";
    content: string;
    workflow?: Workflow | null;
};

type AgentChatProps = {
    onClose: () => void;
    onLoadWorkflow?: (workflow: Workflow) => void;
};

export function AgentChat({ onClose, onLoadWorkflow }: AgentChatProps) {
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage = input.trim();
        setInput("");
        setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
        setIsLoading(true);

        try {
            // Build conversation history
            const history = messages.map((m) => ({
                role: m.role,
                content: m.content,
            }));

            const result = await buildWorkflowWithAI(userMessage, history);

            setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    content: result.explanation || "I've created a workflow for you.",
                    workflow: result.workflow,
                },
            ]);
        } catch (error) {
            console.error("Failed to build workflow:", error);
            setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    content: "Sorry, I couldn't process your request. Please make sure the backend is running.",
                },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    const handleLoadWorkflow = (workflow: Workflow) => {
        if (onLoadWorkflow) {
            onLoadWorkflow(workflow);
        }
    };

    return (
        <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 w-full max-w-2xl px-4 z-50">
            <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden flex flex-col relative">
                {/* Messages Area */}
                {messages.length > 0 && (
                    <div className="max-h-80 overflow-y-auto p-4 space-y-4 border-b border-gray-100">
                        {messages.map((message, index) => (
                            <div
                                key={index}
                                className={`flex ${
                                    message.role === "user" ? "justify-end" : "justify-start"
                                }`}
                            >
                                <div
                                    className={`max-w-[85%] rounded-xl px-4 py-2 ${
                                        message.role === "user"
                                            ? "bg-gray-900 text-white"
                                            : "bg-gray-100 text-gray-900"
                                    }`}
                                >
                                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                                    
                                    {/* Show "Load Workflow" button if workflow was generated */}
                                    {message.workflow && onLoadWorkflow && (
                                        <button
                                            onClick={() => handleLoadWorkflow(message.workflow!)}
                                            className="mt-2 flex items-center gap-2 text-xs bg-blue-500 hover:bg-blue-600 text-white px-3 py-1.5 rounded-lg transition-colors"
                                        >
                                            <HiArrowPath className="w-3.5 h-3.5" />
                                            Load This Workflow
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}
                        
                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="bg-gray-100 rounded-xl px-4 py-3">
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" />
                                        <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce [animation-delay:0.2s]" />
                                        <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce [animation-delay:0.4s]" />
                                    </div>
                                </div>
                            </div>
                        )}
                        
                        <div ref={messagesEndRef} />
                    </div>
                )}

                {/* Input Area */}
                <div className="p-3 flex gap-3 items-center bg-white">
                    <div className="w-10 h-10 rounded-full bg-purple-50 flex items-center justify-center flex-shrink-0">
                        <HiSparkles className="w-5 h-5 text-purple-500" />
                    </div>
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={
                            messages.length === 0
                                ? "Hi! I can help you build a workflow. Describe what you need..."
                                : "Ask me to modify the workflow or create something new..."
                        }
                        className="flex-1 max-h-32 min-h-[44px] py-3 px-2 bg-transparent text-sm text-gray-900 placeholder:text-gray-500 focus:outline-none resize-none leading-normal"
                        rows={1}
                        style={{ fieldSizing: "content" } as any}
                        disabled={isLoading}
                    />
                    <button
                        onClick={handleSubmit}
                        disabled={!input.trim() || isLoading}
                        className="p-2.5 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
                    >
                        <HiPaperAirplane className="w-4 h-4 transform rotate-[-20deg]" />
                    </button>
                </div>
            </div>
        </div>
    );
}
