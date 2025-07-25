"""RESTful API endpoints for task management with user authentication.

This API provides comprehensive task management capabilities with full CRUD operations,
user authentication, and user-specific task filtering. All endpoints return JSON responses
and support standard HTTP status codes.

## Authentication
JWT-based authentication is required for most endpoints. Include the Bearer token
in the Authorization header: `Authorization: Bearer <token>`

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
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error
"""

from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, Depends, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, model_validator
import bleach
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from task_dashboard.database import db_manager, TaskModel, UserModel
from task_dashboard.auth import AuthManager
from task_dashboard.rate_limit_config import RateLimitConfig

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

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
        {"name": "auth", "description": "User authentication operations"},
        {"name": "health", "description": "API health and monitoring"},
    ]
)

# Custom rate limit exceeded handler
from fastapi.responses import JSONResponse

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": exc.detail if exc.detail else "60"
        }
    )

# Add rate limit exceeded handler
api_app.state.limiter = limiter
api_app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Pydantic models for API
class UserRegister(BaseModel):
    """Model for user registration."""
    username: str = Field(description="Unique username", min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    email: str = Field(description="User email address", max_length=255)
    password: str = Field(description="User password (min 6 characters)", min_length=6, max_length=128)
    
    @model_validator(mode='after')
    def validate_email_format(self) -> 'UserRegister':
        # Basic email validation
        if '@' not in self.email or '.' not in self.email.split('@')[-1]:
            raise ValueError('Invalid email format')
        return self

class UserLogin(BaseModel):
    """Model for user login."""
    username: str = Field(description="Username or email")
    password: str = Field(description="User password")

class UserResponse(BaseModel):
    """Response model for user data."""
    id: int = Field(description="User ID")
    username: str = Field(description="Username")
    email: str = Field(description="Email address")

class TaskCreate(BaseModel):
    """Model for creating a new task."""
    title: str = Field(description="Task title (required)", min_length=1, max_length=255)
    description: str = Field("", description="Detailed task description", max_length=1000)
    priority: str = Field("medium", description="Task priority level")
    due_date: Optional[str] = Field(None, description="Due date in YYYY-MM-DD format", pattern=r"^\d{4}-\d{2}-\d{2}$")
    
    @model_validator(mode='after')
    def validate_priority_values(self) -> 'TaskCreate':
        allowed_priorities = ["low", "medium", "high"]
        if self.priority not in allowed_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(allowed_priorities)}")
        return self

class TaskUpdate(BaseModel):
    """Model for updating an existing task. All fields are optional."""
    title: Optional[str] = Field(None, description="Task title", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Task description", max_length=1000)
    status: Optional[str] = Field(None, description="Task status")
    priority: Optional[str] = Field(None, description="Task priority")
    due_date: Optional[str] = Field(None, description="Due date in YYYY-MM-DD format", pattern=r"^\d{4}-\d{2}-\d{2}$")
    
    @model_validator(mode='after')
    def validate_priority_and_status(self) -> 'TaskUpdate':
        allowed_priorities = ["low", "medium", "high"]
        allowed_statuses = ["todo", "in_progress", "done"]
        
        if self.priority is not None and self.priority not in allowed_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(allowed_priorities)}")
        
        if self.status is not None and self.status not in allowed_statuses:
            raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        
        return self

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

    model_config = {"from_attributes": True}

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

# Security setup
security = HTTPBearer()

# Helper function to get current user
def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Get current authenticated user from token."""
    # For simplicity, we'll use username as token
    username = credentials.credentials
    with db_manager.get_session() as session:
        user = session.query(UserModel).filter(
            (UserModel.username == username) | (UserModel.email == username)
        ).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user

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

@api_app.post("/auth/register", response_model=UserResponse, status_code=201, tags=["auth"])
@limiter.limit(RateLimitConfig.REGISTER_LIMIT)
async def register_user(request: Request, user_data: UserRegister):
    """
    Register a new user account.
    
    Creates a new user with the provided credentials. The user ID will be
    returned in the response and can be used for authentication.
    
    - **username**: Unique username (must not exist)
    - **email**: Email address (must be unique)
    - **password**: Password (minimum 6 characters)
    
    Returns the user ID, username, and email.
    """
    # Additional validation
    username = user_data.username.strip()
    email = user_data.email.strip().lower()
    password = user_data.password
    
    # Sanitize username to prevent XSS (though usernames shouldn't contain HTML)
    username = bleach.clean(username)
    
    # Validate username format (additional server-side validation)
    if not username.replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Username can only contain letters, numbers, and underscores")
    
    # Validate email format (additional server-side validation)
    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    user = AuthManager.create_user(username, email, password)
    if not user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return UserResponse(id=user['id'], username=user['username'], email=user['email'])

@api_app.post("/auth/login", response_model=UserResponse, tags=["auth"])
@limiter.limit(RateLimitConfig.LOGIN_LIMIT)
async def login_user(request: Request, user_data: UserLogin):
    """
    Login existing user.
    
    Authenticates user credentials and returns the user information including user ID.
    
    - **username**: Username or email address
    - **password**: User password
    
    Returns the user ID, username, and email.
    """
    user = AuthManager.authenticate_user(user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return UserResponse(id=user['id'], username=user['username'], email=user['email'])

@api_app.get("/auth/me", response_model=UserResponse, tags=["auth"])
async def get_current_user_info(current_user=Depends(get_current_user)):
    """
    Get current user information.
    
    Returns the authenticated user's ID, username, and email.
    Requires authentication via Bearer token.
    """
    return UserResponse(id=current_user.id, username=current_user.username, email=current_user.email)

@api_app.get("/tasks", response_model=List[TaskResponse], tags=["tasks"])
async def get_tasks(
    status: Optional[str] = Query(None, description="Filter by task status"),
    priority: Optional[str] = Query(None, description="Filter by priority level"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    current_user=Depends(get_current_user)
):
    """
    Get all tasks for the authenticated user with optional filtering.
    
    Returns a list of tasks belonging to the authenticated user, filtered by
    status, priority, and/or search query. All filters are optional and can be combined.
    
    **Authentication Required**: Include Bearer token in Authorization header.
    
    - **status**: Filter by task status (todo, in_progress, done)
    - **priority**: Filter by priority level (low, medium, high)
    - **search**: Search within title and description (case-insensitive)
    
    Example: `/tasks?status=todo&priority=high&search=urgent`
    """
    with db_manager.get_session() as session:
        query = session.query(TaskModel).filter(TaskModel.user_id == current_user.id)
        
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
async def get_task(task_id: int, current_user=Depends(get_current_user)):
    """
    Get a specific task by ID.
    
    Returns detailed information about a single task belonging to the authenticated user.
    
    **Authentication Required**: Include Bearer token in Authorization header.
    
    - **task_id**: The unique identifier of the task
    """
    with db_manager.get_session() as session:
        task = session.query(TaskModel).filter(
            TaskModel.id == task_id,
            TaskModel.user_id == current_user.id
        ).first()
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
async def create_task(task: TaskCreate, current_user=Depends(get_current_user)):
    """
    Create a new task for the authenticated user.
    
    Creates a new task with the provided details for the authenticated user.
    The task will be initialized with status "todo".
    
    **Authentication Required**: Include Bearer token in Authorization header.
    
    - **title**: Required task title
    - **description**: Optional task description
    - **priority**: Task priority (low, medium, high)
    - **due_date**: Optional due date in YYYY-MM-DD format
    """
    # Additional server-side validation
    title = task.title.strip()
    description = task.description.strip() if task.description else ""
    priority = task.priority
    due_date = task.due_date
    
    # Validate title
    if not title:
        raise HTTPException(status_code=400, detail="Title is required")
    
    # Sanitize inputs to prevent XSS
    title = bleach.clean(title)
    description = bleach.clean(description)
    
    # Validate priority
    allowed_priorities = ["low", "medium", "high"]
    if priority not in allowed_priorities:
        raise HTTPException(status_code=400, detail=f"Priority must be one of: {', '.join(allowed_priorities)}")
    
    # Validate due_date format if provided
    if due_date:
        import re
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        if not date_pattern.match(due_date):
            raise HTTPException(status_code=400, detail="Due date must be in YYYY-MM-DD format")
    
    with db_manager.get_session() as session:
        new_task = TaskModel(
            user_id=current_user.id,
            title=title,
            description=description,
            status="todo",
            priority=priority,
            due_date=due_date
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
async def update_task(task_id: int, task_update: TaskUpdate, current_user=Depends(get_current_user)):
    """
    Update an existing task for the authenticated user.
    
    Updates any provided fields of an existing task belonging to the authenticated user.
    All fields are optional, and only the provided fields will be updated.
    
    **Authentication Required**: Include Bearer token in Authorization header.
    
    - **task_id**: The unique identifier of the task to update
    - **task_update**: Object containing fields to update
    """
    # Additional server-side validation
    allowed_priorities = ["low", "medium", "high"]
    allowed_statuses = ["todo", "in_progress", "done"]
    
    if task_update.title is not None:
        title = task_update.title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        if len(title) > 255:
            raise HTTPException(status_code=400, detail="Title must be less than 255 characters")
        # Sanitize title to prevent XSS
        title = bleach.clean(title)
    
    if task_update.description is not None:
        description = task_update.description.strip()
        if len(description) > 1000:
            raise HTTPException(status_code=400, detail="Description must be less than 1000 characters")
        # Sanitize description to prevent XSS
        description = bleach.clean(description)
    
    if task_update.priority is not None and task_update.priority not in allowed_priorities:
        raise HTTPException(status_code=400, detail=f"Priority must be one of: {', '.join(allowed_priorities)}")
    
    if task_update.status is not None and task_update.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {', '.join(allowed_statuses)}")
    
    if task_update.due_date is not None:
        import re
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        if task_update.due_date and not date_pattern.match(task_update.due_date):
            raise HTTPException(status_code=400, detail="Due date must be in YYYY-MM-DD format")
    
    with db_manager.get_session() as session:
        task = session.query(TaskModel).filter(
            TaskModel.id == task_id,
            TaskModel.user_id == current_user.id
        ).first()
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
    status_update: TaskStatusUpdate,
    current_user=Depends(get_current_user)
):
    """
    Update only the task status.
    
    A convenience endpoint for quickly updating just the task status
    without needing to send the full task update payload.
    
    **Authentication Required**: Include Bearer token in Authorization header.
    
    - **task_id**: The unique identifier of the task
    - **status**: New status value (todo, in_progress, done)
    """
    with db_manager.get_session() as session:
        task = session.query(TaskModel).filter(
            TaskModel.id == task_id,
            TaskModel.user_id == current_user.id
        ).first()
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
async def delete_task(task_id: int, current_user=Depends(get_current_user)):
    """
    Delete a task.
    
    Permanently removes a task from the database. This action cannot be undone.
    
    **Authentication Required**: Include Bearer token in Authorization header.
    
    - **task_id**: The unique identifier of the task to delete
    """
    with db_manager.get_session() as session:
        task = session.query(TaskModel).filter(
            TaskModel.id == task_id,
            TaskModel.user_id == current_user.id
        ).first()
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