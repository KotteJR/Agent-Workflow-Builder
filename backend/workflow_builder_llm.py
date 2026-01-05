"""
Workflow Builder LLM - AI assistant that helps users build workflows via chat.

This LLM understands the available node types and can suggest/build
workflows based on natural language descriptions.
"""

import json
import re
from typing import Any, Dict, List, Optional

from config import config
from models import get_llm_client


# Node type definitions for the LLM
NODE_DEFINITIONS = """
Available Node Types:

INPUT NODES (always start workflows with one of these):
- prompt: Starting point for text-based workflows. User provides initial query or instructions. Has inline text editor.
- upload: Upload files (PDF, CSV, TXT, MD, DOC, DOCX) to be processed. Has inline file upload interface.

AGENT NODES:
- supervisor: CRITICAL - Analyzes workflow graph structure, understands downstream nodes, plans execution, identifies optimization opportunities. ALWAYS include this node in workflows. Settings: planningStyle (detailed/brief/optimized), optimizationLevel (none/basic/aggressive), supervisorPrompt (optional custom instructions string)
- orchestrator: Intelligently selects which tools to execute based on context and query requirements. Settings: toolSelectionStrategy (conservative/balanced/aggressive), maxTools (1-10)
- semantic_search: Performs semantic search across knowledge base using vector embeddings. Finds relevant documents based on meaning. Settings: topK (1-20), enableReranking (true/false)
- sampler: Generates multiple diverse candidate answers by exploring different reasoning paths. Settings: numResponses (1-10)
- synthesis: Synthesizes information from multiple sources, candidates, and tool outputs into coherent final answer. Settings: maxWords (number)
- summarization: Summarizes long outputs, extracts key points, creates executive summaries. Settings: maxWords (number)
- formatting: Formats outputs to specific format. Settings: outputFormat (json/xml/markdown/html/csv/yaml)
- transformer: Transforms data from one format to another (e.g., PDF to Excel, JSON to XML). Settings: fromFormat (string), toFormat (string)
- image_generator: Generates images from text descriptions. Settings: imageType (diagram/photo/artistic/cartoon/illustration)

OUTPUT NODES (always end workflows with one of these):
- response: Final output node that delivers the workflow result as text/structured data.
- spreadsheet: Output structured data in spreadsheet/Excel format. Use this when user wants Excel/CSV output.

COMING SOON (do NOT include in workflows):
- web_search: Real-time web search (not available yet)
- aggregator: Combines outputs from multiple nodes (not available yet)
- conditional_branch: Routes based on conditions (not available yet)
- research: In-depth research agent (not available yet)
- router: Content-based routing (not available yet)
- planning: Detailed execution planning (not available yet)
"""

SYSTEM_PROMPT = f"""You are a Workflow Builder Assistant. You help users create AI agent workflows by understanding their needs and generating workflow configurations.

{NODE_DEFINITIONS}

CRITICAL REQUIREMENTS:
1. ALWAYS start with the appropriate input node:
   - Use 'upload' node if user mentions uploading files, PDFs, documents, or file processing
   - Use 'prompt' node for text-based queries without file uploads
   - DO NOT use both - choose the most appropriate one based on user's request
2. ALWAYS include a 'supervisor' agent node early in the workflow (after input, before processing)
   - The supervisor analyzes the query/context and provides execution guidance
   - Users can add additional instructions via supervisorPrompt setting if needed
3. ALWAYS end with an appropriate output node:
   - Use 'spreadsheet' if user wants Excel/CSV/structured data output
   - Use 'response' for text/other outputs
4. Connect nodes logically: input -> supervisor -> processing agents -> output

When a user describes what they want to accomplish, analyze their requirements and:
1. Suggest an appropriate workflow with the right nodes
2. Explain why you chose those nodes in clear, natural language (NO markdown formatting like ** or ---)
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
                "settings": {{}},
                "promptText": ""
            }}
        }},
        {{
            "id": "unique-id-2",
            "type": "workflow",
            "position": {{"x": 350, "y": 100}},
            "data": {{
                "nodeType": "supervisor",
                "label": "Supervisor Agent",
                "settings": {{
                    "planningStyle": "optimized",
                    "optimizationLevel": "basic",
                    "supervisorPrompt": ""
                }}
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
- ALWAYS start with 'prompt' node (required)
- ALWAYS include 'supervisor' agent after input (required)
- Connect nodes logically: prompt -> supervisor -> processing -> output
- Position nodes from left to right (x increases): start at x=100, increment by 250 for each column
- Use y=100 for single-row workflows, adjust y for parallel branches
- Include necessary intermediate agents based on requirements:
  * Use 'upload' if user wants to upload files
  * Use 'transformer' if format conversion is needed (e.g., PDF to Excel)
  * Use 'semantic_search' if knowledge base search is needed
  * Use 'orchestrator' for complex tool selection
  * Use 'sampler' + 'synthesis' for high-quality answers
- Configure settings appropriately
- Use 'spreadsheet' output for Excel/CSV/structured data needs
- Keep workflows focused and efficient

Response Format:
- Write explanation in plain, natural language
- NO markdown formatting (no **, ---, #, etc.)
- NO code blocks in explanation
- Just clear, readable text explaining the workflow
- Then provide JSON in ```json code block
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
    
    # Extract JSON from response
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
    
    # Clean up explanation: remove markdown formatting
    if explanation:
        # Remove markdown headers
        import re
        explanation = re.sub(r'^#{1,6}\s+', '', explanation, flags=re.MULTILINE)
        # Remove bold/italic
        explanation = re.sub(r'\*\*([^*]+)\*\*', r'\1', explanation)
        explanation = re.sub(r'\*([^*]+)\*', r'\1', explanation)
        # Remove horizontal rules
        explanation = re.sub(r'^---+$', '', explanation, flags=re.MULTILINE)
        # Remove code blocks
        explanation = re.sub(r'```[a-z]*\n.*?```', '', explanation, flags=re.DOTALL)
        # Clean up extra whitespace
        explanation = re.sub(r'\n{3,}', '\n\n', explanation)
        explanation = explanation.strip()
    
    # Ensure workflow always includes supervisor and appropriate input node
    if workflow and workflow.get("nodes"):
        node_types = [node.get("data", {}).get("nodeType") for node in workflow["nodes"]]
        
        # Detect if user wants file uploads
        user_message_lower = user_message.lower()
        has_upload_keywords = any(keyword in user_message_lower for keyword in [
            "upload", "file", "pdf", "document", "csv", "excel", "spreadsheet", 
            "convert pdf", "pdf to", "document to", "file to"
        ])
        
        # Determine which input node to use
        needs_upload = has_upload_keywords and "upload" not in node_types
        needs_prompt = not has_upload_keywords and "prompt" not in node_types and "upload" not in node_types
        
        # Add upload node if needed (for file processing workflows)
        if needs_upload:
            upload_node = {
                "id": "upload-1",
                "type": "workflow",
                "position": {"x": 100, "y": 100},
                "data": {
                    "nodeType": "upload",
                    "label": "Upload",
                    "settings": {},
                    "uploadedFiles": []
                }
            }
            workflow["nodes"].insert(0, upload_node)
            # Update first edge source if edges exist
            if workflow.get("edges"):
                workflow["edges"][0]["source"] = "upload-1"
        
        # Add prompt node if needed (for text-based workflows)
        elif needs_prompt:
            prompt_node = {
                "id": "prompt-1",
                "type": "workflow",
                "position": {"x": 100, "y": 100},
                "data": {
                    "nodeType": "prompt",
                    "label": "Prompt",
                    "settings": {},
                    "promptText": ""
                }
            }
            workflow["nodes"].insert(0, prompt_node)
            # Update first edge source if edges exist
            if workflow.get("edges"):
                workflow["edges"][0]["source"] = "prompt-1"
        
        # Add supervisor node if missing (after input node)
        if "supervisor" not in node_types:
            supervisor_node = {
                "id": "supervisor-1",
                "type": "workflow",
                "position": {"x": 350, "y": 100},
                "data": {
                    "nodeType": "supervisor",
                    "label": "Supervisor Agent",
                    "settings": {
                        "planningStyle": "optimized",
                        "optimizationLevel": "basic",
                        "supervisorPrompt": ""
                    }
                }
            }
            # Insert after input node (prompt or upload)
            input_idx = next((i for i, n in enumerate(workflow["nodes"]) 
                            if n.get("data", {}).get("nodeType") in ["prompt", "upload"]), 0)
            workflow["nodes"].insert(input_idx + 1, supervisor_node)
            
            # Update edges to connect input -> supervisor -> next node
            if workflow.get("edges"):
                first_edge = workflow["edges"][0]
                old_source = first_edge["source"]
                first_edge["source"] = "supervisor-1"
                # Add edge from input to supervisor
                input_node_id = workflow["nodes"][input_idx]["id"]
                workflow["edges"].insert(0, {
                    "id": f"edge-input-supervisor",
                    "source": input_node_id,
                    "target": "supervisor-1"
                })
    
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

