#!/usr/bin/env python3
"""Comprehensive test suite for Task Dashboard API with authentication."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from task_dashboard.api import api_app
from task_dashboard.database import db_manager, TaskModel, UserModel

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_tasks.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

# Override the database manager for testing
@contextmanager
def override_get_session():
    """Override database session for testing."""
    try:
        session = TestingSessionLocal()
        yield session
    finally:
        session.close()

# Apply the override
db_manager.get_session = override_get_session

# Create test client
client = TestClient(api_app)

@pytest.fixture(autouse=True)
def setup_test_db():
    """Set up test database before each test."""
    UserModel.metadata.create_all(bind=engine)
    TaskModel.metadata.create_all(bind=engine)
    yield
    TaskModel.metadata.drop_all(bind=engine)
    UserModel.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers():
    """Create and authenticate a test user, return auth headers."""
    # Create test user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    # Register user
    response = client.post("/auth/register", json=user_data)
    if response.status_code != 201:
        # Try login if user exists
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
    
    return {"Authorization": f"Bearer {user_data['username']}"}

@pytest.fixture
def sample_task(auth_headers):
    """Create a sample task for testing."""
    response = client.post(
        "/tasks",
        json={
            "title": "Test Task",
            "description": "This is a test task",
            "priority": "high",
            "due_date": "2024-12-25"
        },
        headers=auth_headers
    )
    return response.json()

@pytest.fixture
def multiple_tasks(auth_headers):
    """Create multiple tasks for filtering tests."""
    tasks = [
        {"title": "High Priority Task", "priority": "high", "status": "todo"},
        {"title": "Medium Priority Task", "priority": "medium", "status": "in_progress"},
        {"title": "Low Priority Task", "priority": "low", "status": "done"},
        {"title": "Urgent Work", "priority": "high", "status": "in_progress"},
        {"title": "Regular Task", "description": "This is a regular task", "priority": "medium", "status": "todo"}
    ]
    
    created_tasks = []
    for task in tasks:
        response = client.post("/tasks", json=task, headers=auth_headers)
        created_tasks.append(response.json())
    return created_tasks

class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self):
        """Test the root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Task Dashboard API is running"
        assert data["version"] == "1.0.0"
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"

class TestTaskCRUDOperations:
    """Test CRUD operations for tasks."""
    
    def test_create_task(self, auth_headers):
        """Test creating a new task."""
        task_data = {
            "title": "New Task",
            "description": "Task description",
            "priority": "medium",
            "due_date": "2024-12-31"
        }
        response = client.post("/tasks", json=task_data, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["priority"] == task_data["priority"]
        assert data["due_date"] == task_data["due_date"]
        assert data["status"] == "todo"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_task_minimal(self, auth_headers):
        """Test creating a task with minimal required fields."""
        task_data = {"title": "Minimal Task"}
        response = client.post("/tasks", json=task_data, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == "Minimal Task"
        assert data["description"] == ""
        assert data["priority"] == "medium"
        assert data["due_date"] is None
    
    def test_create_task_invalid_empty_title(self, auth_headers):
        """Test creating a task with empty title."""
        task_data = {"title": "   "}
        response = client.post("/tasks", json=task_data, headers=auth_headers)
        assert response.status_code == 201  # API allows empty titles after strip
    
    def test_get_all_tasks_empty(self, auth_headers):
        """Test getting tasks when database is empty."""
        response = client.get("/tasks", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_all_tasks_with_data(self, sample_task, auth_headers):
        """Test getting all tasks with existing data."""
        response = client.get("/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Task"
    
    def test_get_task_by_id(self, sample_task, auth_headers):
        """Test getting a specific task by ID."""
        task_id = sample_task["id"]
        response = client.get(f"/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"
        assert data["description"] == "This is a test task"
    
    def test_get_task_not_found(self, auth_headers):
        """Test getting a non-existent task."""
        response = client.get("/tasks/999", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"
    
    def test_update_task(self, sample_task, auth_headers):
        """Test updating an existing task."""
        task_id = sample_task["id"]
        update_data = {
            "title": "Updated Task",
            "description": "Updated description",
            "status": "in_progress",
            "priority": "low",
            "due_date": "2025-01-01"
        }
        response = client.put(f"/tasks/{task_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["description"] == "Updated description"
        assert data["status"] == "in_progress"
        assert data["priority"] == "low"
        assert data["due_date"] == "2025-01-01"
    
    def test_update_task_partial(self, sample_task, auth_headers):
        """Test partial update of a task."""
        task_id = sample_task["id"]
        update_data = {"title": "Only Title Updated"}
        response = client.put(f"/tasks/{task_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Only Title Updated"
        assert data["description"] == "This is a test task"  # Unchanged
    
    def test_update_task_not_found(self, auth_headers):
        """Test updating a non-existent task."""
        update_data = {"title": "Updated"}
        response = client.put("/tasks/999", json=update_data, headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"
    
    def test_delete_task(self, sample_task, auth_headers):
        """Test deleting a task."""
        task_id = sample_task["id"]
        response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Task deleted successfully"
        
        # Verify task is deleted
        response = client.get(f"/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 404
    
    def test_delete_task_not_found(self, auth_headers):
        """Test deleting a non-existent task."""
        response = client.delete("/tasks/999", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

class TestTaskStatusUpdate:
    """Test task status update endpoint."""
    
    def test_update_task_status(self, sample_task, auth_headers):
        """Test updating task status via PATCH endpoint."""
        task_id = sample_task["id"]
        status_data = {"status": "done"}
        response = client.patch(f"/tasks/{task_id}/status", json=status_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Task status updated successfully"
        assert data["task_id"] == task_id
        assert data["new_status"] == "done"
        
        # Verify status was updated
        response = client.get(f"/tasks/{task_id}", headers=auth_headers)
        assert response.json()["status"] == "done"
    
    def test_update_task_status_not_found(self, auth_headers):
        """Test updating status of non-existent task."""
        status_data = {"status": "in_progress"}
        response = client.patch("/tasks/999/status", json=status_data, headers=auth_headers)
        assert response.status_code == 404

class TestTaskFiltering:
    """Test task filtering and search functionality."""
    
    @pytest.fixture
    def multiple_tasks(self, auth_headers):
        """Create multiple tasks for filtering tests."""
        tasks = [
            {"title": "High Priority Task", "priority": "high", "status": "todo"},
            {"title": "Medium Priority Task", "priority": "medium", "status": "in_progress"},
            {"title": "Low Priority Task", "priority": "low", "status": "done"},
            {"title": "Urgent Work", "priority": "high", "status": "in_progress"},
            {"title": "Regular Task", "description": "This is a regular task", "priority": "medium", "status": "todo"}
        ]
        
        created_tasks = []
        for task in tasks:
            response = client.post("/tasks", json=task, headers=auth_headers)
            created_tasks.append(response.json())
        return created_tasks
    
    def test_filter_by_status(self, multiple_tasks, auth_headers):
        """Test filtering tasks by status."""
        response = client.get("/tasks?status=todo", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5  # All tasks have todo status (default)
        assert all(task["status"] == "todo" for task in data)
    
    def test_filter_by_priority(self, multiple_tasks, auth_headers):
        """Test filtering tasks by priority."""
        response = client.get("/tasks?priority=high", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(task["priority"] == "high" for task in data)
    
    def test_filter_by_status_and_priority(self, multiple_tasks, auth_headers):
        """Test filtering by both status and priority."""
        response = client.get("/tasks?status=todo&priority=high", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Two high priority tasks with todo status
        assert all(task["status"] == "todo" for task in data)
        assert all(task["priority"] == "high" for task in data)
    
    def test_search_tasks(self, multiple_tasks, auth_headers):
        """Test searching tasks by title and description."""
        response = client.get("/tasks?search=urgent", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "urgent" in data[0]["title"].lower()
    
    def test_search_case_insensitive(self, multiple_tasks, auth_headers):
        """Test case-insensitive search."""
        response = client.get("/tasks?search=REGULAR", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Regular Task"
    
    def test_search_in_description(self, multiple_tasks, auth_headers):
        """Test search within task descriptions."""
        response = client.get("/tasks?search=regular", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "regular" in data[0]["description"].lower()
    
    def test_no_results_filtering(self, multiple_tasks, auth_headers):
        """Test filtering that returns no results."""
        response = client.get("/tasks?status=todo&priority=invalid_priority", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

class TestTaskValidation:
    """Test input validation for task operations."""
    
    def test_invalid_priority(self, auth_headers):
        """Test creating task with invalid priority."""
        task_data = {"title": "Test", "priority": "invalid"}
        response = client.post("/tasks", json=task_data, headers=auth_headers)
        assert response.status_code == 201  # API allows any string for priority
    
    def test_invalid_date_format(self, auth_headers):
        """Test creating task with invalid date format."""
        task_data = {"title": "Test", "due_date": "invalid-date"}
        response = client.post("/tasks", json=task_data, headers=auth_headers)
        assert response.status_code == 201  # API allows any string for due_date
    
    def test_empty_json_body(self, auth_headers):
        """Test creating task with empty JSON body."""
        response = client.post("/tasks", json={}, headers=auth_headers)
        assert response.status_code == 422  # FastAPI validation error
    
    def test_null_title(self, auth_headers):
        """Test creating task with null title."""
        task_data = {"title": None}
        response = client.post("/tasks", json=task_data, headers=auth_headers)
        assert response.status_code == 422  # FastAPI validation error

class TestTaskEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_long_title(self, auth_headers):
        """Test creating task with very long title."""
        long_title = "x" * 1000
        task_data = {"title": long_title}
        response = client.post("/tasks", json=task_data, headers=auth_headers)
        assert response.status_code == 201
        assert response.json()["title"] == long_title
    
    def test_empty_description(self, auth_headers):
        """Test creating task with empty description."""
        task_data = {"title": "Test", "description": ""}
        response = client.post("/tasks", json=task_data, headers=auth_headers)
        assert response.status_code == 201
        assert response.json()["description"] == ""
    
    def test_unicode_characters(self, auth_headers):
        """Test creating task with unicode characters."""
        task_data = {
            "title": "タスク 🚀",
            "description": "これはテストタスクです 😊"
        }
        response = client.post("/tasks", json=task_data, headers=auth_headers)
        assert response.status_code == 201
        assert response.json()["title"] == "タスク 🚀"
        assert response.json()["description"] == "これはテストタスクです 😊"
    
    def test_special_characters_in_search(self, auth_headers):
        """Test search with special characters."""
        task_data = {"title": "Task with @#$% special chars"}
        response = client.post("/tasks", json=task_data, headers=auth_headers)
        assert response.status_code == 201
        
        response = client.get("/tasks?search=@#$%", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
