"""Checkpoint Manager - State persistence for Human-in-the-Loop workflow

This module provides SQLite-based checkpointing for LangGraph workflows,
enabling state persistence and resumption for user approval cycles.
"""

from typing import Optional, Dict, Any, Callable
from pathlib import Path
from langgraph.checkpoint.sqlite import SqliteSaver
from app.core.config import settings
import sqlite3
import logging
import os

# Set up logging
logger = logging.getLogger(__name__)


class CheckpointManager:
    """Manages SQLite checkpoints for workflow state persistence

    This enables Human-in-the-Loop (HITL) workflows where execution
    can be paused for user approval and then resumed.
    """

    def __init__(self, db_path: str | None = None):
        """Initialize checkpoint manager with SQLite database

        Args:
            db_path: Path to SQLite database file (defaults to ./checkpoints.db)
        """
        # Default to checkpoints.db in backend directory
        if db_path is None:
            backend_dir = Path(__file__).parent.parent.parent
            db_path = str(backend_dir / "checkpoints.db")

        self.db_path = db_path
        self._checkpointer: Optional[SqliteSaver] = None

    @property
    def checkpointer(self) -> SqliteSaver:
        """Get or create the SQLite checkpointer

        Returns:
            SqliteSaver instance for use with LangGraph compile()
        """
        if self._checkpointer is None:
            # Ensure directory exists
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)

            # Create checkpointer from connection string
            conn_string = f"sqlite:///{self.db_path}"
            self._checkpointer = SqliteSaver.from_conn_string(conn_string)

        return self._checkpointer

    def get_checkpoint(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest checkpoint for a thread

        Args:
            thread_id: Unique identifier for the conversation thread

        Returns:
            Checkpoint state dict or None if no checkpoint exists
        """
        config = {"configurable": {"thread_id": thread_id}}

        try:
            checkpoint = self.checkpointer.get(config)
            return checkpoint
        except sqlite3.Error as e:
            logger.error(f"Database error getting checkpoint for thread {thread_id}: {e}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error getting checkpoint for thread {thread_id}: {e}"
            )
            return None

    def list_threads(self) -> list[str]:
        """List all thread IDs with checkpoints

        Returns:
            List of thread IDs
        """
        if not os.path.exists(self.db_path):
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Query for distinct thread IDs
            cursor.execute(
                """
                SELECT DISTINCT json_extract(config, '$.configurable.thread_id')
                FROM checkpoints
                WHERE json_extract(config, '$.configurable.thread_id') IS NOT NULL
            """
            )

            threads = [row[0] for row in cursor.fetchall()]
            conn.close()

            return threads
        except sqlite3.Error as e:
            logger.error(f"Database error listing threads: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing threads: {e}")
            return []

    def delete_thread(self, thread_id: str) -> bool:
        """Delete all checkpoints for a thread

        Args:
            thread_id: Unique identifier for the conversation thread

        Returns:
            True if deletion successful, False otherwise
        """
        if not os.path.exists(self.db_path):
            logger.warning(
                f"Cannot delete thread {thread_id}: database file does not exist"
            )
            return False

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Delete checkpoints for this thread
            cursor.execute(
                """
                DELETE FROM checkpoints
                WHERE json_extract(config, '$.configurable.thread_id') = ?
            """,
                (thread_id,),
            )

            conn.commit()
            deleted_count = cursor.rowcount
            conn.close()

            if deleted_count > 0:
                logger.info(f"Deleted {deleted_count} checkpoints for thread {thread_id}")
                return True
            else:
                logger.warning(f"No checkpoints found for thread {thread_id}")
                return False
        except sqlite3.Error as e:
            logger.error(f"Database error deleting thread {thread_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting thread {thread_id}: {e}")
            return False

    def clear_all(self) -> bool:
        """Delete all checkpoints from database

        WARNING: This deletes ALL workflow state. Use with caution.

        Returns:
            True if deletion successful, False otherwise
        """
        if not os.path.exists(self.db_path):
            return True  # Already empty

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM checkpoints")
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            logger.warning(f"Cleared all checkpoints ({deleted_count} records)")
            return True
        except sqlite3.Error as e:
            logger.error(f"Database error clearing all checkpoints: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error clearing all checkpoints: {e}")
            return False

    def get_pending_approvals(self) -> list[Dict[str, Any]]:
        """Get all workflows awaiting user approval

        Returns:
            List of pending approval contexts with thread_id and approval details
        """
        if not os.path.exists(self.db_path):
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Query for checkpoints with requires_approval=True
            cursor.execute(
                """
                SELECT
                    json_extract(config, '$.configurable.thread_id') as thread_id,
                    json_extract(checkpoint, '$.requires_approval') as requires_approval,
                    json_extract(checkpoint, '$.approval_type') as approval_type,
                    json_extract(checkpoint, '$.approval_context') as approval_context,
                    created_at
                FROM checkpoints
                WHERE json_extract(checkpoint, '$.requires_approval') = 1
                ORDER BY created_at DESC
            """
            )

            results = []
            for row in cursor.fetchall():
                thread_id, requires_approval, approval_type, approval_context, created_at = (
                    row
                )

                if requires_approval:
                    results.append(
                        {
                            "thread_id": thread_id,
                            "approval_type": approval_type,
                            "approval_context": approval_context,
                            "created_at": created_at,
                        }
                    )

            conn.close()
            return results
        except sqlite3.Error as e:
            logger.error(f"Database error getting pending approvals: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting pending approvals: {e}")
            return []


# Create singleton instance
checkpoint_manager = CheckpointManager()


# ============================================================================
# Helper Functions
# ============================================================================


def create_config(thread_id: str) -> Dict[str, Any]:
    """Create a LangGraph config with thread_id

    Args:
        thread_id: Unique identifier for the conversation thread

    Returns:
        Config dict for use with workflow.invoke(state, config=config)

    Example:
        config = create_config("user_123_analysis_456")
        result = workflow.invoke(state, config=config)
    """
    return {"configurable": {"thread_id": thread_id}}


def requires_code_approval(state: Dict[str, Any]) -> bool:
    """Check if tool execution requires user approval

    This can be customized based on:
    - Tool type (some tools may be more risky)
    - Data size (large operations may need approval)
    - User preferences (power users may disable approvals)

    Args:
        state: Current workflow state

    Returns:
        True if approval required, False otherwise
    """
    # For now, require approval for all tool executions
    # This can be made configurable later via settings or user preferences
    return True


def requires_insight_approval(state: Dict[str, Any]) -> bool:
    """Check if insights require user approval

    Business-critical insights or recommendations with high impact
    should be approved by users before being acted upon.

    Args:
        state: Current workflow state

    Returns:
        True if approval required, False otherwise
    """
    # Check if approval context indicates high business impact
    approval_context = state.get("approval_context", {})
    business_impact = approval_context.get("business_impact", "low")

    return business_impact in ["high", "critical"]


# ============================================================================
# Code Preview Registry (Scalable Approach)
# ============================================================================

# Type alias for preview generator functions
PreviewGenerator = Callable[[Dict[str, Any]], str]


def _preview_correlation(args: Dict[str, Any]) -> str:
    """Generate preview for correlation tool"""
    threshold = args.get("threshold", 0.7)
    method = args.get("method", "pearson")
    return f"df.corr(method='{method}')  # threshold={threshold}"


def _preview_aggregation(args: Dict[str, Any]) -> str:
    """Generate preview for aggregation tool"""
    column = args.get("column", "column")
    operation = args.get("operation", "mean")
    group_by = args.get("group_by")

    if group_by:
        return f"df.groupby('{group_by}')['{column}'].{operation}()"
    else:
        return f"df['{column}'].{operation}()"


def _preview_filter(args: Dict[str, Any]) -> str:
    """Generate preview for filter tool"""
    column = args.get("column", "column")
    operator = args.get("operator", "==")
    value = args.get("value", "value")
    return f"df[df['{column}'] {operator} {value}]"


def _preview_distribution(args: Dict[str, Any]) -> str:
    """Generate preview for distribution analysis tool"""
    column = args.get("column", "column")
    bins = args.get("bins", 10)
    return f"df['{column}'].hist(bins={bins})"


def _preview_value_counts(args: Dict[str, Any]) -> str:
    """Generate preview for value counts tool"""
    column = args.get("column", "column")
    top_n = args.get("top_n", 10)
    return f"df['{column}'].value_counts().head({top_n})"


def _preview_generic(tool_name: str, args: Dict[str, Any]) -> str:
    """Generic preview for unknown tools"""
    return f"{tool_name}({', '.join(f'{k}={v}' for k, v in args.items())})"


# Registry mapping tool names to preview generator functions
CODE_PREVIEW_REGISTRY: Dict[str, PreviewGenerator] = {
    "calculate_correlation": _preview_correlation,
    "aggregate_data": _preview_aggregation,
    "filter_data": _preview_filter,
    "analyze_distribution": _preview_distribution,
    "count_values": _preview_value_counts,
}


def register_code_preview(tool_name: str, preview_fn: PreviewGenerator) -> None:
    """Register a new code preview generator for a tool

    Args:
        tool_name: Name of the tool
        preview_fn: Function that takes arguments dict and returns preview string

    Example:
        def my_tool_preview(args: Dict[str, Any]) -> str:
            return f"my_tool({args})"

        register_code_preview("my_tool", my_tool_preview)
    """
    CODE_PREVIEW_REGISTRY[tool_name] = preview_fn
    logger.info(f"Registered code preview generator for tool: {tool_name}")


def generate_code_preview(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Generate a human-readable preview of tool execution

    Uses the CODE_PREVIEW_REGISTRY to look up the appropriate preview generator.
    Falls back to generic preview for unknown tools.

    Args:
        tool_name: Name of the tool to be executed
        arguments: Tool arguments

    Returns:
        Formatted code preview string
    """
    # Look up preview generator in registry
    preview_fn = CODE_PREVIEW_REGISTRY.get(tool_name)

    if preview_fn:
        try:
            return preview_fn(arguments)
        except Exception as e:
            logger.error(f"Error generating preview for {tool_name}: {e}")
            return _preview_generic(tool_name, arguments)
    else:
        # Fall back to generic preview
        logger.warning(
            f"No preview generator registered for {tool_name}, using generic preview"
        )
        return _preview_generic(tool_name, arguments)
