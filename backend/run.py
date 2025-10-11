#!/usr/bin/env python3
"""
Recommended way to run DataQuest AI backend.
This script should be run with: uv run python run.py
"""

import sys
import os


def run_app():
    """Run the FastAPI application"""
    print("🚀 Starting DataQuest AI Backend...")
    print("📍 Recommended command: uv run python run.py")
    print("🔗 API will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("-" * 50)

    # Import and run the main application
    try:
        import uvicorn
        from main import app

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True if os.getenv("ENVIRONMENT") == "development" else False,
        )
    except ImportError as e:
        print(f"❌ Error importing dependencies: {e}")
        print("🔧 Make sure you've run: uv sync")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_app()
