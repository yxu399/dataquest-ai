# UV Migration Guide

DataQuest AI has migrated from pip to uv for faster dependency management and improved development experience.

## 🚀 What Changed

- **Dependency Management**: `requirements.txt` → `pyproject.toml`
- **Package Manager**: `pip` → `uv`
- **Docker Build**: Now uses uv for faster container builds
- **Development Workflow**: New commands for dependency management

## ⚡ Benefits

- **10-100x faster** package installation
- **Unified tooling** - one tool for virtual environments and dependencies  
- **Better dependency resolution** and conflict handling
- **Faster Docker builds** and CI/CD pipelines

## 🛠️ Installation

### Install uv
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Alternative: with pip
pip install uv
```

## 📋 New Commands

### Development Setup
```bash
cd backend

# Create virtual environment and install dependencies
uv sync

# Or manually:
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r pyproject.toml
```

### Common Tasks (All Dependency Management with uv)
```bash
# Install new production dependency (auto-updates pyproject.toml)
uv add fastapi

# Install dev dependency (adds to [tool.uv.dev-dependencies])
uv add --dev pytest

# Install with version constraints
uv add "pandas>=2.0,<3.0"

# Install from git repository
uv add git+https://github.com/user/repo.git

# Remove dependency (removes from pyproject.toml)
uv remove package-name

# Update all dependencies to latest versions
uv sync --upgrade

# Install exact dependencies from lockfile
uv sync --frozen

# Run commands in virtual environment
uv run python main.py
uv run pytest
uv run python -m pytest tests/specific_test.py

# Show installed packages
uv pip list
uv pip show package-name

# Check for outdated packages
uv pip list --outdated
```

### Docker (No Changes)
```bash
# Docker usage remains the same
docker-compose up -d
docker-compose build backend
```

## 🔄 Migration Steps for Existing Developers

1. **Install uv** (see installation section above)

2. **Remove old virtual environment** (if exists):
   ```bash
   cd backend
   rm -rf venv/  # or whatever your venv was named
   ```

3. **Set up new environment**:
   ```bash
   uv sync
   ```

4. **Test the setup**:
   ```bash
   uv run python test_uv_migration.py
   ```

5. **Verify API works**:
   ```bash
   uv run python main.py
   # Visit http://localhost:8000/docs
   ```

### ⚠️ Always Use `uv run` for Python Commands

**Why use `uv run`?**
- Ensures you're using the correct virtual environment
- Automatically activates the uv-managed environment
- No need to manually activate/deactivate virtual environments
- Consistent behavior across different systems

## 🐛 Troubleshooting

### Import Errors
- Run `uv sync` to ensure all dependencies are installed
- Check that you're in the correct directory (`backend/`)
- Verify Python version: `python --version` (should be 3.11+)

### Virtual Environment Issues
```bash
# Create fresh environment
rm -rf .venv/
uv venv
uv sync
```

### Docker Build Issues
```bash
# Rebuild containers from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up
```

## 📚 Key Files

- **`pyproject.toml`** - Main configuration file (replaces requirements.txt)
- **`uv.lock`** - Lock file for reproducible builds (auto-generated)
- **`requirements.txt`** - Kept for backwards compatibility (deprecated)

## ⚠️ Important Notes

- **pyproject.toml** is now the source of truth for dependencies
- **requirements.txt** is kept for backwards compatibility but is deprecated
- **uv.lock** should be committed to git for reproducible builds
- **Docker builds** are significantly faster with uv
- **CI/CD pipelines** will automatically benefit from faster builds

## 🎯 Command Reference

| Task | Old (pip) | New (uv) |
|------|-----------|----------|
| Install deps | `pip install -r requirements.txt` | `uv sync` |
| Add package | `pip install package` | `uv add package` |
| Remove package | `pip uninstall package` | `uv remove package` |
| List packages | `pip list` | `uv pip list` |
| **Run script** | `python script.py` | `uv run python script.py` |
| **Run main app** | `python main.py` | `uv run python main.py` |
| **Run tests** | `pytest` or `python -m pytest` | `uv run pytest` |
| Activate venv | `source venv/bin/activate` | Not needed with `uv run` |

## 🆘 Need Help?

- **uv Documentation**: https://docs.astral.sh/uv/
- **Migration Issues**: Check UV_MIGRATION_GUIDE.md
- **Team Support**: Ask in development chat/channels

---

🚀 **Welcome to faster Python development with uv!**