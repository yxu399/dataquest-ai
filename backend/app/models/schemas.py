from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime


# Base schemas
class BaseResponse(BaseModel):
    """Base response model"""

    success: bool
    message: str


# File upload schemas
class FileUploadResponse(BaseModel):
    """Response for file upload"""

    success: bool
    message: str
    file_id: Optional[int] = None
    filename: Optional[str] = None
    file_size: Optional[int] = None


class FileValidationResponse(BaseModel):
    """Response for file validation"""

    is_valid: bool
    message: str
    file_info: Optional[Dict[str, Any]] = None


# Analysis schemas
class AnalysisRequest(BaseModel):
    """Request for starting analysis"""

    file_id: int
    analysis_type: Optional[str] = "comprehensive"


class AnalysisStatus(BaseModel):
    """Analysis status response"""

    id: int
    status: str
    filename: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class DataProfile(BaseModel):
    """Data profiling results"""

    shape: tuple[int, int]
    columns: List[str]
    dtypes: Dict[str, str]
    missing_data: Dict[str, int]
    numeric_columns: List[str]
    categorical_columns: List[str]
    sample_data: List[Dict[str, Any]]
    full_data: Optional[List[Dict[str, Any]]] = None


class AnalysisResults(BaseModel):
    """Complete analysis results"""

    id: int
    filename: str
    status: str
    data_profile: Optional[DataProfile] = None
    analysis_results: Optional[Dict[str, Any]] = None
    visualizations: Optional[List[Dict[str, Any]]] = None
    insights: Optional[List[str]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


# Health check schemas
class HealthCheck(BaseModel):
    """Health check response"""

    status: str
    service: str
    version: str
    database_connected: Optional[bool] = None
    timestamp: datetime


# Error schemas
class ErrorResponse(BaseModel):
    """Error response model"""

    success: bool = False
    error: str
    detail: Optional[str] = None
