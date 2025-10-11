#!/usr/bin/env python3
"""
Setup script for DataQuest AI backend tests.
Creates necessary files and directories for testing.

Run with: python setup_tests.py
"""

import os


def create_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"✅ Created directory: {path}")
    else:
        print(f"📁 Directory exists: {path}")


def create_file(path, content=""):
    """Create file if it doesn't exist"""
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(content)
        print(f"✅ Created file: {path}")
    else:
        print(f"📄 File exists: {path}")


def main():
    """Set up test environment"""
    print("🚀 Setting up DataQuest AI test environment...")

    # Get backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"📍 Backend directory: {backend_dir}")

    # Create tests directory
    tests_dir = os.path.join(backend_dir, "tests")
    create_directory(tests_dir)

    # Create tests/__init__.py
    init_content = '''# backend/tests/__init__.py
"""
Test package for DataQuest AI backend.
Contains test cases for API endpoints, database models, and business logic.
"""

import os
import sys

# Add backend root to Python path for imports
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)
'''
    create_file(os.path.join(tests_dir, "__init__.py"), init_content)

    # Create app/__init__.py files if they don't exist
    app_dirs = [
        "app",
        "app/core",
        "app/api",
        "app/api/v1",
        "app/models",
        "app/services",
    ]

    for dir_path in app_dirs:
        full_path = os.path.join(backend_dir, dir_path)
        create_directory(full_path)
        create_file(
            os.path.join(full_path, "__init__.py"), "# Package initialization\n"
        )

    # Create basic pytest configuration
    pytest_config = """[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
"""
    create_file(os.path.join(backend_dir, "pytest.ini"), pytest_config)

    # Check if required files exist
    required_files = ["main.py", "requirements.txt"]

    print("\n📋 Checking required files:")
    for file_name in required_files:
        file_path = os.path.join(backend_dir, file_name)
        if os.path.exists(file_path):
            print(f"✅ {file_name} exists")
        else:
            print(f"❌ {file_name} missing")

    print("\n🎉 Test environment setup complete!")
    print("\nNext steps:")
    print("1. Run: cd backend")
    print("2. Run: python setup_tests.py")
    print("3. Run: python -m pytest tests/test_basic_api.py -v")


if __name__ == "__main__":
    main()
