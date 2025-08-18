from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import csv
import tempfile
from typing import Optional
from sqlalchemy.sql import func
import asyncio
from app.services.analysis_service import analysis_service

from app.core.database import get_db
from app.core.config import settings
from app.models.database import Analysis
from app.models.schemas import FileUploadResponse, ErrorResponse
from app.models.schemas import AnalysisStatus, AnalysisResults

router = APIRouter()

def validate_csv_file(file: UploadFile) -> tuple[bool, str, Optional[dict]]:
    """Validate uploaded CSV file"""
    
    # Check file extension
    if not file.filename.lower().endswith('.csv'):
        return False, "File must be a CSV file", None
    
    # Check file size (convert MB to bytes)
    max_size = settings.max_file_size_mb * 1024 * 1024
    
    # Read file content for validation
    content = file.file.read()
    file.file.seek(0)  # Reset file pointer
    
    if len(content) > max_size:
        return False, f"File size exceeds {settings.max_file_size_mb}MB limit", None
    
    if len(content) == 0:
        return False, "File is empty", None
    
    # Validate CSV format
    try:
        # Write to temporary file for CSV validation
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.csv') as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Try to read CSV
        with open(temp_path, 'r', encoding='utf-8') as csvfile:
            # Detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            # Read first few rows
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            rows = []
            for i, row in enumerate(reader):
                if i >= 5:  # Only read first 5 rows for validation
                    break
                rows.append(row)
            
            if not rows:
                os.unlink(temp_path)
                return False, "CSV file has no data rows", None
            
            file_info = {
                "rows_sample": len(rows),
                "columns": list(rows[0].keys()) if rows else [],
                "delimiter": delimiter,
                "file_size_bytes": len(content)
            }
            
        # Clean up temp file
        os.unlink(temp_path)
        return True, "Valid CSV file", file_info
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
            except:
                pass
        return False, f"Invalid CSV format: {str(e)}", None

@router.get("/analysis/{analysis_id}/status", response_model=AnalysisStatus)
async def get_analysis_status(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Get analysis status by ID"""
    
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return AnalysisStatus(
        id=analysis.id,
        status=analysis.status,
        filename=analysis.filename,
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
        completed_at=analysis.completed_at,
        error_message=analysis.error_message
    )

@router.get("/analysis/{analysis_id}", response_model=AnalysisResults)
async def get_analysis_results(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Get complete analysis results by ID"""
    
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return AnalysisResults(
        id=analysis.id,
        filename=analysis.filename,
        status=analysis.status,
        data_profile=analysis.data_profile,
        analysis_results=analysis.analysis_results,
        visualizations=analysis.visualizations,
        insights=analysis.insights,
        created_at=analysis.created_at,
        completed_at=analysis.completed_at
    )

@router.post("/analysis/{analysis_id}/start")
async def start_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Start analysis for uploaded file"""
    
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis.status != 'uploaded':
        raise HTTPException(
            status_code=400, 
            detail=f"Analysis is already {analysis.status}. Can only start analysis for uploaded files."
        )
    
    # Update status to processing
    analysis.status = 'processing'
    from datetime import datetime
    analysis.updated_at = datetime.utcnow()
    db.commit()
    
    # Run analysis in background
    try:
        # For now, run synchronously (can be made async later)
        result = analysis_service.run_analysis(analysis_id)
        
        return {
            "success": True,
            "message": "Analysis completed",
            "analysis_id": analysis_id,
            "status": result.get("status", "completed"),
            "results_preview": {
                "data_shape": result.get("results", {}).get("data_profile", {}).get("shape"),
                "insights_count": len(result.get("results", {}).get("insights", []))
            }
        }
    except Exception as e:
        # Update analysis as failed
        analysis.status = 'failed'
        analysis.error_message = str(e)
        analysis.updated_at = datetime.utcnow()
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/analyses")
async def list_analyses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all analyses with pagination"""
    
    analyses = db.query(Analysis).offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "count": len(analyses),
        "analyses": [
            {
                "id": analysis.id,
                "filename": analysis.filename,
                "status": analysis.status,
                "created_at": analysis.created_at,
                "file_size": analysis.file_size
            }
            for analysis in analyses
        ]
    }

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and validate CSV file"""
    
    # Validate file
    is_valid, message, file_info = validate_csv_file(file)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs(settings.upload_dir, exist_ok=True)
        
        # Generate unique filename
        import uuid
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        stored_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(settings.upload_dir, stored_filename)
        
        # Save file
        file.file.seek(0)  # Reset file pointer
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        # Create database record
        analysis = Analysis(
            filename=file.filename,
            file_size=len(content),
            file_path=file_path,
            status='uploaded'
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        return FileUploadResponse(
            success=True,
            message="File uploaded successfully",
            file_id=analysis.id,
            filename=file.filename,
            file_size=len(content)
        )
        
    except Exception as e:
        # Clean up file if database operation fails
        if 'file_path' in locals() and os.path.exists(file_path):
            os.unlink(file_path)
        
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")