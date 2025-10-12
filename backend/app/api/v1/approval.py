"""Approval API endpoints for Human-in-the-Loop workflow

This module provides REST API endpoints for managing workflow approvals
in the HITL (Human-in-the-Loop) system with LangGraph checkpointing.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.database import Analysis
from app.agents.checkpoint_manager import checkpoint_manager, create_config
from app.agents.workflow import compiled_workflow_with_hitl
from app.agents.enhanced_state import initialize_state

router = APIRouter()


# ============================================================================
# Dependency Functions
# ============================================================================


def get_analysis_or_404(analysis_id: int, db: Session = Depends(get_db)) -> Analysis:
    """Dependency to get analysis by ID or raise 404

    Args:
        analysis_id: ID of the analysis
        db: Database session

    Returns:
        Analysis object

    Raises:
        HTTPException: 404 if analysis not found
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


def get_completed_analysis_or_400(
    analysis_id: int, db: Session = Depends(get_db)
) -> Analysis:
    """Dependency to get completed analysis or raise 400

    Args:
        analysis_id: ID of the analysis
        db: Database session

    Returns:
        Completed Analysis object

    Raises:
        HTTPException: 404 if analysis not found, 400 if not completed
    """
    analysis = get_analysis_or_404(analysis_id, db)

    if analysis.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Analysis must be completed first. Current status: {analysis.status}",
        )

    return analysis


# ============================================================================
# Request/Response Models
# ============================================================================


class ApprovalRequest(BaseModel):
    """Request to approve or reject a pending action"""

    approved: bool
    feedback: Optional[str] = None  # Optional feedback if rejected


class StartWorkflowRequest(BaseModel):
    """Request to start a new HITL workflow"""

    user_message: str  # The user's question or query


class ApprovalResponse(BaseModel):
    """Response after approval/rejection"""

    success: bool
    status: str  # completed, awaiting_approval, error
    message: str
    agent_response: Optional[str] = None
    error: Optional[str] = None


class PendingApprovalInfo(BaseModel):
    """Information about a pending approval"""

    thread_id: str
    analysis_id: int
    approval_type: str  # code_execution, insight_recommendation
    approval_context: Dict[str, Any]
    created_at: str
    status: str


class PendingApprovalsResponse(BaseModel):
    """List of pending approvals"""

    count: int
    approvals: List[PendingApprovalInfo]


class WorkflowStatusResponse(BaseModel):
    """Status of a workflow execution"""

    thread_id: str
    status: str
    requires_approval: bool
    approval_type: Optional[str] = None
    approval_context: Optional[Dict[str, Any]] = None
    agent_response: Optional[str] = None
    trace: List[str] = []


# ============================================================================
# API Endpoints
# ============================================================================


@router.post("/approve/{analysis_id}", response_model=ApprovalResponse)
async def approve_action(
    analysis_id: int,
    request: ApprovalRequest,
    analysis: Analysis = Depends(get_analysis_or_404),
):
    """Approve or reject a pending action in the HITL workflow

    This endpoint resumes a paused workflow with the user's approval decision.

    Args:
        analysis_id: ID of the analysis
        request: Approval decision (approved=True/False, optional feedback)
        analysis: Analysis object (injected by dependency)

    Returns:
        ApprovalResponse with workflow result

    Example:
        POST /api/v1/approval/approve/123
        {
            "approved": true,
            "feedback": null
        }
    """
    # Create thread_id from analysis_id
    thread_id = f"analysis_{analysis_id}"

    try:
        # Get the checkpoint to verify workflow is paused
        checkpoint = checkpoint_manager.get_checkpoint(thread_id)
        if not checkpoint:
            raise HTTPException(
                status_code=404,
                detail="No pending approval found for this analysis",
            )

        # Resume workflow with approval decision
        config = create_config(thread_id)

        # Invoke workflow with approval state update
        result = compiled_workflow_with_hitl.invoke(
            {
                "approved": request.approved,
                "approval_feedback": request.feedback,
            },
            config=config,
        )

        # Check if workflow completed or needs another approval
        if result.get("requires_approval"):
            return ApprovalResponse(
                success=True,
                status="awaiting_approval",
                message="Action processed, but another approval is required",
                agent_response=None,
            )
        elif result.get("status") == "completed":
            return ApprovalResponse(
                success=True,
                status="completed",
                message="Workflow completed successfully"
                if request.approved
                else "Workflow terminated by user",
                agent_response=result.get("agent_response"),
            )
        else:
            return ApprovalResponse(
                success=True,
                status=result.get("status", "unknown"),
                message="Workflow status updated",
                agent_response=result.get("agent_response"),
            )

    except HTTPException:
        raise
    except Exception as e:
        return ApprovalResponse(
            success=False,
            status="error",
            message=f"Error processing approval: {str(e)}",
            error=str(e),
        )


@router.get("/pending", response_model=PendingApprovalsResponse)
async def get_pending_approvals(db: Session = Depends(get_db)):
    """Get all workflows awaiting user approval

    Returns:
        List of pending approvals across all analyses

    Example:
        GET /api/v1/approval/pending
        Response: {
            "count": 2,
            "approvals": [
                {
                    "thread_id": "analysis_123",
                    "analysis_id": 123,
                    "approval_type": "code_execution",
                    ...
                }
            ]
        }
    """
    try:
        # Get pending approvals from checkpoint manager
        pending = checkpoint_manager.get_pending_approvals()

        # Enrich with analysis information
        approvals = []
        for item in pending:
            thread_id = item["thread_id"]

            # Extract analysis_id from thread_id (format: "analysis_{id}")
            try:
                analysis_id = int(thread_id.split("_")[1])
            except (IndexError, ValueError):
                analysis_id = 0

            approvals.append(
                PendingApprovalInfo(
                    thread_id=thread_id,
                    analysis_id=analysis_id,
                    approval_type=item["approval_type"],
                    approval_context=item["approval_context"],
                    created_at=item["created_at"],
                    status="awaiting_approval",
                )
            )

        return PendingApprovalsResponse(count=len(approvals), approvals=approvals)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching pending approvals: {str(e)}"
        )


@router.get("/status/{analysis_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    analysis_id: int, analysis: Analysis = Depends(get_analysis_or_404)
):
    """Get current status of a workflow execution

    Args:
        analysis_id: ID of the analysis
        analysis: Analysis object (injected by dependency)

    Returns:
        Workflow status including approval requirements

    Example:
        GET /api/v1/approval/status/123
        Response: {
            "thread_id": "analysis_123",
            "status": "awaiting_approval",
            "requires_approval": true,
            "approval_type": "code_execution",
            ...
        }
    """
    thread_id = f"analysis_{analysis_id}"

    try:
        # Get the checkpoint
        checkpoint = checkpoint_manager.get_checkpoint(thread_id)

        if not checkpoint:
            raise HTTPException(
                status_code=404, detail="No workflow found for this analysis"
            )

        # Extract state from checkpoint
        # Note: Checkpoint structure may vary - adjust based on actual LangGraph API
        state = checkpoint.get("checkpoint", {})

        return WorkflowStatusResponse(
            thread_id=thread_id,
            status=state.get("status", "unknown"),
            requires_approval=state.get("requires_approval", False),
            approval_type=state.get("approval_type"),
            approval_context=state.get("approval_context"),
            agent_response=state.get("agent_response"),
            trace=state.get("trace", []),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching workflow status: {str(e)}"
        )


@router.delete("/cancel/{analysis_id}")
async def cancel_workflow(
    analysis_id: int, analysis: Analysis = Depends(get_analysis_or_404)
):
    """Cancel a workflow and delete its checkpoint

    This terminates the workflow and removes all saved state.

    Args:
        analysis_id: ID of the analysis
        analysis: Analysis object (injected by dependency)

    Returns:
        Success message

    Example:
        DELETE /api/v1/approval/cancel/123
        Response: {
            "success": true,
            "message": "Workflow cancelled and checkpoint deleted"
        }
    """
    thread_id = f"analysis_{analysis_id}"

    try:
        # Delete the checkpoint
        deleted = checkpoint_manager.delete_thread(thread_id)

        if deleted:
            return {
                "success": True,
                "message": "Workflow cancelled and checkpoint deleted",
            }
        else:
            raise HTTPException(
                status_code=404, detail="No workflow checkpoint found to cancel"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error cancelling workflow: {str(e)}"
        )


@router.post("/start/{analysis_id}", response_model=WorkflowStatusResponse)
async def start_hitl_workflow(
    analysis_id: int,
    request: StartWorkflowRequest,
    analysis: Analysis = Depends(get_completed_analysis_or_400),
):
    """Start a new HITL workflow for an analysis

    This initializes a workflow with checkpointing and approval gates.

    Args:
        analysis_id: ID of the analysis
        request: Start workflow request with user_message
        analysis: Completed analysis object (injected by dependency)

    Returns:
        Initial workflow status

    Example:
        POST /api/v1/approval/start/123
        {
            "user_message": "Show me correlations in the data"
        }
    """
    thread_id = f"analysis_{analysis_id}"

    try:
        # Initialize state with user's actual message
        state = initialize_state(
            file_path=analysis.file_path,
            filename=analysis.filename,
            user_message=request.user_message,
            data_profile=analysis.data_profile,
            analysis_results=analysis.analysis_results,
            insights=analysis.insights,
        )

        # Create config with thread_id
        config = create_config(thread_id)

        # Start workflow (will pause at first approval gate)
        result = compiled_workflow_with_hitl.invoke(state, config=config)

        return WorkflowStatusResponse(
            thread_id=thread_id,
            status=result.get("status", "running"),
            requires_approval=result.get("requires_approval", False),
            approval_type=result.get("approval_type"),
            approval_context=result.get("approval_context"),
            agent_response=result.get("agent_response"),
            trace=result.get("trace", []),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error starting HITL workflow: {str(e)}"
        )
