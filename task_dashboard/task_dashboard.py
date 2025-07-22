"""Task Dashboard - Modern task management application built with Reflex."""

import reflex as rx
from rxconfig import config

from task_dashboard.models import Task, User
from task_dashboard.state import State
from task_dashboard.components import task_item, theme_toggle, user_profile_section, auth_buttons
from task_dashboard.modals import add_task_modal, login_modal, register_modal

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