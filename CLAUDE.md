# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Technology Stack
- **Framework**: Reflex (Python reactive web framework)
- **Backend**: FastAPI with SQLAlchemy ORM
- **Database**: SQLite (default) / MySQL (production)
- **Authentication**: JWT-based user authentication with password hashing
- **Styling**: Tailwind CSS via Reflex components
- **Testing**: pytest with FastAPI TestClient

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

# Run tests
python -m pytest tests/ -v          # Run all tests
python tests/test_api.py -v         # Run API tests only
python tests/test_api_auth.py -v    # Run auth tests only
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
# Authentication
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "email": "user1@example.com", "password": "password123"}'

curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "password123"}'

# List all tasks (with auth)
curl -H "Authorization: Bearer user1" http://localhost:8000/tasks

# Filter tasks
curl -H "Authorization: Bearer user1" "http://localhost:8000/tasks?status=todo&priority=high"

# Create task
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer user1" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Task", "description": "Details", "priority": "high"}'

# Update task status
curl -X PATCH http://localhost:8000/tasks/1/status \
  -H "Authorization: Bearer user1" \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

## Architecture Overview

### Dual Interface Architecture
- **Web UI**: Reflex frontend (port 3000) with reactive state management
- **REST API**: FastAPI endpoints (port 8000) with Swagger documentation
- **Database**: SQLAlchemy models auto-synced between interfaces
- **Authentication**: User-specific task isolation with JWT tokens

### Key Files Structure
```
task_dashboard/
├── task_dashboard.py    # Main Reflex app with State management
├── api.py              # FastAPI REST endpoints with authentication
├── auth.py             # Authentication utilities and password hashing
├── database.py         # SQLAlchemy models and DB configuration
└── __init__.py
```

### State Management Pattern
User Action → State Method → DB Update → Reactive Re-render
- State class manages all application state and database operations
- Real-time updates via reactive Reflex components
- Automatic state persistence to database
- User-specific data isolation

### Task Data Model
- **TaskModel**: SQLAlchemy entity (user_id, title, description, status, priority, due_date)
- **Task**: Pydantic model for API responses
- **UserModel**: SQLAlchemy entity (username, email, password_hash)
- Status: todo, in_progress, done
- Priority: low, medium, high

### Authentication Flow
- Registration with unique username/email validation
- Login returns user info (used as Bearer token)
- All API endpoints require Authorization: Bearer <username>
- User-specific task filtering on all endpoints

## API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### API Endpoints
- **Auth**: POST /auth/register, POST /auth/login, GET /auth/me
- **Tasks**: GET /tasks, POST /tasks, GET /tasks/{id}, PUT /tasks/{id}, PATCH /tasks/{id}/status, DELETE /tasks/{id}
- **Health**: GET /health, GET /

## Development Notes
- Database auto-migrates on startup
- Test database uses separate SQLite files (test_tasks.db)
- All test scripts must be placed in the `tests/` directory
- User management system with individual task dashboards implemented
- Authentication required for API endpoints via Bearer tokens
- Responsive design with dark mode support
- Real-time statistics and filtering