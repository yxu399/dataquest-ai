"""Metrics collection and monitoring for LangGraph workflows

This module provides observability into workflow execution:
- Execution times
- Agent routing decisions
- Quality scores
- Error rates
- Tool usage statistics
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field, asdict
import time
import json
from pathlib import Path
from app.core.feature_flags import is_metrics_enabled


@dataclass
class WorkflowMetrics:
    """Metrics for a single workflow execution"""

    # Identification
    workflow_id: str
    workflow_mode: str  # "regular" | "hitl"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    # Performance
    total_duration_ms: float = 0.0
    agent_duration_ms: Dict[str, float] = field(default_factory=dict)
    tool_execution_times: Dict[str, float] = field(default_factory=dict)

    # Routing
    query_type: Optional[str] = None
    agents_used: List[str] = field(default_factory=list)
    routing_path: List[str] = field(default_factory=list)

    # Quality
    quality_scores: List[float] = field(default_factory=list)
    final_quality_score: Optional[float] = None
    iterations_count: int = 0
    critic_evaluations: int = 0

    # Outcomes
    status: str = "unknown"  # "completed" | "error" | "cancelled" | "awaiting_approval"
    error_message: Optional[str] = None
    requires_approval: bool = False

    # Tool usage
    tools_called: List[str] = field(default_factory=list)
    tool_success_count: int = 0
    tool_failure_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class MetricsCollector:
    """Collects and stores workflow metrics"""

    def __init__(self, output_dir: str = "metrics"):
        """Initialize metrics collector

        Args:
            output_dir: Directory to store metrics files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.current_metrics: Dict[str, WorkflowMetrics] = {}

    def start_workflow(self, workflow_id: str, workflow_mode: str = "regular") -> None:
        """Start tracking a workflow execution

        Args:
            workflow_id: Unique identifier for this workflow
            workflow_mode: "regular" or "hitl"
        """
        if not is_metrics_enabled():
            return

        self.current_metrics[workflow_id] = WorkflowMetrics(
            workflow_id=workflow_id, workflow_mode=workflow_mode
        )

    def record_agent_execution(
        self, workflow_id: str, agent_name: str, duration_ms: float
    ) -> None:
        """Record agent execution time

        Args:
            workflow_id: Workflow identifier
            agent_name: Name of the agent
            duration_ms: Execution time in milliseconds
        """
        if not is_metrics_enabled() or workflow_id not in self.current_metrics:
            return

        metrics = self.current_metrics[workflow_id]
        metrics.agents_used.append(agent_name)
        metrics.agent_duration_ms[agent_name] = duration_ms
        metrics.routing_path.append(agent_name)

    def record_tool_execution(
        self,
        workflow_id: str,
        tool_name: str,
        duration_ms: float,
        success: bool = True,
    ) -> None:
        """Record tool execution

        Args:
            workflow_id: Workflow identifier
            tool_name: Name of the tool
            duration_ms: Execution time in milliseconds
            success: Whether tool executed successfully
        """
        if not is_metrics_enabled() or workflow_id not in self.current_metrics:
            return

        metrics = self.current_metrics[workflow_id]
        metrics.tools_called.append(tool_name)
        metrics.tool_execution_times[tool_name] = duration_ms

        if success:
            metrics.tool_success_count += 1
        else:
            metrics.tool_failure_count += 1

    def record_quality_score(
        self, workflow_id: str, score: float, iteration: int
    ) -> None:
        """Record Critic Agent quality score

        Args:
            workflow_id: Workflow identifier
            score: Quality score (0.0 - 1.0)
            iteration: Iteration number
        """
        if not is_metrics_enabled() or workflow_id not in self.current_metrics:
            return

        metrics = self.current_metrics[workflow_id]
        metrics.quality_scores.append(score)
        metrics.final_quality_score = score
        metrics.iterations_count = iteration
        metrics.critic_evaluations += 1

    def complete_workflow(
        self,
        workflow_id: str,
        status: str,
        total_duration_ms: float,
        query_type: Optional[str] = None,
        error_message: Optional[str] = None,
        requires_approval: bool = False,
    ) -> WorkflowMetrics:
        """Mark workflow as complete and save metrics

        Args:
            workflow_id: Workflow identifier
            status: Final status
            total_duration_ms: Total execution time
            query_type: Type of query (optional)
            error_message: Error message if status is "error"
            requires_approval: Whether workflow paused for approval

        Returns:
            WorkflowMetrics instance
        """
        if not is_metrics_enabled() or workflow_id not in self.current_metrics:
            # Return empty metrics if not enabled
            return WorkflowMetrics(workflow_id=workflow_id, workflow_mode="unknown")

        metrics = self.current_metrics[workflow_id]
        metrics.status = status
        metrics.total_duration_ms = total_duration_ms
        metrics.query_type = query_type
        metrics.error_message = error_message
        metrics.requires_approval = requires_approval

        # Save to file
        self._save_metrics(metrics)

        # Remove from current tracking
        del self.current_metrics[workflow_id]

        return metrics

    def _save_metrics(self, metrics: WorkflowMetrics) -> None:
        """Save metrics to file

        Args:
            metrics: WorkflowMetrics to save
        """
        # Create filename with timestamp
        filename = f"{metrics.workflow_id}_{metrics.timestamp.replace(':', '-')}.json"
        filepath = self.output_dir / filename

        # Write to file
        with open(filepath, "w") as f:
            f.write(metrics.to_json())

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics from all saved metrics

        Returns:
            Dictionary with aggregated statistics
        """
        if not is_metrics_enabled():
            return {"metrics_enabled": False}

        all_metrics = []
        for filepath in self.output_dir.glob("*.json"):
            with open(filepath, "r") as f:
                all_metrics.append(json.load(f))

        if not all_metrics:
            return {
                "metrics_enabled": True,
                "total_workflows": 0,
                "message": "No metrics collected yet",
            }

        # Calculate statistics
        total_workflows = len(all_metrics)
        completed = sum(1 for m in all_metrics if m["status"] == "completed")
        errors = sum(1 for m in all_metrics if m["status"] == "error")
        hitl_workflows = sum(1 for m in all_metrics if m["workflow_mode"] == "hitl")

        avg_duration = (
            sum(m["total_duration_ms"] for m in all_metrics) / total_workflows
        )

        quality_scores = [
            m["final_quality_score"]
            for m in all_metrics
            if m.get("final_quality_score") is not None
        ]
        avg_quality = (
            sum(quality_scores) / len(quality_scores) if quality_scores else None
        )

        # Tool usage statistics
        all_tools = []
        for m in all_metrics:
            all_tools.extend(m.get("tools_called", []))

        tool_usage_counts = {}
        for tool in all_tools:
            tool_usage_counts[tool] = tool_usage_counts.get(tool, 0) + 1

        return {
            "metrics_enabled": True,
            "total_workflows": total_workflows,
            "completed_workflows": completed,
            "error_workflows": errors,
            "hitl_workflows": hitl_workflows,
            "success_rate": completed / total_workflows if total_workflows > 0 else 0,
            "avg_duration_ms": avg_duration,
            "avg_quality_score": avg_quality,
            "tool_usage": tool_usage_counts,
            "most_used_tool": max(tool_usage_counts.items(), key=lambda x: x[1])[0]
            if tool_usage_counts
            else None,
        }


# Singleton instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create metrics collector

    Returns:
        MetricsCollector instance
    """
    global _metrics_collector

    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()

    return _metrics_collector


# Context manager for easy metrics tracking
class WorkflowMetricsContext:
    """Context manager for tracking workflow metrics

    Example:
        with WorkflowMetricsContext("workflow_123", "regular") as metrics:
            metrics.record_agent_execution("statistical_agent", 150.5)
            metrics.record_tool_execution("calculate_correlation", 27.3)
            metrics.record_quality_score(0.85, iteration=1)
            # Automatically saves on exit
    """

    def __init__(self, workflow_id: str, workflow_mode: str = "regular"):
        self.workflow_id = workflow_id
        self.workflow_mode = workflow_mode
        self.collector = get_metrics_collector()
        self.start_time = None

    def __enter__(self) -> "WorkflowMetricsContext":
        self.start_time = time.time()
        self.collector.start_workflow(self.workflow_id, self.workflow_mode)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000

        if exc_type is not None:
            # Error occurred
            self.collector.complete_workflow(
                self.workflow_id,
                status="error",
                total_duration_ms=duration_ms,
                error_message=str(exc_val),
            )
        else:
            # Success
            self.collector.complete_workflow(
                self.workflow_id, status="completed", total_duration_ms=duration_ms
            )

    def record_agent_execution(self, agent_name: str, duration_ms: float) -> None:
        """Record agent execution"""
        self.collector.record_agent_execution(self.workflow_id, agent_name, duration_ms)

    def record_tool_execution(
        self, tool_name: str, duration_ms: float, success: bool = True
    ) -> None:
        """Record tool execution"""
        self.collector.record_tool_execution(
            self.workflow_id, tool_name, duration_ms, success
        )

    def record_quality_score(self, score: float, iteration: int) -> None:
        """Record quality score"""
        self.collector.record_quality_score(self.workflow_id, score, iteration)
