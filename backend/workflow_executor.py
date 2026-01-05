"""
Graph-Based Workflow Executor

Executes user-defined workflows respecting graph topology.
Only executes nodes that are reachable from input nodes,
following strict dependency order using topological sort.
"""

import json
import time
from collections import deque
from typing import Any, AsyncGenerator, Dict, List, Optional, Set, Tuple

from config import config
from models import get_llm_client, LLMClientProtocol
from agents.base import AgentResult
from agents.supervisor import SupervisorAgent
from agents.orchestrator import OrchestratorAgent
from agents.semantic_search import SemanticSearchAgent
from agents.sampler import SamplerAgent
from agents.synthesis import SynthesisAgent
from agents.summarization import SummarizationAgent
from agents.formatting import FormattingAgent
from agents.transformer import TransformerAgent
from agents.image_generator import ImageGeneratorAgent
import retrieval


# Agent registry - maps node types to agent classes
AGENT_REGISTRY = {
    "supervisor": SupervisorAgent,
    "orchestrator": OrchestratorAgent,
    "semantic_search": SemanticSearchAgent,
    "sampler": SamplerAgent,
    "synthesis": SynthesisAgent,
    "summarization": SummarizationAgent,
    "formatting": FormattingAgent,
    "transformer": TransformerAgent,
    "image_generator": ImageGeneratorAgent,
}

# Input node types (don't require agents)
INPUT_NODE_TYPES = {"prompt", "upload", "spreadsheet"}

# Output node types (don't require agents)
OUTPUT_NODE_TYPES = {"response"}


def topological_sort(nodes: List[str], edges: List[Dict[str, str]]) -> List[str]:
    """
    Topologically sort nodes based on edges.
    Returns nodes in execution order (dependencies first).
    """
    # Build in-degree count
    in_degree: Dict[str, int] = {node: 0 for node in nodes}
    adjacency: Dict[str, List[str]] = {node: [] for node in nodes}
    
    for edge in edges:
        source = edge["source"]
        target = edge["target"]
        if source in nodes and target in nodes:
            adjacency[source].append(target)
            in_degree[target] = in_degree.get(target, 0) + 1
    
    # Kahn's algorithm
    queue = deque([node for node in nodes if in_degree[node] == 0])
    result = []
    
    while queue:
        node = queue.popleft()
        result.append(node)
        
        for neighbor in adjacency.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # Add any remaining nodes (cycles or disconnected)
    remaining = [node for node in nodes if node not in result]
    result.extend(remaining)
    
    return result


def find_reachable_nodes(
    start_nodes: Set[str],
    edges: List[Dict[str, str]],
    all_nodes: Set[str],
) -> Set[str]:
    """
    Find all nodes reachable from start nodes via BFS.
    This ensures only connected nodes are executed.
    """
    # Build adjacency list (forward direction)
    adjacency: Dict[str, Set[str]] = {node: set() for node in all_nodes}
    for edge in edges:
        if edge["source"] in all_nodes and edge["target"] in all_nodes:
            adjacency[edge["source"]].add(edge["target"])
    
    # BFS from start nodes
    reachable = set(start_nodes)
    queue = deque(start_nodes)
    
    while queue:
        node = queue.popleft()
        for neighbor in adjacency.get(node, set()):
            if neighbor not in reachable:
                reachable.add(neighbor)
                queue.append(neighbor)
    
    return reachable


def get_node_dependencies(node_id: str, edges: List[Dict[str, str]]) -> List[str]:
    """Get all nodes that must execute before this node."""
    return [edge["source"] for edge in edges if edge["target"] == node_id]


def _sse_event(event_type: str, data: Dict[str, Any]) -> str:
    """Format a Server-Sent Event."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


async def execute_workflow(
    user_message: str,
    workflow_nodes: List[Dict[str, Any]],
    workflow_edges: List[Dict[str, str]],
) -> AsyncGenerator[str, None]:
    """
    Execute a custom workflow defined by nodes and edges.
    
    Respects graph topology:
    - Only executes nodes reachable from input nodes
    - Follows topological order (dependencies first)
    - Passes context between connected nodes
    
    Args:
        user_message: User's query
        workflow_nodes: List of node configurations
        workflow_edges: List of edges defining connections
        
    Yields:
        SSE events for workflow execution
    """
    workflow_start = time.time()
    steps: List[Dict[str, Any]] = []
    
    # Get LLM client and models
    llm_client = get_llm_client()
    small_model = config.get_model_config()["small"]
    large_model = config.get_model_config()["large"]
    
    # Extract node IDs and types
    node_map = {node["id"]: node for node in workflow_nodes}
    all_node_ids = set(node_map.keys())
    
    # Find input nodes (nodes with no incoming edges or input types)
    nodes_with_incoming = {edge["target"] for edge in workflow_edges}
    input_nodes = set()
    
    for node_id, node in node_map.items():
        node_type = node.get("data", {}).get("nodeType", node_id.split("-")[0])
        if node_type in INPUT_NODE_TYPES or node_id not in nodes_with_incoming:
            input_nodes.add(node_id)
    
    # Find all nodes reachable from inputs
    reachable_nodes = find_reachable_nodes(input_nodes, workflow_edges, all_node_ids)
    
    # Filter edges to only include reachable nodes
    valid_edges = [
        edge for edge in workflow_edges
        if edge["source"] in reachable_nodes and edge["target"] in reachable_nodes
    ]
    
    # Topologically sort reachable nodes
    execution_order = topological_sort(list(reachable_nodes), valid_edges)
    
    print(f"[WORKFLOW] Input nodes: {input_nodes}")
    print(f"[WORKFLOW] Reachable nodes: {reachable_nodes}")
    print(f"[WORKFLOW] Execution order: {execution_order}")
    
    # Execution context - shared state between nodes
    context: Dict[str, Any] = {
        "user_message": user_message,
        "context_snippets": [],
        "candidates": [],
        "semantic_results": [],
        "docs": [],
        "tool_outputs": {
            "images": [],
            "calculations": [],
            "web_results": [],
        },
        "orchestrator_result": {"tools_to_execute": []},
        "final_answer": "",
    }
    
    # Track executed and excluded nodes
    executed_nodes: Set[str] = set()
    excluded_nodes: Set[str] = set()
    
    try:
        for node_id in execution_order:
            node = node_map.get(node_id)
            if not node:
                continue
            
            node_data = node.get("data", {})
            node_type = node_data.get("nodeType", node_id.split("-")[0])
            node_settings = node_data.get("settings", {})
            
            # Skip input/output nodes (they don't have agents)
            if node_type in INPUT_NODE_TYPES:
                executed_nodes.add(node_id)
                yield _sse_event("agent_complete", {
                    "agent": node_id,
                    "step": {
                        "agent": node_type,
                        "model": "none",
                        "action": "input",
                        "content": user_message,
                    }
                })
                continue
            
            if node_type in OUTPUT_NODE_TYPES:
                executed_nodes.add(node_id)
                yield _sse_event("agent_complete", {
                    "agent": node_id,
                    "step": {
                        "agent": node_type,
                        "model": "none",
                        "action": "output",
                        "content": context.get("final_answer", ""),
                    }
                })
                continue
            
            # Check dependencies
            dependencies = get_node_dependencies(node_id, valid_edges)
            missing_deps = [
                dep for dep in dependencies
                if dep not in executed_nodes and dep not in excluded_nodes
            ]
            
            if missing_deps:
                print(f"[WORKFLOW] Skipping {node_id}: missing dependencies {missing_deps}")
                continue
            
            # Special handling for tool nodes connected to orchestrator
            should_execute = True
            if node_type == "image_generator":
                # Check if orchestrator decided to use this tool
                tools_to_execute = context.get("orchestrator_result", {}).get("tools_to_execute", [])
                is_connected_to_orchestrator = any(
                    edge["source"].startswith("orchestrator") and edge["target"] == node_id
                    for edge in valid_edges
                )
                if is_connected_to_orchestrator and "image_generator" not in tools_to_execute:
                    should_execute = False
                    excluded_nodes.add(node_id)
                    yield _sse_event("agent_complete", {
                        "agent": node_id,
                        "step": {
                            "agent": node_type,
                            "model": "none",
                            "action": "exclude",
                            "content": "Excluded (not selected by orchestrator)",
                            "excluded": True,
                        }
                    })
                    continue
            
            # Skip sampler if images were generated
            if node_type == "sampler":
                if context.get("tool_outputs", {}).get("images"):
                    should_execute = False
                    excluded_nodes.add(node_id)
                    context["candidates"] = []
                    yield _sse_event("agent_complete", {
                        "agent": node_id,
                        "step": {
                            "agent": node_type,
                            "model": small_model,
                            "action": "exclude",
                            "content": "Excluded (image generation request)",
                            "excluded": True,
                        }
                    })
                    continue
            
            if not should_execute:
                continue
            
            # Execute the agent
            yield _sse_event("agent_start", {"agent": node_id, "status": "working"})
            
            result = await _execute_agent(
                node_type=node_type,
                user_message=user_message,
                context=context,
                settings=node_settings,
                llm_client=llm_client,
                small_model=small_model,
                large_model=large_model,
                valid_edges=valid_edges,
                reachable_nodes=reachable_nodes,
            )
            
            if result:
                # Update context with agent's results
                for key, value in result.context_updates.items():
                    if key == "context_snippets":
                        context["context_snippets"].extend(value)
                    elif key == "images":
                        context["tool_outputs"]["images"].extend(value)
                    elif key == "docs":
                        context["docs"].extend(value)
                    else:
                        context[key] = value
                
                # Record step
                step = {
                    "agent": result.agent,
                    "model": result.model,
                    "action": result.action,
                    "content": result.content,
                    **result.metadata,
                }
                steps.append(step)
                executed_nodes.add(node_id)
                
                yield _sse_event("agent_complete", {"agent": node_id, "step": step})
            else:
                executed_nodes.add(node_id)
                yield _sse_event("agent_complete", {
                    "agent": node_id,
                    "step": {
                        "agent": node_type,
                        "model": "none",
                        "action": "skip",
                        "content": "Skipped",
                    }
                })
        
        # Determine final answer
        final_answer = context.get("final_answer", "")
        if not final_answer and context.get("context_snippets"):
            final_answer = "\n\n".join(context["context_snippets"])
        if not final_answer:
            final_answer = "No output generated."
        
        # Calculate metrics
        workflow_latency = round((time.time() - workflow_start) * 1000, 2)
        
        # Prepare final tool outputs
        final_tool_outputs = {
            "images": [
                {
                    "prompt": img.get("prompt"),
                    "style": img.get("style"),
                    "url": img.get("url"),
                    "has_data": bool(img.get("url")),
                }
                for img in context["tool_outputs"].get("images", [])
            ],
            "calculations": context["tool_outputs"].get("calculations", []),
            "web_results": context["tool_outputs"].get("web_results", []),
            "docs": context.get("docs", []),
        }
        
        yield _sse_event("done", {
            "answer": final_answer,
            "tool_outputs": final_tool_outputs,
            "trace": {"steps": steps},
            "latency_ms": workflow_latency,
        })
        
    except Exception as exc:
        import traceback
        print(f"[WORKFLOW] ERROR: {exc}")
        traceback.print_exc()
        yield _sse_event("error", {"message": str(exc)})


async def _execute_agent(
    node_type: str,
    user_message: str,
    context: Dict[str, Any],
    settings: Dict[str, Any],
    llm_client: LLMClientProtocol,
    small_model: str,
    large_model: str,
    valid_edges: List[Dict[str, str]],
    reachable_nodes: Set[str],
) -> Optional[AgentResult]:
    """
    Execute a single agent based on node type.
    
    Args:
        node_type: Type of node to execute
        user_message: Original user query
        context: Shared execution context
        settings: Node-specific settings
        llm_client: LLM client for completions
        small_model: Small model name
        large_model: Large model name
        valid_edges: Valid workflow edges
        reachable_nodes: Set of reachable node IDs
        
    Returns:
        AgentResult or None if agent not found
    """
    # Get agent class from registry
    agent_class = AGENT_REGISTRY.get(node_type)
    
    if not agent_class:
        print(f"[WORKFLOW] Unknown agent type: {node_type}")
        return None
    
    # Create agent instance
    if node_type == "semantic_search":
        agent = agent_class(llm_client, retrieval)
    else:
        agent = agent_class(llm_client)
    
    # Determine which model to use
    if agent.default_model == "large":
        model = large_model
    elif agent.default_model == "embedding":
        model = None  # Semantic search uses embeddings
    else:
        model = small_model
    
    # Add downstream nodes to context for supervisor
    if node_type == "supervisor":
        context["downstream_nodes"] = list(reachable_nodes)
    
    # Add available tools to context for orchestrator
    if node_type == "orchestrator":
        available_tools = []
        for node_id in reachable_nodes:
            if "image_generator" in node_id:
                available_tools.append("image_generator")
            elif "web_search" in node_id:
                available_tools.append("web_search")
        context["available_tools"] = available_tools
    
    # Execute agent
    result = await agent.execute(
        user_message=user_message,
        context=context,
        settings=settings,
        model=model,
    )
    
    return result

