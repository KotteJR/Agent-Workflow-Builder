"""
Comprehensive Workflow Logging System

Provides detailed logging for debugging workflow execution,
especially branch routing and node selection issues.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from functools import wraps

# Configure the workflow logger
workflow_logger = logging.getLogger("workflow")
workflow_logger.setLevel(logging.DEBUG)

# Create console handler with formatting
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class WorkflowFormatter(logging.Formatter):
    """Custom formatter with colors and structured output."""
    
    LEVEL_COLORS = {
        logging.DEBUG: Colors.CYAN,
        logging.INFO: Colors.GREEN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
    }
    
    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, Colors.END)
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Format the message
        formatted = f"{color}[{timestamp}] [{record.levelname:7}] {record.getMessage()}{Colors.END}"
        return formatted


console_handler.setFormatter(WorkflowFormatter())
workflow_logger.addHandler(console_handler)

# Prevent propagation to root logger
workflow_logger.propagate = False


class WorkflowDebugger:
    """
    Centralized workflow debugging utility.
    
    Provides structured logging for:
    - Workflow initialization
    - Node execution flow
    - Branch routing decisions
    - Context updates
    - Agent outputs
    """
    
    def __init__(self):
        self.execution_id = None
        self.node_execution_log: List[Dict] = []
        self.branch_decisions: List[Dict] = []
        self.context_snapshots: List[Dict] = []
        
    def start_execution(self, execution_id: str):
        """Mark the start of a new workflow execution."""
        self.execution_id = execution_id
        self.node_execution_log = []
        self.branch_decisions = []
        self.context_snapshots = []
        self._log_header(f"WORKFLOW EXECUTION STARTED: {execution_id}")
        
    def _log_header(self, message: str):
        """Log a prominent header."""
        border = "=" * 70
        workflow_logger.info(f"\n{Colors.BOLD}{Colors.HEADER}{border}")
        workflow_logger.info(f"{message}")
        workflow_logger.info(f"{border}{Colors.END}\n")
        
    def _log_section(self, title: str):
        """Log a section header."""
        workflow_logger.info(f"\n{Colors.BOLD}{Colors.BLUE}--- {title} ---{Colors.END}")
        
    def log_workflow_setup(
        self,
        input_nodes: Set[str],
        reachable_nodes: Set[str],
        execution_order: List[str],
        edges: List[Dict[str, str]],
    ):
        """Log the initial workflow setup."""
        self._log_section("WORKFLOW TOPOLOGY")
        
        workflow_logger.info(f"Input nodes: {sorted(input_nodes)}")
        workflow_logger.info(f"Reachable nodes: {sorted(reachable_nodes)}")
        workflow_logger.info(f"Execution order: {execution_order}")
        
        # Log edge connections
        workflow_logger.debug("Edge connections:")
        for edge in edges:
            workflow_logger.debug(f"  {edge['source']} --> {edge['target']}")
            
    def log_node_start(self, node_id: str, node_type: str, dependencies: List[str]):
        """Log when a node is about to be evaluated."""
        self._log_section(f"EVALUATING NODE: {node_id}")
        workflow_logger.info(f"Node type: {node_type}")
        workflow_logger.info(f"Dependencies: {dependencies}")
        
    def log_dependency_check(
        self,
        node_id: str,
        dependencies: List[str],
        executed_nodes: Set[str],
        excluded_nodes: Set[str],
    ):
        """Log dependency status for a node."""
        workflow_logger.debug(f"Dependency check for {node_id}:")
        for dep in dependencies:
            in_executed = dep in executed_nodes
            in_excluded = dep in excluded_nodes
            status = "EXECUTED" if in_executed else ("EXCLUDED" if in_excluded else "PENDING")
            color = Colors.GREEN if in_executed else (Colors.YELLOW if in_excluded else Colors.RED)
            workflow_logger.debug(f"  {color}  {dep}: {status}{Colors.END}")
            
    def log_branch_decision(
        self,
        node_id: str,
        node_type: str,
        decision: str,
        reason: str,
        context_data: Optional[Dict] = None,
    ):
        """Log a branch routing decision."""
        decision_entry = {
            "node_id": node_id,
            "node_type": node_type,
            "decision": decision,
            "reason": reason,
            "context": context_data,
        }
        self.branch_decisions.append(decision_entry)
        
        color = Colors.GREEN if decision == "EXECUTE" else Colors.YELLOW
        workflow_logger.info(f"{color}BRANCH DECISION for {node_id}: {decision}{Colors.END}")
        workflow_logger.info(f"  Reason: {reason}")
        
        if context_data:
            workflow_logger.debug(f"  Context data: {json.dumps(context_data, indent=2, default=str)[:500]}")
            
    def log_orchestrator_decision(
        self,
        tools_selected: List[str],
        available_tools: List[str],
        reasoning: str,
    ):
        """Log orchestrator tool selection."""
        self._log_section("ORCHESTRATOR DECISION")
        workflow_logger.info(f"Available tools: {available_tools}")
        workflow_logger.info(f"{Colors.BOLD}Selected tools: {tools_selected}{Colors.END}")
        workflow_logger.info(f"Reasoning: {reasoning}")
        
        if tools_selected:
            workflow_logger.warning(f"⚠️  Orchestrator selected path: {tools_selected}")
            workflow_logger.warning(f"   Other paths should be EXCLUDED!")
        else:
            workflow_logger.info("No specific tools selected - default path will be used")
            
    def log_node_execution(
        self,
        node_id: str,
        node_type: str,
        action: str,
        result_preview: str,
    ):
        """Log successful node execution."""
        entry = {
            "node_id": node_id,
            "node_type": node_type,
            "action": action,
            "result_preview": result_preview[:200],
        }
        self.node_execution_log.append(entry)
        
        workflow_logger.info(f"{Colors.GREEN}✓ EXECUTED: {node_id} ({node_type}){Colors.END}")
        workflow_logger.debug(f"  Action: {action}")
        workflow_logger.debug(f"  Result: {result_preview[:200]}...")
        
    def log_node_excluded(self, node_id: str, node_type: str, reason: str):
        """Log when a node is excluded from execution."""
        entry = {
            "node_id": node_id,
            "node_type": node_type,
            "action": "excluded",
            "reason": reason,
        }
        self.node_execution_log.append(entry)
        
        workflow_logger.warning(f"{Colors.YELLOW}✗ EXCLUDED: {node_id} ({node_type}){Colors.END}")
        workflow_logger.warning(f"  Reason: {reason}")
        
    def log_node_skipped(self, node_id: str, reason: str):
        """Log when a node is skipped."""
        workflow_logger.info(f"{Colors.CYAN}⊘ SKIPPED: {node_id}{Colors.END}")
        workflow_logger.info(f"  Reason: {reason}")
        
    def log_context_update(self, key: str, value: Any, node_id: str):
        """Log context updates."""
        value_preview = str(value)[:200] if not isinstance(value, (list, dict)) else json.dumps(value, default=str)[:200]
        workflow_logger.debug(f"Context update from {node_id}:")
        workflow_logger.debug(f"  {key} = {value_preview}...")
        
    def log_execution_summary(
        self,
        executed_nodes: Set[str],
        excluded_nodes: Set[str],
        total_nodes: int,
        duration_ms: float,
    ):
        """Log final execution summary."""
        self._log_header("EXECUTION SUMMARY")
        
        workflow_logger.info(f"Total nodes in workflow: {total_nodes}")
        workflow_logger.info(f"{Colors.GREEN}Executed nodes ({len(executed_nodes)}): {sorted(executed_nodes)}{Colors.END}")
        workflow_logger.info(f"{Colors.YELLOW}Excluded nodes ({len(excluded_nodes)}): {sorted(excluded_nodes)}{Colors.END}")
        workflow_logger.info(f"Execution time: {duration_ms:.2f}ms")
        
        # Log branch decision summary
        if self.branch_decisions:
            workflow_logger.info("\nBranch decisions made:")
            for bd in self.branch_decisions:
                decision_color = Colors.GREEN if bd["decision"] == "EXECUTE" else Colors.YELLOW
                workflow_logger.info(f"  {decision_color}{bd['node_id']}: {bd['decision']} - {bd['reason']}{Colors.END}")
                
    def log_error(self, message: str, exception: Optional[Exception] = None):
        """Log an error."""
        workflow_logger.error(f"{Colors.RED}ERROR: {message}{Colors.END}")
        if exception:
            workflow_logger.error(f"Exception: {str(exception)}")
            import traceback
            workflow_logger.error(traceback.format_exc())


# Global debugger instance
debugger = WorkflowDebugger()


def log_agent_call(func):
    """Decorator to log agent execute calls."""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        agent_name = getattr(self, 'agent_id', 'unknown')
        workflow_logger.debug(f"Agent {agent_name} execute() called")
        workflow_logger.debug(f"  Args: {str(args)[:200]}")
        workflow_logger.debug(f"  Kwargs keys: {list(kwargs.keys())}")
        
        try:
            result = await func(self, *args, **kwargs)
            workflow_logger.debug(f"Agent {agent_name} completed successfully")
            if result:
                workflow_logger.debug(f"  Action: {result.action}")
                workflow_logger.debug(f"  Content preview: {result.content[:200]}...")
            return result
        except Exception as e:
            workflow_logger.error(f"Agent {agent_name} failed: {e}")
            raise
            
    return wrapper

