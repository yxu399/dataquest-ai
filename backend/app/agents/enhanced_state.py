"""Enhanced state for advanced LangGraph multi-agent workflow"""

from typing import Annotated, List, Optional, Dict, Any, Literal
from typing_extensions import TypedDict
import operator


class ToolCall(TypedDict):
    """Represents a tool call made by an agent"""

    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[Any]
    error: Optional[str]


class CritiqueResult(TypedDict):
    """Result from Critic Agent evaluation"""

    score: float  # 0-1, quality score
    critique: str  # Explanation of quality assessment
    reroute_to: Optional[str]  # Agent to retry with if score < threshold
    passed: bool  # True if score >= threshold


class DataAnalysisState(TypedDict):
    """Enhanced state for data analysis workflow with tools, HITL, and critic support

    Using Annotated with operator.add for list fields ensures proper accumulation across nodes.
    """

    # Core data context
    file_path: str
    filename: str
    data_profile: Optional[Dict[str, Any]]
    analysis_results: Optional[Dict[str, Any]]
    insights: Optional[List[str]]

    # User interaction
    user_message: str
    conversation_history: Annotated[
        List[Dict[str, str]], operator.add
    ]  # Accumulates with operator.add

    # Routing and classification
    query_type: Optional[str]  # profiling, statistical, visualization, insights, query
    next: Optional[str]  # Next node to route to

    # Agent outputs
    agent_response: Optional[str]
    chart_type: Optional[str]
    chart_data: Optional[Dict[str, Any]]

    # Tool execution tracking (uses operator.add reducer)
    tool_calls: Annotated[List[ToolCall], operator.add]  # History accumulates
    pending_tool: Optional[ToolCall]  # Tool awaiting execution
    tool_result: Optional[Any]  # Result from last tool execution

    # Human-in-the-loop
    requires_approval: bool
    approval_type: Optional[Literal["code_execution", "insight_recommendation"]]
    approval_context: Optional[Dict[str, Any]]  # Context for approval decision
    approved: Optional[bool]  # User's approval decision
    approval_feedback: Optional[str]  # User's feedback if rejected

    # Critic and self-correction
    critique: Optional[CritiqueResult]  # Latest critique result
    iteration_count: int  # Number of refinement iterations
    critique_history: Annotated[
        List[CritiqueResult], operator.add
    ]  # All critiques accumulate
    max_iterations: int  # Maximum allowed iterations (default: 3)

    # Metadata and debugging (trace uses operator.add for complete audit trail)
    status: str  # pending, profiled, analyzed, completed, error, awaiting_approval
    error: Optional[str]
    processing_time: float
    agent_used: Optional[str]  # Name of last agent that processed
    trace: Annotated[List[str], operator.add]  # Complete execution path audit


# Configuration constants
MAX_ITERATIONS = 3
CRITIC_THRESHOLD = 0.8  # Minimum score to pass critic evaluation
TOOL_TIMEOUT = 30  # Maximum seconds for tool execution


def initialize_state(
    file_path: str,
    filename: str,
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    data_profile: Optional[Dict[str, Any]] = None,
    analysis_results: Optional[Dict[str, Any]] = None,
    insights: Optional[List[str]] = None,
) -> DataAnalysisState:
    """Initialize a new DataAnalysisState with defaults

    Args:
        file_path: Path to the CSV file
        filename: Name of the file
        user_message: User's query
        conversation_history: Previous conversation messages (optional)
        data_profile: Pre-computed data profile (optional, from simple_workflow)
        analysis_results: Pre-computed analysis (optional, from simple_workflow)
        insights: Pre-computed insights (optional, from simple_workflow)

    Returns:
        Initialized DataAnalysisState ready for workflow execution
    """
    return DataAnalysisState(
        # Core
        file_path=file_path,
        filename=filename,
        user_message=user_message,
        conversation_history=conversation_history or [],
        # Data (may be pre-populated from simple_workflow)
        data_profile=data_profile,
        analysis_results=analysis_results,
        insights=insights,
        # Routing
        query_type=None,
        next=None,
        # Outputs
        agent_response=None,
        chart_type=None,
        chart_data=None,
        # Tools
        tool_calls=[],
        pending_tool=None,
        tool_result=None,
        # HITL
        requires_approval=False,
        approval_type=None,
        approval_context=None,
        approved=None,
        approval_feedback=None,
        # Critic
        critique=None,
        iteration_count=0,
        critique_history=[],
        max_iterations=MAX_ITERATIONS,
        # Metadata
        status="pending",
        error=None,
        processing_time=0.0,
        agent_used=None,
        trace=[],
    )


def add_tool_call(
    state: DataAnalysisState,
    tool_name: str,
    arguments: Dict[str, Any],
    result: Optional[Any] = None,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a tool call to the state history

    Returns a partial state update dict that will be merged by LangGraph.
    The tool_calls list uses operator.add, so it will append to existing list.
    """
    tool_call = ToolCall(
        tool_name=tool_name, arguments=arguments, result=result, error=error
    )

    return {
        "tool_calls": [tool_call],  # Will be appended due to operator.add
        "tool_result": result,
        "trace": [f"🔧 Tool call: {tool_name} with args: {arguments}"],
    }


def add_trace(state: DataAnalysisState, message: str) -> Dict[str, Any]:
    """Add a trace message for debugging

    Returns a partial state update. The trace list uses operator.add,
    so messages will accumulate across all nodes.

    Usage in every node:
        state.update(add_trace(state, "📊 Profiling Agent: Starting data profiling"))
    """
    return {"trace": [message]}


def increment_iteration(state: DataAnalysisState) -> Dict[str, Any]:
    """Increment iteration count for critic refinement

    Returns a partial state update with incremented count and trace.
    """
    current = state.get("iteration_count", 0)
    new_count = current + 1

    return {
        "iteration_count": new_count,
        "trace": [
            f"🔄 Iteration {new_count}/{state.get('max_iterations', MAX_ITERATIONS)}"
        ],
    }


def add_critique(
    state: DataAnalysisState,
    score: float,
    critique: str,
    reroute_to: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a critique result to state

    Returns a partial state update. The critique_history uses operator.add
    to accumulate all critique results.
    """
    passed = score >= CRITIC_THRESHOLD

    critique_result = CritiqueResult(
        score=score, critique=critique, reroute_to=reroute_to, passed=passed
    )

    return {
        "critique": critique_result,
        "critique_history": [critique_result],  # Will be appended due to operator.add
        "trace": [
            f"🎯 Critic: Score={score:.2f}, Passed={passed}, Reroute={reroute_to}"
        ],
    }


def should_continue_iteration(state: DataAnalysisState) -> bool:
    """Check if we should continue iterating based on max_iterations"""
    current = state.get("iteration_count", 0)
    maximum = state.get("max_iterations", MAX_ITERATIONS)
    return current < maximum


def get_full_trace(state: DataAnalysisState) -> str:
    """Get complete execution trace as formatted string"""
    trace = state.get("trace", [])
    if not trace:
        return "No trace available"

    return "\n".join(f"{i + 1}. {msg}" for i, msg in enumerate(trace))


def get_trace_summary(state: DataAnalysisState) -> Dict[str, Any]:
    """Get summary of execution trace for debugging"""
    trace = state.get("trace", [])
    tool_calls = state.get("tool_calls", [])
    critiques = state.get("critique_history", [])

    return {
        "total_steps": len(trace),
        "total_tool_calls": len(tool_calls),
        "total_critiques": len(critiques),
        "iterations": state.get("iteration_count", 0),
        "current_agent": state.get("agent_used"),
        "status": state.get("status"),
        "trace_messages": trace,
    }
