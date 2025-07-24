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
The application supports both SQLite (default for development) and MySQL (for production).

#### Environment Files
- `.env` - Development configuration (default: SQLite)
- `.env.production` - Production configuration (MySQL)

#### SQLite Configuration (Default)
```bash
DB_TYPE=sqlite
DB_PATH=task_dashboard.db
```

#### MySQL Configuration
```bash
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=task_dashboard
```

To use MySQL, either:
1. Set `DB_TYPE=mysql` in your .env file
2. Or use the `.env.production` file

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

### Modular Code Structure (Post-Refactor)
```
task_dashboard/
├── task_dashboard.py    # Main Reflex app with State management
├── api.py              # FastAPI REST endpoints with authentication
├── auth.py             # Authentication utilities and password hashing
├── database.py         # SQLAlchemy models and DB configuration
├── models.py           # Pydantic data models (Task, User)
├── state.py            # Reflex State class with business logic
├── components.py       # Reusable UI components
├── modals.py           # Modal dialogs for forms
├── translations.py     # Multi-language support system
├── rate_limit_config.py # Rate limiting configuration
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
- **Rate Limiting**: All endpoints protected with rate limiting to prevent abuse

### Security Features
- **Password Hashing**: Secure bcrypt password hashing for user credentials
- **Rate Limiting**: API rate limiting using slowapi to prevent brute force attacks
- **Input Validation**: Comprehensive input validation and sanitization
- **Authentication**: JWT-based authentication with Bearer token validation
- **XSS Protection**: Input sanitization using bleach to prevent cross-site scripting

## Development Notes
- Database auto-migrates on startup
- Test database uses separate SQLite files (test_tasks.db)
- All test scripts must be placed in the `tests/` directory
- User management system with individual task dashboards implemented
- Authentication required for API endpoints via Bearer tokens
- Responsive design with dark mode support
- Real-time statistics and filtering
- Multi-page navigation system (Tasks/Statistics)
- Modern statistics dashboard with gradient cards and progress indicators
- Version 1.2.0 released with enhanced security features and rate limiting
- Rate limiting implemented using slowapi for API protection
- Enhanced authentication with bcrypt password hashing

## Key Architecture Patterns

### Component Architecture
- **Separation of Concerns**: UI components, state logic, and data models are modularized
- **Reusable Components**: task_item, theme_toggle, auth_buttons are reusable across pages
- **Modal System**: Centralized modal dialogs for forms (add task, login, register)
- **Translation System**: Custom multilingual support with 60+ translated keys

### State Management
- **Centralized State**: Single State class handles all business logic
- **Reactive Updates**: Reflex automatically re-renders on state changes
- **Database Sync**: State methods directly interact with SQLAlchemy models
- **User Isolation**: All operations are scoped to authenticated user
- **Language Management**: Real-time language switching with reactive translation updates

### Translation System
- **Custom i18n**: Dictionary-based translation manager with Chinese/English support
- **Reactive Translations**: All UI elements update instantly on language change
- **Select Options**: Custom translated dropdown options using rx.cond and rx.match
- **State Variables**: 60+ reactive translation variables for complete UI localization

### Testing Strategy
- **API Tests**: FastAPI TestClient for REST endpoint testing
- **Auth Tests**: Dedicated authentication flow testing
- **Database Tests**: Isolated test database with cleanup
- **Translation Tests**: Verify multilingual UI consistency
- **Security Tests**: Authentication security validation and rate limiting tests
- **Rate Limiting Tests**: Verify API rate limiting functionality

## Common Development Tasks

### Adding a New Language
1. Edit `task_dashboard/translations.py`
2. Add new language dictionary in the `translations` dictionary
3. Add language to `get_available_languages()` method
4. Restart the application

Example structure for new language:
```python
"es": {
    "app_title": "Panel de Tareas",
    "sign_in": "Iniciar Sesión",
    # ... add all required translation keys
}
```

### Deploying the Application

#### Deployment Files
The application includes deployment configuration files in the `deploy/` directory:
- `nginx.conf` - Nginx reverse proxy configuration
- `task-dashboard.service` - Systemd service file for running the application
- `deploy.sh` - Automated deployment script that uses environment variables
- `README.md` - Deployment instructions

#### Deployment Process
1. Set the required environment variables:
   ```bash
   export DOMAIN_NAME=your-domain.com
   export SSL_CERT_PATH=/path/to/certificate.crt
   export SSL_KEY_PATH=/path/to/private.key
   export APP_PATH=/path/to/task-dashboard
   export VENV_PATH=/path/to/venv
   export SERVICE_USER=www-data
   ```

2. Run the automated deployment script:
   ```bash
   cd deploy/
   ./deploy.sh all
   ```

3. Start the service:
   ```bash
   sudo systemctl start task-dashboard
   ```

#### Environment Configuration
For production deployment, use the `.env.production` file with MySQL configuration:
```bash
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=task_dashboard
```

### Adding New Task Fields
1. Update `TaskModel` in `database.py` with new column
2. Update `Task` Pydantic model in `models.py`
3. Update `TaskCreate` and `TaskUpdate` models in `api.py`
4. Update state management in `state.py`
5. Update UI components in `components.py` and `task_dashboard.py`
6. Update API endpoints in `api.py`
7. Add translations in `translations.py`

### Adding New API Endpoints
1. Define Pydantic models for request/response in `api.py`
2. Add new endpoint with proper authentication
3. Implement business logic using database models
4. Add comprehensive tests in `tests/`
5. Update API documentation with docstrings
6. Add rate limiting decorators to new endpoints

### Modifying Database Schema
1. Update SQLAlchemy models in `database.py`
2. The application will auto-migrate on startup
3. Update Pydantic models in `models.py`
4. Update API models in `api.py`
5. Update state management in `state.py`
6. Update UI components as needed

### Implementing Rate Limiting
1. Update rate limits in `rate_limit_config.py`
2. Add rate limiting decorators to new endpoints
3. Test rate limiting behavior in development
4. Monitor rate limiting in production

### Enhancing Security
1. Review authentication flow in `auth.py`
2. Update password validation rules if needed
3. Add new security tests in `tests/test_auth_security.py`
4. Verify input validation in API endpoints