# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Technology Stack
- **Framework**: Reflex (Python reactive web framework)
- **Database**: SQLAlchemy ORM with SQLite/MySQL
- **API**: FastAPI REST endpoints
- **Styling**: Tailwind CSS via Reflex components

## Core Commands

### Development
```bash
pip install -r requirements.txt
reflex run                          # Dev server with API (http://localhost:3000)
python -m task_dashboard.api        # API server only (http://localhost:8000)
uvicorn task_dashboard.api:api_app --reload --port 8000  # Alternative API launch
reflex export                       # Static build for deployment
```

### Database
Auto-creates SQLite database. For MySQL:
```bash
export DB_TYPE=mysql
export DB_HOST=localhost DB_PORT=3306
export DB_USER=root DB_PASSWORD=password
export DB_NAME=task_dashboard
```

### API Usage
```bash
curl http://localhost:8000/tasks          # List tasks
curl http://localhost:8000/tasks/1        # Get task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "New", "priority": "high"}'
curl -X PATCH http://localhost:8000/tasks/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Architecture

### Dual Interface
- **Web UI**: Reflex frontend with reactive state (port 3000)
- **REST API**: FastAPI endpoints (port 8000)
- **Database**: SQLAlchemy models auto-synced

### Key Files
- `task_dashboard/task_dashboard.py`: Main app with State class
- `task_dashboard/database.py`: SQLAlchemy models and DB setup
- `task_dashboard/api.py`: FastAPI REST endpoints with rich Swagger docs
- `rxconfig.py`: Reflex configuration

### Launch Troubleshooting
If `python task_dashboard/api.py` fails, use:
- `python -m task_dashboard.api` (module import)
- `uvicorn task_dashboard.api:api_app --reload --port 8000` (direct uvicorn)

### State Pattern
User Action → State Method → DB Update → Reactive Re-render

### Task Model
- `TaskModel`: SQLAlchemy entity with title, description, status, priority, due_date
- `Task`: Pydantic model for API responses
- Supports todo/in_progress/done status and low/medium/high priority