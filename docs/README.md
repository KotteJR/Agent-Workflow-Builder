# Workflow Builder Standalone

A powerful, graph-based multi-agent workflow execution system that allows users to build, execute, and manage complex AI-powered workflows through an intuitive visual interface.

## 🎯 Project Overview

The Workflow Builder is a full-stack application that enables users to create custom workflows by connecting different AI agents in a graph structure. Each workflow can process documents, perform semantic searches, generate content, create images, and produce structured outputs like spreadsheets.

### Key Features

- **Visual Workflow Builder**: Drag-and-drop interface for creating workflows
- **Multi-Agent System**: 10+ specialized AI agents for different tasks
- **Graph-Based Execution**: Topological sorting ensures proper dependency resolution
- **Branch Routing**: Intelligent path selection based on orchestrator decisions
- **Knowledge Base Integration**: Semantic search over legal and audit documents
- **Real-time Execution**: Server-Sent Events (SSE) for live workflow progress
- **Workflow Persistence**: Save, load, and manage multiple workflows
- **AI-Powered Workflow Generation**: Natural language to workflow conversion
- **Comprehensive Logging**: Detailed execution logs for debugging

## 🏗️ Architecture

### System Components

```
┌─────────────────┐
│   Frontend      │  Next.js + React + React Flow
│   (Port 3000)   │
└────────┬────────┘
         │ HTTP/SSE
         ▼
┌─────────────────┐
│   Backend       │  FastAPI + Python
│   (Port 8000)   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│ LLM   │ │Vector │
│ APIs  │ │Store  │
└───────┘ └───────┘
```

### Technology Stack

**Backend:**
- FastAPI (Python web framework)
- Uvicorn (ASGI server)
- OpenAI/Anthropic/Ollama (LLM providers)
- NumPy (Vector operations)
- PyPDF, python-docx (Document processing)

**Frontend:**
- Next.js 16 (React framework)
- React Flow (@xyflow/react) (Graph visualization)
- TypeScript
- Tailwind CSS

## 📁 Project Structure

```
workflow-builder-standalone/
├── backend/
│   ├── agents/              # AI agent implementations
│   │   ├── base.py          # Base agent class
│   │   ├── supervisor.py    # Workflow planning agent
│   │   ├── orchestrator.py  # Tool selection agent
│   │   ├── semantic_search.py # Document search agent
│   │   ├── sampler.py       # Content sampling agent
│   │   ├── synthesis.py     # Content synthesis agent
│   │   ├── transformer.py   # Data extraction agent
│   │   ├── image_generator.py # Image generation agent
│   │   ├── formatting.py    # Output formatting agent
│   │   └── summarization.py # Summarization agent
│   ├── documents/           # Knowledge base documents
│   │   ├── legal/           # Legal documents
│   │   └── audit/           # Audit documents
│   ├── workflows/           # Saved workflow JSON files
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── models.py            # LLM client implementations
│   ├── workflow_executor.py # Core execution engine
│   ├── workflow_logger.py   # Logging system
│   ├── workflows.py          # Workflow storage
│   ├── retrieval.py         # Vector store & semantic search
│   ├── workflow_builder_llm.py # AI workflow generation
│   └── demo_handler.py      # Demo mode handler
│
└── frontend/
    ├── app/                 # Next.js app directory
    ├── components/          # React components
    │   ├── Node.tsx         # Workflow node component
    │   ├── Sidebar.tsx      # Node palette
    │   ├── WorkflowSidebar.tsx # Workflow management
    │   ├── AgentChat.tsx    # AI assistant chat
    │   └── modals/          # Modal dialogs
    ├── lib/                 # Utilities
    │   ├── api.ts           # API client
    │   ├── types.ts          # TypeScript types
    │   └── nodes.ts          # Node definitions
    └── public/              # Static assets
```

## 🔧 Major Modules

### 1. Workflow Executor (`workflow_executor.py`)

The core execution engine that:
- Parses workflow graphs (nodes and edges)
- Performs topological sorting for dependency resolution
- Executes agents in the correct order
- Handles branch routing based on orchestrator decisions
- Manages execution context between nodes
- Provides comprehensive logging

**Key Functions:**
- `execute_workflow()`: Main execution entry point
- `topological_sort()`: Dependency ordering
- `find_reachable_nodes()`: Graph traversal
- `_execute_agent()`: Individual agent execution

### 2. Agent System (`agents/`)

Modular AI agents, each with a specific role:

| Agent | Purpose | Model |
|-------|---------|-------|
| **Supervisor** | Analyzes queries, plans execution | Small |
| **Orchestrator** | Selects which tools to use | Small |
| **Semantic Search** | Searches knowledge base | Embedding |
| **Sampler** | Generates candidate responses | Small |
| **Synthesis** | Synthesizes final answer | Large |
| **Transformer** | Extracts structured data | Large |
| **Image Generator** | Creates images/diagrams | Large |
| **Formatting** | Formats output | Small |
| **Summarization** | Summarizes content | Small |

### 3. Configuration (`config.py`)

Centralized configuration management:
- LLM provider selection (OpenAI, Anthropic, Ollama)
- Model configuration
- Image generation provider (DALL-E, Gemini)
- Knowledge base paths
- Server settings

### 4. Vector Store (`retrieval.py`)

Semantic search system:
- Document embedding and storage
- Multi-knowledge base support (legal, audit)
- Similarity search with reranking
- Embedding cache management

### 5. Workflow Storage (`workflows.py`)

Persistent workflow management:
- Save/load workflows as JSON
- User-based workflow isolation
- Workflow metadata tracking

### 6. Logging System (`workflow_logger.py`)

Comprehensive debugging:
- Color-coded console output
- Execution flow tracking
- Branch decision logging
- Context update monitoring

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# LLM Provider (openai, anthropic, ollama)
LLM_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
SMALL_MODEL=gpt-4o-mini
LARGE_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small

# Image Generation (dalle, gemini)
IMAGE_PROVIDER=gemini
GOOGLE_API_KEY=your-google-api-key

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Ollama (if using)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

### Model Configuration

The system supports multiple LLM providers:

**OpenAI:**
- Small: `gpt-4o-mini` (default)
- Large: `gpt-4o` (default)
- Embedding: `text-embedding-3-small`

**Anthropic:**
- Small: `claude-3-haiku-20240307`
- Large: `claude-3-5-sonnet-20241022`

**Ollama:**
- Small: `llama3.1:8b`
- Large: `llama3.1:8b`
- Embedding: `nomic-embed-text`

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Create .env file with your API keys
cp .env.example .env  # Edit with your keys

# Run the server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📊 How It Works

### Workflow Execution Flow

1. **User Input**: User provides a query and workflow graph
2. **Topological Sort**: System determines execution order
3. **Node Execution**: Each node executes in dependency order:
   - **Input Nodes**: Extract user data/files
   - **Supervisor**: Analyzes query and plans execution
   - **Orchestrator**: Decides which tools to use
   - **Tool Nodes**: Execute based on orchestrator selection
   - **Output Nodes**: Format and return results
4. **Branch Routing**: Nodes are excluded if their dependencies weren't executed
5. **Context Passing**: Results flow between connected nodes
6. **Final Output**: Formatted result returned to user

### Branch Routing Logic

The system intelligently routes execution:

- **Dependency Check**: Node only executes if dependencies completed
- **Orchestrator Selection**: Tool nodes check if orchestrator selected them
- **Path Exclusion**: If image_generator is selected, sampler path is excluded (and vice versa)
- **Context Updates**: Each agent updates shared context

### Example Workflow

```
[Prompt] → [Supervisor] → [Orchestrator]
                              ├─→ [Semantic Search] → [Sampler] → [Synthesis] → [Response]
                              └─→ [Image Generator] → [Response]
```

## 🎨 Frontend Components

### Node Types

**Input Nodes:**
- `prompt`: User query input
- `upload`: File upload (PDF, DOCX, TXT)

**Agent Nodes:**
- `supervisor`: Workflow planning
- `orchestrator`: Tool selection
- `semantic_search`: Document search
- `sampler`: Content sampling
- `synthesis`: Answer synthesis
- `transformer`: Data extraction
- `image_generator`: Image creation
- `formatting`: Output formatting
- `summarization`: Content summarization

**Output Nodes:**
- `response`: Text output
- `spreadsheet`: CSV/table output

### Workflow Management

- **Save Workflow**: Persist workflow to disk
- **Load Workflow**: Restore saved workflow
- **Delete Workflow**: Remove saved workflow
- **AI Assistant**: Generate workflows from natural language

## 📝 Recent Developments

### Comprehensive Logging System

Added detailed logging for debugging workflow execution:
- Color-coded console output
- Execution flow tracking
- Branch decision logging
- Context update monitoring
- Dependency status visualization

### Branch Routing Fixes

Fixed orchestrator tool detection:
- Now correctly identifies available tools by checking node types
- Properly routes execution based on orchestrator decisions
- Prevents conflicting paths from executing simultaneously

### Spreadsheet Output Enhancement

Improved spreadsheet output display:
- CSV parsing and table rendering
- Toggle between table and raw CSV view
- Better formatting and statistics

## 🔍 Debugging

### Logging

The system provides comprehensive logging:

```python
# Enable debug logging
# Logs are automatically output to console with colors:
# - DEBUG: Cyan
# - INFO: Green  
# - WARNING: Yellow
# - ERROR: Red
```

### Execution Flow

Watch the terminal for:
- Workflow topology (nodes, edges, execution order)
- Node evaluation and dependency checks
- Branch routing decisions
- Orchestrator tool selections
- Context updates
- Execution summary

## 📚 Knowledge Bases

The system supports multiple knowledge bases:

- **Legal**: EU regulations and legal documents
- **Audit**: Audit-related documents

Documents are stored in `backend/documents/{knowledge_base}/` and automatically indexed on startup.

## 🛠️ Development

### Adding a New Agent

1. Create `agents/your_agent.py`:
```python
from agents.base import BaseAgent, AgentResult

class YourAgent(BaseAgent):
    agent_id = "your_agent"
    display_name = "Your Agent"
    default_model = "small"  # or "large"
    
    async def execute(self, user_message, context, settings, model):
        # Your agent logic
        return AgentResult(...)
```

2. Register in `agents/__init__.py`
3. Add to `AGENT_REGISTRY` in `workflow_executor.py`

### Testing

```bash
# Backend
cd backend
python -m pytest  # If tests exist

# Frontend
cd frontend
npm test
```

## 📄 License

[Your License Here]

## 🤝 Contributing

[Contributing Guidelines]

## 📞 Support

[Support Information]

