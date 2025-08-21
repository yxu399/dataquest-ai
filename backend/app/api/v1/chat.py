# backend/app/api/v1/chat.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.database import Analysis
from app.models.schemas import BaseResponse
from app.services.chat_service import ChatService
from pydantic import BaseModel

router = APIRouter()

# Request/Response Models
class ChatMessage(BaseModel):
    id: str
    type: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    analysis_id: Optional[int] = None
    chart_data: Optional[dict] = None
    chart_type: Optional[str] = None
    error: Optional[str] = None

class ChatRequest(BaseModel):
    analysis_id: int
    message: str
    conversation_history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    message: ChatMessage
    analysis: Optional[dict] = None
    chart_suggestion: Optional[str] = None
    error: Optional[str] = None

@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Send a chat message and get AI analysis response"""
    
    # Validate analysis exists and is completed
    analysis = db.query(Analysis).filter(Analysis.id == request.analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis.status != 'completed':
        raise HTTPException(
            status_code=400, 
            detail=f"Analysis must be completed first. Current status: {analysis.status}"
        )
    
    try:
        # Initialize chat service
        chat_service = ChatService()
        
        # Process the chat message with context
        response = await chat_service.process_message(
            user_message=request.message,
            analysis_data=analysis,
            conversation_history=request.conversation_history
        )
        
        # Create response message
        response_message = ChatMessage(
            id=f"assistant-{int(datetime.now().timestamp() * 1000)}",
            type="assistant",
            content=response["content"],
            timestamp=datetime.now(),
            analysis_id=request.analysis_id,
            chart_data=response.get("chart_data"),
            chart_type=response.get("chart_type")
        )
        
        return ChatResponse(
            message=response_message,
            analysis=response.get("analysis"),
            chart_suggestion=response.get("chart_type"),
            error=None
        )
        
    except Exception as e:
        # Return error message
        error_message = ChatMessage(
            id=f"error-{int(datetime.now().timestamp() * 1000)}",
            type="assistant",
            content=f"I'm sorry, I encountered an error processing your request: {str(e)}",
            timestamp=datetime.now(),
            analysis_id=request.analysis_id,
            error=str(e)
        )
        
        return ChatResponse(
            message=error_message,
            error=str(e)
        )

@router.get("/conversation/{analysis_id}")
async def get_conversation_history(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Get conversation history for an analysis (future enhancement)"""
    
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # For now, return empty history - could be enhanced to store chat history in DB
    return {
        "analysis_id": analysis_id,
        "conversation": [],
        "data_summary": {
            "shape": analysis.data_profile.get("shape") if analysis.data_profile else None,
            "columns": analysis.data_profile.get("columns") if analysis.data_profile else None,
            "insights_count": len(analysis.insights or [])
        }
    }