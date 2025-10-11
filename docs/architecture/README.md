# Architecture Documentation

This directory contains technical architecture documentation for DataQuest AI, including system design, data flows, and component interactions.

## 📋 Architecture Documents

### System Flow Diagrams
- **[User Query Flow Diagrams](user_query_flow_diagram.md)** - Complete visual documentation of how user queries are processed through the system, from frontend input to AI response and chart generation

## 🏗️ High-Level Architecture

DataQuest AI follows a modern full-stack architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────┐
│                    Frontend Layer                   │
│  React + TypeScript + Tailwind CSS + Plotly.js    │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP/REST API
┌─────────────────────▼───────────────────────────────┐
│                  Backend Layer                      │
│        FastAPI + SQLAlchemy + LangGraph            │
└─────────────────────┬───────────────────────────────┘
                      │
        ┌─────────────▼──────────────┐
        │                            │
        ▼                            ▼
┌───────────────┐              ┌──────────────┐
│ PostgreSQL DB │              │ Claude 3.5   │
│   • Analysis  │              │ Sonnet API   │
│   • Results   │              │ • Insights   │
│   • Metadata  │              │ • Charts     │
└───────────────┘              └──────────────┘
```

## 🔄 Core Processing Flows

### 1. Data Upload & Analysis Flow
```
User uploads CSV → File validation → Database storage → 
Analysis workflow → AI processing → Results storage → 
Frontend display
```

### 2. Chat Interaction Flow  
```
User query → Context building → AI/Fallback processing → 
Chart suggestion → Response generation → Frontend update → 
Chart rendering
```

### 3. Real-time Updates Flow
```
Analysis start → Status polling → Progress updates → 
Completion notification → Results display
```

## 🧩 Component Architecture

### Frontend Components
- **Dashboard.tsx** - Main application container
- **FileUpload.tsx** - CSV file upload with validation
- **ChatInterface.tsx** - Conversational AI interface
- **Chart Components** - Interactive Plotly.js visualizations
- **API Service** - HTTP client with type safety

### Backend Components  
- **API Routers** - FastAPI endpoints with validation
- **Services** - Business logic and AI integration
- **Models** - Database schemas and API models
- **Agents** - LangGraph AI workflows

## 🔐 Security Architecture

### Data Protection
- Input validation and sanitization
- File type and size restrictions
- SQL injection prevention via ORM
- XSS protection in frontend

### API Security
- CORS configuration
- Request rate limiting (production)
- Error message sanitization
- Environment variable protection

## 🚀 Scalability Considerations

### Performance Optimizations
- Database indexing on analysis queries
- Frontend state management with React Query
- Lazy loading of chart components
- API response caching

### Horizontal Scaling
- Stateless backend design
- Database connection pooling
- Container orchestration ready
- Load balancer compatible

## 🔧 Technology Decisions

### Frontend Stack Rationale
- **React 18**: Modern hooks-based architecture
- **TypeScript**: Type safety and developer experience  
- **Vite**: Fast development and optimized builds
- **Tailwind CSS**: Utility-first styling efficiency
- **Plotly.js**: Rich interactive data visualizations

### Backend Stack Rationale
- **FastAPI**: High performance, automatic OpenAPI docs
- **SQLAlchemy**: Mature ORM with migration support
- **LangGraph**: AI workflow orchestration
- **Pandas**: Proven data analysis capabilities

## 📊 Data Architecture

### Database Schema
```sql
analyses
├── id (PRIMARY KEY)
├── filename
├── file_path  
├── status
├── data_profile (JSON)
├── analysis_results (JSON)
├── insights (JSON)
├── created_at
├── updated_at
└── completed_at
```

### Data Flow Patterns
1. **Upload** → Validation → Storage → Metadata persistence
2. **Analysis** → Processing → Results aggregation → JSON storage  
3. **Chat** → Context loading → AI processing → Response formatting

## 🔄 AI Integration Architecture

### LangGraph Workflow
```python
DataAnalysisState → ProfilerAgent → StatisticalAgent → 
InsightsAgent → Results
```

### Fallback Strategy
- Primary: Claude 3.5 Sonnet API
- Fallback: Rule-based pattern matching
- Context: Always uses actual data profile

## 🐳 Deployment Architecture

### Container Strategy
- **Frontend**: Nginx + React build
- **Backend**: Python + FastAPI + Uvicorn
- **Database**: PostgreSQL with persistent volumes
- **Orchestration**: Docker Compose

### Environment Management
- Development: Local containers
- Production: Cloud deployment ready
- Configuration: Environment variables
- Secrets: External secret management

---

📊 **Next Steps**: Review the [detailed flow diagrams](user_query_flow_diagram.md) to understand specific request/response patterns.