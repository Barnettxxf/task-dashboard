# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Technology Stack
- **Framework**: Reflex (Python reactive web framework)
- **Database**: SQLAlchemy ORM with SQLite/MySQL support
- **API**: FastAPI REST endpoints with comprehensive Swagger docs
- **Styling**: Tailwind CSS via Reflex components
- **Backend**: Python 3.8+

## Core Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Full stack development (web UI + API)
reflex run                          # Dev server (http://localhost:3000)

# API-only development
python -m task_dashboard.api        # API server (http://localhost:8000)
uvicorn task_dashboard.api:api_app --reload --port 8000

# Production build
reflex export                       # Static build for deployment
```

### Database Configuration
Auto-creates SQLite database. For MySQL:
```bash
export DB_TYPE=mysql
export DB_HOST=localhost DB_PORT=3306
export DB_USER=root DB_PASSWORD=password
export DB_NAME=task_dashboard
```

### API Usage Examples
```bash
# List all tasks
curl http://localhost:8000/tasks

# Filter tasks
curl "http://localhost:8000/tasks?status=todo&priority=high"

# Create task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "New Task", "description": "Details", "priority": "high"}'

# Update task status
curl -X PATCH http://localhost:8000/tasks/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

## Architecture Overview

### Dual Interface Architecture
- **Web UI**: Reflex frontend with reactive state (port 3000)
- **REST API**: FastAPI endpoints (port 8000)
- **Database**: SQLAlchemy models auto-synced between interfaces

### Key Files Structure
```
task_dashboard/
├── task_dashboard.py    # Main Reflex app with State management
├── api.py              # FastAPI REST endpoints with Swagger docs
├── database.py         # SQLAlchemy models and DB configuration
└── __init__.py
```

### State Management Pattern
User Action → State Method → DB Update → Reactive Re-render
- State class manages all application state and database operations
- Real-time updates via reactive Reflex components
- Automatic state persistence to database

### Task Data Model
- **TaskModel**: SQLAlchemy entity (title, description, status, priority, due_date)
- **Task**: Pydantic model for API responses and frontend state
- Status: todo, in_progress, done
- Priority: low, medium, high

## API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Development Notes
- Database auto-migrates on startup
- Sample data auto-creates if database is empty
- Both web UI and API share the same database models
- Hot reload enabled for both Reflex and FastAPI servers

## Additional Memories
- to memorize