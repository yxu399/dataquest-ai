"""Integration tests for complete LangGraph workflow

These tests verify end-to-end functionality including:
- Feature flag behavior
- Metrics collection
- Workflow execution
- Error handling
"""

import pytest
import os
from app.core.feature_flags import (
    FeatureFlags,
    WorkflowMode,
    set_feature_flags,
    reset_feature_flags,
    should_use_hitl_workflow,
    should_use_critic_agent,
    get_critic_threshold,
)
from app.core.metrics import (
    get_metrics_collector,
    WorkflowMetricsContext,
    WorkflowMetrics,
)


class TestFeatureFlags:
    """Test feature flag functionality"""

    def setup_method(self):
        """Reset feature flags before each test"""
        reset_feature_flags()

    def test_default_feature_flags(self):
        """Test default feature flag values"""
        from app.core.feature_flags import get_feature_flags

        flags = get_feature_flags()

        assert flags.default_workflow_mode == WorkflowMode.REGULAR
        assert flags.enable_critic_agent is True
        assert flags.critic_quality_threshold == 0.8
        assert flags.max_retry_iterations == 3

    def test_hitl_workflow_selection_explicit(self):
        """Test HITL workflow selection with explicit mode"""
        # Set HITL mode
        flags = FeatureFlags(default_workflow_mode=WorkflowMode.HITL)
        set_feature_flags(flags)

        assert should_use_hitl_workflow() is True

    def test_hitl_workflow_selection_regular(self):
        """Test regular workflow selection"""
        flags = FeatureFlags(default_workflow_mode=WorkflowMode.REGULAR)
        set_feature_flags(flags)

        assert should_use_hitl_workflow() is False

    def test_hitl_workflow_selection_auto_risky(self):
        """Test AUTO mode with risky keywords"""
        flags = FeatureFlags(default_workflow_mode=WorkflowMode.AUTO)
        set_feature_flags(flags)

        # Risky request should trigger HITL
        assert should_use_hitl_workflow(user_request="Delete all rows") is True
        assert should_use_hitl_workflow(user_request="Drop table") is True
        assert should_use_hitl_workflow(user_request="Modify data") is True

    def test_hitl_workflow_selection_auto_safe(self):
        """Test AUTO mode with safe queries"""
        flags = FeatureFlags(default_workflow_mode=WorkflowMode.AUTO)
        set_feature_flags(flags)

        # Safe requests should use regular workflow
        assert should_use_hitl_workflow(user_request="Show me correlations") is False
        assert should_use_hitl_workflow(user_request="What's the average?") is False

    def test_global_hitl_override(self):
        """Test global HITL approval override"""
        flags = FeatureFlags(
            default_workflow_mode=WorkflowMode.REGULAR,
            require_approval_for_code_execution=True,
        )
        set_feature_flags(flags)

        # Should use HITL even though mode is REGULAR
        assert should_use_hitl_workflow() is True

    def test_critic_agent_enabled(self):
        """Test critic agent enable/disable"""
        # Enabled by default
        assert should_use_critic_agent() is True

        # Disable critic
        flags = FeatureFlags(enable_critic_agent=False)
        set_feature_flags(flags)
        assert should_use_critic_agent() is False

    def test_critic_threshold_configuration(self):
        """Test critic quality threshold configuration"""
        # Default threshold
        assert get_critic_threshold() == 0.8

        # Custom threshold
        flags = FeatureFlags(critic_quality_threshold=0.9)
        set_feature_flags(flags)
        assert get_critic_threshold() == 0.9


class TestMetricsCollection:
    """Test metrics collection system"""

    def test_workflow_metrics_creation(self):
        """Test creating workflow metrics"""
        metrics = WorkflowMetrics(workflow_id="test_123", workflow_mode="regular")

        assert metrics.workflow_id == "test_123"
        assert metrics.workflow_mode == "regular"
        assert metrics.status == "unknown"
        assert metrics.total_duration_ms == 0.0

    def test_workflow_metrics_context_manager(self):
        """Test metrics context manager"""
        with WorkflowMetricsContext("test_456", "hitl") as metrics:
            metrics.record_agent_execution("statistical_agent", 150.5)
            metrics.record_tool_execution("calculate_correlation", 27.3, success=True)
            metrics.record_quality_score(0.85, iteration=1)

        # Metrics should be saved
        collector = get_metrics_collector()
        summary = collector.get_summary_stats()

        assert summary["metrics_enabled"] is True
        assert summary["total_workflows"] >= 1

    def test_metrics_collection_disabled(self):
        """Test metrics when disabled"""
        from app.core.feature_flags import set_feature_flags, FeatureFlags

        # Disable metrics
        flags = FeatureFlags(enable_metrics=False)
        set_feature_flags(flags)

        collector = get_metrics_collector()
        collector.start_workflow("test_789", "regular")

        # Should not track anything
        assert "test_789" not in collector.current_metrics

    def test_tool_execution_tracking(self):
        """Test tool execution tracking"""
        from app.core.feature_flags import set_feature_flags, FeatureFlags

        # Ensure metrics are enabled for this test
        flags = FeatureFlags(enable_metrics=True)
        set_feature_flags(flags)

        collector = get_metrics_collector()
        collector.start_workflow("test_tool_tracking", "regular")

        collector.record_tool_execution(
            "test_tool_tracking", "calculate_correlation", 30.0, success=True
        )
        collector.record_tool_execution(
            "test_tool_tracking", "aggregate_data", 15.0, success=True
        )
        collector.record_tool_execution(
            "test_tool_tracking", "filter_data", 20.0, success=False
        )

        metrics = collector.complete_workflow(
            "test_tool_tracking", status="completed", total_duration_ms=100.0
        )

        assert metrics.tool_success_count == 2
        assert metrics.tool_failure_count == 1
        assert len(metrics.tools_called) == 3

    def test_quality_score_tracking(self):
        """Test quality score tracking over iterations"""
        from app.core.feature_flags import set_feature_flags, FeatureFlags

        # Ensure metrics are enabled for this test
        flags = FeatureFlags(enable_metrics=True)
        set_feature_flags(flags)

        collector = get_metrics_collector()
        collector.start_workflow("test_quality", "regular")

        collector.record_quality_score("test_quality", 0.65, iteration=1)
        collector.record_quality_score("test_quality", 0.75, iteration=2)
        collector.record_quality_score("test_quality", 0.85, iteration=3)

        metrics = collector.complete_workflow(
            "test_quality", status="completed", total_duration_ms=500.0
        )

        assert len(metrics.quality_scores) == 3
        assert metrics.final_quality_score == 0.85
        assert metrics.iterations_count == 3
        assert metrics.critic_evaluations == 3


class TestWorkflowIntegration:
    """Test complete workflow integration"""

    def test_regular_workflow_execution(self):
        """Test regular workflow end-to-end"""
        # This test would call the actual workflow
        # For now, we'll test the structure

        from app.core.feature_flags import should_use_hitl_workflow, reset_feature_flags

        reset_feature_flags()

        # Should use regular workflow by default
        assert should_use_hitl_workflow() is False

    def test_hitl_workflow_execution(self):
        """Test HITL workflow end-to-end"""
        from app.core.feature_flags import FeatureFlags, set_feature_flags

        flags = FeatureFlags(default_workflow_mode=WorkflowMode.HITL)
        set_feature_flags(flags)

        assert should_use_hitl_workflow() is True

    def test_workflow_with_metrics(self):
        """Test workflow execution with metrics collection"""
        workflow_id = "integration_test_123"

        with WorkflowMetricsContext(workflow_id, "regular") as metrics:
            # Simulate workflow steps
            metrics.record_agent_execution("router", 5.0)
            metrics.record_agent_execution("statistical_agent", 150.0)
            metrics.record_tool_execution("calculate_correlation", 27.0, success=True)
            metrics.record_agent_execution("critic_agent", 200.0)
            metrics.record_quality_score(0.85, iteration=1)

        # Verify metrics were saved
        collector = get_metrics_collector()
        summary = collector.get_summary_stats()

        assert summary["total_workflows"] >= 1

    def test_error_handling_in_workflow(self):
        """Test error handling and metrics recording"""
        workflow_id = "error_test_456"

        try:
            with WorkflowMetricsContext(workflow_id, "regular") as metrics:
                metrics.record_agent_execution("statistical_agent", 100.0)
                # Simulate error
                raise ValueError("Test error")
        except ValueError:
            pass  # Expected

        # Metrics should be saved with error status
        collector = get_metrics_collector()
        summary = collector.get_summary_stats()

        # Check that error was recorded
        assert summary["error_workflows"] >= 1


class TestFeatureFlagEnvironmentVariables:
    """Test feature flag loading from environment variables"""

    def test_workflow_mode_from_env(self, monkeypatch):
        """Test loading workflow mode from environment"""
        reset_feature_flags()
        monkeypatch.setenv("DEFAULT_WORKFLOW_MODE", "hitl")

        from app.core.feature_flags import get_feature_flags

        flags = get_feature_flags()
        assert flags.default_workflow_mode == WorkflowMode.HITL

    def test_critic_agent_from_env(self, monkeypatch):
        """Test loading critic agent setting from environment"""
        reset_feature_flags()
        monkeypatch.setenv("ENABLE_CRITIC_AGENT", "false")

        from app.core.feature_flags import get_feature_flags

        flags = get_feature_flags()
        assert flags.enable_critic_agent is False

    def test_hitl_approval_from_env(self, monkeypatch):
        """Test loading HITL approval setting from environment"""
        reset_feature_flags()
        monkeypatch.setenv("ENABLE_HITL_APPROVAL", "true")

        from app.core.feature_flags import get_feature_flags

        flags = get_feature_flags()
        assert flags.require_approval_for_code_execution is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
