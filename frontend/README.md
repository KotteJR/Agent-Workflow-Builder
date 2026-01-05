# Workflow Builder - Standalone

A standalone frontend project for building and visualizing AI workflows using React Flow.

## Features

- 🎨 **Light Theme** - Clean, modern light theme interface
- 🎯 **React Flow Canvas** - Interactive workflow canvas as the main page
- 📦 **Component Library** - Drag-and-drop components in the left sidebar
- ⚙️ **Properties Panel** - Right sidebar for node properties (ready for future features)
- 💬 **Chat Input** - Placeholder for chat functionality at the bottom

## Getting Started

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
app/
  ├── page.tsx          # Main workflow builder page
  ├── layout.tsx        # Root layout
  └── globals.css       # Global styles with light theme
```

## Features Overview

### Left Sidebar
- Component library with draggable workflow nodes
- Shows which components have been added to the canvas

### Main Canvas
- React Flow canvas for building workflows
- Drag nodes from the sidebar onto the canvas
- Connect nodes by dragging from source to target handles
- Delete nodes and edges with hover actions

### Right Sidebar
- Properties panel (ready for future node property editing)

### Chat Input
- Placeholder input at the bottom
- Ready for future chat functionality integration

## Available Components

- **Query** - Input node
- **Supervisor Agent** - Orchestration agent
- **Semantic Search** - Search tool
- **Tool Orchestrator** - Tool selection agent
- **Web Search** - Web search tool
- **Code Interpreter** - Code execution tool
- **Image Generator** - Image generation tool
- **Verbalized Sampling** - Sampling agent
- **Synthesis Agent** - Final synthesis agent
- **Response** - Output node

## Next Steps

- Backend integration (when ready)
- Chat functionality implementation
- Node property editing
- Workflow save/load functionality
- Execution and visualization
