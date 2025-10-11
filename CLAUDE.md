# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
- **Docker (Recommended)**: `docker-compose up -d` - Starts all services (PostgreSQL, backend, frontend)
- **Environment Check**: `docker-compose ps` - Check service status
- **Logs**: `docker-compose logs [service_name]` - View service logs

### Backend Development (Python/FastAPI with uv)
- **Setup environment**: `cd backend && uv sync` (installs all deps + creates venv)
- **Run locally**: `cd backend && uv run python main.py` (requires local PostgreSQL)
- **Run tests**: `cd backend && uv run pytest`
- **Run specific test**: `cd backend && uv run pytest tests/test_basic_api.py::TestBasicEndpoints::test_health_check -v`
- **Add production dependency**: `cd backend && uv add package-name`
- **Add dev dependency**: `cd backend && uv add --dev package-name`
- **Update dependencies**: `cd backend && uv sync --upgrade`
- **Remove dependency**: `cd backend && uv remove package-name`
- **Database check**: Backend includes automatic table creation on startup

### Frontend Development (React/TypeScript)
- **Run locally**: `cd frontend && npm run dev`
- **Build**: `cd frontend && npm run build`
- **Lint**: `cd frontend && npm run lint`
- **Test**: `cd frontend && npm test`
- **Type check**: `cd frontend && tsc --noEmit`

### Integration Testing
- **Full stack**: Start with `docker-compose up -d`, then run `cd backend && pytest`
- **API testing**: Backend runs on http://localhost:8000 with interactive docs at `/docs`
- **Frontend testing**: Frontend runs on http://localhost:3000

## Architecture Overview

### Request Flow Architecture
DataQuest AI processes user queries through a sophisticated multi-layer architecture:

1. **Frontend (React/TypeScript)**:
   - `ChatInterface.tsx` handles user input and conversation state
   - `apiService.sendChatMessage()` formats requests with conversation history
   - Real-time UI updates with loading states and auto-scroll

2. **Backend API Layer (FastAPI)**:
   - `/api/v1/chat/message` endpoint validates analysis status and routes requests
   - Request validation ensures analysis exists and is completed before processing
   - Automatic error handling and response formatting

3. **AI Processing Layer**:
   - `ChatService` in `app/services/chat_service.py` handles the core logic
   - **Dual-path processing**: Claude API (when ANTHROPIC_API_KEY available) or intelligent fallback
   - Context building from database analysis results, data profiles, and insights
   - Chart suggestion parsing and data preparation

4. **Data Processing**:
   - `simple_workflow.py` contains pandas-based analysis pipeline
   - Database stores analysis results as JSON in PostgreSQL
   - File uploads processed with CSV validation and delimiter detection

### Key Architectural Patterns

**AI Integration Strategy**: The system intelligently falls back to rule-based responses when Claude API is unavailable, using actual data context to provide meaningful responses. Both paths use the same data analysis results.

**Context Preservation**: Chat conversations maintain context through:
- Last 6 messages sent with each request for continuity
- Analysis data loaded from database for each chat interaction
- Dynamic chart suggestions based on available data types

**Chart Generation Pipeline**: 
- Frontend chart components (BarChart, ScatterPlot, etc.) receive data from chat responses
- Backend determines available chart types from data structure (numeric/categorical columns)
- Chart suggestions flow: User query → AI/fallback analysis → Chart type determination → Frontend rendering

**Database Schema Pattern**: The `Analysis` table stores all results as JSON fields (data_profile, analysis_results, insights), enabling flexible data storage while maintaining query performance.

### Service Dependencies
- **Database**: PostgreSQL with SQLAlchemy ORM, automatic table creation
- **AI Services**: Optional Anthropic Claude API (graceful degradation)
- **File Storage**: Local uploads directory with CSV processing
- **Frontend State**: TanStack Query for API state management, React hooks for UI state

### Testing Strategy
The codebase uses pytest for backend testing with these patterns:
- `TestBasicEndpoints` for API functionality
- `TestApplicationStartup` for configuration validation  
- `test_basic_api.py` covers core endpoints and CORS configuration
- Integration tests verify full request-response cycles

## Environment Configuration

### Required Environment Variables
```bash
# Database (required)
DATABASE_URL=postgresql://user:password@localhost:5432/dataquest_ai
POSTGRES_USER=dataquest_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=dataquest_ai

# AI Services (optional - system has fallbacks)
ANTHROPIC_API_KEY=your_anthropic_key
LANGCHAIN_API_KEY=your_langchain_key

# Application
ENVIRONMENT=development
```

### AI Service Behavior
- **With ANTHROPIC_API_KEY**: Uses Claude 3.5 Sonnet for natural language understanding
- **Without API key**: Automatically uses intelligent rule-based pattern matching
- Both modes leverage the same data analysis context and provide chart suggestions

## Development Patterns

### Adding New Dependencies with uv
- **Production dependency**: `uv add package-name` (automatically updates pyproject.toml)
- **Dev dependency**: `uv add --dev package-name` (adds to [tool.uv.dev-dependencies])
- **Optional dependency**: `uv add --optional extra-name package-name`
- **Version constraints**: `uv add "package-name>=1.0,<2.0"`
- **From git**: `uv add git+https://github.com/user/repo.git`
- **Update all**: `uv sync --upgrade`

### Adding New Chart Types
1. Create React component in `frontend/src/components/charts/`
2. Add chart type to `ChatService._get_chart_data()` method
3. Update available_charts logic in `_build_analysis_context()`
4. Add chart type recognition in fallback processing patterns
5. **Install any new Python viz dependencies**: `uv add new-viz-package`

### Extending Analysis Pipeline
- Modify `backend/app/agents/simple_workflow.py` for data processing changes
- Update database JSON schemas in `app/models/database.py`
- Extend Pydantic models in `app/models/schemas.py` for API responses
- **Add analysis dependencies**: `uv add pandas-extension scipy-stats`

### Chat Service Extension
- AI prompts are built in `_create_system_prompt()` with dataset context
- Fallback patterns use keyword matching in `_process_with_fallback()`
- Column mention extraction in `_extract_column_mentions()` enables contextual responses
- **Add AI dependencies**: `uv add new-llm-package`

### uv Dependency Management Patterns
- **Never edit pyproject.toml manually for dependencies** - use `uv add/remove`
- **Always commit uv.lock** for reproducible builds
- **Use `uv sync`** after pulling changes to update local environment
- **Development workflow**: `uv sync && uv run python main.py`
- **Testing workflow**: `uv run pytest` (automatically uses dev dependencies)

### Database Patterns
The system uses JSON storage for flexible data structures:
- `data_profile`: Column types, statistics, sample data
- `analysis_results`: Correlations, summaries, distributions  
- `insights`: Generated analysis insights
- Database sessions managed via dependency injection with `get_db()`