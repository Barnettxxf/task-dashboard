"""RESTful API endpoints for task management.

This API provides comprehensive task management capabilities with full CRUD operations,
real-time filtering, and statistics. All endpoints return JSON responses and support
standard HTTP status codes.

## Authentication
No authentication required for this demo application.

## Rate Limiting
No rate limiting implemented.

## Base URL
- Development: `http://localhost:8000`
- Production: Configure via environment variables

## Response Format
All responses use standard JSON format with appropriate HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error
"""

from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from task_dashboard.database import db_manager, TaskModel

# Initialize FastAPI app with enhanced metadata
api_app = FastAPI(
    title="Task Dashboard API",
    description="Comprehensive task management API with full CRUD operations, filtering, and statistics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Task Dashboard Team",
        "url": "https://github.com/your-org/task-dashboard",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {"url": "http://localhost:8000", "description": "Development server"},
        {"url": "https://api.taskdashboard.com", "description": "Production server"},
    ],
    tags=[
        {"name": "tasks", "description": "Task management operations"},
        {"name": "health", "description": "API health and monitoring"},
    ]
)

# Pydantic models for API
class TaskCreate(BaseModel):
    """Model for creating a new task."""
    title: str = Field(description="Task title (required)")
    description: str = Field("", description="Detailed task description")
    priority: str = Field("medium", description="Task priority level")
    due_date: Optional[str] = Field(None, description="Due date in YYYY-MM-DD format")

class TaskUpdate(BaseModel):
    """Model for updating an existing task. All fields are optional."""
    title: Optional[str] = Field(None, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: Optional[str] = Field(None, description="Task status")
    priority: Optional[str] = Field(None, description="Task priority")
    due_date: Optional[str] = Field(None, description="Due date in YYYY-MM-DD format")

class TaskResponse(BaseModel):
    """Response model for task data."""
    id: int = Field(description="Unique task identifier")
    title: str = Field(description="Task title")
    description: str = Field(description="Task description")
    status: str = Field(description="Task status")
    priority: str = Field(description="Task priority")
    due_date: Optional[str] = Field(None, description="Due date in YYYY-MM-DD format")
    created_at: str = Field(description="Creation timestamp in ISO format")
    updated_at: str = Field(description="Last update timestamp in ISO format")

    class Config:
        from_attributes = True

class TaskStatusUpdate(BaseModel):
    """Model for updating only task status."""
    status: str = Field(description="New task status")

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(description="API status")
    database: str = Field(description="Database connection status")

class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str = Field(description="Error message")

# Helper function to convert TaskModel to TaskResponse
def task_to_response(task: TaskModel) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description or "",
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        created_at=task.created_at.isoformat() if task.created_at else "",
        updated_at=task.updated_at.isoformat() if task.updated_at else ""
    )

@api_app.get("/tasks", response_model=List[TaskResponse], tags=["tasks"])
async def get_tasks(
    status: Optional[str] = Query(None, description="Filter by task status"),
    priority: Optional[str] = Query(None, description="Filter by priority level"),
    search: Optional[str] = Query(None, description="Search in title and description")
):
    """
    Get all tasks with optional filtering.
    
    Returns a list of tasks filtered by status, priority, and/or search query.
    All filters are optional and can be combined.
    
    - **status**: Filter by task status (todo, in_progress, done)
    - **priority**: Filter by priority level (low, medium, high)
    - **search**: Search within title and description (case-insensitive)
    
    Example: `/tasks?status=todo&priority=high&search=urgent`
    """
    with db_manager.get_session() as session:
        query = session.query(TaskModel)
        
        if status:
            query = query.filter(TaskModel.status == status)
        if priority:
            query = query.filter(TaskModel.priority == priority)
        if search:
            query = query.filter(
                TaskModel.title.contains(search) | 
                TaskModel.description.contains(search)
            )
        
        tasks = query.all()
        return [task_to_response(task) for task in tasks]

@api_app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["tasks"],
    responses={
        200: {"description": "Task found", "model": TaskResponse},
        404: {"description": "Task not found", "model": ErrorResponse},
    }
)
async def get_task(task_id: int):
    """
    Get a specific task by ID.
    
    Returns detailed information about a single task including its current status,
    priority, due date, and timestamps.
    
    - **task_id**: The unique identifier of the task
    """
    with db_manager.get_session() as session:
        task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task_to_response(task)

@api_app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=201,
    tags=["tasks"],
    responses={
        201: {"description": "Task created successfully", "model": TaskResponse},
        400: {"description": "Invalid input data", "model": ErrorResponse},
    }
)
async def create_task(task: TaskCreate):
    """
    Create a new task.
    
    Creates a new task with the provided details. The task will be initialized
    with status "todo" regardless of any status provided in the request.
    
    - **title**: Required task title
    - **description**: Optional task description
    - **priority**: Task priority (low, medium, high)
    - **due_date**: Optional due date in YYYY-MM-DD format
    """
    with db_manager.get_session() as session:
        new_task = TaskModel(
            title=task.title.strip(),
            description=task.description.strip(),
            status="todo",
            priority=task.priority,
            due_date=task.due_date
        )
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        return task_to_response(new_task)

@api_app.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["tasks"],
    responses={
        200: {"description": "Task updated successfully", "model": TaskResponse},
        404: {"description": "Task not found", "model": ErrorResponse},
        400: {"description": "Invalid input data", "model": ErrorResponse},
    }
)
async def update_task(task_id: int, task_update: TaskUpdate):
    """
    Update an existing task.
    
    Updates any provided fields of an existing task. All fields are optional,
    and only the provided fields will be updated.
    
    - **task_id**: The unique identifier of the task to update
    - **task_update**: Object containing fields to update
    """
    with db_manager.get_session() as session:
        task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task_update.title is not None:
            task.title = task_update.title.strip()
        if task_update.description is not None:
            task.description = task_update.description.strip()
        if task_update.status is not None:
            task.status = task_update.status
        if task_update.priority is not None:
            task.priority = task_update.priority
        if task_update.due_date is not None:
            task.due_date = task_update.due_date
        
        session.commit()
        session.refresh(task)
        return task_to_response(task)

@api_app.patch(
    "/tasks/{task_id}/status",
    tags=["tasks"],
    responses={
        200: {"description": "Status updated successfully"},
        404: {"description": "Task not found", "model": ErrorResponse},
        400: {"description": "Invalid status value", "model": ErrorResponse},
    }
)
async def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate
):
    """
    Update only the task status.
    
    A convenience endpoint for quickly updating just the task status
    without needing to send the full task update payload.
    
    - **task_id**: The unique identifier of the task
    - **status**: New status value (todo, in_progress, done)
    """
    with db_manager.get_session() as session:
        task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task.status = status_update.status
        session.commit()
        return {"message": "Task status updated successfully", "task_id": task_id, "new_status": status_update.status}

@api_app.delete(
    "/tasks/{task_id}",
    tags=["tasks"],
    responses={
        200: {"description": "Task deleted successfully"},
        404: {"description": "Task not found", "model": ErrorResponse},
    }
)
async def delete_task(task_id: int):
    """
    Delete a task.
    
    Permanently removes a task from the database. This action cannot be undone.
    
    - **task_id**: The unique identifier of the task to delete
    """
    with db_manager.get_session() as session:
        task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        session.delete(task)
        session.commit()
        return {"message": "Task deleted successfully", "task_id": task_id}

@api_app.get(
    "/",
    tags=["health"],
    response_model=dict
)
async def root():
    """
    API root endpoint.
    
    Returns basic information about the API including its name and version.
    """
    return {"message": "Task Dashboard API is running", "version": "1.0.0"}

@api_app.get(
    "/health",
    tags=["health"],
    response_model=HealthResponse
)
async def health_check():
    """
    Health check endpoint.
    
    Returns the current health status of the API and database connection.
    This endpoint is useful for monitoring and load balancer health checks.
    """
    return HealthResponse(status="healthy", database="connected")