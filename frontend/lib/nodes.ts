import {
    HiChatBubbleLeftRight,
    HiArrowUpTray,
    HiTableCells,
    HiMapPin,
    HiMagnifyingGlass,
    HiCursorArrowRays,
    HiGlobeAlt,
    HiCalculator,
    HiPhoto,
    HiCube,
    HiSparkles,
    HiCheck,
    HiDocumentText,
    HiShare,
    HiAcademicCap,
    HiArrowPath,
    HiFunnel,
    HiClipboardDocumentCheck,
    HiChartBar,
    HiArrowRightCircle,
} from "react-icons/hi2";

export type NodeSettings = {
    // Shared settings
    maxWords?: number; // Used by summarization and synthesis
    
    // Formatting settings
    outputFormat?: "json" | "xml" | "markdown" | "html" | "csv" | "yaml";
    
    // Conditional branch settings
    conditionPrompt?: string;
    
    // Transformer settings
    fromFormat?: string;
    toFormat?: string;
    
    // Router settings
    routingRules?: string;
    confidenceThreshold?: number;
    
    // Supervisor settings
    planningStyle?: "detailed" | "brief" | "optimized";
    optimizationLevel?: "none" | "basic" | "aggressive";
    
    // Orchestrator settings
    toolSelectionStrategy?: "conservative" | "balanced" | "aggressive";
    maxTools?: number;
    
    // Semantic Search settings
    topK?: number;
    enableReranking?: boolean;
    
    // Web Search settings
    numResults?: number;
    timeRange?: "any" | "day" | "week" | "month" | "year";
    
    // Image Generator settings
    imageType?: "diagram" | "photo" | "artistic" | "cartoon" | "illustration";
    
    // Sampler settings
    numResponses?: number;
    
    // Planning settings
    planningDepth?: "shallow" | "medium" | "deep";
    detailLevel?: "high-level" | "detailed" | "step-by-step";
    
    // Research settings
    researchDepth?: "quick" | "standard" | "comprehensive";
    numSources?: number;
    
    // Aggregator settings
    mergeStrategy?: "concatenate" | "summarize" | "prioritize";
    conflictResolution?: "first" | "latest" | "consensus";
};

export type NodeType = {
    id: string;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    color: string; // Tailwind color class
    category: "input" | "agent" | "tool" | "output";
    description: string;
    hasSettings?: boolean; // Whether this node has configurable settings
    defaultSettings?: NodeSettings; // Default settings for this node type
    comingSoon?: boolean; // Whether this node is coming soon
};

export const NODE_TYPES: NodeType[] = [
    {
        id: "prompt",
        label: "Prompt",
        icon: HiChatBubbleLeftRight,
        color: "bg-rose-100 text-rose-600 border-rose-200",
        category: "input",
        description: "Initial instruction or data context for the workflow."
    },
    {
        id: "upload",
        label: "Upload",
        icon: HiArrowUpTray,
        color: "bg-blue-100 text-blue-600 border-blue-200",
        category: "input",
        description: "Upload files (PDF, CSV, TXT) to be processed."
    },
    {
        id: "spreadsheet",
        label: "Spreadsheet",
        icon: HiTableCells,
        color: "bg-teal-100 text-teal-600 border-teal-200",
        category: "output",
        description: "Load or create structured data in spreadsheet format."
    },
    {
        id: "supervisor",
        label: "Supervisor Agent",
        icon: HiMapPin,
        color: "bg-amber-100 text-amber-600 border-amber-200",
        category: "agent",
        description: "Analyzes the workflow graph structure, understands downstream nodes, and optimizes execution plans. Coordinates task delegation and identifies parallel execution opportunities.",
        hasSettings: true,
        defaultSettings: {
            planningStyle: "optimized",
            optimizationLevel: "basic"
        }
    },
    {
        id: "semantic_search",
        label: "Semantic Search",
        icon: HiMagnifyingGlass,
        color: "bg-cyan-100 text-cyan-600 border-cyan-200",
        category: "tool",
        description: "Performs semantic search across your knowledge base using vector embeddings. Finds relevant documents based on meaning, not just keywords. Configure result count and reranking in settings.",
        hasSettings: true,
        defaultSettings: {
            topK: 5,
            enableReranking: true
        }
    },
    {
        id: "orchestrator",
        label: "Tool Orchestrator",
        icon: HiCursorArrowRays,
        color: "bg-indigo-100 text-indigo-600 border-indigo-200",
        category: "agent",
        description: "Intelligently selects which tools to execute based on context and query requirements. Uses semantic search results to make informed decisions about tool usage. Configure selection strategy and tool limits in settings.",
        hasSettings: true,
        defaultSettings: {
            toolSelectionStrategy: "balanced",
            maxTools: 3
        }
    },
    {
        id: "web_search",
        label: "Web Search",
        icon: HiGlobeAlt,
        color: "bg-green-100 text-green-600 border-green-200",
        category: "tool",
        description: "Searches the web for current, real-time information. Useful for queries requiring up-to-date data, news, or information not in your knowledge base.",
        comingSoon: true
    },
    {
        id: "image_generator",
        label: "Image Generator",
        icon: HiPhoto,
        color: "bg-pink-100 text-pink-600 border-pink-200",
        category: "tool",
        description: "Generates images from text descriptions using AI models. Supports various types including diagrams, photos, and artistic renderings. Configure image type in settings.",
        hasSettings: true,
        defaultSettings: {
            imageType: "photo"
        }
    },
    {
        id: "sampler",
        label: "Verbalized Sampling",
        icon: HiCube,
        color: "bg-purple-100 text-purple-600 border-purple-200",
        category: "agent",
        description: "Generates multiple diverse candidate answers by exploring different reasoning paths. Improves accuracy by considering various perspectives and approaches. Configure number of responses in settings.",
        hasSettings: true,
        defaultSettings: {
            numResponses: 5
        }
    },
    {
        id: "synthesis",
        label: "Synthesis Agent",
        icon: HiSparkles,
        color: "bg-emerald-100 text-emerald-600 border-emerald-200",
        category: "agent",
        description: "Synthesizes information from multiple sources, candidates, and tool outputs into a coherent, well-structured final answer. Handles citations, formatting, and ensures comprehensive coverage. Configure maximum word count in settings.",
        hasSettings: true,
        defaultSettings: {
            maxWords: 500
        }
    },
    {
        id: "response",
        label: "Response",
        icon: HiCheck,
        color: "bg-green-100 text-green-600 border-green-200",
        category: "output",
        description: "Finalize and format the workflow result for delivery."
    },
    // Modern Agent Types
    {
        id: "planning",
        label: "Planning Agent",
        icon: HiDocumentText,
        color: "bg-slate-100 text-slate-600 border-slate-200",
        category: "agent",
        description: "Creates detailed, step-by-step execution plans for complex tasks. Breaks down high-level goals into actionable subtasks and optimizes task sequences.",
        comingSoon: true
    },
    {
        id: "router",
        label: "Router Agent",
        icon: HiShare,
        color: "bg-violet-100 text-violet-600 border-violet-200",
        category: "agent",
        description: "Analyzes input content and intelligently routes it to the most appropriate downstream node. Uses content analysis, topic detection, and user-defined routing rules to make routing decisions.",
        comingSoon: true
    },
    {
        id: "research",
        label: "Research Agent",
        icon: HiAcademicCap,
        color: "bg-amber-100 text-amber-600 border-amber-200",
        category: "agent",
        description: "Conducts in-depth research by gathering information from multiple sources, synthesizing findings, and providing proper citations. Ideal for comprehensive analysis and fact-checking.",
        comingSoon: true
    },
    {
        id: "transformer",
        label: "Transformer Agent",
        icon: HiArrowPath,
        color: "bg-cyan-100 text-cyan-600 border-cyan-200",
        category: "agent",
        description: "Transforms data from one format to another. Configure source and target formats (JSON, XML, CSV, Markdown, etc.).",
        hasSettings: true,
        defaultSettings: {
            fromFormat: "json",
            toFormat: "xml"
        }
    },
    {
        id: "conditional_branch",
        label: "Conditional Branch",
        icon: HiArrowRightCircle,
        color: "bg-fuchsia-100 text-fuchsia-600 border-fuchsia-200",
        category: "agent",
        description: "Evaluates custom conditions specified by the user and routes to different paths based on if/else logic.",
        comingSoon: true
    },
    {
        id: "aggregator",
        label: "Aggregator Agent",
        icon: HiFunnel,
        color: "bg-teal-100 text-teal-600 border-teal-200",
        category: "agent",
        description: "Combines outputs from multiple nodes, merges parallel execution results, and resolves conflicts. Essential for workflows with branching paths or parallel processing.",
        comingSoon: true
    },
    {
        id: "summarization",
        label: "Summarization Agent",
        icon: HiClipboardDocumentCheck,
        color: "bg-lime-100 text-lime-600 border-lime-200",
        category: "agent",
        description: "Summarizes long outputs, extracts key points, and creates executive summaries. Configure maximum word limit in settings.",
        hasSettings: true,
        defaultSettings: {
            maxWords: 100
        }
    },
    {
        id: "formatting",
        label: "Formatting Agent",
        icon: HiChartBar,
        color: "bg-sky-100 text-sky-600 border-sky-200",
        category: "agent",
        description: "Formats outputs to a specific format. Select the desired output format (JSON, XML, Markdown, HTML, CSV, YAML) in settings.",
        hasSettings: true,
        defaultSettings: {
            outputFormat: "json"
        }
    },
];
