"""Task Dashboard - Modern task management application built with Reflex."""

import reflex as rx
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from rxconfig import config
from task_dashboard.database import db_manager, TaskModel, UserModel
from task_dashboard.auth import AuthManager

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
    current_page: int = 1
    
    # UI State
    show_add_modal: bool = False
    show_login_modal: bool = False
    show_register_modal: bool = False
    continuous_add: bool = False
    
    # Cache for computed values
    _computed_tasks: Dict[str, List[Task]] = {}
    
    def toggle_add_modal(self):
        """Toggle the add task modal."""
        self.show_add_modal = not self.show_add_modal
    
    def on_load(self):
        """Load tasks from database when the app loads."""
        if self.is_authenticated and self.current_user:
            self.load_tasks()
        else:
            # Initialize with empty tasks for non-authenticated users
            self.tasks = []

    def add_task(self):
        """Add a new task to database."""
        if not self.new_task_title.strip():
            return
            
        with db_manager.get_session() as session:
            new_db_task = TaskModel(
                title=self.new_task_title.strip(),
                description=self.new_task_description.strip(),
                status="todo",
                priority=self.new_task_priority,
                due_date=self.new_task_due_date if self.new_task_due_date else None
            )
            session.add(new_db_task)
            session.commit()
            
            new_task = Task(
                id=str(new_db_task.id),
                title=new_db_task.title,
                description=new_db_task.description,
                status=new_db_task.status,
                priority=new_db_task.priority,
                due_date=new_db_task.due_date,
                created_at=new_db_task.created_at.isoformat() if new_db_task.created_at else None,
                updated_at=new_db_task.updated_at.isoformat() if new_db_task.updated_at else None
            )
            
            self.tasks.append(new_task)
            
            if not self.continuous_add:
                self.show_add_modal = False
                self.reset_form()
    
    def reset_form(self):
        """Reset the create task form."""
        self.new_task_title = ""
        self.new_task_description = ""
        self.new_task_priority = "medium"
        self.new_task_due_date = ""
    
    def set_due_date_today(self):
        """Set due date to today."""
        from datetime import datetime
        self.new_task_due_date = datetime.now().strftime("%Y-%m-%d")
    
    def set_due_date_tomorrow(self):
        """Set due date to tomorrow."""
        from datetime import datetime, timedelta
        tomorrow = datetime.now() + timedelta(days=1)
        self.new_task_due_date = tomorrow.strftime("%Y-%m-%d")
    
    def set_due_date_next_week(self):
        """Set due date to next week."""
        from datetime import datetime, timedelta
        next_week = datetime.now() + timedelta(days=7)
        self.new_task_due_date = next_week.strftime("%Y-%m-%d")
    
    def update_task_status(self, task_id: str, new_status: str):
        """Update task status in database."""
        with db_manager.get_session() as session:
            db_task = session.query(TaskModel).filter(TaskModel.id == int(task_id)).first()
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
    
    def delete_task(self, task_id: str):
        """Delete a task from database."""
        with db_manager.get_session() as session:
            db_task = session.query(TaskModel).filter(TaskModel.id == int(task_id)).first()
            if db_task:
                session.delete(db_task)
                session.commit()
                
                # Remove from in-memory state
                self.tasks = [task for task in self.tasks if task.id != task_id]
    
    def edit_task(self, task: Task):
        """Start editing a task."""
        self.editing_task = task
        self.is_editing = True
        self.new_task_title = task.title
        self.new_task_description = task.description
        self.new_task_priority = task.priority
        self.new_task_due_date = task.due_date or ""
    
    def update_task(self):
        """Update an existing task in database."""
        if not self.editing_task or not self.new_task_title.strip():
            return
            
        with db_manager.get_session() as session:
            db_task = session.query(TaskModel).filter(
                TaskModel.id == int(self.editing_task.id)
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
    
    def cancel_edit(self):
        """Cancel editing."""
        self.reset_form()
        self.is_editing = False
        self.editing_task = None
        self.show_add_modal = False
    
    # Authentication methods
    @rx.event
    def register_user(self, form_data: dict):
        """Register a new user."""
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
                
                self.tasks = [
                    Task(
                        id=str(task.id),
                        title=task.title,
                        description=task.description or "",
                        status=task.status,
                        priority=task.priority,
                        due_date=task.due_date or "",
                        created_at=task.created_at.isoformat() if task.created_at else "",
                        updated_at=task.updated_at.isoformat() if task.updated_at else ""
                    )
                    for task in db_tasks
                ]
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
                
                new_task = Task(
                    id=str(new_db_task.id),
                    title=new_db_task.title,
                    description=new_db_task.description or "",
                    status=new_db_task.status,
                    priority=new_db_task.priority,
                    due_date=new_db_task.due_date or "",
                    created_at=new_db_task.created_at.isoformat() if new_db_task.created_at else "",
                    updated_at=new_db_task.updated_at.isoformat() if new_db_task.updated_at else ""
                )
                
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
    
    # Authentication UI methods
    def toggle_login_modal(self):
        """Toggle login modal."""
        self.show_login_modal = not self.show_login_modal
        self.auth_error = ""
    
    def toggle_register_modal(self):
        """Toggle register modal."""
        self.show_register_modal = not self.show_register_modal
        self.auth_error = ""
    
    def reset_form(self):
        """Reset form fields."""
        self.new_task_title = ""
        self.new_task_description = ""
        self.new_task_priority = "medium"
        self.new_task_due_date = ""
    
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

def task_item(task: Task) -> rx.Component:
    """Individual task item component."""
    priority_color = rx.match(
        task.priority,
        ("low", "blue"),
        ("medium", "yellow"),
        ("high", "red"),
        "gray"
    )
    
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(task.title, font_weight="bold", class_name="truncate text-gray-900 dark:text-gray-100"),
                rx.badge(task.priority.upper(), color_scheme=priority_color, size="1"),
                justify="between",
                align="center",
                width="100%"
            ),
            rx.text(task.description, size="2", class_name="line-clamp-2 text-gray-700 dark:text-gray-300"),
            rx.hstack(
                rx.cond(
                    task.due_date != "",
                    rx.text(f"Due: {task.due_date}", size="1", class_name="text-gray-600 dark:text-gray-400"),
                    rx.text("No due date", size="1", class_name="text-gray-600 dark:text-gray-400")
                ),
                rx.cond(
                    task.created_at != "",
                    rx.text(f"Created: {task.created_at[:10]}", size="1", class_name="text-gray-600 dark:text-gray-400"),
                    rx.text("")
                ),
                spacing="2"
            ),
            rx.hstack(
                rx.select(
                    ["todo", "in_progress", "done"],
                    default_value=task.status,
                    on_change=lambda value: State.update_task_status(task.id, value),
                    size="1",
                    width="100px"
                ),
                rx.button(
                    "Edit",
                    on_click=lambda: [State.edit_task(task), State.toggle_add_modal()],
                    size="1",
                    variant="soft"
                ),
                rx.button(
                    "Delete",
                    on_click=lambda: State.delete_task(task.id),
                    size="1",
                    variant="soft",
                    color_scheme="red"
                ),
                spacing="2"
            ),
            spacing="2",
            width="100%"
        ),
        class_name="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow duration-200"
    )


def add_task_modal() -> rx.Component:
    """Modern modal dialog for adding/editing tasks with refined design."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                # Modern header with gradient
                rx.dialog.title(
                    rx.cond(State.is_editing, "Edit Task", "Add New Task"),
                    class_name="text-2xl font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6 dark:from-blue-400 dark:to-purple-400"
                ),
                
                # Modern form container
                rx.vstack(
                    # Title with compact styling
                    rx.vstack(
                        rx.text("Title", 
                               class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                        rx.input(
                            placeholder="Task title...",
                            value=State.new_task_title,
                            on_change=State.set_new_task_title,
                            class_name="w-full px-3 py-2.5 border-0 bg-gray-50 dark:bg-gray-700 dark:text-white rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-600 transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500"
                        ),
                        spacing="1",
                        align_items="start"
                    ),
                    
                    # Description with compact styling
                    rx.vstack(
                        rx.text("Description", 
                               class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                        rx.text_area(
                            placeholder="Add details...",
                            value=State.new_task_description,
                            on_change=State.set_new_task_description,
                            rows="2",
                            class_name="w-full px-3 py-2.5 border-0 bg-gray-50 dark:bg-gray-700 dark:text-white rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-600 transition-all duration-200 resize-none placeholder-gray-400 dark:placeholder-gray-500"
                        ),
                        spacing="1",
                        align_items="start"
                    ),
                    
                    # Priority and Due Date with compact layout
                    rx.hstack(
                        rx.vstack(
                            rx.text("Priority", 
                                   class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                            rx.select(
                                ["low", "medium", "high"],
                                value=State.new_task_priority,
                                on_change=State.set_new_task_priority,
                                class_name="w-full bg-gray-50 dark:bg-gray-700 dark:text-white rounded-lg border-0 px-3 py-2 h-10 focus:outline-none focus:ring-1 focus:ring-blue-500 transition-all duration-200"
                            ),
                            spacing="1",
                            width="100%",
                            align_items="start"
                        ),
                        rx.vstack(
                            rx.text("Due Date", 
                                   class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                            rx.hstack(
                                rx.input(
                                    type="date",
                                    value=State.new_task_due_date,
                                    on_change=State.set_new_task_due_date,
                                    class_name="w-full px-3 py-2 border-0 bg-gray-50 dark:bg-gray-700 dark:text-white rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-600 transition-all duration-200 h-10 text-sm"
                                ),
                                rx.button(
                                    "Clear",
                                    on_click=State.set_new_task_due_date(""),
                                    variant="ghost",
                                    size="1",
                                    class_name="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 px-2 h-10 flex items-center text-sm"
                                ),
                                spacing="1",
                                width="100%"
                            ),
                            # Quick selection buttons
                            rx.hstack(
                                rx.button(
                                    "Today",
                                    on_click=State.set_due_date_today,
                                    size="1",
                                    variant="soft",
                                    class_name="text-xs px-2 py-1 h-6"
                                ),
                                rx.button(
                                    "Tomorrow",
                                    on_click=State.set_due_date_tomorrow,
                                    size="1",
                                    variant="soft",
                                    class_name="text-xs px-2 py-1 h-6"
                                ),
                                rx.button(
                                    "Next Week",
                                    on_click=State.set_due_date_next_week,
                                    size="1",
                                    variant="soft",
                                    class_name="text-xs px-2 py-1 h-6"
                                ),
                                spacing="1",
                                width="100%"
                            ),
                            spacing="1",
                            width="100%",
                            align_items="start"
                        ),
                        spacing="3"
                    ),
                    
                    spacing="4",
                    align_items="stretch"
                ),
                
                # Compact continuous add option
                rx.hstack(
                    rx.checkbox(
                        "Keep adding",
                        checked=State.continuous_add,
                        on_change=State.set_continuous_add,
                        class_name="text-sm text-gray-600 dark:text-gray-400"
                    ),
                    spacing="2"
                ),
                
                # Compact action buttons
                rx.hstack(
                    rx.dialog.close(
                        rx.button(
                            "Cancel",
                            variant="ghost",
                            on_click=lambda: State.cancel_edit(),
                            class_name="px-4 py-2 text-sm font-semibold text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all duration-200"
                        )
                    ),
                    rx.dialog.close(
                        rx.button(
                            rx.cond(State.is_editing, "Save", "Create"),
                            on_click=lambda: rx.cond(
                                State.is_editing,
                                State.update_task(),
                                State.add_task()
                            ),
                            class_name="px-4 py-2 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-lg transition-all duration-200 shadow-md"
                        )
                    ),
                    spacing="2",
                    justify="end",
                    width="100%"
                ),
                
                spacing="4",
                class_name="w-full max-w-sm"
            ),
            class_name="bg-white dark:bg-gray-800 rounded-xl shadow-lg border-0 p-4 max-w-sm"
        ),
        open=State.show_add_modal
    )

def login_modal() -> rx.Component:
    """Login modal dialog."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title(
                    "Sign In",
                    class_name="text-2xl font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6 dark:from-blue-400 dark:to-purple-400"
                ),
                
                rx.form(
                    rx.vstack(
                        rx.vstack(
                            rx.text("Username or Email", 
                                   class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                            rx.input(
                                placeholder="Enter username or email",
                                name="username",
                                required=True,
                                class_name="w-full px-3 py-2.5 border-0 bg-gray-50 dark:bg-gray-700 dark:text-white rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-600 transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500"
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%"
                        ),
                        
                        rx.vstack(
                            rx.text("Password", 
                                   class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                            rx.input(
                                type="password",
                                placeholder="Enter password",
                                name="password",
                                required=True,
                                class_name="w-full px-3 py-2.5 border-0 bg-gray-50 dark:bg-gray-700 dark:text-white rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-600 transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500"
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%"
                        ),
                        
                        rx.cond(
                            State.auth_error != "",
                            rx.text(
                                State.auth_error,
                                color="red",
                                font_size="sm",
                                class_name="text-red-500 dark:text-red-400"
                            )
                        ),
                        
                        rx.hstack(
                            rx.dialog.close(
                                rx.button(
                                    "Cancel",
                                    variant="ghost",
                                    class_name="px-4 py-2 text-sm font-semibold text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all duration-200"
                                )
                            ),
                            rx.dialog.close(
                                rx.button(
                                    "Sign In",
                                    type="submit",
                                    class_name="px-4 py-2 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-lg transition-all duration-200 shadow-md"
                                )
                            ),
                            spacing="2",
                            justify="end",
                            width="100%"
                        ),
                        
                        rx.text(
                            "Don't have an account? ",
                            rx.button(
                                "Sign up here",
                                variant="ghost",
                                on_click=lambda: [
                                    State.toggle_login_modal(),
                                    State.toggle_register_modal()
                                ],
                                class_name="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                            ),
                            class_name="text-sm text-center text-gray-600 dark:text-gray-400"
                        ),
                        
                        spacing="4",
                        width="100%"
                    ),
                    on_submit=State.login_user,
                    reset_on_submit=False,
                ),
                
                spacing="4",
                class_name="w-full max-w-sm"
            ),
            class_name="bg-white dark:bg-gray-800 rounded-xl shadow-lg border-0 p-6 max-w-sm"
        ),
        open=State.show_login_modal
    )

def register_modal() -> rx.Component:
    """Registration modal dialog."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title(
                    "Create Account",
                    class_name="text-2xl font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6 dark:from-blue-400 dark:to-purple-400"
                ),
                
                rx.form(
                    rx.vstack(
                        rx.vstack(
                            rx.text("Username", 
                                   class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                            rx.input(
                                placeholder="Choose a username",
                                name="username",
                                required=True,
                                class_name="w-full px-3 py-2.5 border-0 bg-gray-50 dark:bg-gray-700 dark:text-white rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-600 transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500"
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%"
                        ),
                        
                        rx.vstack(
                            rx.text("Email", 
                                   class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                            rx.input(
                                type="email",
                                placeholder="Enter your email",
                                name="email",
                                required=True,
                                class_name="w-full px-3 py-2.5 border-0 bg-gray-50 dark:bg-gray-700 dark:text-white rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-600 transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500"
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%"
                        ),
                        
                        rx.vstack(
                            rx.text("Password", 
                                   class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                            rx.input(
                                type="password",
                                placeholder="Create a password (min 6 characters)",
                                name="password",
                                required=True,
                                class_name="w-full px-3 py-2.5 border-0 bg-gray-50 dark:bg-gray-700 dark:text-white rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-600 transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500"
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%"
                        ),
                        
                        rx.vstack(
                            rx.text("Confirm Password", 
                                   class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                            rx.input(
                                type="password",
                                placeholder="Confirm your password",
                                name="confirm_password",
                                required=True,
                                class_name="w-full px-3 py-2.5 border-0 bg-gray-50 dark:bg-gray-700 dark:text-white rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-600 transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500"
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%"
                        ),
                        
                        rx.cond(
                            State.auth_error != "",
                            rx.text(
                                State.auth_error,
                                color="red",
                                font_size="sm",
                                class_name="text-red-500 dark:text-red-400"
                            )
                        ),
                        
                        rx.hstack(
                            rx.dialog.close(
                                rx.button(
                                    "Cancel",
                                    variant="ghost",
                                    class_name="px-4 py-2 text-sm font-semibold text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all duration-200"
                                )
                            ),
                            rx.dialog.close(
                                rx.button(
                                    "Create Account",
                                    type="submit",
                                    class_name="px-4 py-2 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-lg transition-all duration-200 shadow-md"
                                )
                            ),
                            spacing="2",
                            justify="end",
                            width="100%"
                        ),
                        
                        rx.text(
                            "Already have an account? ",
                            rx.button(
                                "Sign in here",
                                variant="ghost",
                                on_click=lambda: [
                                    State.toggle_register_modal(),
                                    State.toggle_login_modal()
                                ],
                                class_name="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                            ),
                            class_name="text-sm text-center text-gray-600 dark:text-gray-400"
                        ),
                        
                        spacing="4",
                        width="100%"
                    ),
                    on_submit=State.register_user,
                    reset_on_submit=False,
                ),
                
                spacing="4",
                class_name="w-full max-w-sm"
            ),
            class_name="bg-white dark:bg-gray-800 rounded-xl shadow-lg border-0 p-6 max-w-sm"
        ),
        open=State.show_register_modal
    )

def theme_toggle() -> rx.Component:
    """Theme toggle button component."""
    return rx.color_mode.button(
        variant="ghost",
        size="2",
        class_name="rounded-full p-2 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
    )

def user_profile_section() -> rx.Component:
    """User profile section showing current user info and logout."""
    return rx.hstack(
        rx.hstack(
            rx.icon("user", class_name="w-5 h-5"),
            rx.text(State.current_user.username, font_weight="medium"),
            spacing="2",
            align="center"
        ),
        rx.button(
            "Logout",
            on_click=State.logout_user,
            variant="soft",
            size="1",
            color_scheme="red",
            class_name="text-xs"
        ),
        spacing="3",
        align="center"
    )

def auth_buttons() -> rx.Component:
    """Authentication buttons for login/register."""
    return rx.hstack(
        rx.button(
            "Sign In",
            on_click=State.toggle_login_modal,
            variant="soft",
            size="2"
        ),
        rx.button(
            "Sign Up",
            on_click=State.toggle_register_modal,
            variant="surface",
            size="2",
            color_scheme="blue"
        ),
        spacing="2"
    )

def index() -> rx.Component:
    return rx.fragment(
        rx.container(
            rx.vstack(
                # Header with logo, user info, and theme toggle
                rx.hstack(
                    rx.hstack(
                        rx.icon("clipboard-list", class_name="w-8 h-8 text-blue-600"),
                        rx.heading("Task Dashboard", size="8", class_name="font-bold text-gray-900 dark:text-gray-100"),
                        spacing="3",
                        align="center"
                    ),
                    rx.hstack(
                        rx.cond(
                            State.is_authenticated,
                            user_profile_section(),
                            auth_buttons()
                        ),
                        theme_toggle(),
                        spacing="3",
                        align="center"
                    ),
                    justify="between",
                    align="center",
                    width="100%",
                    class_name="mb-6"
                ),
                
                # Welcome message for non-authenticated users
                rx.cond(
                    ~State.is_authenticated,
                    rx.card(
                        rx.vstack(
                            rx.heading("Welcome to Task Dashboard", size="6", class_name="text-center text-gray-900 dark:text-gray-100"),
                            rx.text(
                                "Your personal task management solution. Create an account to get started with your own task dashboard.",
                                class_name="text-center text-gray-600 dark:text-gray-300",
                                size="4"
                            ),
                            rx.hstack(
                                rx.button(
                                    "Get Started",
                                    on_click=State.toggle_register_modal,
                                    variant="surface",
                                    size="3",
                                    color_scheme="blue",
                                    class_name="font-medium"
                                ),
                                rx.button(
                                    "Sign In",
                                    on_click=State.toggle_login_modal,
                                    variant="soft",
                                    size="3"
                                ),
                                spacing="3",
                                justify="center"
                            ),
                            spacing="4",
                            align="center"
                        ),
                        padding="8",
                        class_name="bg-white dark:bg-gray-800 shadow-lg rounded-xl mb-6"
                    )
                ),

                # Main content - only show when authenticated
                rx.cond(
                    State.is_authenticated,
                    rx.vstack(
                        # Stats cards
                        rx.grid(
                            rx.card(
                                rx.vstack(
                                    rx.text("Total Tasks", size="2", class_name="text-gray-500 dark:text-gray-300"),
                                    rx.text(State.total_tasks, size="6", weight="bold", color="blue"),
                                    rx.text(f"{State.completion_rate}% complete", size="1", class_name="text-gray-500 dark:text-gray-300"),
                                    spacing="1"
                                ),
                                padding="4"
                            ),
                            rx.card(
                                rx.vstack(
                                    rx.text("To Do", size="2", class_name="text-gray-500 dark:text-gray-300"),
                                    rx.text(State.todo_count, size="6", weight="bold", color="orange"),
                                    spacing="1"
                                ),
                                padding="4"
                            ),
                            rx.card(
                                rx.vstack(
                                    rx.text("In Progress", size="2", class_name="text-gray-500 dark:text-gray-300"),
                                    rx.text(State.in_progress_count, size="6", weight="bold", color="yellow"),
                                    spacing="1"
                                ),
                                padding="4"
                            ),
                            rx.card(
                                rx.vstack(
                                    rx.text("Done", size="2", class_name="text-gray-500 dark:text-gray-300"),
                                    rx.text(State.done_count, size="6", weight="bold", color="green"),
                                    spacing="1"
                                ),
                                padding="4"
                            ),
                            columns="4",
                            spacing="4",
                            class_name="grid-cols-2 md:grid-cols-4 mb-6"
                        ),
                        
                        # Search and Filter Controls with Add Task Button
                        rx.card(
                            rx.hstack(
                                rx.input(
                                    placeholder="Search tasks...",
                                    value=State.search_query,
                                    on_change=State.set_search_query,
                                    width="300px",
                                    class_name="border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 bg-white dark:bg-gray-700 dark:text-white"
                                ),
                                rx.select(
                                    ["all", "todo", "in_progress", "done"],
                                    placeholder="Filter by status",
                                    value=State.filter_status,
                                    on_change=State.set_filter_status,
                                    width="150px",
                                    class_name="border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 bg-white dark:bg-gray-700 dark:text-white"
                                ),
                                rx.select(
                                    ["created_at", "due_date", "priority", "title"],
                                    placeholder="Sort by",
                                    value=State.sort_by,
                                    on_change=State.set_sort_by,
                                    width="150px",
                                    class_name="border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 bg-white dark:bg-gray-700 dark:text-white"
                                ),
                                rx.select(
                                    ["asc", "desc"],
                                    placeholder="Order",
                                    value=State.sort_order,
                                    on_change=State.set_sort_order,
                                    width="100px",
                                    class_name="border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 bg-white dark:bg-gray-700 dark:text-white"
                                ),
                                rx.button(
                                    "+ Add Task",
                                    on_click=State.toggle_add_modal,
                                    color_scheme="blue",
                                    size="2",
                                    variant="surface",
                                    class_name="font-medium transition-all duration-200 hover:scale-105"
                                ),
                                spacing="4",
                                align="center",
                                class_name="flex-wrap"
                            ),
                            class_name="bg-white dark:bg-gray-800 border-0 shadow-sm hover:shadow-md transition-all duration-200 mb-6"
                        ),
                    
                        # Task columns
                        rx.grid(
                            rx.vstack(
                                rx.heading("To Do", size="5", class_name="text-gray-900 dark:text-gray-100"),
                                rx.text(f"({State.todo_count} tasks)", size="2", class_name="text-gray-500 dark:text-gray-400"),
                                rx.foreach(
                                    State.tasks_by_status["todo"],
                                    task_item
                                ),
                                spacing="2",
                                width="100%",
                                align_items="stretch"
                            ),
                            rx.vstack(
                                rx.heading("In Progress", size="5", class_name="text-gray-900 dark:text-gray-100"),
                                rx.text(f"({State.in_progress_count} tasks)", size="2", class_name="text-gray-500 dark:text-gray-400"),
                                rx.foreach(
                                    State.tasks_by_status["in_progress"],
                                    task_item
                                ),
                                spacing="2",
                                width="100%",
                                align_items="stretch"
                            ),
                            rx.vstack(
                                rx.heading("Done", size="5", class_name="text-gray-900 dark:text-gray-100"),
                                rx.text(f"({State.done_count} tasks)", size="2", class_name="text-gray-500 dark:text-gray-400"),
                                rx.foreach(
                                    State.tasks_by_status["done"],
                                    task_item
                                ),
                                spacing="2",
                                width="100%",
                                align_items="stretch"
                            ),
                            columns="3",
                            spacing="4",
                            width="100%",
                            class_name="grid-cols-1 md:grid-cols-3"
                        ),
                        
                        rx.cond(
                            State.filtered_tasks.length() == 0,
                            rx.card(
                                rx.text("No tasks found", text_align="center", class_name="text-gray-600 dark:text-gray-300"),
                                padding="8"
                            )
                        ),
                        
                        spacing="4"
                    )
                ),
                
                spacing="4",
                padding="4",
                width="100%"
            ),
            max_width="1200px",
            margin="auto"
        ),
        add_task_modal(),
        login_modal(),
        register_modal()
    )

from task_dashboard.api import api_app

app = rx.App(
    theme=rx.theme(
        accent_color="blue",
        has_background=True,
        radius="large",
        scaling="100%",
    )
)
app.add_page(index, title="Task Dashboard", on_load=State.on_load)

# Mount the FastAPI app for RESTful API endpoints
app._cached_fastapi_app = api_app
