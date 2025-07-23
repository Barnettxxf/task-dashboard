"""UI components for task dashboard application."""

import reflex as rx
from task_dashboard.models import Task
from task_dashboard.state import State

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
                rx.badge(
                    rx.match(
                        task.priority,
                        ("low", State.t_low.upper()),
                        ("medium", State.t_medium.upper()),
                        ("high", State.t_high.upper()),
                        task.priority.upper()
                    ),
                    color_scheme=priority_color, 
                    size="1"
                ),
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
                    rx.cond(
                        State.current_language == "zh",
                        ["待办", "进行中", "已完成"],
                        ["To Do", "In Progress", "Done"]
                    ),
                    default_value=rx.cond(
                        State.current_language == "zh",
                        rx.match(
                            task.status,
                            ("todo", "待办"),
                            ("in_progress", "进行中"),
                            ("done", "已完成"),
                            task.status
                        ),
                        rx.match(
                            task.status,
                            ("todo", "To Do"),
                            ("in_progress", "In Progress"),
                            ("done", "Done"),
                            task.status
                        )
                    ),
                    on_change=lambda value: State.update_task_status(
                        task.id,
                        rx.match(
                            value,
                            ("待办", "todo"),
                            ("进行中", "in_progress"),
                            ("已完成", "done"),
                            ("To Do", "todo"),
                            ("In Progress", "in_progress"),
                            ("Done", "done"),
                            value
                        )
                    ),
                    size="1",
                    width="100px"
                ),
                rx.button(
                    State.t_edit_task,
                    on_click=lambda: State.edit_task(task),
                    size="1",
                    variant="soft"
                ),
                rx.button(
                    State.t_delete_task,
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
            State.t_logout,
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

def language_selector() -> rx.Component:
    """Language selector component."""
    return rx.select.root(
        rx.select.trigger(
            rx.cond(
                State.current_language == "zh",
                rx.text("中文", class_name="text-sm font-medium"),
                rx.text("English", class_name="text-sm font-medium")
            ),
            class_name="text-sm"
        ),
        rx.select.content(
            rx.select.item("English", value="en"),
            rx.select.item("中文", value="zh"),
        ),
        value=State.current_language,
        on_change=State.set_language,
        width="100px"
    )