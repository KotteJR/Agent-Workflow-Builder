"use client";

import { useState, useEffect, memo, useCallback } from "react";
import { HiXMark, HiCog6Tooth } from "react-icons/hi2";
import { NodeSettings, NODE_TYPES } from "@/lib/nodes";

interface NodeSettingsPanelProps {
    nodeId: string;
    nodeType: string;
    currentSettings?: NodeSettings;
    onClose: () => void;
    onSave: (settings: NodeSettings) => void;
}

export const NodeSettingsPanel = memo(function NodeSettingsPanel({
    nodeId,
    nodeType,
    currentSettings,
    onClose,
    onSave,
}: NodeSettingsPanelProps) {
    const nodeConfig = NODE_TYPES.find((n) => n.id === nodeType);
    const [settings, setSettings] = useState<NodeSettings>(
        currentSettings || nodeConfig?.defaultSettings || {}
    );

    useEffect(() => {
        setSettings(currentSettings || nodeConfig?.defaultSettings || {});
    }, [currentSettings, nodeConfig]);

    const handleSave = useCallback(() => {
        onSave(settings);
        onClose();
    }, [onSave, onClose, settings]);

    const handleBackdropClick = useCallback(() => {
        onClose();
    }, [onClose]);

    const handleContentClick = useCallback((e: React.MouseEvent) => {
        e.stopPropagation();
    }, []);

    if (!nodeConfig) return null;

    return (
        <div
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100]"
            onClick={handleBackdropClick}
        >
            <div
                className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto"
                onClick={handleContentClick}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-200">
                    <div className="flex items-center gap-3">
                        <div
                            className={`w-10 h-10 rounded-lg ${nodeConfig.color} flex items-center justify-center`}
                        >
                            <HiCog6Tooth className="w-5 h-5" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-gray-900">
                                {nodeConfig.label} Settings
                            </h2>
                            <p className="text-sm text-gray-500">Configure node behavior</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors"
                    >
                        <HiXMark className="w-5 h-5" />
                    </button>
                </div>

                {/* Settings Content */}
                <div className="p-6 space-y-6">
                    {/* Summarization Agent Settings */}
                    {nodeType === "summarization" && (
                        <NumberSetting
                            label="Maximum Words"
                            value={settings.maxWords ?? 100}
                            onChange={(v) => setSettings({ ...settings, maxWords: v })}
                            min={1}
                            helpText="Maximum number of words in the summary"
                        />
                    )}

                    {/* Formatting Agent Settings */}
                    {nodeType === "formatting" && (
                        <SelectSetting
                            label="Output Format"
                            value={settings.outputFormat ?? "html"}
                            onChange={(v) =>
                                setSettings({
                                    ...settings,
                                    outputFormat: v as NodeSettings["outputFormat"],
                                })
                            }
                            options={[
                                { value: "presentation", label: "📊 Presentation (HTML Slides)" },
                                { value: "html", label: "🌐 HTML Document" },
                                { value: "tsx", label: "⚛️ React/TSX Component" },
                                { value: "react", label: "⚛️ React Component (JSX)" },
                                { value: "json", label: "📋 JSON" },
                                { value: "xml", label: "📄 XML" },
                                { value: "markdown", label: "📝 Markdown" },
                                { value: "csv", label: "📊 CSV" },
                                { value: "yaml", label: "⚙️ YAML" },
                            ]}
                            helpText="Select the desired output format. Use 'Presentation' for interactive slides."
                        />
                    )}

                    {/* Transformer Agent Settings */}
                    {nodeType === "transformer" && (
                        <div className="space-y-4">
                            <TextSetting
                                label="From Format"
                                value={settings.fromFormat ?? "text"}
                                onChange={(v) => setSettings({ ...settings, fromFormat: v })}
                                placeholder="text"
                                helpText="Source format (e.g., text, pdf, json, xml, csv)"
                            />
                            <TextSetting
                                label="To Format"
                                value={settings.toFormat ?? "csv"}
                                onChange={(v) => setSettings({ ...settings, toFormat: v })}
                                placeholder="csv"
                                helpText="Target format (e.g., csv, json, xml, markdown)"
                            />
                            <CheckboxSetting
                                label="Advanced Analysis (GPT-4)"
                                checked={settings.useAdvancedModel ?? true}
                                onChange={(v) => setSettings({ ...settings, useAdvancedModel: v })}
                                helpText="Use GPT-4 for deep document understanding and comprehensive extraction. Recommended for complex documents."
                            />
                        </div>
                    )}

                    {/* Spreadsheet Output Settings */}
                    {nodeType === "spreadsheet" && (
                        <div className="space-y-4">
                            <TextareaSetting
                                label="Custom Columns"
                                value={settings.customColumns ?? ""}
                                onChange={(v) => setSettings({ ...settings, customColumns: v })}
                                placeholder="e.g., Title, Author, Date, Summary, Key Points, Citations"
                                helpText="Specify columns you want extracted (comma-separated). Leave empty for AI-determined columns."
                            />
                            <SelectSetting
                                label="Extraction Depth"
                                value={settings.extractionDepth ?? "comprehensive"}
                                onChange={(v) =>
                                    setSettings({
                                        ...settings,
                                        extractionDepth: v as NodeSettings["extractionDepth"],
                                    })
                                }
                                options={[
                                    { value: "basic", label: "Basic (quick, fewer details)" },
                                    { value: "detailed", label: "Detailed (balanced)" },
                                    { value: "comprehensive", label: "Comprehensive (deep analysis)" },
                                ]}
                                helpText="How thoroughly to analyze the document for data extraction"
                            />
                        </div>
                    )}

                    {/* Supervisor Agent Settings */}
                    {nodeType === "supervisor" && (
                        <div className="space-y-4">
                            <SelectSetting
                                label="Planning Style"
                                value={settings.planningStyle ?? "optimized"}
                                onChange={(v) =>
                                    setSettings({
                                        ...settings,
                                        planningStyle: v as NodeSettings["planningStyle"],
                                    })
                                }
                                options={[
                                    { value: "detailed", label: "Detailed" },
                                    { value: "brief", label: "Brief" },
                                    { value: "optimized", label: "Optimized" },
                                ]}
                                helpText="Level of detail in execution planning"
                            />
                            <SelectSetting
                                label="Optimization Level"
                                value={settings.optimizationLevel ?? "basic"}
                                onChange={(v) =>
                                    setSettings({
                                        ...settings,
                                        optimizationLevel: v as NodeSettings["optimizationLevel"],
                                    })
                                }
                                options={[
                                    { value: "none", label: "None" },
                                    { value: "basic", label: "Basic" },
                                    { value: "aggressive", label: "Aggressive" },
                                ]}
                                helpText="How aggressively to optimize workflow execution"
                            />
                            <CheckboxSetting
                                label="Auto-RAG (Auto-retrieve context)"
                                checked={settings.autoRAG ?? false}
                                onChange={(v) => setSettings({ ...settings, autoRAG: v })}
                                helpText="Automatically search knowledge base and include relevant context before planning"
                            />
                            <TextareaSetting
                                label="Supervisor Instructions"
                                value={settings.supervisorPrompt ?? ""}
                                onChange={(v) => setSettings({ ...settings, supervisorPrompt: v })}
                                placeholder="Enter specific instructions for what the supervisor should focus on..."
                                helpText="Additional context or specific instructions for the supervisor agent"
                            />
                        </div>
                    )}

                    {/* Orchestrator Agent Settings */}
                    {nodeType === "orchestrator" && (
                        <div className="space-y-4">
                            <SelectSetting
                                label="Tool Selection Strategy"
                                value={settings.toolSelectionStrategy ?? "balanced"}
                                onChange={(v) =>
                                    setSettings({
                                        ...settings,
                                        toolSelectionStrategy: v as NodeSettings["toolSelectionStrategy"],
                                    })
                                }
                                options={[
                                    { value: "conservative", label: "Conservative" },
                                    { value: "balanced", label: "Balanced" },
                                    { value: "aggressive", label: "Aggressive" },
                                ]}
                                helpText="How liberally to use tools"
                            />
                            <NumberSetting
                                label="Maximum Tools"
                                value={settings.maxTools ?? 3}
                                onChange={(v) => setSettings({ ...settings, maxTools: v })}
                                min={1}
                                max={10}
                                helpText="Maximum number of tools to execute per query"
                            />
                        </div>
                    )}

                    {/* Semantic Search Settings */}
                    {nodeType === "semantic_search" && (
                        <div className="space-y-4">
                            <NumberSetting
                                label="Top K Results"
                                value={settings.topK ?? 5}
                                onChange={(v) => setSettings({ ...settings, topK: v })}
                                min={1}
                                max={20}
                                helpText="Number of top results to return"
                            />
                            <CheckboxSetting
                                label="Enable Reranking"
                                checked={settings.enableReranking ?? true}
                                onChange={(v) => setSettings({ ...settings, enableReranking: v })}
                                helpText="Use reranking to improve result relevance"
                            />
                        </div>
                    )}

                    {/* Image Generator Settings */}
                    {nodeType === "image_generator" && (
                        <div className="space-y-5">
                            <SelectSetting
                                label="Image Type"
                                value={settings.imageType ?? "diagram"}
                                onChange={(v) =>
                                    setSettings({
                                        ...settings,
                                        imageType: v as NodeSettings["imageType"],
                                    })
                                }
                                options={[
                                    { value: "diagram", label: "📊 Diagram" },
                                    { value: "flowchart", label: "📋 Flowchart" },
                                    { value: "infographic", label: "📈 Infographic" },
                                    { value: "photo", label: "📷 Photo" },
                                    { value: "illustration", label: "🎨 Illustration" },
                                ]}
                                helpText="Base type of image to generate"
                            />
                            
                            <SelectSetting
                                label="Style Preset"
                                value={settings.stylePreset ?? "professional"}
                                onChange={(v) =>
                                    setSettings({
                                        ...settings,
                                        stylePreset: v as NodeSettings["stylePreset"],
                                    })
                                }
                                options={[
                                    { value: "professional", label: "Professional (Business/Corporate)" },
                                    { value: "minimal", label: "Minimal (Simple/Clean)" },
                                    { value: "detailed", label: "Detailed (Comprehensive)" },
                                ]}
                                helpText="Overall style approach"
                            />
                            
                            {/* Detail Level Slider */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Detail Level: {settings.imageDetailLevel ?? 50}%
                                </label>
                                <input
                                    type="range"
                                    min={0}
                                    max={100}
                                    value={settings.imageDetailLevel ?? 50}
                                    onChange={(e) =>
                                        setSettings({
                                            ...settings,
                                            imageDetailLevel: parseInt(e.target.value),
                                        })
                                    }
                                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-pink-500"
                                />
                                <div className="flex justify-between text-xs text-gray-500 mt-1">
                                    <span>Simple</span>
                                    <span>Balanced</span>
                                    <span>Intricate</span>
                                </div>
                            </div>
                            
                            {/* Custom Instructions */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Custom Style Instructions
                                </label>
                                <textarea
                                    value={settings.customInstructions ?? ""}
                                    onChange={(e) =>
                                        setSettings({
                                            ...settings,
                                            customInstructions: e.target.value,
                                        })
                                    }
                                    placeholder="Add your own style requirements... e.g., 'blue color scheme, include company logo space, vertical layout'"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 text-sm"
                                    rows={3}
                                />
                                <p className="mt-1 text-xs text-gray-500">
                                    Optional: Add custom instructions to fine-tune the output
                                </p>
                            </div>
                            
                            {/* Quick Style Presets */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Quick Presets
                                </label>
                                <div className="flex flex-wrap gap-2">
                                    {[
                                        { label: "Corporate", value: "corporate colors, clean, formal" },
                                        { label: "Technical", value: "technical documentation, precise, labeled" },
                                        { label: "Modern", value: "modern design, sleek, contemporary" },
                                        { label: "Colorful", value: "vibrant colors, engaging, eye-catching" },
                                    ].map((preset) => (
                                        <button
                                            key={preset.label}
                                            type="button"
                                            onClick={() =>
                                                setSettings({
                                                    ...settings,
                                                    customInstructions: preset.value,
                                                })
                                            }
                                            className="px-3 py-1 text-xs bg-pink-50 text-pink-700 rounded-full hover:bg-pink-100 transition-colors border border-pink-200"
                                        >
                                            {preset.label}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Translator Settings */}
                    {nodeType === "translator" && (
                        <div className="space-y-4">
                            <SelectSetting
                                label="Source Language"
                                value={settings.sourceLanguage ?? "auto"}
                                onChange={(v) =>
                                    setSettings({
                                        ...settings,
                                        sourceLanguage: v,
                                    })
                                }
                                options={[
                                    { value: "auto", label: "🔍 Auto-detect" },
                                    { value: "en", label: "🇬🇧 English" },
                                    { value: "ar", label: "🇸🇦 Arabic" },
                                    { value: "zh", label: "🇨🇳 Chinese (Simplified)" },
                                    { value: "zh-TW", label: "🇹🇼 Chinese (Traditional)" },
                                    { value: "fr", label: "🇫🇷 French" },
                                    { value: "de", label: "🇩🇪 German" },
                                    { value: "es", label: "🇪🇸 Spanish" },
                                    { value: "pt", label: "🇵🇹 Portuguese" },
                                    { value: "ru", label: "🇷🇺 Russian" },
                                    { value: "ja", label: "🇯🇵 Japanese" },
                                    { value: "ko", label: "🇰🇷 Korean" },
                                    { value: "it", label: "🇮🇹 Italian" },
                                    { value: "nl", label: "🇳🇱 Dutch" },
                                    { value: "pl", label: "🇵🇱 Polish" },
                                    { value: "tr", label: "🇹🇷 Turkish" },
                                    { value: "vi", label: "🇻🇳 Vietnamese" },
                                    { value: "th", label: "🇹🇭 Thai" },
                                    { value: "id", label: "🇮🇩 Indonesian" },
                                    { value: "hi", label: "🇮🇳 Hindi" },
                                    { value: "bn", label: "🇧🇩 Bengali" },
                                    { value: "ur", label: "🇵🇰 Urdu" },
                                    { value: "fa", label: "🇮🇷 Persian (Farsi)" },
                                    { value: "he", label: "🇮🇱 Hebrew" },
                                    { value: "sv", label: "🇸🇪 Swedish" },
                                    { value: "da", label: "🇩🇰 Danish" },
                                    { value: "no", label: "🇳🇴 Norwegian" },
                                    { value: "fi", label: "🇫🇮 Finnish" },
                                    { value: "el", label: "🇬🇷 Greek" },
                                    { value: "cs", label: "🇨🇿 Czech" },
                                    { value: "ro", label: "🇷🇴 Romanian" },
                                    { value: "hu", label: "🇭🇺 Hungarian" },
                                    { value: "uk", label: "🇺🇦 Ukrainian" },
                                    { value: "ms", label: "🇲🇾 Malay" },
                                    { value: "tl", label: "🇵🇭 Filipino" },
                                    { value: "sw", label: "🇰🇪 Swahili" },
                                    { value: "sr", label: "🇷🇸 Serbian" },
                                    { value: "mk", label: "🇲🇰 Macedonian" },
                                ]}
                                helpText="Language of the input text (auto-detect recommended)"
                            />
                            
                            <SelectSetting
                                label="Target Language"
                                value={settings.targetLanguage ?? "en"}
                                onChange={(v) =>
                                    setSettings({
                                        ...settings,
                                        targetLanguage: v,
                                    })
                                }
                                options={[
                                    { value: "en", label: "🇬🇧 English" },
                                    { value: "ar", label: "🇸🇦 Arabic" },
                                    { value: "zh", label: "🇨🇳 Chinese (Simplified)" },
                                    { value: "zh-TW", label: "🇹🇼 Chinese (Traditional)" },
                                    { value: "fr", label: "🇫🇷 French" },
                                    { value: "de", label: "🇩🇪 German" },
                                    { value: "es", label: "🇪🇸 Spanish" },
                                    { value: "pt", label: "🇵🇹 Portuguese" },
                                    { value: "ru", label: "🇷🇺 Russian" },
                                    { value: "ja", label: "🇯🇵 Japanese" },
                                    { value: "ko", label: "🇰🇷 Korean" },
                                    { value: "it", label: "🇮🇹 Italian" },
                                    { value: "nl", label: "🇳🇱 Dutch" },
                                    { value: "pl", label: "🇵🇱 Polish" },
                                    { value: "tr", label: "🇹🇷 Turkish" },
                                    { value: "vi", label: "🇻🇳 Vietnamese" },
                                    { value: "th", label: "🇹🇭 Thai" },
                                    { value: "id", label: "🇮🇩 Indonesian" },
                                    { value: "hi", label: "🇮🇳 Hindi" },
                                    { value: "bn", label: "🇧🇩 Bengali" },
                                    { value: "ur", label: "🇵🇰 Urdu" },
                                    { value: "fa", label: "🇮🇷 Persian (Farsi)" },
                                    { value: "he", label: "🇮🇱 Hebrew" },
                                    { value: "sv", label: "🇸🇪 Swedish" },
                                    { value: "da", label: "🇩🇰 Danish" },
                                    { value: "no", label: "🇳🇴 Norwegian" },
                                    { value: "fi", label: "🇫🇮 Finnish" },
                                    { value: "el", label: "🇬🇷 Greek" },
                                    { value: "cs", label: "🇨🇿 Czech" },
                                    { value: "ro", label: "🇷🇴 Romanian" },
                                    { value: "hu", label: "🇭🇺 Hungarian" },
                                    { value: "uk", label: "🇺🇦 Ukrainian" },
                                    { value: "ms", label: "🇲🇾 Malay" },
                                    { value: "tl", label: "🇵🇭 Filipino" },
                                    { value: "sw", label: "🇰🇪 Swahili" },
                                    { value: "sr", label: "🇷🇸 Serbian" },
                                    { value: "mk", label: "🇲🇰 Macedonian" },
                                ]}
                                helpText="Language to translate into"
                            />
                        </div>
                    )}

                    {/* Sampler Settings */}
                    {nodeType === "sampler" && (
                        <NumberSetting
                            label="Number of Responses"
                            value={settings.numResponses ?? 5}
                            onChange={(v) => setSettings({ ...settings, numResponses: v })}
                            min={1}
                            max={10}
                            helpText="Number of diverse candidate responses to generate"
                        />
                    )}

                    {/* Synthesis Agent Settings */}
                    {nodeType === "synthesis" && (
                        <NumberSetting
                            label="Maximum Words"
                            value={settings.maxWords ?? 500}
                            onChange={(v) => setSettings({ ...settings, maxWords: v })}
                            min={1}
                            helpText="Maximum number of words in the final output"
                        />
                    )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSave}
                        className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        Save Settings
                    </button>
                </div>
            </div>
        </div>
    );
});

// Reusable setting components
interface NumberSettingProps {
    label: string;
    value: number;
    onChange: (value: number) => void;
    min?: number;
    max?: number;
    helpText?: string;
}

const NumberSetting = memo(function NumberSetting({
    label,
    value,
    onChange,
    min,
    max,
    helpText,
}: NumberSettingProps) {
    return (
        <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
            <input
                type="number"
                min={min}
                max={max}
                value={value}
                onChange={(e) => onChange(parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            {helpText && <p className="mt-1 text-xs text-gray-500">{helpText}</p>}
        </div>
    );
});

interface TextSettingProps {
    label: string;
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
    helpText?: string;
}

const TextSetting = memo(function TextSetting({
    label,
    value,
    onChange,
    placeholder,
    helpText,
}: TextSettingProps) {
    return (
        <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
            <input
                type="text"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder={placeholder}
            />
            {helpText && <p className="mt-1 text-xs text-gray-500">{helpText}</p>}
        </div>
    );
});

interface SelectSettingProps {
    label: string;
    value: string;
    onChange: (value: string) => void;
    options: Array<{ value: string; label: string }>;
    helpText?: string;
}

const SelectSetting = memo(function SelectSetting({
    label,
    value,
    onChange,
    options,
    helpText,
}: SelectSettingProps) {
    return (
        <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
            <select
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
                {options.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                        {opt.label}
                    </option>
                ))}
            </select>
            {helpText && <p className="mt-1 text-xs text-gray-500">{helpText}</p>}
        </div>
    );
});

interface CheckboxSettingProps {
    label: string;
    checked: boolean;
    onChange: (checked: boolean) => void;
    helpText?: string;
}

const CheckboxSetting = memo(function CheckboxSetting({
    label,
    checked,
    onChange,
    helpText,
}: CheckboxSettingProps) {
    return (
        <div>
            <label className="flex items-center gap-2">
                <input
                    type="checkbox"
                    checked={checked}
                    onChange={(e) => onChange(e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">{label}</span>
            </label>
            {helpText && <p className="mt-1 text-xs text-gray-500">{helpText}</p>}
        </div>
    );
});

interface TextareaSettingProps {
    label: string;
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
    helpText?: string;
}

const TextareaSetting = memo(function TextareaSetting({
    label,
    value,
    onChange,
    placeholder,
    helpText,
}: TextareaSettingProps) {
    return (
        <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
            <textarea
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[100px] resize-y"
                placeholder={placeholder}
            />
            {helpText && <p className="mt-1 text-xs text-gray-500">{helpText}</p>}
        </div>
    );
});
