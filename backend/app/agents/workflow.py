"""LangGraph Workflow - Multi-agent data analysis with self-correction

This module implements the complete LangGraph workflow with:
- Tool-based execution (Tool Agent + Statistical Agent)
- Critic Agent with quality evaluation
- Cyclical graph structure for iterative refinement
- Human-in-the-Loop (HITL) with checkpointing (optional)
"""

from typing import Dict, Any, Literal, Optional
from langgraph.graph import StateGraph, END
from app.agents.enhanced_state import (
    DataAnalysisState,
    should_continue_iteration,
    add_trace,
)
from app.agents.tool_agent import tool_agent
from app.agents.statistical_agent import statistical_agent
from app.agents.critic_agent import critic_agent
from app.agents.checkpoint_manager import (
    checkpoint_manager,
    requires_code_approval,
    generate_code_preview,
    create_config,
)


def router(state: DataAnalysisState) -> Dict[str, Any]:
    """Router node - determines which agent to route to

    This router handles:
    1. Normal routing based on query_type
    2. Re-routing based on critic feedback

    Args:
        state: Current workflow state

    Returns:
        Partial state update with next agent
    """
    updates = add_trace(state, "🔀 Router: Determining next agent")

    # Check if we're re-routing based on critic feedback
    critique = state.get("critique")
    if critique and critique.get("reroute_to"):
        reroute_agent = critique["reroute_to"]
        return {
            **updates,
            "next": reroute_agent,
            "trace": [
                *updates.get("trace", []),
                f"🔀 Router: Re-routing to {reroute_agent} based on critic feedback",
            ],
        }

    # Normal routing based on query_type
    query_type = state.get("query_type", "statistical")

    # For now, default to statistical_agent
    # In Phase 1, we only have statistical_agent implemented
    next_agent = "statistical_agent"

    return {
        **updates,
        "next": next_agent,
        "trace": [
            *updates.get("trace", []),
            f"🔀 Router: Routing to {next_agent} for query_type={query_type}",
        ],
    }


def decide_next_from_statistical(
    state: DataAnalysisState,
) -> Literal["tool_agent", "critic_agent", "end"]:
    """Conditional edge from statistical_agent

    Returns:
        - "tool_agent" if a tool needs to be executed
        - "critic_agent" if agent generated a response to evaluate
        - "end" if there was an error
    """
    # Check for error
    if state.get("error"):
        return "end"

    # Check if we need to execute a tool
    if state.get("pending_tool"):
        return "tool_agent"

    # Check if we have a response to evaluate
    if state.get("agent_response"):
        return "critic_agent"

    # Default: end workflow
    return "end"


def decide_next_from_tool(state: DataAnalysisState) -> Literal["statistical_agent"]:
    """Conditional edge from tool_agent

    After tool execution, always return to statistical_agent for interpretation.
    """
    return "statistical_agent"


def decide_next_from_critic(
    state: DataAnalysisState,
) -> Literal["router", "end"]:
    """Conditional edge from critic_agent

    Returns:
        - "router" if quality check failed and we should retry
        - "end" if quality check passed or max iterations reached
    """
    critique = state.get("critique")

    # If no critique (shouldn't happen), end workflow
    if not critique:
        return "end"

    # Check if quality check passed
    if critique.get("passed"):
        return "end"

    # Check if we've exceeded max iterations
    if not should_continue_iteration(state):
        return "end"

    # Quality check failed, retry
    return "router"


def approval_gate(state: DataAnalysisState) -> Dict[str, Any]:
    """Approval gate node - checks if user approval is needed before tool execution

    This node acts as an interrupt point for Human-in-the-Loop workflows.
    If approval is required, it sets requires_approval=True and the workflow
    will pause until the user provides approval via the API.

    Args:
        state: Current workflow state

    Returns:
        Partial state update with approval requirements
    """
    updates = add_trace(state, "🛡️ Approval Gate: Checking if approval needed")

    # Get the pending tool
    pending_tool = state.get("pending_tool")
    if not pending_tool:
        # No tool to approve, continue
        return {
            **updates,
            "trace": [
                *updates.get("trace", []),
                "🛡️ Approval Gate: No pending tool, continuing",
            ],
        }

    # Check if approval is required
    if requires_code_approval(state):
        # Generate code preview for user
        tool_name = pending_tool["tool_name"]
        arguments = pending_tool["arguments"]
        code_preview = generate_code_preview(tool_name, arguments)

        return {
            **updates,
            "requires_approval": True,
            "approval_type": "code_execution",
            "approval_context": {
                "tool_name": tool_name,
                "arguments": arguments,
                "code_preview": code_preview,
                "question": f"Execute {tool_name} with the following code?",
            },
            "status": "awaiting_approval",
            "trace": [
                *updates.get("trace", []),
                f"⏸️ Approval Gate: Requesting approval for {tool_name}",
            ],
        }
    else:
        # Approval not required, continue
        return {
            **updates,
            "trace": [
                *updates.get("trace", []),
                "🛡️ Approval Gate: Approval not required, continuing",
            ],
        }


def decide_next_from_approval_gate(
    state: DataAnalysisState,
) -> Literal["tool_agent", "end"]:
    """Conditional edge from approval_gate

    Returns:
        - "tool_agent" if approved or approval not required
        - "end" if rejected

    Note: When requires_approval=True, the workflow will interrupt here
    and wait for user input via API before continuing.
    """
    # Check if approval was explicitly rejected
    if state.get("approved") is False:
        return "end"

    # Otherwise, proceed to tool execution
    # (either approved=True or approval wasn't required)
    return "tool_agent"


def create_workflow(enable_hitl: bool = False) -> StateGraph:
    """Create the complete LangGraph workflow

    Args:
        enable_hitl: Enable Human-in-the-Loop approval gates

    Graph structure (without HITL):
        START
          ↓
        router → statistical_agent → [conditional]
                      ↓                    ↓
                  tool_agent ←─────────────┘
                      ↓
                  statistical_agent (interpretation)
                      ↓
                  critic_agent → [conditional]
                      ↓              ↓
                    END    ←─────────┘
                      ↑              ↓
                      └───── router (retry)

    Graph structure (with HITL):
        START
          ↓
        router → statistical_agent → [conditional]
                      ↓                    ↓
                  approval_gate ←─────────┘
                      ↓
                  tool_agent  (after approval)
                      ↓
                  statistical_agent (interpretation)
                      ↓
                  critic_agent → [conditional]
                      ↓              ↓
                    END    ←─────────┘
                      ↑              ↓
                      └───── router (retry)

    Returns:
        StateGraph ready to be compiled
    """
    # Create graph builder
    workflow = StateGraph(DataAnalysisState)

    # Add nodes
    workflow.add_node("router", router)
    workflow.add_node("statistical_agent", lambda s: statistical_agent.process(s))
    workflow.add_node("tool_agent", tool_agent)
    workflow.add_node("critic_agent", lambda s: critic_agent.process(s))

    if enable_hitl:
        workflow.add_node("approval_gate", approval_gate)

    # Set entry point
    workflow.set_entry_point("router")

    # Add edges from router
    workflow.add_edge("router", "statistical_agent")

    # Add conditional edges from statistical_agent
    if enable_hitl:
        # Route through approval_gate for HITL
        workflow.add_conditional_edges(
            "statistical_agent",
            decide_next_from_statistical,
            {
                "tool_agent": "approval_gate",  # Go to approval gate first
                "critic_agent": "critic_agent",
                "end": END,
            },
        )

        # Add conditional edges from approval_gate (with interrupt)
        workflow.add_conditional_edges(
            "approval_gate",
            decide_next_from_approval_gate,
            {
                "tool_agent": "tool_agent",
                "end": END,
            },
        )
    else:
        # Direct route to tool_agent (no approval)
        workflow.add_conditional_edges(
            "statistical_agent",
            decide_next_from_statistical,
            {
                "tool_agent": "tool_agent",
                "critic_agent": "critic_agent",
                "end": END,
            },
        )

    # Add conditional edge from tool_agent (always returns to statistical_agent)
    workflow.add_edge("tool_agent", "statistical_agent")

    # Add conditional edges from critic_agent (cyclical!)
    workflow.add_conditional_edges(
        "critic_agent",
        decide_next_from_critic,
        {
            "router": "router",  # Cycle back for retry
            "end": END,
        },
    )

    return workflow


def create_compiled_workflow(enable_hitl: bool = False, use_checkpointer: bool = False):
    """Create and compile the workflow

    Args:
        enable_hitl: Enable Human-in-the-Loop approval gates
        use_checkpointer: Enable SQLite checkpointing for state persistence

    Returns:
        Compiled workflow ready for invocation

    Example (without HITL):
        workflow = create_compiled_workflow()
        result = workflow.invoke(state)

    Example (with HITL):
        workflow = create_compiled_workflow(enable_hitl=True, use_checkpointer=True)
        config = create_config(thread_id="user_123")
        result = workflow.invoke(state, config=config)
    """
    workflow = create_workflow(enable_hitl=enable_hitl)

    if use_checkpointer:
        # Compile with checkpointer for state persistence
        return workflow.compile(
            checkpointer=checkpoint_manager.checkpointer,
            interrupt_before=["approval_gate"] if enable_hitl else None,
        )
    else:
        # Compile without checkpointer
        return workflow.compile()


# Create singleton compiled workflows
# Default workflow without HITL (for backward compatibility)
compiled_workflow = create_compiled_workflow(enable_hitl=False, use_checkpointer=False)

# HITL workflow with checkpointing
compiled_workflow_with_hitl = create_compiled_workflow(
    enable_hitl=True, use_checkpointer=True
)

# Legacy alias for backward compatibility
analysis_workflow = compiled_workflow
