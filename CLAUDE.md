# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Technology Stack
- **Framework**: Reflex (formerly Pynecone) - Python reactive web framework
- **Language**: Python 3.8+
- **Styling**: Tailwind CSS via Reflex's component system
- **State Management**: Built-in reactive state with WebSocket sync

## Development Commands

### Setup and Installation
```bash
pip install -r requirements.txt
```

### Development Server
```bash
reflex run                    # Start dev server on http://localhost:3000
reflex run --port 8080       # Custom port
reflex run --env prod        # Production mode
```

### Build and Export
```bash
reflex export                 # Generate static build for deployment
```

### Debugging
```bash
reflex log                   # View application logs
```

## Architecture Overview

### Core Data Model
- **Task**: Main entity with fields - id, title, description, status (todo/in_progress/done), priority (low/medium/high), due_date, created_at, updated_at

### State Management
- **State class**: Centralized reactive state in task_dashboard.py:21
- **Computed vars**: Real-time filtering, sorting, and statistics (filtered_tasks, task counts, completion rates)
- **CRUD operations**: Full task lifecycle through state methods

### Component Structure
- **index()**: Main dashboard page with statistics header, search/filter controls, and kanban board
- **task_item()**: Reusable task card component with status updates, edit/delete actions
- **add_task_modal()**: Dialog for creating/editing tasks

### Key Features
- **Kanban Board**: Three-column layout (todo, in_progress, done)
- **Search & Filter**: Real-time search, status filtering, sorting by multiple criteria
- **Statistics**: Live task counts, completion rates, priority distribution
- **Responsive Design**: Mobile-first grid layout using Tailwind classes

### Data Flow Pattern
User interaction → State method → Reactive update → UI re-render via WebSocket

### File Structure
- **task_dashboard.py**: All application logic and components
- **rxconfig.py**: Reflex configuration with app settings
- **assets/**: Static assets (favicon.ico)