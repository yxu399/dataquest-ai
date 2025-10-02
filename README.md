# DataQuest AI - Intelligent Data Analysis Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-blue.svg)](https://www.typescriptlang.org/)
[![Claude AI](https://img.shields.io/badge/Claude-3.5_Sonnet-purple.svg)](https://www.anthropic.com/)

DataQuest AI is a full-stack data analysis platform that combines automated data profiling, AI-powered insights, and conversational data exploration. Upload CSV files and interact with your data through natural language queries while generating interactive visualizations.

## 🚀 Features

- **📊 Automated Data Analysis**: Intelligent profiling of CSV files with statistical summaries
- **🤖 AI-Powered Chat Interface**: Conversational data exploration using Claude 3.5 Sonnet
- **📈 Interactive Visualizations**: Dynamic charts powered by Plotly.js (scatter, bar, histogram, correlation heatmaps, box plots)
- **⚡ Real-time Processing**: Live analysis progress tracking with WebSocket-like updates
- **🔄 Fallback Intelligence**: Rule-based responses when AI services are unavailable
- **🐳 Docker Ready**: Containerized deployment with Docker Compose

## 🏗️ Architecture

DataQuest AI follows a modern full-stack architecture:

- **Frontend**: React + TypeScript with Vite, Tailwind CSS, and Plotly.js
- **Backend**: FastAPI (Python) with SQLAlchemy ORM
- **Database**: PostgreSQL for persistent storage
- **AI Integration**: Anthropic Claude API with LangGraph workflows
- **Data Processing**: Pandas + NumPy for statistical analysis

### 📋 Architecture Flow
For detailed system architecture and user query processing flow, see:
- [**User Query Flow Diagrams**](docs/architecture/user_query_flow_diagram.md) - Complete request/response flow from frontend to backend

## 💻 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM and migrations
- **LangGraph** - AI workflow orchestration
- **Pandas/NumPy** - Data analysis and processing
- **Anthropic Claude** - Large language model for insights
- **Plotly** - Chart data generation

### Frontend
- **React 18** - UI framework with hooks
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **TanStack Query** - Server state management
- **Plotly.js** - Interactive data visualizations
- **Axios** - HTTP client

### Infrastructure
- **PostgreSQL** - Primary database
- **Docker & Docker Compose** - Containerization
- **GitHub Actions** - CI/CD pipeline

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager (replaces pip)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dataquest-ai
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development Setup

#### Backend Setup
```bash
cd backend
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up complete development environment with uv
uv sync  # Creates venv + installs all deps (production + dev)

# Run the application with uv
uv run python main.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 📖 Usage

1. **Upload Data**: Drag and drop a CSV file onto the upload area
2. **Automatic Analysis**: The system automatically profiles your data and generates insights
3. **Interactive Chat**: Ask questions about your data in natural language:
   - "Show me the key insights"
   - "Create a correlation heatmap"
   - "What's the relationship between sales and profit?"
   - "Show distribution of categories"
4. **Dynamic Visualizations**: Charts are automatically generated based on your queries
5. **Explore Further**: Use the chart selector to switch between different visualization types

## 💬 Example Queries

DataQuest AI understands natural language queries about your data:

- **Insights**: "What are the main findings?" "Show key insights"
- **Correlations**: "Show relationships between variables" "Create correlation heatmap"
- **Distributions**: "Show me a histogram of sales" "Bar chart of categories"
- **Comparisons**: "Compare revenue across departments" "How does age vary by region?"
- **Column-specific**: "Analyze the profit column" "What affects customer satisfaction?"

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://dataquest_user:your_password@localhost:5432/dataquest_ai

# AI Services
ANTHROPIC_API_KEY=your_anthropic_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=dataquest-ai

# Application
ENVIRONMENT=development
SECRET_KEY=your-secret-key-change-in-production
MAX_FILE_SIZE_MB=50
```

### AI Service Behavior

The system provides intelligent fallbacks:
- **With AI**: Uses Claude 3.5 Sonnet for natural language understanding
- **Without AI**: Falls back to rule-based pattern matching and contextual responses

## 📁 Project Structure

```
dataquest-ai/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── agents/          # LangGraph AI workflows
│   │   ├── core/            # Configuration & database
│   │   ├── models/          # Database models & schemas
│   │   └── services/        # Business logic
│   ├── tests/               # Backend tests
│   ├── uploads/             # File upload storage
│   ├── main.py             # FastAPI application
│   └── pyproject.toml      # Python dependencies (uv)
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API client
│   │   └── types/          # TypeScript definitions
│   ├── package.json       # Node.js dependencies
│   └── vite.config.ts     # Vite configuration
├── docs/
│   ├── architecture/      # Technical documentation
│   └── api/              # API documentation
├── database/
│   ├── init/             # Database initialization
│   └── migrations/       # Schema migrations
├── docker-compose.yml    # Docker services
└── README.md            # Project documentation
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
uv run pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
# Start services
docker-compose up -d

# Run integration tests with uv
cd backend
uv run python -m pytest tests/test_basic_api.py
```

## 🚢 Deployment

### Production Docker
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Setup
- Configure production database credentials
- Set secure SECRET_KEY
- Configure AI service API keys
- Set up proper CORS origins
- Configure file upload limits
