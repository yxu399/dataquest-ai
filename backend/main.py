from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from app.api.v1 import files

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import our modules with error handling
try:
    from app.core.config import settings
    from app.core.database import get_database, create_tables, test_database_connection
    from app.models.schemas import HealthCheck, BaseResponse
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    # Create minimal app for testing
    settings = None

# Create FastAPI application
app = FastAPI(
    title="DataQuest AI API",
    description="Intelligent Data Analysis Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(files.router, prefix="/api/v1/files", tags=["files"])

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001",  # Add this line
        "http://frontend:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("🚀 Starting DataQuest AI API...")
    
    if settings and test_database_connection:
        # Test database connection
        if test_database_connection():
            print("✅ Database connection successful")
            # Create tables
            create_tables()
            print("✅ Database tables ready")
        else:
            print("❌ Database connection failed")
    else:
        print("⚠️ Starting in minimal mode (some imports failed)")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and monitoring"""
    return {
        "status": "healthy",
        "service": "DataQuest AI API",
        "version": "1.0.0",
        "database_connected": False,  # Will be updated when DB is working
        "timestamp": datetime.utcnow().isoformat()
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to DataQuest AI API",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }

# Test endpoint
@app.get("/api/v1/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "success": True,
        "message": "API is working correctly!",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)