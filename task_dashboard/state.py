"""State management for task dashboard application."""

import reflex as rx
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from task_dashboard.models import Task, User
from task_dashboard.database import db_manager, TaskModel
from task_dashboard.translations import translation_manager

class State(rx.State):
    """The app state for task management."""
    
    # User authentication
    current_user: Optional[User] = None
    is_authenticated: bool = False
    
    # Authentication form state
    login_username: str = ""
    login_password: str = ""
    register_username: str = ""
    register_email: str = ""
    register_password: str = ""
    register_confirm_password: str = ""
    auth_error: str = ""
    
    # Task data (user-specific)
    tasks: List[Task] = []
    
    # Form state
    new_task_title: str = ""
    new_task_description: str = ""
    new_task_priority: str = "medium"
    new_task_due_date: str = ""
    
    # Filter and search
    search_query: str = ""
    filter_status: str = "all"
    sort_by: str = "created_at"  # created_at, due_date, priority, title
    sort_order: str = "desc"  # asc, desc
    
    # Editing state
    editing_task: Optional[Task] = None
    is_editing: bool = False
    
    # Pagination
    items_per_page: int = 20
    page_number: int = 1  # Renamed to avoid conflict with navigation
    
    # UI State
    show_add_modal: bool = False
    show_login_modal: bool = False
    show_register_modal: bool = False
    continuous_add: bool = False
    
    # Navigation
    current_page: str = "tasks"  # "tasks", "stats"
    
    # Translation
    current_language: str = "en"
    
    @rx.var
    def t_app_title(self) -> str:
        """Get app title in current language."""
        return translation_manager.get_translation(self.current_language, "app_title")
    
    @rx.var
    def t_welcome_to_dashboard(self) -> str:
        """Get welcome message in current language."""
        return translation_manager.get_translation(self.current_language, "welcome_to_dashboard")
    
    @rx.var
    def t_dashboard_description(self) -> str:
        """Get dashboard description in current language."""
        return translation_manager.get_translation(self.current_language, "dashboard_description")
    
    @rx.var
    def t_get_started(self) -> str:
        """Get get started button text in current language."""
        return translation_manager.get_translation(self.current_language, "get_started")
    
    @rx.var
    def t_sign_in(self) -> str:
        """Get sign in button text in current language."""
        return translation_manager.get_translation(self.current_language, "sign_in")
    
    @rx.var
    def t_sign_up(self) -> str:
        """Get sign up button text in current language."""
        return translation_manager.get_translation(self.current_language, "sign_up")
    
    @rx.var
    def t_total_tasks(self) -> str:
        """Get total tasks text in current language."""
        return translation_manager.get_translation(self.current_language, "total_tasks")
    
    @rx.var
    def t_completion_rate(self) -> str:
        """Get completion rate text in current language."""
        return translation_manager.get_translation(self.current_language, "completion_rate")
    
    @rx.var
    def t_todo(self) -> str:
        """Get todo text in current language."""
        return translation_manager.get_translation(self.current_language, "todo")
    
    @rx.var
    def t_in_progress(self) -> str:
        """Get in progress text in current language."""
        return translation_manager.get_translation(self.current_language, "in_progress")
    
    @rx.var
    def t_done(self) -> str:
        """Get done text in current language."""
        return translation_manager.get_translation(self.current_language, "done")
    
    @rx.var
    def t_search_tasks(self) -> str:
        """Get search tasks placeholder in current language."""
        return translation_manager.get_translation(self.current_language, "search_tasks")
    
    @rx.var
    def t_filter_by_status(self) -> str:
        """Get filter by status placeholder in current language."""
        return translation_manager.get_translation(self.current_language, "filter_by_status")
    
    @rx.var
    def t_sort_by(self) -> str:
        """Get sort by placeholder in current language."""
        return translation_manager.get_translation(self.current_language, "sort_by")
    
    @rx.var
    def t_order(self) -> str:
        """Get order placeholder in current language."""
        return translation_manager.get_translation(self.current_language, "order")
    
    @rx.var
    def t_all(self) -> str:
        """Get all text in current language."""
        return translation_manager.get_translation(self.current_language, "all")
    
    @rx.var
    def t_created_at(self) -> str:
        """Get created at text in current language."""
        return translation_manager.get_translation(self.current_language, "created_at")
    
    @rx.var
    def t_title(self) -> str:
        """Get title text in current language."""
        return translation_manager.get_translation(self.current_language, "title")
    
    @rx.var
    def t_ascending(self) -> str:
        """Get ascending text in current language."""
        return translation_manager.get_translation(self.current_language, "ascending")
    
    @rx.var
    def t_descending(self) -> str:
        """Get descending text in current language."""
        return translation_manager.get_translation(self.current_language, "descending")
    
    def get_status_display(self, status: str) -> str:
        """Get display text for status in current language."""
        status_map = {
            "todo": self.t_todo,
            "in_progress": self.t_in_progress,
            "done": self.t_done,
            "all": self.t_all
        }
        return status_map.get(status, status)
    
    def get_priority_display(self, priority: str) -> str:
        """Get display text for priority in current language."""
        priority_map = {
            "low": self.t_low,
            "medium": self.t_medium,
            "high": self.t_high
        }
        return priority_map.get(priority, priority)
    
    def get_sort_display(self, sort_by: str) -> str:
        """Get display text for sort options in current language."""
        sort_map = {
            "created_at": self.t_created_at,
            "due_date": self.t_due_date,
            "priority": self.t_priority,
            "title": self.t_title
        }
        return sort_map.get(sort_by, sort_by)
    
    def get_order_display(self, order: str) -> str:
        """Get display text for order options in current language."""
        order_map = {
            "asc": self.t_ascending,
            "desc": self.t_descending
        }
        return order_map.get(order, order)
    
    @rx.var
    def t_add_task(self) -> str:
        """Get add task text in current language."""
        return translation_manager.get_translation(self.current_language, "add_task")
    
    @rx.var
    def t_no_tasks_found(self) -> str:
        """Get no tasks found text in current language."""
        return translation_manager.get_translation(self.current_language, "no_tasks_found")
    
    @rx.var
    def t_title(self) -> str:
        """Get title text in current language."""
        return translation_manager.get_translation(self.current_language, "title")
    
    @rx.var
    def t_description(self) -> str:
        """Get description text in current language."""
        return translation_manager.get_translation(self.current_language, "description")
    
    @rx.var
    def t_priority(self) -> str:
        """Get priority text in current language."""
        return translation_manager.get_translation(self.current_language, "priority")
    
    @rx.var
    def t_status(self) -> str:
        """Get status text in current language."""
        return translation_manager.get_translation(self.current_language, "status")
    
    @rx.var
    def t_due_date(self) -> str:
        """Get due date text in current language."""
        return translation_manager.get_translation(self.current_language, "due_date")
    
    @rx.var
    def t_low(self) -> str:
        """Get low priority text in current language."""
        return translation_manager.get_translation(self.current_language, "low")
    
    @rx.var
    def t_medium(self) -> str:
        """Get medium priority text in current language."""
        return translation_manager.get_translation(self.current_language, "medium")
    
    @rx.var
    def t_high(self) -> str:
        """Get high priority text in current language."""
        return translation_manager.get_translation(self.current_language, "high")
    
    @rx.var
    def t_clear(self) -> str:
        """Get clear text in current language."""
        return translation_manager.get_translation(self.current_language, "clear")
    
    @rx.var
    def t_today(self) -> str:
        """Get today text in current language."""
        return translation_manager.get_translation(self.current_language, "today")
    
    @rx.var
    def t_tomorrow(self) -> str:
        """Get tomorrow text in current language."""
        return translation_manager.get_translation(self.current_language, "tomorrow")
    
    @rx.var
    def t_next_week(self) -> str:
        """Get next week text in current language."""
        return translation_manager.get_translation(self.current_language, "next_week")
    
    @rx.var
    def t_keep_adding(self) -> str:
        """Get keep adding text in current language."""
        return translation_manager.get_translation(self.current_language, "keep_adding")
    
    @rx.var
    def t_cancel(self) -> str:
        """Get cancel text in current language."""
        return translation_manager.get_translation(self.current_language, "cancel")
    
    @rx.var
    def t_create_task(self) -> str:
        """Get create task text in current language."""
        return translation_manager.get_translation(self.current_language, "create_task")
    
    @rx.var
    def t_save(self) -> str:
        """Get save text in current language."""
        return translation_manager.get_translation(self.current_language, "save")
    
    @rx.var
    def t_username(self) -> str:
        """Get username text in current language."""
        return translation_manager.get_translation(self.current_language, "username")
    
    @rx.var
    def t_email(self) -> str:
        """Get email text in current language."""
        return translation_manager.get_translation(self.current_language, "email")
    
    @rx.var
    def t_password(self) -> str:
        """Get password text in current language."""
        return translation_manager.get_translation(self.current_language, "password")
    
    @rx.var
    def t_confirm_password(self) -> str:
        """Get confirm password text in current language."""
        return translation_manager.get_translation(self.current_language, "confirm_password")
    
    @rx.var
    def t_create_account(self) -> str:
        """Get create account text in current language."""
        return translation_manager.get_translation(self.current_language, "create_account")
    
    @rx.var
    def t_already_have_account(self) -> str:
        """Get already have account text in current language."""
        return translation_manager.get_translation(self.current_language, "already_have_account")
    
    @rx.var
    def t_dont_have_account(self) -> str:
        """Get don't have account text in current language."""
        return translation_manager.get_translation(self.current_language, "dont_have_account")
    
    @rx.var
    def t_logout(self) -> str:
        """Get logout text in current language."""
        return translation_manager.get_translation(self.current_language, "logout")
    
    @rx.var
    def t_sign_up_here(self) -> str:
        """Get sign up here text in current language."""
        return translation_manager.get_translation(self.current_language, "sign_up_here")
    
    @rx.var
    def t_sign_in_here(self) -> str:
        """Get sign in here text in current language."""
        return translation_manager.get_translation(self.current_language, "sign_in_here")
    
    @rx.var
    def t_edit_task(self) -> str:
        """Get edit task text in current language."""
        return translation_manager.get_translation(self.current_language, "edit_task")
    
    @rx.var
    def t_delete_task(self) -> str:
        """Get delete task text in current language."""
        return translation_manager.get_translation(self.current_language, "delete_task")
    
    @rx.var
    def t_update_task(self) -> str:
        """Get update task text in current language."""
        return translation_manager.get_translation(self.current_language, "update_task")
    
    @rx.var
    def t_add_task(self) -> str:
        """Get add task text in current language."""
        return translation_manager.get_translation(self.current_language, "add_task")
    
    @rx.var
    def t_create_task(self) -> str:
        """Get create task text in current language."""
        return translation_manager.get_translation(self.current_language, "create_task")
    
    @rx.var
    def t_save(self) -> str:
        """Get save text in current language."""
        return translation_manager.get_translation(self.current_language, "save")
    
    @rx.var
    def t_title(self) -> str:
        """Get title text in current language."""
        return translation_manager.get_translation(self.current_language, "title")
    
    @rx.var
    def t_description(self) -> str:
        """Get description text in current language."""
        return translation_manager.get_translation(self.current_language, "description")
    
    @rx.var
    def t_priority(self) -> str:
        """Get priority text in current language."""
        return translation_manager.get_translation(self.current_language, "priority")
    
    @rx.var
    def t_due_date(self) -> str:
        """Get due date text in current language."""
        return translation_manager.get_translation(self.current_language, "due_date")
    
    @rx.var
    def t_low(self) -> str:
        """Get low priority text in current language."""
        return translation_manager.get_translation(self.current_language, "low")
    
    @rx.var
    def t_medium(self) -> str:
        """Get medium priority text in current language."""
        return translation_manager.get_translation(self.current_language, "medium")
    
    @rx.var
    def t_high(self) -> str:
        """Get high priority text in current language."""
        return translation_manager.get_translation(self.current_language, "high")
    
    @rx.var
    def t_clear(self) -> str:
        """Get clear text in current language."""
        return translation_manager.get_translation(self.current_language, "clear")
    
    @rx.var
    def t_today(self) -> str:
        """Get today text in current language."""
        return translation_manager.get_translation(self.current_language, "today")
    
    @rx.var
    def t_tomorrow(self) -> str:
        """Get tomorrow text in current language."""
        return translation_manager.get_translation(self.current_language, "tomorrow")
    
    @rx.var
    def t_next_week(self) -> str:
        """Get next week text in current language."""
        return translation_manager.get_translation(self.current_language, "next_week")
    
    @rx.var
    def t_keep_adding(self) -> str:
        """Get keep adding text in current language."""
        return translation_manager.get_translation(self.current_language, "keep_adding")
    
    @rx.var
    def t_cancel(self) -> str:
        """Get cancel text in current language."""
        return translation_manager.get_translation(self.current_language, "cancel")
    
    @rx.var
    def t_username(self) -> str:
        """Get username text in current language."""
        return translation_manager.get_translation(self.current_language, "username")
    
    @rx.var
    def t_email(self) -> str:
        """Get email text in current language."""
        return translation_manager.get_translation(self.current_language, "email")
    
    @rx.var
    def t_password(self) -> str:
        """Get password text in current language."""
        return translation_manager.get_translation(self.current_language, "password")
    
    @rx.var
    def t_confirm_password(self) -> str:
        """Get confirm password text in current language."""
        return translation_manager.get_translation(self.current_language, "confirm_password")
    
    @rx.var
    def t_create_account(self) -> str:
        """Get create account text in current language."""
        return translation_manager.get_translation(self.current_language, "create_account")
    
    @rx.var
    def t_already_have_account(self) -> str:
        """Get already have account text in current language."""
        return translation_manager.get_translation(self.current_language, "already_have_account")
    
    @rx.var
    def t_dont_have_account(self) -> str:
        """Get don't have account text in current language."""
        return translation_manager.get_translation(self.current_language, "dont_have_account")
    
    @rx.var
    def t_logout(self) -> str:
        """Get logout text in current language."""
        return translation_manager.get_translation(self.current_language, "logout")
    
    @rx.var
    def t_sign_up_here(self) -> str:
        """Get sign up here text in current language."""
        return translation_manager.get_translation(self.current_language, "sign_up_here")
    
    @rx.var
    def t_sign_in_here(self) -> str:
        """Get sign in here text in current language."""
        return translation_manager.get_translation(self.current_language, "sign_in_here")
    
    @rx.var
    def t_password_too_short(self) -> str:
        """Get password too short text in current language."""
        return translation_manager.get_translation(self.current_language, "password_too_short")
    
    @rx.event
    def set_language(self, language: str):
        """Set the current language."""
        if language in translation_manager.get_available_languages():
            self.current_language = language
    
    def toggle_add_modal(self):
        """Toggle the add task modal."""
        self.show_add_modal = not self.show_add_modal
    
    @rx.var
    def t_statistics(self) -> str:
        """Get statistics text in current language."""
        return translation_manager.get_translation(self.current_language, "statistics")
    
    @rx.var
    def t_dashboard(self) -> str:
        """Get dashboard text in current language."""
        return translation_manager.get_translation(self.current_language, "dashboard")
    
    @rx.var
    def t_task_management(self) -> str:
        """Get task management text in current language."""
        return translation_manager.get_translation(self.current_language, "task_management")
    
    @rx.var
    def t_tasks_page(self) -> str:
        """Get tasks page text in current language."""
        return translation_manager.get_translation(self.current_language, "tasks_page")
    
    @rx.var
    def t_stats_page(self) -> str:
        """Get stats page text in current language."""
        return translation_manager.get_translation(self.current_language, "stats_page")
    
    @rx.var
    def t_task_statistics(self) -> str:
        """Get task statistics text in current language."""
        return translation_manager.get_translation(self.current_language, "task_statistics")
    
    @rx.var
    def t_task_breakdown(self) -> str:
        """Get task breakdown text in current language."""
        return translation_manager.get_translation(self.current_language, "task_breakdown")
    
    @rx.var
    def t_priority_breakdown(self) -> str:
        """Get priority breakdown text in current language."""
        return translation_manager.get_translation(self.current_language, "priority_breakdown")
    
    @rx.var
    def todo_percentage(self) -> int:
        """Get todo percentage."""
        total = len(self.tasks)
        todo = len([t for t in self.tasks if t.status == "todo"])
        return int(todo / total * 100) if total > 0 else 0
    
    @rx.var
    def in_progress_percentage(self) -> int:
        """Get in progress percentage."""
        total = len(self.tasks)
        in_progress = len([t for t in self.tasks if t.status == "in_progress"])
        return int(in_progress / total * 100) if total > 0 else 0
    
    @rx.var
    def done_percentage(self) -> int:
        """Get done percentage."""
        total = len(self.tasks)
        done = len([t for t in self.tasks if t.status == "done"])
        return int(done / total * 100) if total > 0 else 0

    def reset_form(self):
        """Reset form fields."""
        self.new_task_title = ""
        self.new_task_description = ""
        self.new_task_priority = "medium"
        self.new_task_due_date = ""
    
    def set_due_date_today(self):
        """Set due date to today."""
        self.new_task_due_date = datetime.now().strftime("%Y-%m-%d")
    
    def set_due_date_tomorrow(self):
        """Set due date to tomorrow."""
        tomorrow = datetime.now() + timedelta(days=1)
        self.new_task_due_date = tomorrow.strftime("%Y-%m-%d")
    
    def set_due_date_next_week(self):
        """Set due date to next week."""
        next_week = datetime.now() + timedelta(days=7)
        self.new_task_due_date = next_week.strftime("%Y-%m-%d")
    
    def _db_task_to_task(self, db_task: TaskModel) -> Task:
        """Convert database task to Task model."""
        return Task(
            id=str(db_task.id),
            title=db_task.title,
            description=db_task.description or "",
            status=db_task.status,
            priority=db_task.priority,
            due_date=db_task.due_date or "",
            created_at=db_task.created_at.isoformat() if db_task.created_at else "",
            updated_at=db_task.updated_at.isoformat() if db_task.updated_at else ""
        )
    
    # Authentication methods
    @rx.event
    def register_user(self, form_data: dict):
        """Register a new user."""
        from task_dashboard.auth import AuthManager
        
        username = form_data.get("username", "").strip()
        email = form_data.get("email", "").strip()
        password = form_data.get("password", "")
        confirm_password = form_data.get("confirm_password", "")
        
        if not username or not email or not password:
            self.auth_error = "All fields are required"
            return
            
        if password != confirm_password:
            self.auth_error = "Passwords do not match"
            return
            
        if len(password) < 6:
            self.auth_error = "Password must be at least 6 characters"
            return
            
        user = AuthManager.create_user(username, email, password)
        if user:
            self.current_user = User(**user)
            self.is_authenticated = True
            self.auth_error = ""
            self.show_register_modal = False
            self.load_tasks()
            return rx.toast.success(f"Welcome, {username}!")
        else:
            self.auth_error = "Username or email already exists"
    
    @rx.event
    def login_user(self, form_data: dict):
        """Login existing user."""
        from task_dashboard.auth import AuthManager
        
        username = form_data.get("username", "").strip()
        password = form_data.get("password", "")
        
        if not username or not password:
            self.auth_error = "Username and password are required"
            return
            
        user = AuthManager.authenticate_user(username, password)
        if user:
            self.current_user = User(**user)
            self.is_authenticated = True
            self.auth_error = ""
            self.show_login_modal = False
            self.load_tasks()
            return rx.toast.success(f"Welcome back, {user['username']}!")
        else:
            self.auth_error = "Invalid username or password"
    
    @rx.event
    def logout_user(self):
        """Logout current user."""
        self.current_user = None
        self.is_authenticated = False
        self.tasks = []
        self.auth_error = ""
        return rx.toast.success("Logged out successfully")
    
    @rx.event
    def load_tasks(self):
        """Load tasks for the current authenticated user."""
        if not self.is_authenticated or not self.current_user:
            self.tasks = []
            return
            
        try:
            with db_manager.get_session() as session:
                db_tasks = session.query(TaskModel).filter(
                    TaskModel.user_id == self.current_user.id
                ).order_by(TaskModel.created_at.desc()).all()
                
                self.tasks = [self._db_task_to_task(task) for task in db_tasks]
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self.tasks = []
    
    @rx.event
    def add_task(self):
        """Add new task for current user."""
        if not self.is_authenticated or not self.current_user:
            return rx.toast.error("Please login to add tasks")
            
        if not self.new_task_title.strip():
            return
            
        try:
            with db_manager.get_session() as session:
                new_db_task = TaskModel(
                    user_id=self.current_user.id,
                    title=self.new_task_title.strip(),
                    description=self.new_task_description.strip(),
                    status="todo",
                    priority=self.new_task_priority,
                    due_date=self.new_task_due_date if self.new_task_due_date else None
                )
                
                session.add(new_db_task)
                session.commit()
                session.refresh(new_db_task)
                
                new_task = self._db_task_to_task(new_db_task)
                self.tasks = [new_task] + self.tasks
                
                if not self.continuous_add:
                    self.reset_form()
                    self.show_add_modal = False
                else:
                    # Reset form fields but keep modal open
                    self.new_task_title = ""
                    self.new_task_description = ""
                    self.new_task_priority = "medium"
                    self.new_task_due_date = ""
                
                return rx.toast.success("Task added successfully!")
                
        except Exception as e:
            print(f"Error adding task: {e}")
            return rx.toast.error("Failed to add task")
    
    @rx.event
    def update_task(self):
        """Update existing task."""
        if not self.is_authenticated or not self.current_user:
            return rx.toast.error("Please login to update tasks")
            
        if not self.editing_task or not self.new_task_title.strip():
            return
            
        try:
            with db_manager.get_session() as session:
                db_task = session.query(TaskModel).filter(
                    TaskModel.id == int(self.editing_task.id),
                    TaskModel.user_id == self.current_user.id
                ).first()
                
                if db_task:
                    db_task.title = self.new_task_title.strip()
                    db_task.description = self.new_task_description.strip()
                    db_task.priority = self.new_task_priority
                    db_task.due_date = self.new_task_due_date if self.new_task_due_date else None
                    db_task.updated_at = datetime.utcnow()
                    session.commit()
                    
                    # Update in-memory state
                    for task in self.tasks:
                        if task.id == self.editing_task.id:
                            task.title = db_task.title
                            task.description = db_task.description
                            task.priority = db_task.priority
                            task.due_date = db_task.due_date
                            task.updated_at = db_task.updated_at.isoformat()
                            break
                    
                    self.reset_form()
                    self.is_editing = False
                    self.editing_task = None
                    self.show_add_modal = False
                    return rx.toast.success("Task updated successfully!")
                else:
                    return rx.toast.error("Task not found")
                    
        except Exception as e:
            print(f"Error updating task: {e}")
            return rx.toast.error("Failed to update task")
    
    @rx.event
    def edit_task(self, task: Task):
        """Set task for editing."""
        self.editing_task = task
        self.is_editing = True
        self.new_task_title = task.title
        self.new_task_description = task.description
        self.new_task_priority = task.priority
        self.new_task_due_date = task.due_date
    
    @rx.event
    def cancel_edit(self):
        """Cancel editing mode."""
        self.reset_form()
        self.is_editing = False
        self.editing_task = None
    
    @rx.event
    def delete_task(self, task_id: str):
        """Delete task (user-specific)."""
        if not self.is_authenticated or not self.current_user:
            return rx.toast.error("Please login to delete tasks")
            
        try:
            with db_manager.get_session() as session:
                db_task = session.query(TaskModel).filter(
                    TaskModel.id == int(task_id),
                    TaskModel.user_id == self.current_user.id
                ).first()
                
                if db_task:
                    session.delete(db_task)
                    session.commit()
                    
                    # Remove from in-memory state
                    self.tasks = [task for task in self.tasks if task.id != task_id]
                    return rx.toast.success("Task deleted successfully!")
                else:
                    return rx.toast.error("Task not found")
                    
        except Exception as e:
            print(f"Error deleting task: {e}")
            return rx.toast.error("Failed to delete task")
    
    @rx.event
    def update_task_status(self, task_id: str, new_status: str):
        """Update task status (user-specific)."""
        if not self.is_authenticated or not self.current_user:
            return
            
        try:
            with db_manager.get_session() as session:
                db_task = session.query(TaskModel).filter(
                    TaskModel.id == int(task_id),
                    TaskModel.user_id == self.current_user.id
                ).first()
                
                if db_task:
                    db_task.status = new_status
                    db_task.updated_at = datetime.utcnow()
                    session.commit()
                    
                    # Update in-memory state
                    for task in self.tasks:
                        if task.id == task_id:
                            task.status = new_status
                            task.updated_at = db_task.updated_at.isoformat()
                            break
                            
        except Exception as e:
            print(f"Error updating task status: {e}")
    
    def edit_task(self, task: Task):
        """Start editing a task."""
        self.editing_task = task
        self.is_editing = True
        self.new_task_title = task.title
        self.new_task_description = task.description
        self.new_task_priority = task.priority
        self.new_task_due_date = task.due_date or ""
        self.show_add_modal = True
    
    def cancel_edit(self):
        """Cancel editing."""
        self.reset_form()
        self.is_editing = False
        self.editing_task = None
        self.show_add_modal = False
    
    # Authentication UI methods
    def toggle_login_modal(self):
        """Toggle login modal."""
        self.show_login_modal = not self.show_login_modal
        self.auth_error = ""
    
    def toggle_register_modal(self):
        """Toggle register modal."""
        self.show_register_modal = not self.show_register_modal
        self.auth_error = ""
    
    @rx.event
    def on_load(self):
        """Load tasks when page loads."""
        if self.is_authenticated and self.current_user:
            self.load_tasks()
        else:
            # Initialize with empty tasks for non-authenticated users
            self.tasks = []
    
    @rx.var
    def filtered_tasks(self) -> List[Task]:
        """Get filtered and sorted tasks."""
        # Filter tasks
        filtered = self.tasks
        
        if self.search_query:
            query = self.search_query.lower()
            filtered = [task for task in filtered 
                       if query in task.title.lower() or query in task.description.lower()]
        
        # When filter_status is "all", show all tasks regardless of status
        if self.filter_status != "all":
            filtered = [task for task in filtered if task.status == self.filter_status]
        
        # Sort tasks
        def sort_key(task):
            if self.sort_by == "priority":
                priority_order = {"high": 3, "medium": 2, "low": 1}
                return priority_order.get(task.priority, 0)
            elif self.sort_by == "due_date":
                return task.due_date or "9999-12-31"
            elif self.sort_by == "title":
                return task.title.lower()
            else:  # created_at
                return task.created_at or ""
        
        filtered.sort(key=sort_key, reverse=(self.sort_order == "desc"))
        
        return filtered
    
    @rx.var
    def total_tasks(self) -> int:
        """Get total number of tasks."""
        return len(self.tasks)
    
    @rx.var
    def todo_count(self) -> int:
        """Get todo count."""
        return len([t for t in self.tasks if t.status == "todo"])
    
    @rx.var
    def in_progress_count(self) -> int:
        """Get in progress count."""
        return len([t for t in self.tasks if t.status == "in_progress"])
    
    @rx.var
    def done_count(self) -> int:
        """Get done count."""
        return len([t for t in self.tasks if t.status == "done"])
    
    @rx.var
    def completion_rate(self) -> int:
        """Get completion rate."""
        total = len(self.tasks)
        done = len([t for t in self.tasks if t.status == "done"])
        return int(done / total * 100) if total > 0 else 0
    
    @rx.var
    def high_priority_count(self) -> int:
        """Get high priority count."""
        return len([t for t in self.tasks if t.priority == "high"])
    
    @rx.var
    def medium_priority_count(self) -> int:
        """Get medium priority count."""
        return len([t for t in self.tasks if t.priority == "medium"])
    
    @rx.var
    def low_priority_count(self) -> int:
        """Get low priority count."""
        return len([t for t in self.tasks if t.priority == "low"])
    
    @rx.var
    def tasks_by_status(self) -> Dict[str, List[Task]]:
        """Get tasks grouped by status for efficient rendering."""
        return {
            "todo": [task for task in self.filtered_tasks if task.status == "todo"],
            "in_progress": [task for task in self.filtered_tasks if task.status == "in_progress"],
            "done": [task for task in self.filtered_tasks if task.status == "done"]
        }
    
    def navigate_to_page(self, page: str):
        """Navigate to a specific page."""
        self.current_page = page