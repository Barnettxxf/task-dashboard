"""Data models for task management application."""

import reflex as rx
from typing import Optional

class Task(rx.Base):
    """Task data model."""
    id: str
    title: str
    description: str
    status: str  # "todo", "in_progress", "done"
    priority: str  # "low", "medium", "high"
    due_date: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class User(rx.Base):
    """User data model."""
    id: int
    username: str
    email: str