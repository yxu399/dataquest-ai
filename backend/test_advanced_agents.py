#!/usr/bin/env python3
"""
Test script for advanced LangGraph agents
Tests Tool Agent and Statistical Agent with real data
"""
import sys
import os

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.enhanced_state import initialize_state
from app.agents.tool_agent import tool_agent, create_tool_call_request
from app.agents.tools import TOOL_EXECUTORS, AVAILABLE_TOOLS


# ============================================================================
# Helper Functions
# ============================================================================

def find_test_file():
    """Find an available test CSV file"""
    test_files = [
        "test_data/sample.csv",
        "uploads/business_sales_data copy.csv",
        "test_data/test_1000x10.csv"
    ]

    for f in test_files:
        if os.path.exists(f):
            return f
    return None


def get_test_column(file_path, column_type='numeric'):
    """Get a test column from the file"""
    import pandas as pd
    try:
        df = pd.read_csv(file_path)
        if column_type == 'numeric':
            cols = df.select_dtypes(include=['number']).columns.tolist()
        else:
            cols = df.select_dtypes(include=['object']).columns.tolist()

        return cols[0] if cols else None
    except Exception:
        return None


def run_tool_test(test_name, tool_name, tool_args, expected_result_keys=None):
    """Generic function to test any tool

    Args:
        test_name: Name of the test
        tool_name: Name of tool to test
        tool_args: Dict of tool arguments
        expected_result_keys: List of keys expected in tool_result

    Returns:
        True if test passed, False otherwise
    """
    print("\n" + "=" * 80)
    print(f"TEST: {test_name}")
    print("=" * 80)

    # Find test file
    test_file = find_test_file()
    if not test_file:
        print("❌ No test CSV file found")
        return False

    print(f"Using test file: {test_file}")

    # Initialize state
    state = initialize_state(
        file_path=test_file,
        filename=os.path.basename(test_file),
        user_message=f"Testing {tool_name}"
    )

    # Create tool request
    tool_request = create_tool_call_request(
        tool_name=tool_name,
        arguments=tool_args
    )

    state["pending_tool"] = tool_request

    print(f"\n🔧 Executing Tool Agent with {tool_name}...")
    print(f"   Arguments: {tool_args}")

    # Execute Tool Agent
    result = tool_agent(state)

    # Check results
    print("\n📊 Results:")
    print(f"  - Status: {result.get('status')}")

    if result.get('error'):
        print(f"  - Error: {result.get('error')}")
        print("\n❌ Test FAILED")
        return False

    if not result.get('tool_result'):
        print("  - No tool result returned")
        print("\n❌ Test FAILED")
        return False

    tool_result = result['tool_result']

    # Print relevant results based on tool type
    if tool_name == 'calculate_correlation':
        print(f"  - Correlations found: {tool_result.get('total_pairs', 0)}")
        print(f"  - Method: {tool_result.get('method')}")
        if tool_result.get('correlations'):
            print("\n  Top correlations:")
            for corr in tool_result['correlations'][:3]:
                print(f"    - {corr['column1']} ↔ {corr['column2']}: "
                      f"{corr['correlation']}")

    elif tool_name == 'aggregate_data':
        print(f"  - Operation: {tool_result.get('operation')}")
        print(f"  - Column: {tool_result.get('column')}")
        print(f"  - Result: {tool_result.get('result')}")

    elif tool_name == 'filter_data':
        print(f"  - Original rows: {tool_result.get('original_rows')}")
        print(f"  - Filtered rows: {tool_result.get('filtered_rows')}")
        print(f"  - Filter: {tool_result.get('column')} "
              f"{tool_result.get('operator')}")

    elif tool_name == 'analyze_distribution':
        print(f"  - Column: {tool_result.get('column')}")
        if tool_result.get('statistics'):
            stats = tool_result['statistics']
            print(f"  - Mean: {stats.get('mean'):.2f}")
            print(f"  - Median: {stats.get('median'):.2f}")

    elif tool_name == 'count_values':
        print(f"  - Column: {tool_result.get('column')}")
        print(f"  - Total unique: {tool_result.get('total_unique')}")
        counts = tool_result.get('counts', {})
        print(f"  - Top values: {len(counts)}")

    # Print trace
    print("\n📝 Execution Trace:")
    for trace_msg in result.get('trace', []):
        print(f"  {trace_msg}")

    # Verify expected result keys
    if expected_result_keys:
        missing_keys = set(expected_result_keys) - set(tool_result.keys())
        if missing_keys:
            print(f"\n❌ Missing expected keys: {missing_keys}")
            return False

    # Success check
    success = (result.get('status') == 'tool_executed' and
               result.get('tool_result') is not None)

    print(f"\n{'✅ Test PASSED' if success else '❌ Test FAILED'}")
    return success


# ============================================================================
# Test Functions
# ============================================================================

def test_tool_agent_correlation():
    """Test Tool Agent with correlation analysis"""
    return run_tool_test(
        test_name="Tool Agent - Correlation Analysis",
        tool_name="calculate_correlation",
        tool_args={"threshold": 0.7, "method": "pearson"},
        expected_result_keys=["correlations", "method", "total_pairs"]
    )


def test_tool_agent_aggregation():
    """Test Tool Agent with aggregation"""
    test_file = find_test_file()
    if not test_file:
        print("\n❌ No test file found for aggregation test")
        return False

    test_column = get_test_column(test_file, column_type='numeric')
    if not test_column:
        print("\n❌ No numeric column found in test file")
        return False

    return run_tool_test(
        test_name=f"Tool Agent - Aggregation (mean of {test_column})",
        tool_name="aggregate_data",
        tool_args={"column": test_column, "operation": "mean"},
        expected_result_keys=["result", "operation", "column"]
    )


def test_tool_agent_filter():
    """Test Tool Agent with filtering"""
    test_file = find_test_file()
    if not test_file:
        return False

    test_column = get_test_column(test_file, column_type='numeric')
    if not test_column:
        return False

    return run_tool_test(
        test_name=f"Tool Agent - Filter ({test_column} > 100)",
        tool_name="filter_data",
        tool_args={
            "column": test_column,
            "operator": ">",
            "value": 100,
            "limit": 5
        },
        expected_result_keys=[
            "filtered_data", "original_rows", "filtered_rows"
        ]
    )


def test_tool_agent_distribution():
    """Test Tool Agent with distribution analysis"""
    test_file = find_test_file()
    if not test_file:
        return False

    test_column = get_test_column(test_file, column_type='numeric')
    if not test_column:
        return False

    return run_tool_test(
        test_name=f"Tool Agent - Distribution ({test_column})",
        tool_name="analyze_distribution",
        tool_args={"column": test_column, "bins": 10, "include_stats": True},
        expected_result_keys=["histogram", "statistics", "column"]
    )


def test_tool_agent_value_counts():
    """Test Tool Agent with value counts"""
    test_file = find_test_file()
    if not test_file:
        return False

    test_column = get_test_column(test_file, column_type='categorical')
    if not test_column:
        print("\n⚠️  No categorical column found - skipping value_counts test")
        return None  # Skip, not fail

    return run_tool_test(
        test_name=f"Tool Agent - Value Counts ({test_column})",
        tool_name="count_values",
        tool_args={"column": test_column, "top_n": 5},
        expected_result_keys=["counts", "total_unique", "column"]
    )


def test_statistical_agent():
    """Test Statistical Agent with tool planning"""
    print("\n" + "=" * 80)
    print("TEST: Statistical Agent - Tool Planning")
    print("=" * 80)

    # Check if ANTHROPIC_API_KEY is available
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY not found - skipping")
        print("   Set ANTHROPIC_API_KEY in .env to test LLM-based planning")
        return None  # Not a failure, just skipped

    try:
        from app.agents.statistical_agent import statistical_agent
        import pandas as pd

        # Find test file
        test_file = find_test_file()
        if not test_file:
            print("❌ No test CSV file found")
            return False

        print(f"Using test file: {test_file}")

        # Load file to get data profile
        df = pd.read_csv(test_file)

        data_profile = {
            "shape": list(df.shape),
            "columns": df.columns.tolist(),
            "numeric_columns": df.select_dtypes(
                include=['number']
            ).columns.tolist(),
            "categorical_columns": df.select_dtypes(
                include=['object']
            ).columns.tolist()
        }

        # Initialize state
        state = initialize_state(
            file_path=test_file,
            filename=os.path.basename(test_file),
            user_message="Show me the correlations in this dataset",
            data_profile=data_profile
        )

        print(f"\n📊 Dataset Info:")
        print(f"  - Shape: {data_profile['shape']}")
        print(f"  - Numeric columns: {data_profile['numeric_columns']}")

        # Execute Statistical Agent (planning phase)
        print("\n🤖 Executing Statistical Agent...")
        result = statistical_agent.process(state)

        # Check results
        print("\n📊 Results:")
        print(f"  - Agent used: {result.get('agent_used')}")
        print(f"  - Next node: {result.get('next')}")

        has_response = result.get('agent_response') is not None
        has_tool = result.get('pending_tool') is not None

        if has_tool:
            pending = result['pending_tool']
            print(f"  - Tool requested: {pending['tool_name']}")
            print(f"  - Arguments: {pending['arguments']}")

        if has_response:
            response = result['agent_response']
            preview = response[:200] + "..." if len(response) > 200 else response
            print(f"  - Response: {preview}")

        print("\n📝 Execution Trace:")
        for trace_msg in result.get('trace', []):
            print(f"  {trace_msg}")

        # Success if agent either planned a tool call OR provided a response
        success = has_tool or has_response
        print(f"\n{'✅ Test PASSED' if success else '❌ Test FAILED'}")

        return success

    except Exception as e:
        print(f"❌ Test FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_registry():
    """Test that all tools are properly registered"""
    print("\n" + "=" * 80)
    print("TEST: Tool Registry Validation")
    print("=" * 80)

    print(f"\nAvailable tools: {len(AVAILABLE_TOOLS)}")
    for tool in AVAILABLE_TOOLS:
        print(f"  - {tool.name}")

    print(f"\nTool executors: {len(TOOL_EXECUTORS)}")
    for name in TOOL_EXECUTORS.keys():
        print(f"  - {name}")

    # Check consistency
    tool_names = {tool.name for tool in AVAILABLE_TOOLS}
    executor_names = set(TOOL_EXECUTORS.keys())

    missing_executors = tool_names - executor_names
    missing_tools = executor_names - tool_names

    if missing_executors:
        print(f"\n❌ Tools missing executors: {missing_executors}")
        return False

    if missing_tools:
        print(f"\n❌ Executors without tools: {missing_tools}")
        return False

    print("\n✅ All tools have executors and vice versa")
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("TESTING ADVANCED LANGGRAPH AGENTS")
    print("=" * 80)

    # Define all tests
    tests = [
        ("tool_agent_correlation", test_tool_agent_correlation),
        ("tool_agent_aggregation", test_tool_agent_aggregation),
        ("tool_agent_filter", test_tool_agent_filter),
        ("tool_agent_distribution", test_tool_agent_distribution),
        ("tool_agent_value_counts", test_tool_agent_value_counts),
        ("statistical_agent", test_statistical_agent),
        ("tool_registry", test_tool_registry),
    ]

    results = {}

    # Run all tests
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    for test_name, result in results.items():
        if result is True:
            status = "✅ PASSED"
        elif result is None:
            status = "⚠️  SKIPPED"
        else:
            status = "❌ FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")

    if failed > 0:
        print("\n❌ Some tests failed")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
