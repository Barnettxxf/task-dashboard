"""Task Dashboard - Modern task management application built with Reflex."""

import reflex as rx
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from rxconfig import config
from task_dashboard.database import db_manager, TaskModel

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

class State(rx.State):
    """The app state for task management."""
    
    # Task data
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
    continuous_add: bool = False
    
    # Cache for computed values
    _computed_tasks: Dict[str, List[Task]] = {}
    
    def toggle_add_modal(self):
        """Toggle the add task modal."""
        self.show_add_modal = not self.show_add_modal
    
    def on_load(self):
        """Load tasks from database when the app loads."""
        with db_manager.get_session() as session:
            db_tasks = session.query(TaskModel).all()
            
            if not db_tasks:
                # Initialize with sample data if database is empty
                sample_tasks = [
                    TaskModel(
                        title="Design new dashboard",
                        description="Create wireframes and mockups for the new dashboard",
                        status="in_progress",
                        priority="high",
                        due_date="2024-12-25"
                    ),
                    TaskModel(
                        title="Implement user authentication",
                        description="Add login and registration functionality",
                        status="todo",
                        priority="medium",
                        due_date="2024-12-28"
                    ),
                    TaskModel(
                        title="Write documentation",
                        description="Document API endpoints and usage examples",
                        status="done",
                        priority="low",
                        due_date="2024-12-20"
                    ),
                ]
                
                session.add_all(sample_tasks)
                session.commit()
                db_tasks = sample_tasks
            
            self.tasks = [
                Task(
                    id=str(task.id),
                    title=task.title,
                    description=task.description,
                    status=task.status,
                    priority=task.priority,
                    due_date=task.due_date,
                    created_at=task.created_at.isoformat() if task.created_at else None,
                    updated_at=task.updated_at.isoformat() if task.updated_at else None
                )
                for task in db_tasks
            ]

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
                rx.text(task.title, font_weight="bold", class_name="truncate"),
                rx.badge(task.priority.upper(), color_scheme=priority_color, size="1"),
                justify="between",
                align="center",
                width="100%"
            ),
            rx.text(task.description, size="2", color="gray", class_name="line-clamp-2"),
            rx.hstack(
                rx.cond(
                    task.due_date != "",
                    rx.text(f"Due: {task.due_date}", size="1", color="gray"),
                    rx.text("No due date", size="1", color="gray")
                ),
                rx.cond(
                    task.created_at != "",
                    rx.text(f"Created: {task.created_at[:10]}", size="1", color="gray"),
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
        class_name="hover:shadow-md transition-shadow duration-200"
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

def theme_toggle() -> rx.Component:
    """Theme toggle button component."""
    return rx.color_mode.button(
        variant="ghost",
        size="2",
        class_name="rounded-full p-2 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
    )

def index() -> rx.Component:
    return rx.fragment(
        rx.container(
            rx.vstack(
                # Header with logo and theme toggle
                rx.hstack(
                    rx.hstack(
                        rx.icon("clipboard-list", class_name="w-8 h-8 text-blue-600"),
                        rx.heading("Task Dashboard", size="8", class_name="font-bold text-gray-900"),
                        spacing="3",
                        align="center"
                    ),
                    theme_toggle(),
                    justify="between",
                    align="center",
                    width="100%",
                    class_name="mb-6"
                ),
                
                # Stats cards
                rx.grid(
                    rx.card(
                        rx.vstack(
                            rx.text("Total Tasks", size="2", color="gray"),
                            rx.text(State.total_tasks, size="6", weight="bold", color="blue"),
                            rx.text(f"{State.completion_rate}% complete", size="1", color="gray"),
                            spacing="1"
                        ),
                        padding="4"
                    ),
                    rx.card(
                        rx.vstack(
                            rx.text("To Do", size="2", color="gray"),
                            rx.text(State.todo_count, size="6", weight="bold", color="orange"),
                            spacing="1"
                        ),
                        padding="4"
                    ),
                    rx.card(
                        rx.vstack(
                            rx.text("In Progress", size="2", color="gray"),
                            rx.text(State.in_progress_count, size="6", weight="bold", color="yellow"),
                            spacing="1"
                        ),
                        padding="4"
                    ),
                    rx.card(
                        rx.vstack(
                            rx.text("Done", size="2", color="gray"),
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
                    class_name="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-all duration-200 mb-6"
                ),
            
                # Task columns
                rx.grid(
                    rx.vstack(
                        rx.heading("To Do", size="5"),
                        rx.text(f"({State.todo_count} tasks)", size="2", color="gray"),
                        rx.foreach(
                            State.tasks_by_status["todo"],
                            task_item
                        ),
                        spacing="2",
                        width="100%",
                        align_items="stretch"
                    ),
                    rx.vstack(
                        rx.heading("In Progress", size="5"),
                        rx.text(f"({State.in_progress_count} tasks)", size="2", color="gray"),
                        rx.foreach(
                            State.tasks_by_status["in_progress"],
                            task_item
                        ),
                        spacing="2",
                        width="100%",
                        align_items="stretch"
                    ),
                    rx.vstack(
                        rx.heading("Done", size="5"),
                        rx.text(f"({State.done_count} tasks)", size="2", color="gray"),
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
                        rx.text("No tasks found", text_align="center", color="gray"),
                        padding="8"
                    )
                ),
                
                spacing="4",
                padding="4",
                width="100%"
            ),
            max_width="1200px",
            margin="auto"
        ),
        add_task_modal()
    )

from task_dashboard.api import api_app

app = rx.App(theme=rx.theme(accent_color="blue"))
app.add_page(index, title="Task Dashboard", on_load=State.on_load)

# Mount the FastAPI app for RESTful API endpoints
app._cached_fastapi_app = api_app
