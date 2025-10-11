"""LangChain tool definitions for safe data manipulation

These tools are used by Statistical and Query agents to request specific
data operations. The Tool Agent executes these requests safely using the
TOOL_EXECUTORS registry.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool
import pandas as pd
import numpy as np


# ============================================================================
# Tool Input Schemas (Pydantic models for structured tool calls)
# ============================================================================


class CorrelationInput(BaseModel):
    """Input for correlation analysis tool"""

    columns: Optional[List[str]] = Field(
        None,
        description="Specific columns to analyze. If None, analyze all numeric columns.",
    )
    method: str = Field(
        "pearson", description="Correlation method: 'pearson', 'spearman', or 'kendall'"
    )
    threshold: float = Field(
        0.7, description="Minimum absolute correlation value to report (0-1)"
    )


class AggregationInput(BaseModel):
    """Input for data aggregation tool"""

    column: str = Field(description="Column to aggregate")
    operation: str = Field(
        description="Aggregation operation: 'mean', 'median', 'sum', 'min', 'max', 'count', 'std'"
    )
    group_by: Optional[str] = Field(
        None, description="Column to group by before aggregating"
    )


class FilterInput(BaseModel):
    """Input for data filtering tool"""

    column: str = Field(description="Column to filter on")
    operator: str = Field(
        description="Comparison operator: '>', '<', '>=', '<=', '==', '!=', 'contains', 'in'"
    )
    value: Any = Field(description="Value to compare against")
    limit: Optional[int] = Field(
        10, description="Maximum number of rows to return after filtering"
    )


class DistributionInput(BaseModel):
    """Input for distribution analysis tool"""

    column: str = Field(description="Column to analyze distribution")
    bins: int = Field(10, description="Number of bins for histogram")
    include_stats: bool = Field(
        True, description="Include statistical summary (mean, median, quartiles)"
    )


class ValueCountsInput(BaseModel):
    """Input for value counts tool"""

    column: str = Field(description="Categorical column to count values")
    top_n: int = Field(10, description="Number of top values to return")
    normalize: bool = Field(False, description="Return proportions instead of counts")


# ============================================================================
# Tool Definitions (Used by LLMs to structure requests)
# ============================================================================


@tool
def calculate_correlation(
    columns: Optional[List[str]] = None, method: str = "pearson", threshold: float = 0.7
) -> Dict[str, Any]:
    """Calculate correlation between numeric columns in the dataset.

    IMPORTANT: This is the PRIMARY way to answer questions about:
    - Relationships between variables
    - Correlations or associations
    - Which columns are related
    - Statistical dependencies

    Args:
        columns: Specific columns to analyze (None = all numeric)
        method: 'pearson' (linear), 'spearman' (rank), or 'kendall'
        threshold: Minimum |correlation| to report (0-1)

    Returns:
        Dict with correlations list, method, and total_pairs
    """
    # Tool schema only - execution happens in Tool Agent
    pass


@tool
def aggregate_data(
    column: str, operation: str, group_by: Optional[str] = None
) -> Dict[str, Any]:
    """Perform aggregation on a column, optionally grouped by another column.

    IMPORTANT: This is the PRIMARY way to answer questions like:
    - "What's the average/mean of X?"
    - "Sum of Y by category"
    - "Maximum value in Z"
    - "Count of items per group"

    Args:
        column: Column to aggregate
        operation: 'mean', 'median', 'sum', 'min', 'max', 'count', 'std'
        group_by: Column to group by (None = aggregate entire column)

    Returns:
        Dict with result, operation, column, and group_by
    """
    pass


@tool
def filter_data(
    column: str, operator: str, value: Any, limit: int = 10
) -> Dict[str, Any]:
    """Filter dataset based on a condition and return matching rows.

    IMPORTANT: This is the PRIMARY way to answer questions like:
    - "Show me rows where X > 100"
    - "Filter data by category = 'A'"
    - "Find records with Y contains 'keyword'"
    - "Which rows have Z in [list]?"

    Args:
        column: Column to filter on
        operator: '>', '<', '>=', '<=', '==', '!=', 'contains', 'in'
        value: Value to compare against
        limit: Max rows to return (default: 10)

    Returns:
        Dict with filtered_data, original_rows, filtered_rows, column, operator
    """
    pass


@tool
def analyze_distribution(
    column: str, bins: int = 10, include_stats: bool = True
) -> Dict[str, Any]:
    """Analyze the distribution of values in a numeric column.

    IMPORTANT: This is the PRIMARY way to answer questions like:
    - "How is X distributed?"
    - "Show me the spread of Y"
    - "What's the distribution of Z?"
    - "Histogram for column A"

    Args:
        column: Numeric column to analyze
        bins: Number of bins for histogram
        include_stats: Include mean, median, quartiles

    Returns:
        Dict with histogram, statistics, and column
    """
    pass


@tool
def count_values(
    column: str, top_n: int = 10, normalize: bool = False
) -> Dict[str, Any]:
    """Count occurrences of each unique value in a categorical column.

    IMPORTANT: This is the PRIMARY way to answer questions like:
    - "What are the most common values in X?"
    - "Count by category Y"
    - "How many of each type in Z?"
    - "Distribution of categorical column A"

    Args:
        column: Categorical column to count
        top_n: Number of top values to return
        normalize: Return proportions instead of counts

    Returns:
        Dict with counts, total_unique, and column
    """
    pass


# ============================================================================
# Tool Execution Functions (Called by Tool Agent)
# ============================================================================


def execute_correlation(df: pd.DataFrame, params: CorrelationInput) -> Dict[str, Any]:
    """Execute correlation analysis on DataFrame"""
    # Select numeric columns
    if params.columns:
        numeric_cols = [
            col
            for col in params.columns
            if col in df.select_dtypes(include=[np.number]).columns
        ]
    else:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if len(numeric_cols) < 2:
        return {"correlations": [], "method": params.method, "total_pairs": 0}

    # Calculate correlation matrix
    corr_matrix = df[numeric_cols].corr(method=params.method)

    # Extract significant correlations
    correlations = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            corr_val = corr_matrix.iloc[i, j]
            if not pd.isna(corr_val) and abs(corr_val) >= params.threshold:
                correlations.append(
                    {
                        "column1": corr_matrix.columns[i],
                        "column2": corr_matrix.columns[j],
                        "correlation": round(float(corr_val), 3),
                        "strength": "strong" if abs(corr_val) >= 0.8 else "moderate",
                    }
                )

    # Sort by absolute correlation
    correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)

    return {
        "correlations": correlations,
        "method": params.method,
        "total_pairs": len(correlations),
    }


def execute_aggregation(df: pd.DataFrame, params: AggregationInput) -> Dict[str, Any]:
    """Execute aggregation on DataFrame"""
    if params.column not in df.columns:
        raise ValueError(f"Column '{params.column}' not found")

    if params.group_by:
        # Grouped aggregation
        if params.group_by not in df.columns:
            raise ValueError(f"Group by column '{params.group_by}' not found")

        grouped = df.groupby(params.group_by)[params.column]

        operations = {
            "mean": grouped.mean,
            "median": grouped.median,
            "sum": grouped.sum,
            "min": grouped.min,
            "max": grouped.max,
            "count": grouped.count,
            "std": grouped.std,
        }

        if params.operation not in operations:
            raise ValueError(f"Unknown operation: {params.operation}")

        result_series = operations[params.operation]()
        # Convert to serializable format
        result = {
            str(k): float(v) if pd.notna(v) else None
            for k, v in result_series.to_dict().items()
        }

    else:
        # Simple aggregation
        series = df[params.column]

        operations = {
            "mean": lambda: float(series.mean()),
            "median": lambda: float(series.median()),
            "sum": lambda: float(series.sum()),
            "min": lambda: float(series.min()),
            "max": lambda: float(series.max()),
            "count": lambda: int(series.count()),
            "std": lambda: float(series.std()),
        }

        if params.operation not in operations:
            raise ValueError(f"Unknown operation: {params.operation}")

        result = operations[params.operation]()

    return {
        "result": result,
        "operation": params.operation,
        "column": params.column,
        "group_by": params.group_by,
    }


def execute_filter(df: pd.DataFrame, params: FilterInput) -> Dict[str, Any]:
    """Execute filtering on DataFrame"""
    if params.column not in df.columns:
        raise ValueError(f"Column '{params.column}' not found")

    original_rows = len(df)

    # Apply filter based on operator
    operators = {
        ">": lambda: df[df[params.column] > params.value],
        "<": lambda: df[df[params.column] < params.value],
        ">=": lambda: df[df[params.column] >= params.value],
        "<=": lambda: df[df[params.column] <= params.value],
        "==": lambda: df[df[params.column] == params.value],
        "!=": lambda: df[df[params.column] != params.value],
        "contains": lambda: df[
            df[params.column].astype(str).str.contains(str(params.value), na=False)
        ],
        "in": lambda: df[df[params.column].isin(params.value)],
    }

    if params.operator not in operators:
        raise ValueError(f"Unknown operator: {params.operator}")

    filtered_df = operators[params.operator]()

    # Apply limit
    if params.limit:
        filtered_df = filtered_df.head(params.limit)

    # Convert to dict format
    filtered_data = filtered_df.to_dict("records")

    return {
        "filtered_data": filtered_data,
        "original_rows": original_rows,
        "filtered_rows": len(filtered_df),
        "column": params.column,
        "operator": params.operator,
    }


def execute_distribution(df: pd.DataFrame, params: DistributionInput) -> Dict[str, Any]:
    """Execute distribution analysis on DataFrame"""
    if params.column not in df.columns:
        raise ValueError(f"Column '{params.column}' not found")

    series = df[params.column].dropna()

    if not pd.api.types.is_numeric_dtype(series):
        raise ValueError(f"Column '{params.column}' is not numeric")

    # Create histogram
    counts, bin_edges = np.histogram(series, bins=params.bins)
    bins = [
        (float(bin_edges[i]), float(bin_edges[i + 1]))
        for i in range(len(bin_edges) - 1)
    ]

    histogram = {"bins": bins, "counts": counts.tolist()}

    # Calculate statistics if requested
    statistics = None
    if params.include_stats:
        statistics = {
            "mean": float(series.mean()),
            "median": float(series.median()),
            "std": float(series.std()),
            "min": float(series.min()),
            "max": float(series.max()),
            "q1": float(series.quantile(0.25)),
            "q3": float(series.quantile(0.75)),
        }

    return {"histogram": histogram, "statistics": statistics, "column": params.column}


def execute_value_counts(df: pd.DataFrame, params: ValueCountsInput) -> Dict[str, Any]:
    """Execute value counts on DataFrame"""
    if params.column not in df.columns:
        raise ValueError(f"Column '{params.column}' not found")

    series = df[params.column]

    # Get value counts
    value_counts = series.value_counts(normalize=params.normalize).head(params.top_n)

    # Convert to dict (handle various dtypes)
    counts = {str(k): float(v) for k, v in value_counts.items()}

    return {
        "counts": counts,
        "total_unique": int(series.nunique()),
        "column": params.column,
    }


# ============================================================================
# Tool Registry (Simplifies Tool Agent implementation)
# ============================================================================

AVAILABLE_TOOLS = [
    calculate_correlation,
    aggregate_data,
    filter_data,
    analyze_distribution,
    count_values,
]

TOOL_EXECUTORS = {
    "calculate_correlation": execute_correlation,
    "aggregate_data": execute_aggregation,
    "filter_data": execute_filter,
    "analyze_distribution": execute_distribution,
    "count_values": execute_value_counts,
}

TOOL_INPUT_SCHEMAS = {
    "calculate_correlation": CorrelationInput,
    "aggregate_data": AggregationInput,
    "filter_data": FilterInput,
    "analyze_distribution": DistributionInput,
    "count_values": ValueCountsInput,
}
