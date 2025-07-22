#!/usr/bin/env python3
"""Test script for API authentication endpoints - converted to pytest tests."""

import pytest
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

@pytest.fixture
def base_url():
    """Base URL for API."""
    return "http://localhost:8000"

@pytest.fixture
def auth_headers():
    """Create and authenticate a test user, return auth headers."""
    import uuid
    unique_suffix = str(uuid.uuid4())[:8]
    
    # Create test user data
    user_data = {
        "username": f"testuser_{unique_suffix}",
        "email": f"test_{unique_suffix}@example.com",
        "password": "testpass123"
    }
    
    # Register user
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    if response.status_code != 201:
        # Try login if user exists
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "username": user_data["username"],
            "password": user_data["password"]
        })
        if login_response.status_code == 200:
            user_info = login_response.json()
            return {"Authorization": f"Bearer {user_info['username']}"}
        else:
            raise Exception("Failed to create/authenticate test user")
    
    return {"Authorization": f"Bearer {user_data['username']}"}

def test_registration(base_url):
    """Test user registration endpoint."""
    import uuid
    unique_suffix = str(uuid.uuid4())[:8]
    data = {
        "username": f"regtestuser_{unique_suffix}",
        "email": f"regtest_{unique_suffix}@example.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{base_url}/auth/register", json=data)
    assert response.status_code == 201
    
    data = response.json()
    assert "id" in data
    assert data["username"] == f"regtestuser_{unique_suffix}"
    assert data["email"] == f"regtest_{unique_suffix}@example.com"

def test_login(base_url):
    """Test user login endpoint."""
    import uuid
    unique_suffix = str(uuid.uuid4())[:8]
    
    # First register a user
    register_data = {
        "username": f"logintest_{unique_suffix}",
        "email": f"logintest_{unique_suffix}@example.com",
        "password": "testpass123"
    }
    
    register_response = requests.post(f"{base_url}/auth/register", json=register_data)
    assert register_response.status_code == 201
    
    # Then test login
    login_data = {
        "username": f"logintest_{unique_suffix}",
        "password": "testpass123"
    }
    
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "id" in data
    assert data["username"] == f"logintest_{unique_suffix}"

def test_get_user_info(base_url, auth_headers):
    """Test getting current user info."""
    response = requests.get(f"{base_url}/auth/me", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "id" in data
    assert "username" in data
    assert "email" in data

def test_create_task(base_url, auth_headers):
    """Test creating a task."""
    import uuid
    unique_suffix = str(uuid.uuid4())[:8]
    data = {
        "title": f"Test API Task {unique_suffix}",
        "description": "This is a test task created via API",
        "priority": "high"
    }
    
    response = requests.post(f"{base_url}/tasks", json=data, headers=auth_headers)
    assert response.status_code == 201
    
    data = response.json()
    assert data["title"] == f"Test API Task {unique_suffix}"
    assert data["priority"] == "high"
    assert data["status"] == "todo"
    task_id = data["id"]
    # Store for potential use by other tests if needed
    pytest.current_task_id = task_id

def test_get_tasks(base_url, auth_headers):
    """Test getting all tasks for user."""
    response = requests.get(f"{base_url}/tasks", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)

def test_update_task_status(base_url, auth_headers):
    """Test updating task status."""
    import uuid
    unique_suffix = str(uuid.uuid4())[:8]
    
    # First create a task
    task_data = {
        "title": f"Status Update Test {unique_suffix}",
        "description": "Testing status update",
        "priority": "medium"
    }
    
    create_response = requests.post(f"{base_url}/tasks", json=task_data, headers=auth_headers)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    
    # Update status
    status_data = {"status": "done"}
    response = requests.patch(f"{base_url}/tasks/{task_id}/status", json=status_data, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["task_id"] == task_id
    assert data["new_status"] == "done"

def test_delete_task(base_url, auth_headers):
    """Test deleting a task."""
    import uuid
    unique_suffix = str(uuid.uuid4())[:8]
    
    # First create a task
    task_data = {
        "title": f"Delete Test Task {unique_suffix}",
        "description": "Testing task deletion",
        "priority": "low"
    }
    
    create_response = requests.post(f"{base_url}/tasks", json=task_data, headers=auth_headers)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    
    # Delete task
    response = requests.delete(f"{base_url}/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify task is deleted
    get_response = requests.get(f"{base_url}/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 404