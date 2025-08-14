from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, Float
from sqlalchemy.sql import func
import sys
import os

# Add the app directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base

class Analysis(Base):
    """Model for storing analysis sessions"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    
    # Data profile information
    data_profile = Column(JSON, nullable=True)
    
    # Analysis results
    analysis_results = Column(JSON, nullable=True)
    visualizations = Column(JSON, nullable=True)
    insights = Column(JSON, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

class UploadedFile(Base):
    """Model for tracking uploaded files"""
    __tablename__ = "uploaded_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=True)
    
    # File validation
    is_valid = Column(Boolean, default=False)
    validation_message = Column(Text, nullable=True)
    
    # Processing status
    processed = Column(Boolean, default=False)
    analysis_id = Column(Integer, nullable=True)  # References analyses.id
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

class SystemHealth(Base):
    """Model for system health monitoring"""
    __tablename__ = "system_health"
    
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)  # healthy, unhealthy, degraded
    response_time_ms = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())