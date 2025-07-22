# Reflex Development Guide

## How to Develop Reflex Apps

### 1. Core Architecture Pattern

**State-Driven Development**: Every Reflex app follows a reactive state pattern:
- **State Class**: Central data store with reactive variables
- **Event Handlers**: Pure functions that modify state
- **Components**: Declarative UI that reacts to state changes
- **Database Integration**: Seamless SQLAlchemy ORM integration

### 2. Essential Development Steps

#### Setup & Project Structure
```bash
# Install Reflex
pip install reflex

# Create new project
reflex init  # Choose blank template (0)

# Development server
reflex run   # Hot reload enabled
```

#### Basic Component Structure
```python
import reflex as rx

class State(rx.State):
    # Reactive state variables
    tasks: list[dict] = []
    
    # Event handlers (must use @rx.event decorator)
    @rx.event
    def add_task(self, form_data: dict):
        self.tasks.append(form_data)

def index() -> rx.Component:
    return rx.vstack(
        # UI components referencing state
        rx.foreach(State.tasks, render_task),
        spacing="4"
    )

app = rx.App()
app.add_page(index, on_load=State.load_tasks)
```

### 3. Modern Reflex Patterns (2024+)

#### Form Handling with Validation
```python
class TaskFormState(rx.State):
    # Real-time validation
    title: str = ""
    
    @rx.var
    def is_title_valid(self) -> bool:
        return len(self.title.strip()) > 0
    
    @rx.event
    def handle_submit(self, form_data: dict):
        # Server-side validation
        if not self.is_title_valid:
            return rx.toast.error("Title required")
        # Process form...
```

#### Advanced Table Patterns
```python
class TableState(rx.State):
    data: list[dict] = []
    search_value: str = ""
    sort_column: str = "name"
    
    @rx.var(cache=True)
    def filtered_data(self) -> list[dict]:
        # Computed vars for reactive filtering
        data = self.data
        if self.search_value:
            data = [item for item in data 
                   if self.search_value.lower() in str(item).lower()]
        return sorted(data, key=lambda x: x[self.sort_column])
```

### 4. Database Integration Best Practices

#### SQLAlchemy Models
```python
from sqlmodel import SQLModel, Field

class Task(rx.Model, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    status: str = "todo"
    priority: str = "medium"
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

#### Database Operations
```python
class TaskState(rx.State):
    tasks: list[Task] = []
    
    @rx.event
    def load_tasks(self):
        with rx.session() as session:
            self.tasks = session.exec(select(Task)).all()
    
    @rx.event
    def add_task(self, form_data: dict):
        with rx.session() as session:
            task = Task(**form_data)
            session.add(task)
            session.commit()
            self.load_tasks()  # Refresh
```

### 5. Modal/Dialog Implementation

#### Standard Dialog Pattern
```python
def task_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button("Add Task", rx.icon("plus"))
        ),
        rx.dialog.content(
            rx.dialog.title("Create New Task"),
            rx.form(
                rx.vstack(
                    rx.input(placeholder="Task title", name="title", required=True),
                    rx.select(["high", "medium", "low"], name="priority"),
                    rx.flex(
                        rx.dialog.close(rx.button("Cancel", variant="soft")),
                        rx.dialog.close(rx.button("Create", type="submit")),
                        spacing="3"
                    )
                ),
                on_submit=TaskState.add_task
            )
        )
    )
```

### 6. Performance Optimization

#### Efficient State Management
```python
class OptimizedState(rx.State):
    # Backend-only variables (reduce network traffic)
    _all_tasks: list[Task] = []
    
    # Cached computed vars
    @rx.var(cache=True)
    def visible_tasks(self) -> list[Task]:
        # Only recalculates when dependencies change
        return [task for task in self._all_tasks if task.status == "active"]
```

#### Pagination Pattern
```python
class PaginatedState(rx.State):
    offset: int = 0
    limit: int = 10
    
    @rx.event
    def next_page(self):
        self.offset += self.limit
        self.load_data()
    
    @rx.event
    def prev_page(self):
        self.offset = max(0, self.offset - self.limit)
        self.load_data()
```

### 7. Styling & Theming

#### Modern Styling Approach
```python
app = rx.App(
    theme=rx.theme(
        radius="large",
        accent_color="indigo",
        appearance="light"
    )
)
```

#### Component Styling
```python
rx.card(
    rx.text("Task content"),
    style={
        "padding": "1.5rem",
        "border_radius": "0.75rem",
        "box_shadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
        "_hover": {"transform": "translateY(-2px)"}
    }
)
```

### 8. Testing & Deployment

#### Testing Pattern
```python
# Use FastAPI TestClient for API testing
from fastapi.testclient import TestClient

def test_create_task():
    response = client.post("/tasks", json={"title": "Test Task"})
    assert response.status_code == 200
```

#### Production Build
```bash
# Export static build
reflex export

# Deploy to cloud
reflex deploy
```

### 9. Common Patterns Summary

| Pattern | Implementation |
|---------|----------------|
| **CRUD Operations** | State methods + SQLAlchemy |
| **Form Validation** | Client + server validation |
| **Real-time Updates** | Reactive state variables |
| **Modal Forms** | rx.dialog + rx.form |
| **Data Tables** | rx.table + sorting/filtering |
| **File Uploads** | rx.upload component |
| **Authentication** | State-based auth flow |
| **API Integration** | FastAPI backend endpoints |

### 10. Advanced Features

#### Custom Components
```python
@rx.memo
def task_card(task: dict) -> rx.Component:
    return rx.card(
        rx.heading(task["title"]),
        rx.text(task["description"]),
        rx.badge(task["status"])
    )
```

#### Background Tasks
```python
@rx.event(background=True)
def long_running_task(self):
    # Runs in background thread
    result = expensive_computation()
    yield TaskState.update_result(result)
```

---

*This guide is based on Reflex 0.5+ modern patterns and best practices.*