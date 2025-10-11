# DataQuest AI Documentation

Welcome to the DataQuest AI documentation! This directory contains comprehensive technical documentation for the platform.

## 📁 Documentation Structure

### Architecture Documentation
- **[User Query Flow](architecture/user_query_flow_diagram.md)** - Complete system flow diagrams showing how user queries are processed from frontend to backend
- **[System Architecture](architecture/)** - High-level system design and component relationships

### API Documentation  
- **[API Reference](api/)** - Detailed endpoint documentation and examples
- **Interactive Docs** - Available at `/docs` when running the backend locally

## 🔍 Quick Navigation

| Topic | Description | Location |
|-------|-------------|----------|
| **System Flow** | How user queries flow through the system | [Architecture Diagrams](architecture/user_query_flow_diagram.md) |
| **API Endpoints** | REST API documentation | [API Docs](api/) |
| **Setup Guide** | Installation and configuration | [Main README](../README.md) |
| **Component Guide** | Frontend/backend component structure | [Main README](../README.md#project-structure) |

## 📊 Architecture Overview

DataQuest AI is built with a modern full-stack architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend │◄───┤   FastAPI Backend │◄───┤  PostgreSQL DB  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         │                        ▼                       │
         │              ┌──────────────────┐              │
         │              │   Claude 3.5 AI  │              │
         │              └──────────────────┘              │
         │                                                │
         └──────────────── User Interaction ──────────────┘
```

## 🚀 Getting Started

1. **New to DataQuest AI?** Start with the [main README](../README.md)
2. **Want to understand the system?** Check out the [architecture diagrams](architecture/user_query_flow_diagram.md)
3. **Building integrations?** See the [API documentation](api/)
4. **Contributing code?** Review the project structure in the [main README](../README.md#project-structure)

## 📝 Document Conventions

- **Diagrams**: Written in Mermaid format for GitHub compatibility
- **Code Examples**: Include both request and response examples
- **Links**: Use relative paths for internal documentation
- **Updates**: Keep documentation synchronized with code changes

## 🔄 Keeping Docs Updated

When making changes to the codebase:
1. Update relevant documentation files
2. Regenerate architecture diagrams if system flow changes  
3. Update API documentation for endpoint changes
4. Test all documentation links and examples

---

📚 **Need Help?** Check the [main README](../README.md) or open an issue on GitHub.