"""
Workflow Builder LLM - AI assistant that helps users build workflows via chat.

This LLM understands the available node types and can suggest/build
workflows based on natural language descriptions.
"""

import json
from typing import Any, Dict, List, Optional

from config import config
from models import get_llm_client


# Node type definitions for the LLM
NODE_DEFINITIONS = """
Available Node Types:

INPUT NODES:
- prompt: Starting point for text-based workflows. User provides initial query or instructions.
- upload: Upload files (PDF, CSV, TXT) to be processed in the workflow.
- spreadsheet: Load or create structured data in spreadsheet format.

AGENT NODES:
- supervisor: Analyzes workflow graph, plans execution, identifies optimization opportunities. Settings: planningStyle (detailed/brief/optimized), optimizationLevel (none/basic/aggressive)
- orchestrator: Intelligently selects which tools to execute based on context. Settings: toolSelectionStrategy (conservative/balanced/aggressive), maxTools (1-10)
- semantic_search: Searches knowledge base using vector embeddings. Settings: topK (1-20), enableReranking (true/false)
- sampler: Generates multiple diverse candidate answers. Settings: numResponses (1-10)
- synthesis: Synthesizes final answer from multiple sources. Settings: maxWords (number)
- summarization: Summarizes long outputs to specified word limit. Settings: maxWords (number)
- formatting: Formats output to specific format. Settings: outputFormat (json/xml/markdown/html/csv/yaml)
- transformer: Transforms data between formats. Settings: fromFormat (string), toFormat (string)
- image_generator: Generates images from text descriptions. Settings: imageType (diagram/photo/artistic/cartoon/illustration)

OUTPUT NODES:
- response: Final output node that delivers the workflow result.

COMING SOON (don't include in workflows yet):
- web_search: Real-time web search
- aggregator: Combines outputs from multiple nodes
- conditional_branch: Routes based on conditions
- research: In-depth research agent
- router: Content-based routing
- planning: Detailed execution planning
"""

SYSTEM_PROMPT = f"""You are a Workflow Builder Assistant. You help users create AI agent workflows by understanding their needs and generating workflow configurations.

{NODE_DEFINITIONS}

When a user describes what they want to accomplish, analyze their requirements and:
1. Suggest an appropriate workflow with the right nodes
2. Explain why you chose those nodes
3. Provide the workflow configuration in JSON format

Workflow JSON format:
{{
    "name": "Workflow Name",
    "description": "What this workflow does",
    "nodes": [
        {{
            "id": "unique-id-1",
            "type": "workflow",
            "position": {{"x": 100, "y": 100}},
            "data": {{
                "nodeType": "prompt",
                "label": "Prompt",
                "settings": {{}}
            }}
        }}
    ],
    "edges": [
        {{
            "id": "edge-1",
            "source": "unique-id-1",
            "target": "unique-id-2"
        }}
    ]
}}

Guidelines:
- Always start with an input node (usually 'prompt')
- Connect nodes logically based on data flow
- End with a 'response' node for final output
- Position nodes from left to right (x increases) and top to bottom (y increases)
- Use appropriate spacing: x += 250 for each column, y += 150 for parallel nodes
- Include necessary intermediate agents (supervisor, orchestrator, semantic_search, etc.)
- Configure settings based on user requirements
- Keep workflows focused and efficient

Respond with:
1. A brief explanation of the workflow
2. The complete JSON configuration wrapped in ```json ... ```
"""


async def build_workflow_from_chat(
    user_message: str,
    conversation_history: List[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Use LLM to build a workflow based on user's natural language description.
    
    Args:
        user_message: User's description of what they want
        conversation_history: Previous messages for context
        
    Returns:
        Dict with 'explanation' and 'workflow' (the JSON config)
    """
    llm_client = get_llm_client()
    model = config.get_model_config()["large"]
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history)
    
    messages.append({"role": "user", "content": user_message})
    
    response = await llm_client.chat(
        model=model,
        messages=messages,
        temperature=0.3,
        max_tokens=2000,
    )
    
    # Parse the response to extract JSON
    explanation = response
    workflow = None
    
    if "```json" in response:
        try:
            json_start = response.index("```json") + 7
            json_end = response.index("```", json_start)
            json_str = response[json_start:json_end].strip()
            workflow = json.loads(json_str)
            explanation = response[:response.index("```json")].strip()
        except (ValueError, json.JSONDecodeError) as e:
            print(f"[WORKFLOW_BUILDER] Failed to parse workflow JSON: {e}")
    elif "```" in response:
        try:
            json_start = response.index("```") + 3
            json_end = response.index("```", json_start)
            json_str = response[json_start:json_end].strip()
            workflow = json.loads(json_str)
            explanation = response[:response.index("```")].strip()
        except (ValueError, json.JSONDecodeError) as e:
            print(f"[WORKFLOW_BUILDER] Failed to parse workflow JSON: {e}")
    
    return {
        "explanation": explanation,
        "workflow": workflow,
        "raw_response": response,
    }


async def suggest_workflow_improvements(
    current_workflow: Dict[str, Any],
    user_feedback: str = None,
) -> Dict[str, Any]:
    """
    Analyze a workflow and suggest improvements.
    
    Args:
        current_workflow: The current workflow configuration
        user_feedback: Optional user feedback about issues
        
    Returns:
        Dict with 'suggestions' and optionally 'improved_workflow'
    """
    llm_client = get_llm_client()
    model = config.get_model_config()["large"]
    
    workflow_json = json.dumps(current_workflow, indent=2)
    
    prompt = f"""Analyze this workflow and suggest improvements:

```json
{workflow_json}
```

{"User feedback: " + user_feedback if user_feedback else ""}

Provide:
1. Analysis of the current workflow (strengths and weaknesses)
2. Specific suggestions for improvement
3. If there are significant improvements, provide an updated workflow JSON

Consider:
- Are all necessary agents included?
- Is the node order optimal?
- Are there missing connections?
- Are the settings appropriate?
- Could performance be improved?
"""
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    
    response = await llm_client.chat(
        model=model,
        messages=messages,
        temperature=0.3,
        max_tokens=2000,
    )
    
    # Parse response similar to build_workflow_from_chat
    suggestions = response
    improved_workflow = None
    
    if "```json" in response:
        try:
            json_start = response.index("```json") + 7
            json_end = response.index("```", json_start)
            json_str = response[json_start:json_end].strip()
            improved_workflow = json.loads(json_str)
            suggestions = response[:response.index("```json")].strip()
        except (ValueError, json.JSONDecodeError):
            pass
    
    return {
        "suggestions": suggestions,
        "improved_workflow": improved_workflow,
        "raw_response": response,
    }


# Example workflows for common use cases
EXAMPLE_WORKFLOWS = {
    "basic_qa": {
        "name": "Basic Q&A",
        "description": "Simple question answering with semantic search",
        "nodes": [
            {"id": "prompt-1", "type": "workflow", "position": {"x": 50, "y": 200},
             "data": {"nodeType": "prompt", "label": "Prompt", "settings": {}}},
            {"id": "semantic_search-1", "type": "workflow", "position": {"x": 300, "y": 200},
             "data": {"nodeType": "semantic_search", "label": "Semantic Search", "settings": {"topK": 5, "enableReranking": True}}},
            {"id": "synthesis-1", "type": "workflow", "position": {"x": 550, "y": 200},
             "data": {"nodeType": "synthesis", "label": "Synthesis Agent", "settings": {"maxWords": 300}}},
            {"id": "response-1", "type": "workflow", "position": {"x": 800, "y": 200},
             "data": {"nodeType": "response", "label": "Response", "settings": {}}},
        ],
        "edges": [
            {"id": "e1", "source": "prompt-1", "target": "semantic_search-1"},
            {"id": "e2", "source": "semantic_search-1", "target": "synthesis-1"},
            {"id": "e3", "source": "synthesis-1", "target": "response-1"},
        ],
    },
    "advanced_research": {
        "name": "Advanced Research",
        "description": "Full multi-agent pipeline with sampling and optimization",
        "nodes": [
            {"id": "prompt-1", "type": "workflow", "position": {"x": 50, "y": 200},
             "data": {"nodeType": "prompt", "label": "Prompt", "settings": {}}},
            {"id": "supervisor-1", "type": "workflow", "position": {"x": 300, "y": 100},
             "data": {"nodeType": "supervisor", "label": "Supervisor Agent", "settings": {"planningStyle": "optimized", "optimizationLevel": "basic"}}},
            {"id": "semantic_search-1", "type": "workflow", "position": {"x": 300, "y": 300},
             "data": {"nodeType": "semantic_search", "label": "Semantic Search", "settings": {"topK": 5, "enableReranking": True}}},
            {"id": "orchestrator-1", "type": "workflow", "position": {"x": 550, "y": 200},
             "data": {"nodeType": "orchestrator", "label": "Tool Orchestrator", "settings": {"toolSelectionStrategy": "balanced", "maxTools": 3}}},
            {"id": "sampler-1", "type": "workflow", "position": {"x": 800, "y": 200},
             "data": {"nodeType": "sampler", "label": "Verbalized Sampling", "settings": {"numResponses": 5}}},
            {"id": "synthesis-1", "type": "workflow", "position": {"x": 1050, "y": 200},
             "data": {"nodeType": "synthesis", "label": "Synthesis Agent", "settings": {"maxWords": 500}}},
            {"id": "response-1", "type": "workflow", "position": {"x": 1300, "y": 200},
             "data": {"nodeType": "response", "label": "Response", "settings": {}}},
        ],
        "edges": [
            {"id": "e1", "source": "prompt-1", "target": "supervisor-1"},
            {"id": "e2", "source": "prompt-1", "target": "semantic_search-1"},
            {"id": "e3", "source": "supervisor-1", "target": "orchestrator-1"},
            {"id": "e4", "source": "semantic_search-1", "target": "orchestrator-1"},
            {"id": "e5", "source": "orchestrator-1", "target": "sampler-1"},
            {"id": "e6", "source": "sampler-1", "target": "synthesis-1"},
            {"id": "e7", "source": "synthesis-1", "target": "response-1"},
        ],
    },
    "summarization": {
        "name": "Document Summarization",
        "description": "Summarize content with configurable length",
        "nodes": [
            {"id": "prompt-1", "type": "workflow", "position": {"x": 50, "y": 200},
             "data": {"nodeType": "prompt", "label": "Prompt", "settings": {}}},
            {"id": "semantic_search-1", "type": "workflow", "position": {"x": 300, "y": 200},
             "data": {"nodeType": "semantic_search", "label": "Semantic Search", "settings": {"topK": 3}}},
            {"id": "summarization-1", "type": "workflow", "position": {"x": 550, "y": 200},
             "data": {"nodeType": "summarization", "label": "Summarization Agent", "settings": {"maxWords": 100}}},
            {"id": "response-1", "type": "workflow", "position": {"x": 800, "y": 200},
             "data": {"nodeType": "response", "label": "Response", "settings": {}}},
        ],
        "edges": [
            {"id": "e1", "source": "prompt-1", "target": "semantic_search-1"},
            {"id": "e2", "source": "semantic_search-1", "target": "summarization-1"},
            {"id": "e3", "source": "summarization-1", "target": "response-1"},
        ],
    },
}


def get_example_workflow(workflow_type: str) -> Optional[Dict[str, Any]]:
    """Get an example workflow by type."""
    return EXAMPLE_WORKFLOWS.get(workflow_type)


def list_example_workflows() -> List[Dict[str, str]]:
    """List available example workflows."""
    return [
        {"id": key, "name": val["name"], "description": val["description"]}
        for key, val in EXAMPLE_WORKFLOWS.items()
    ]

