# Task Dashboard

A modern, full-stack task management application built with Reflex (Python reactive web framework) and FastAPI. Features a responsive web interface with real-time updates and a comprehensive REST API.

![Task Dashboard UI](dashboard-ui.png)

## Features

- **Web Interface**: Modern, responsive UI with drag-and-drop task management
- **REST API**: Full CRUD operations with filtering, search, and pagination
- **Real-time Updates**: Instant synchronization between web UI and database
- **Task Filtering**: Filter by status, priority, and search terms
- **Task Statistics**: Real-time completion rates and task counts
- **Dark Mode**: Toggle between light and dark themes
- **Database**: SQLite by default, MySQL support available
- **API Documentation**: Auto-generated Swagger/OpenAPI docs

## Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd task-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the development server:
```bash
reflex run
```

4. Open your browser to [http://localhost:3000](http://localhost:3000)

## Development

### Running the Application

#### Full Stack (Web UI + API)
```bash
# Development server with hot reload
reflex run

# Access at http://localhost:3000
```

#### API Only
```bash
# Run API server on port 8000
python -m task_dashboard.api

# Or with uvicorn directly
uvicorn task_dashboard.api:api_app --reload --port 8000
```

#### Production Build
```bash
# Generate static build for deployment
reflex export
```

### Database Configuration

The application uses SQLite by default. To use MySQL:

```bash
export DB_TYPE=mysql
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=password
export DB_NAME=task_dashboard
```

### Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python tests/test_api.py -v

# Run with coverage
python -m pytest tests/ --cov=task_dashboard
```

## API Usage

The REST API is available at `http://localhost:8000` when running the API server.

### Endpoints

- **GET** `/tasks` - List all tasks with optional filtering
- **POST** `/tasks` - Create a new task
- **GET** `/tasks/{id}` - Get a specific task
- **PUT** `/tasks/{id}` - Update a task
- **PATCH** `/tasks/{id}/status` - Update task status only
- **DELETE** `/tasks/{id}` - Delete a task
- **GET** `/health` - Health check endpoint

### API Examples

```bash
# List all tasks
curl http://localhost:8000/tasks

# Filter tasks by status and priority
curl "http://localhost:8000/tasks?status=todo&priority=high"

# Search tasks
curl "http://localhost:8000/tasks?search=urgent"

# Create a new task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive README and API docs",
    "priority": "high",
    "due_date": "2024-12-31"
  }'

# Update task status
curl -X PATCH http://localhost:8000/tasks/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

### API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Architecture

### Technology Stack
- **Frontend**: Reflex (Python reactive web framework)
- **Backend**: FastAPI with SQLAlchemy ORM
- **Database**: SQLite (development) / MySQL (production)
- **Styling**: Tailwind CSS with Reflex components
- **Testing**: pytest with FastAPI TestClient

### Project Structure
```
task-dashboard/
├── task_dashboard/
│   ├── __init__.py
│   ├── task_dashboard.py    # Main Reflex app
│   ├── api.py              # FastAPI endpoints
│   └── database.py         # SQLAlchemy models
├── tests/
│   ├── __init__.py
│   └── test_api.py         # API tests
├── assets/
│   └── favicon.ico
├── requirements.txt        # Python dependencies
├── rxconfig.py            # Reflex configuration
└── task_dashboard.db      # SQLite database
```

### State Management
The application uses Reflex's reactive state management:
- User actions trigger state methods
- State methods update the database
- Database changes automatically re-render the UI
- All state is synchronized between web UI and database

## Task Model

Each task contains:
- **title**: Task title (required)
- **description**: Detailed description (optional)
- **status**: todo, in_progress, or done
- **priority**: low, medium, or high
- **due_date**: Optional due date (YYYY-MM-DD format)
- **created_at**: Auto-generated creation timestamp
- **updated_at**: Auto-generated update timestamp

## Features in Detail

### Web Interface
- **Kanban-style columns**: Todo, In Progress, Done
- **Task statistics**: Real-time counters and completion rates
- **Advanced filtering**: Filter by status, priority, search terms
- **Sorting**: Sort by creation date, due date, priority, or title
- **Quick actions**: Edit, delete, and update status
- **Responsive design**: Works on desktop, tablet, and mobile

### API Features
- **Full CRUD operations**: Create, read, update, delete tasks
- **Filtering**: Filter by status, priority, and search terms
- **Validation**: Input validation and error handling
- **Pagination**: Support for large datasets
- **Health checks**: API health monitoring endpoint

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `python -m pytest tests/`
6. Commit your changes: `git commit -am 'Add new feature'`
7. Push to the branch: `git push origin feature-name`
8. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions or issues:
- Check the [API documentation](http://localhost:8000/docs)
- Review the [test files](tests/) for usage examples
- Open an issue on the repository