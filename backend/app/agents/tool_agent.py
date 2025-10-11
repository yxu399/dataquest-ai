"""Tool Agent - Safely executes data manipulation operations

This agent is the "doer" - it receives structured tool calls from other agents
and executes them safely on the actual DataFrame.
"""
import time
import os
import pandas as pd
from typing import Dict, Any
from app.agents.enhanced_state import DataAnalysisState, add_tool_call, add_trace
from app.agents.tools import TOOL_EXECUTORS, TOOL_INPUT_SCHEMAS


def tool_agent(state: DataAnalysisState) -> Dict[str, Any]:
    """Execute pending tool call from state

    This node is the central execution point for all data operations.
    It uses the TOOL_EXECUTORS and TOOL_INPUT_SCHEMAS registries to:
    1. Validate file_path and pending_tool exist
    2. Load the DataFrame (with sampling for large datasets)
    3. Parse tool parameters using the appropriate Pydantic schema
    4. Execute the tool function
    5. Return results to state

    The agent does NOT use an LLM - it only executes pre-structured requests.

    Args:
        state: Current workflow state with pending_tool populated

    Returns:
        Partial state update with tool_result, tool_calls, and trace
    """
    start_time = time.time()

    # Validate file_path exists in state
    file_path = state.get("file_path")
    if not file_path:
        return {
            **add_trace(state, "❌ Tool Agent: No file_path in state"),
            "error": "Missing file_path in state",
            "status": "error"
        }

    # Validate file exists on disk
    if not os.path.exists(file_path):
        return {
            **add_trace(state, f"❌ Tool Agent: File not found: {file_path}"),
            "error": f"File not found: {file_path}",
            "status": "error"
        }

    # Extract pending tool call
    pending_tool = state.get("pending_tool")
    if not pending_tool:
        return {
            **add_trace(state, "🔧 Tool Agent: No pending tool to execute"),
            "error": "No pending tool call in state",
            "status": "error"
        }

    tool_name = pending_tool.get("tool_name")
    arguments = pending_tool.get("arguments", {})

    # Validate tool_name exists
    if not tool_name:
        return {
            **add_trace(state, "❌ Tool Agent: pending_tool missing tool_name"),
            "error": "Tool call missing tool_name",
            "status": "error"
        }

    # Add trace for execution start
    updates = add_trace(state, f"🔧 Tool Agent: Executing {tool_name} with args: {arguments}")

    try:
        # Validate tool exists in registry
        if tool_name not in TOOL_EXECUTORS:
            raise ValueError(f"Unknown tool: {tool_name}. Available: {list(TOOL_EXECUTORS.keys())}")

        # Load DataFrame with sampling for large datasets
        df = load_data_with_sampling(file_path, max_rows=10000)

        # Parse arguments using Pydantic schema
        input_schema = TOOL_INPUT_SCHEMAS[tool_name]
        validated_params = input_schema(**arguments)

        # Execute tool function
        executor = TOOL_EXECUTORS[tool_name]
        result = executor(df, validated_params)

        execution_time = (time.time() - start_time) * 1000  # Convert to ms

        # Add successful tool call to state
        tool_call_update = add_tool_call(
            state,
            tool_name=tool_name,
            arguments=arguments,
            result=result,
            error=None
        )

        # Merge updates
        updates = {
            **updates,
            **tool_call_update,
            "pending_tool": None,  # Clear pending tool
            "status": "tool_executed",
            "trace": [
                *updates.get("trace", []),
                f"✅ Tool Agent: {tool_name} completed in {execution_time:.2f}ms"
            ]
        }

        return updates

    except Exception as e:
        execution_time = (time.time() - start_time) * 1000

        error_message = f"Tool execution failed: {str(e)}"

        # Add failed tool call to state
        tool_call_update = add_tool_call(
            state,
            tool_name=tool_name,
            arguments=arguments,
            result=None,
            error=error_message
        )

        # Merge updates
        updates = {
            **updates,
            **tool_call_update,
            "pending_tool": None,
            "error": error_message,
            "status": "tool_error",
            "trace": [
                *updates.get("trace", []),
                f"❌ Tool Agent: {tool_name} failed after {execution_time:.2f}ms - {error_message}"
            ]
        }

        return updates


def load_data_with_sampling(file_path: str, max_rows: int = 10000) -> pd.DataFrame:
    """Load CSV data with automatic sampling for large datasets

    This prevents memory issues and keeps tool execution fast.

    Args:
        file_path: Path to CSV file
        max_rows: Maximum rows to load (default: 10,000)

    Returns:
        DataFrame (sampled if original > max_rows)

    Raises:
        FileNotFoundError: If file doesn't exist
        pd.errors.EmptyDataError: If file is empty
        pd.errors.ParserError: If CSV is malformed
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # First, get row count without loading full data
    # This is fast even for large files
    try:
        with open(file_path, 'r') as f:
            row_count = sum(1 for _ in f) - 1  # Subtract header
    except Exception as e:
        raise IOError(f"Failed to read file: {str(e)}")

    if row_count <= 0:
        raise ValueError("File is empty or has no data rows")

    if row_count <= max_rows:
        # Load full dataset
        return pd.read_csv(file_path)
    else:
        # Load with sampling
        # Use skiprows to randomly sample without loading everything
        import numpy as np

        # Calculate skip probability
        skip_prob = 1 - (max_rows / row_count)

        # Create random skip mask
        np.random.seed(42)  # For reproducibility
        skip_rows = np.random.choice([True, False], size=row_count, p=[skip_prob, 1 - skip_prob])

        # Convert to indices (accounting for header)
        skip_indices = [i + 1 for i, skip in enumerate(skip_rows) if skip]

        df = pd.read_csv(file_path, skiprows=skip_indices)

        print(f"⚠️ Sampled {len(df):,} rows from {row_count:,} total for tool execution")

        return df


def create_tool_call_request(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function for agents to create tool call requests

    Usage in Statistical/Query agents:
        # Agent determines it needs to call calculate_correlation tool
        tool_request = create_tool_call_request(
            "calculate_correlation",
            {"columns": ["age", "salary"], "method": "pearson", "threshold": 0.7}
        )

        return {
            "pending_tool": tool_request,
            "next": "tool_agent",  # Route to Tool Agent
            **add_trace(state, "📊 Statistical Agent: Requesting correlation analysis")
        }

    Args:
        tool_name: Name of tool to call (must be in TOOL_EXECUTORS)
        arguments: Dict of tool arguments (will be validated by Pydantic schema)

    Returns:
        Dict formatted as pending_tool request

    Raises:
        ValueError: If tool_name is not in TOOL_EXECUTORS
    """
    if tool_name not in TOOL_EXECUTORS:
        raise ValueError(f"Unknown tool: {tool_name}. Available: {list(TOOL_EXECUTORS.keys())}")

    return {
        "tool_name": tool_name,
        "arguments": arguments,
        "result": None,
        "error": None
    }
