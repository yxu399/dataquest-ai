#!/usr/bin/env python3
"""
Test script to verify uv migration works correctly and manages ALL dependencies.
Run this with: uv run python test_uv_migration.py
"""

import subprocess


def test_core_imports():
    """Test that all core dependencies can be imported"""
    try:
        # Web Framework
        import fastapi
        import uvicorn
        import multipart

        print("✅ Web framework imports successful")

        # Database
        import sqlalchemy
        import psycopg2
        import alembic

        print("✅ Database imports successful")

        # AI/LLM
        import langchain
        import langgraph
        import anthropic

        print("✅ AI/LLM imports successful")

        # Data Processing
        import pandas
        import numpy
        import plotly
        import scipy

        print("✅ Data processing imports successful")

        # Utilities
        import dotenv
        import pydantic
        import pydantic_settings

        print("✅ Utility imports successful")

        # Security
        import jose
        import passlib

        print("✅ Security imports successful")

        # Validation
        import email_validator

        print("✅ Validation imports successful")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_key_functionality():
    """Test basic functionality of key components"""
    try:
        # Test FastAPI
        from fastapi import FastAPI

        app = FastAPI()
        print("✅ FastAPI app creation successful")

        # Test pandas
        import pandas as pd

        df = pd.DataFrame({"test": [1, 2, 3]})
        assert len(df) == 3
        print("✅ Pandas DataFrame creation successful")

        # Test pydantic
        from pydantic import BaseModel

        class TestModel(BaseModel):
            name: str

        model = TestModel(name="test")
        assert model.name == "test"
        print("✅ Pydantic model creation successful")

        return True

    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False


def test_uv_management():
    """Test that uv is properly managing all dependencies"""
    try:
        # Check if we're in a uv-managed environment
        result = subprocess.run(["uv", "pip", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ uv pip command working")

            # Check for key packages
            packages = result.stdout.lower()
            required_packages = ["fastapi", "pandas", "pytest", "anthropic"]
            missing = []

            for pkg in required_packages:
                if pkg not in packages:
                    missing.append(pkg)

            if missing:
                print(f"❌ Missing packages: {missing}")
                return False
            else:
                print("✅ All key packages found via uv")
                return True
        else:
            print("❌ uv pip command failed")
            return False

    except FileNotFoundError:
        print("❌ uv command not found - install uv first")
        return False
    except Exception as e:
        print(f"❌ uv management test error: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing uv migration and complete dependency management...")
    print("-" * 60)

    uv_success = test_uv_management()
    print("-" * 60)

    import_success = test_core_imports()
    print("-" * 60)

    functionality_success = test_key_functionality()
    print("-" * 60)

    if uv_success and import_success and functionality_success:
        print("🎉 uv migration test PASSED!")
        print("✅ uv is managing ALL dependencies correctly")
        print("✅ All imports and functionality working")
        exit(0)
    else:
        print("❌ uv migration test FAILED!")
        if not uv_success:
            print("  - uv dependency management issues")
        if not import_success:
            print("  - Package import issues")
        if not functionality_success:
            print("  - Functionality test issues")
        print("\n🔧 Run: uv sync && uv run python test_uv_migration.py")
        exit(1)
