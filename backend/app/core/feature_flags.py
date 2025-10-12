"""Feature flags for gradual rollout and A/B testing

This module provides a simple feature flag system for controlling
which workflow version (regular vs HITL) is used for different users/scenarios.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel
import os


class WorkflowMode(str, Enum):
    """Available workflow modes"""

    REGULAR = "regular"  # Fast, no approval gates
    HITL = "hitl"  # Human-in-the-loop with approval gates
    AUTO = "auto"  # Automatically choose based on context


class FeatureFlags(BaseModel):
    """Feature flags configuration"""

    # Workflow selection
    default_workflow_mode: WorkflowMode = WorkflowMode.REGULAR
    enable_hitl_for_destructive_ops: bool = True  # Auto-enable HITL for risky operations

    # Quality control
    enable_critic_agent: bool = True
    critic_quality_threshold: float = 0.8
    max_retry_iterations: int = 3

    # Performance
    enable_caching: bool = False  # TODO: Implement in future
    max_tool_execution_time: float = 10.0  # seconds

    # Monitoring
    enable_metrics: bool = True
    enable_tracing: bool = False  # LangSmith tracing

    # Safety
    require_approval_for_code_execution: bool = False  # Global HITL toggle
    auto_reject_unsafe_operations: bool = False


# Singleton instance
_feature_flags: Optional[FeatureFlags] = None


def get_feature_flags() -> FeatureFlags:
    """Get or create feature flags instance

    Returns:
        FeatureFlags instance

    Environment Variables:
        - DEFAULT_WORKFLOW_MODE: "regular" | "hitl" | "auto"
        - ENABLE_CRITIC_AGENT: "true" | "false"
        - ENABLE_HITL_APPROVAL: "true" | "false"
        - ENABLE_METRICS: "true" | "false"
    """
    global _feature_flags

    if _feature_flags is None:
        # Load from environment
        workflow_mode_str = os.getenv("DEFAULT_WORKFLOW_MODE", "regular").lower()
        workflow_mode = WorkflowMode(workflow_mode_str)

        enable_critic = os.getenv("ENABLE_CRITIC_AGENT", "true").lower() == "true"
        enable_hitl = os.getenv("ENABLE_HITL_APPROVAL", "false").lower() == "true"
        enable_metrics = os.getenv("ENABLE_METRICS", "true").lower() == "true"

        _feature_flags = FeatureFlags(
            default_workflow_mode=workflow_mode,
            enable_critic_agent=enable_critic,
            require_approval_for_code_execution=enable_hitl,
            enable_metrics=enable_metrics,
        )

    return _feature_flags


def should_use_hitl_workflow(
    user_request: Optional[str] = None, operation_type: Optional[str] = None
) -> bool:
    """Determine if HITL workflow should be used

    Args:
        user_request: Optional user query text
        operation_type: Optional operation type ("read" | "write" | "analysis")

    Returns:
        True if HITL should be used, False for regular workflow

    Logic:
        1. If require_approval_for_code_execution=True → Always HITL
        2. If mode=HITL → Always HITL
        3. If mode=AUTO → Decide based on context
        4. If mode=REGULAR → Regular workflow
    """
    flags = get_feature_flags()

    # Global override
    if flags.require_approval_for_code_execution:
        return True

    # Explicit mode selection
    if flags.default_workflow_mode == WorkflowMode.HITL:
        return True
    elif flags.default_workflow_mode == WorkflowMode.REGULAR:
        return False

    # AUTO mode - intelligent selection
    if flags.default_workflow_mode == WorkflowMode.AUTO:
        # Enable HITL for destructive operations
        if operation_type in ["write", "modify", "delete"]:
            return flags.enable_hitl_for_destructive_ops

        # Enable HITL if request contains risky keywords
        if user_request:
            risky_keywords = ["delete", "drop", "remove", "modify", "update", "change"]
            user_request_lower = user_request.lower()
            if any(keyword in user_request_lower for keyword in risky_keywords):
                return True

        # Default to regular workflow
        return False

    return False


def should_use_critic_agent() -> bool:
    """Check if Critic Agent should be enabled

    Returns:
        True if critic should evaluate responses
    """
    return get_feature_flags().enable_critic_agent


def get_critic_threshold() -> float:
    """Get quality threshold for Critic Agent

    Returns:
        Quality threshold (0.0 - 1.0)
    """
    return get_feature_flags().critic_quality_threshold


def get_max_iterations() -> int:
    """Get maximum retry iterations

    Returns:
        Max number of quality improvement iterations
    """
    return get_feature_flags().max_retry_iterations


def is_metrics_enabled() -> bool:
    """Check if metrics collection is enabled

    Returns:
        True if metrics should be collected
    """
    return get_feature_flags().enable_metrics


# Convenience function for testing
def set_feature_flags(flags: FeatureFlags) -> None:
    """Override feature flags (for testing)

    Args:
        flags: FeatureFlags instance to use
    """
    global _feature_flags
    _feature_flags = flags


def reset_feature_flags() -> None:
    """Reset feature flags to default (for testing)"""
    global _feature_flags
    _feature_flags = None
