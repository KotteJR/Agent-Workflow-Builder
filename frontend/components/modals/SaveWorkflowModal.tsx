"use client";

import { memo } from "react";

interface SaveWorkflowModalProps {
    isOpen: boolean;
    workflowName: string;
    onNameChange: (name: string) => void;
    onSave: () => void;
    onClose: () => void;
}

export const SaveWorkflowModal = memo(function SaveWorkflowModal({
    isOpen,
    workflowName,
    onNameChange,
    onSave,
    onClose,
}: SaveWorkflowModalProps) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100]">
            <div className="bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Save Workflow</h2>
                <input
                    type="text"
                    value={workflowName}
                    onChange={(e) => onNameChange(e.target.value)}
                    placeholder="Workflow name..."
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 mb-4"
                />
                <div className="flex gap-3 justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={onSave}
                        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                    >
                        Save
                    </button>
                </div>
            </div>
        </div>
    );
});

