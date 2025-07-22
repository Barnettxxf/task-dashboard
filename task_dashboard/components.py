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
                    on_click=lambda: State.edit_task(task),
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