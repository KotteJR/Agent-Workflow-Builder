# CogniVeil Workflow Builder

## Overview

CogniVeil is a powerful, modular AI workflow builder that enables you to create sophisticated document processing, content generation, and AI-powered analysis pipelines. Built on a visual node-based editor, it allows you to design complex workflows by connecting specialized AI agents and tools.

**The key principle: Your output is determined by how you structure your workflow.** You can make it as simple or as complex as you need—every workflow is fully customizable and modular.

---

## 🎯 Core Capabilities

### 📄 Document Processing & Extraction

Transform any document into structured, actionable data.

| Input | Output | Use Case |
|-------|--------|----------|
| PDF | CSV, JSON, Excel | Regulatory compliance extraction |
| PDF | Spreadsheet | GRC (Governance, Risk, Compliance) analysis |
| Text | Structured data | Contract analysis, data extraction |
| Uploaded files | Any format | Invoice processing, report analysis |

**Example Workflow: PDF to Compliance Spreadsheet**
```
[Upload] → [Supervisor] → [Transformer] → [Spreadsheet]
```
- Extracts regulatory standards, risks, controls
- Outputs 12-column compliance matrix
- Supports JCI, CBAHI, financial regulations, and more

---

### 🎨 Content Generation

Create professional content from prompts or source material.

#### Presentations (PowerPoint-exportable HTML)
```
[Prompt] → [Semantic Search] → [Synthesis] → [Code Agent] → [Viewer]
```
- Interactive HTML presentations with:
  - 8 slide types (title, content, cards, columns, stats, quotes)
  - Keyboard navigation (← →)
  - Smooth animations
  - Professional SVG icons
  - Export to PowerPoint-compatible HTML

#### React/TypeScript Components
```
[Prompt] → [Code Agent (tsx)] → [Viewer]
```
- Production-ready React components
- Tailwind CSS styling
- Complete TypeScript types
- Runnable code output

#### Website Sections
```
[Prompt] → [Code Agent (html)] → [Viewer]
```
- Full HTML/CSS sections
- Responsive design
- Modern styling with gradients, animations
- No external dependencies

---

### 🖼️ Visual Content & Diagrams

Generate AI-powered images, diagrams, and infographics.

```
[Prompt] → [Image Generator] → [Response]
```

**Image Types:**
- 📊 **Diagrams** - Technical, system architecture
- 📈 **Flowcharts** - Process flows, decision trees
- 📋 **Infographics** - Data visualization, statistics
- 🎨 **Illustrations** - Custom artwork
- 📸 **Photos** - Photorealistic images

**Style Presets:**
- Professional (boardroom-ready)
- Minimal (clean, simple)
- Detailed (comprehensive)

**Providers:** DALL-E, Gemini, Nano Banana Pro (up to 4K)

---

### 🔍 Knowledge Base & RAG

Build intelligent Q&A systems with your own documents.

```
[Prompt] → [Supervisor (Auto-RAG)] → [Semantic Search] → [Sampler] → [Synthesis] → [Response]
```

**Features:**
- Vector-based semantic search
- Automatic relevance reranking
- Multi-candidate answer generation
- Source citations ([1], [2], [3])
- Switchable knowledge bases

---

### 💬 Chatbot / Q&A System

Create conversational AI powered by your knowledge base.

**Simple Chatbot:**
```
[Prompt] → [Semantic Search] → [Synthesis] → [Response]
```

**Advanced Chatbot with Reasoning:**
```
[Prompt] → [Supervisor] → [Semantic Search] → [Orchestrator] → [Sampler] → [Synthesis] → [Response]
```

---

### 🌐 Multi-Language Support

Translate any content to 50+ languages.

```
[Upload/Prompt] → [Transformer] → [Translator] → [Response]
```

**Supported Languages:**
- Major: English, Spanish, French, German, Chinese, Japanese, Korean, Arabic
- European: Italian, Dutch, Polish, Portuguese, Russian, Greek, Swedish, Danish, Norwegian
- Asian: Hindi, Bengali, Thai, Vietnamese, Indonesian, Malay, Tamil, Telugu
- Middle Eastern: Arabic, Hebrew, Persian (Farsi), Turkish, Urdu
- African: Swahili, Amharic, Afrikaans
- And 20+ more

**Format Preservation:** CSV, JSON, Markdown tables retain their structure during translation.

---

## 🧩 Available Nodes

### Input Nodes

| Node | Description | Use Cases |
|------|-------------|-----------|
| **Prompt** | Text input for queries/instructions | Questions, prompts, data |
| **Upload** | File upload (PDF, CSV, TXT) | Document processing, data import |

### Agent Nodes

| Node | Description | Settings |
|------|-------------|----------|
| **Supervisor** | Analyzes workflow, creates execution plan | Planning style, Auto-RAG toggle |
| **Semantic Search** | Searches knowledge base | Top-K results, Reranking |
| **Orchestrator** | Selects tools intelligently | Strategy (conservative/balanced/aggressive) |
| **Sampler** | Generates diverse candidates | Number of responses (1-10) |
| **Synthesis** | Combines sources into final answer | Max words |
| **Transformer** | Extracts structured data from documents | Format (CSV/JSON/Excel) |
| **Summarization** | Creates concise summaries | Max words |
| **Code Agent** | Generates code/presentations | Format (HTML/TSX/React/JSON/XML) |
| **Translator** | Translates between languages | Source/Target language |

### Tool Nodes

| Node | Description | Settings |
|------|-------------|----------|
| **Image Generator** | Creates AI images | Type, Style preset, Custom instructions |
| **Web Search** | Real-time web search | (Coming Soon) |

### Output Nodes

| Node | Description | Formats |
|------|-------------|---------|
| **Response** | Final text output | Text with citations |
| **Spreadsheet** | Tabular data output | CSV, Excel-compatible |
| **Viewer** | Code/presentation display | HTML, TSX, React, JSON |

---

## 🔧 Node Configuration

Every agent node has configurable settings. Click the ⚙️ icon on any node to access:

### Supervisor Agent
```json
{
  "planningStyle": "detailed | brief | optimized",
  "optimizationLevel": "none | basic | aggressive",
  "autoRAG": true,  // Auto-retrieve context before planning
  "supervisorPrompt": "Custom instructions..."
}
```

### Semantic Search
```json
{
  "topK": 5,  // Number of results (1-20)
  "enableReranking": true  // LLM-based relevance reranking
}
```

### Image Generator
```json
{
  "imageType": "diagram | flowchart | infographic | photo | illustration",
  "stylePreset": "professional | minimal | detailed",
  "customInstructions": "Your style requirements...",
  "imageDetailLevel": 50  // 0-100 slider
}
```

### Transformer
```json
{
  "fromFormat": "text | pdf | json",
  "toFormat": "csv | json | excel",
  "useAdvancedModel": true  // Use GPT-4 for complex documents
}
```

### Translator
```json
{
  "sourceLanguage": "auto",  // Auto-detect or specify
  "targetLanguage": "ar"     // Any of 50+ language codes
}
```

### Code Agent
```json
{
  "outputFormat": "html | presentation | tsx | react | json | xml | yaml | csv | markdown"
}
```

---

## 📋 Example Workflows

### 1. Regulatory Compliance Extraction
**Goal:** Extract JCI standards into a compliance spreadsheet

```
[Upload (PDF)] → [Supervisor] → [Transformer] → [Spreadsheet]
```

**Output:** 12-column CSV with:
- Regulation, Chapter, Section, Article
- Article Description (full text)
- Risk, Risk Description, Compliance Risk Category
- Mandated Control, Control Description, Mandated Control Category

---

### 2. Presentation Generator
**Goal:** Create a professional presentation from research

```
[Prompt] → [Semantic Search] → [Synthesis] → [Code Agent (presentation)] → [Viewer]
```

**Output:** Interactive HTML presentation with:
- Animated slide transitions
- Keyboard navigation
- 8 different slide layouts
- Professional styling

---

### 3. Multi-Source Research Report
**Goal:** Comprehensive answer with citations from knowledge base

```
[Prompt] → [Supervisor (Auto-RAG)] → [Semantic Search] → [Sampler] → [Synthesis] → [Response]
```

**Output:** Structured response with:
- Multiple perspective analysis
- Source citations [1], [2], [3]
- Word-limit control
- Coherent synthesis

---

### 4. Document Translation Pipeline
**Goal:** Extract data from Arabic PDF, output English spreadsheet

```
[Upload] → [Supervisor] → [Transformer] → [Translator (ar → en)] → [Spreadsheet]
```

---

### 5. Diagram Generator
**Goal:** Create a visual diagram from a concept

```
[Prompt] → [Image Generator (diagram)] → [Response]
```

**Settings:**
- `imageType: "diagram"`
- `stylePreset: "professional"`
- `customInstructions: "Clean white background, blue accents"`

---

### 6. Website Component Generator
**Goal:** Generate React component for a feature

```
[Prompt] → [Code Agent (tsx)] → [Viewer]
```

**Example prompt:** "Create a pricing table component with 3 tiers: Basic, Pro, Enterprise"

**Output:** Complete TSX component with Tailwind styling

---

## 🏗️ Architecture

### Modular Design Philosophy

The workflow builder follows a **modular, composable architecture**:

1. **Nodes are independent** - Each node performs one specific task well
2. **Context flows downstream** - Each node enriches the shared context
3. **Settings per node** - Fine-tune behavior at each step
4. **Visual connections** - Drag to connect nodes and build pipelines
5. **Real-time execution** - Watch each node execute in sequence

### Execution Flow

```
[Input Nodes] → [Agent Nodes] → [Output Nodes]
     ↓              ↓               ↓
  Raw Data    Processing      Final Output
              Context
              Enrichment
```

### Context Passing

Each agent adds to a shared context object:

```typescript
{
  // From Input
  "uploaded_file_content": "...",
  "promptText": "...",
  
  // From Supervisor
  "supervisor_plan": "...",
  "supervisor_guidance": "...",
  
  // From Semantic Search
  "semantic_results": [...],
  "context_snippets": [...],
  
  // From Sampler
  "candidates": [...],
  
  // From Synthesis
  "final_answer": "...",
  
  // From Transformer
  "transformed_content": "...",
  
  // From Translator
  "translated_content": "..."
}
```

---

## 🚀 Getting Started

### 1. Create a New Workflow
- Click **"New Workflow"** in the sidebar
- Or start fresh with the empty canvas

### 2. Add Nodes
- Drag nodes from the right sidebar onto the canvas
- Click a node to select it
- Configure settings via the ⚙️ icon

### 3. Connect Nodes
- Drag from a node's output handle to another node's input handle
- Connections define the execution order

### 4. Configure Input
- **Prompt node:** Type your query directly in the node
- **Upload node:** Drop files (PDF, CSV, TXT) into the node

### 5. Run the Workflow
- Click the **▶ Play** button
- Watch nodes execute in real-time (green = complete, blue = running)
- View results in output nodes

### 6. Save and Reuse
- Click **"Save Workflow"** to persist
- Load saved workflows from the sidebar
- Modify and iterate on existing workflows

---

## 📊 Output Formats

| Format | Extension | Use Case |
|--------|-----------|----------|
| CSV | .csv | Spreadsheet data, Excel import |
| JSON | .json | Structured data, API integration |
| HTML | .html | Presentations, documents, web pages |
| TSX | .tsx | React components |
| XML | .xml | Data interchange |
| YAML | .yaml | Configuration files |
| Markdown | .md | Documentation |
| Image | .png | Diagrams, infographics |

---

## 🔒 Knowledge Base

### Switching Knowledge Bases
Toggle between knowledge bases using the sidebar switch:
- **Legal** - Legal documents, contracts, regulations
- **Audit** - Audit standards, compliance documents

### Adding Documents
Documents are indexed into the vector database for semantic search:
1. Upload documents to the knowledge base
2. Documents are chunked and embedded
3. Semantic search finds relevant passages
4. Reranking improves relevance

---

## 🎓 Advanced Features

### Auto-RAG (Retrieval-Augmented Generation)
Enable in Supervisor to automatically:
1. Search knowledge base before planning
2. Include relevant context in analysis
3. Ground responses in source documents

### Multi-Candidate Sampling
The **Sampler** agent generates multiple diverse answers:
- Explores different reasoning paths
- Improves accuracy through diversity
- Synthesis combines the best insights

### Execution History
View past executions:
- Step-by-step agent outputs
- Node-level results
- Timing and performance metrics

---

## 📁 File Support

| Type | Extensions | Max Size |
|------|------------|----------|
| PDF | .pdf | 10MB |
| Text | .txt | 5MB |
| CSV | .csv | 5MB |
| JSON | .json | 5MB |

---

## 🛠️ Technical Stack

- **Frontend:** Next.js 15, React, Tailwind CSS, React Flow
- **Backend:** FastAPI, Python 3.11+
- **AI:** OpenAI GPT-4o, GPT-4o-mini, DALL-E 3, Gemini
- **Vector DB:** PostgreSQL + pgvector (or file-based)
- **Embeddings:** OpenAI text-embedding-3-small

---

*CogniVeil Workflow Builder - Design your AI workflow, your way.*

