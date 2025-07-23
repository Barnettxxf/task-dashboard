"""Task Dashboard - Modern task management application built with Reflex."""

import reflex as rx
from rxconfig import config

from task_dashboard.models import Task, User
from task_dashboard.state import State
from task_dashboard.components import task_item, theme_toggle, user_profile_section, auth_buttons, language_selector
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
                        language_selector(),
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
                            rx.heading(State.t_welcome_to_dashboard, size="6", class_name="text-center text-gray-900 dark:text-gray-100"),
                            rx.text(
                                State.t_dashboard_description,
                                class_name="text-center text-gray-600 dark:text-gray-300",
                                size="4"
                            ),
                            rx.hstack(
                                rx.button(
                                    State.t_get_started,
                                    on_click=State.toggle_register_modal,
                                    variant="surface",
                                    size="3",
                                    color_scheme="blue",
                                    class_name="font-medium"
                                ),
                                rx.button(
                                    State.t_sign_in,
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
                                    rx.text(State.t_total_tasks, size="2", class_name="text-gray-500 dark:text-gray-300"),
                                    rx.text(State.total_tasks, size="6", weight="bold", color="blue"),
                                    rx.text(f"{State.completion_rate}% {State.t_completion_rate.lower()}", size="1", class_name="text-gray-500 dark:text-gray-300"),
                                    spacing="1"
                                ),
                                padding="4"
                            ),
                            rx.card(
                                rx.vstack(
                                    rx.text(State.t_todo, size="2", class_name="text-gray-500 dark:text-gray-300"),
                                    rx.text(State.todo_count, size="6", weight="bold", color="orange"),
                                    spacing="1"
                                ),
                                padding="4"
                            ),
                            rx.card(
                                rx.vstack(
                                    rx.text(State.t_in_progress, size="2", class_name="text-gray-500 dark:text-gray-300"),
                                    rx.text(State.in_progress_count, size="6", weight="bold", color="yellow"),
                                    spacing="1"
                                ),
                                padding="4"
                            ),
                            rx.card(
                                rx.vstack(
                                    rx.text(State.t_done, size="2", class_name="text-gray-500 dark:text-gray-300"),
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
                                    placeholder=State.t_search_tasks,
                                    value=State.search_query,
                                    on_change=State.set_search_query,
                                    width="300px",
                                    class_name="border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 bg-white dark:bg-gray-700 dark:text-white"
                                ),
                                rx.select(
                                    rx.cond(
                                        State.current_language == "zh",
                                        ["全部", "待办", "进行中", "已完成"],
                                        ["All", "To Do", "In Progress", "Done"]
                                    ),
                                    placeholder=State.t_filter_by_status,
                                    value=rx.cond(
                                        State.current_language == "zh",
                                        rx.match(
                                            State.filter_status,
                                            ("all", "全部"),
                                            ("todo", "待办"),
                                            ("in_progress", "进行中"),
                                            ("done", "已完成"),
                                            State.filter_status
                                        ),
                                        rx.match(
                                            State.filter_status,
                                            ("all", "All"),
                                            ("todo", "To Do"),
                                            ("in_progress", "In Progress"),
                                            ("done", "Done"),
                                            State.filter_status
                                        )
                                    ),
                                    on_change=lambda value: State.set_filter_status(
                                        rx.match(
                                            value,
                                            ("全部", "all"),
                                            ("待办", "todo"),
                                            ("进行中", "in_progress"),
                                            ("已完成", "done"),
                                            ("All", "all"),
                                            ("To Do", "todo"),
                                            ("In Progress", "in_progress"),
                                            ("Done", "done"),
                                            value
                                        )
                                    ),
                                    width="150px",
                                    class_name="border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 bg-white dark:bg-gray-700 dark:text-white"
                                ),
                                rx.select(
                                    rx.cond(
                                        State.current_language == "zh",
                                        ["创建时间", "截止日期", "优先级", "标题"],
                                        ["Created At", "Due Date", "Priority", "Title"]
                                    ),
                                    placeholder=State.t_sort_by,
                                    value=rx.cond(
                                        State.current_language == "zh",
                                        rx.match(
                                            State.sort_by,
                                            ("created_at", "创建时间"),
                                            ("due_date", "截止日期"),
                                            ("priority", "优先级"),
                                            ("title", "标题"),
                                            State.sort_by
                                        ),
                                        rx.match(
                                            State.sort_by,
                                            ("created_at", "Created At"),
                                            ("due_date", "Due Date"),
                                            ("priority", "Priority"),
                                            ("title", "Title"),
                                            State.sort_by
                                        )
                                    ),
                                    on_change=lambda value: State.set_sort_by(
                                        rx.match(
                                            value,
                                            ("创建时间", "created_at"),
                                            ("截止日期", "due_date"),
                                            ("优先级", "priority"),
                                            ("标题", "title"),
                                            ("Created At", "created_at"),
                                            ("Due Date", "due_date"),
                                            ("Priority", "priority"),
                                            ("Title", "title"),
                                            value
                                        )
                                    ),
                                    width="150px",
                                    class_name="border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 bg-white dark:bg-gray-700 dark:text-white"
                                ),
                                rx.select(
                                    rx.cond(
                                        State.current_language == "zh",
                                        ["升序", "降序"],
                                        ["Ascending", "Descending"]
                                    ),
                                    placeholder=State.t_order,
                                    value=rx.cond(
                                        State.current_language == "zh",
                                        rx.match(
                                            State.sort_order,
                                            ("asc", "升序"),
                                            ("desc", "降序"),
                                            State.sort_order
                                        ),
                                        rx.match(
                                            State.sort_order,
                                            ("asc", "Ascending"),
                                            ("desc", "Descending"),
                                            State.sort_order
                                        )
                                    ),
                                    on_change=lambda value: State.set_sort_order(
                                        rx.match(
                                            value,
                                            ("升序", "asc"),
                                            ("降序", "desc"),
                                            ("Ascending", "asc"),
                                            ("Descending", "desc"),
                                            value
                                        )
                                    ),
                                    width="100px",
                                    class_name="border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 bg-white dark:bg-gray-700 dark:text-white"
                                ),
                                rx.button(
                                    State.t_add_task,
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
                                rx.heading(State.t_todo, size="5", class_name="text-gray-900 dark:text-gray-100"),
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
                                rx.heading(State.t_in_progress, size="5", class_name="text-gray-900 dark:text-gray-100"),
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
                                rx.heading(State.t_done, size="5", class_name="text-gray-900 dark:text-gray-100"),
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
                                rx.text(State.t_no_tasks_found, text_align="center", class_name="text-gray-600 dark:text-gray-300"),
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