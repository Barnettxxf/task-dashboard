"""UI components for task dashboard application."""

import reflex as rx
from task_dashboard.models import Task
from task_dashboard.state import State

def task_item(task: Task) -> rx.Component:
    """Individual task item component with modern design."""
    priority_color = rx.match(
        task.priority,
        ("low", "blue"),
        ("medium", "yellow"),
        ("high", "red"),
        "gray"
    )
    
    status_icon = rx.match(
        task.status,
        ("todo", "circle"),
        ("in_progress", "loader"),
        ("done", "circle-check"),
        "circle"
    )
    
    status_color = rx.match(
        task.status,
        ("todo", "text-orange-500"),
        ("in_progress", "text-yellow-500"),
        ("done", "text-green-500"),
        "text-gray-500"
    )
    
    priority_gradient = rx.match(
        task.priority,
        ("low", "bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20"),
        ("medium", "bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20"),
        ("high", "bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20"),
        "bg-gray-50 dark:bg-gray-800/50"
    )
    
    return rx.card(
        rx.vstack(
            # Header with title and priority badge
            rx.hstack(
                rx.hstack(
                    rx.icon(status_icon, class_name=f"w-5 h-5 {status_color} flex-shrink-0"),
                    rx.text(
                        task.title, 
                        font_weight="bold", 
                        class_name="text-lg text-gray-900 dark:text-gray-100 truncate flex-1"
                    ),
                    spacing="2",
                    align="center",
                    flex="1",
                    min_width="0"
                ),
                rx.badge(
                    rx.match(
                        task.priority,
                        ("low", State.t_low.title()),
                        ("medium", State.t_medium.title()),
                        ("high", State.t_high.title()),
                        task.priority.title()
                    ),
                    color_scheme=priority_color,
                    variant="surface",
                    size="2",
                    class_name="font-medium flex-shrink-0"
                ),
                justify="between",
                align="center",
                width="100%",
                spacing="3"
            ),
            
            # Description - more compact
            rx.cond(
                task.description != "",
                rx.text(
                    task.description, 
                    class_name="text-gray-600 dark:text-gray-400 text-sm leading-relaxed line-clamp-2"
                ),
                rx.text(
                    "No description", 
                    class_name="text-gray-400 dark:text-gray-500 text-xs italic"
                )
            ),
            
            # Compact metadata row
            rx.hstack(
                # Due date
                rx.hstack(
                    rx.icon("calendar-days", class_name="w-3.5 h-3.5 text-blue-500"),
                    rx.cond(
                        task.due_date != "",
                        rx.text(
                            task.due_date, 
                            class_name="text-xs text-blue-600 dark:text-blue-400"
                        ),
                        rx.text(
                            "No due", 
                            class_name="text-xs text-gray-400"
                        )
                    ),
                    spacing="1",
                    align="center"
                ),
                
                # Created date
                rx.hstack(
                    rx.icon("clock", class_name="w-3.5 h-3.5 text-green-500"),
                    rx.text(
                        rx.cond(
                            task.created_at != "",
                            task.created_at[:10],
                            "Recent"
                        ), 
                        class_name="text-xs text-green-600 dark:text-green-400"
                    ),
                    spacing="1",
                    align="center"
                ),
                
                # Status
                rx.hstack(
                    rx.icon("tag", class_name="w-3.5 h-3.5 text-purple-500"),
                    rx.text(
                        rx.match(
                            task.status,
                            ("todo", State.t_todo.title()),
                            ("in_progress", State.t_in_progress.title()),
                            ("done", State.t_done.title()),
                            task.status.title()
                        ),
                        class_name="text-xs text-purple-600 dark:text-purple-400 font-medium"
                    ),
                    spacing="1",
                    align="center"
                ),
                spacing="4",
                align="center",
                class_name="flex-wrap"
            ),
            
            # Actions - improved layout
            rx.divider(),
            rx.hstack(
                # Status buttons for direct clicking
                rx.hstack(
                    rx.button(
                        rx.cond(
                            State.current_language == "zh",
                            "待办",
                            "To Do"
                        ),
                        on_click=lambda: State.update_task_status(task.id, "todo"),
                        size="1",
                        variant=rx.cond(task.status == "todo", "surface", "ghost"),
                        color_scheme=rx.cond(task.status == "todo", "orange", "gray"),
                        class_name=rx.cond(
                            task.status == "todo",
                            "font-medium px-2 py-1",
                            "font-medium px-2 py-1 opacity-60"
                        )
                    ),
                    rx.button(
                        rx.cond(
                            State.current_language == "zh",
                            "进行中",
                            "In Progress"
                        ),
                        on_click=lambda: State.update_task_status(task.id, "in_progress"),
                        size="1",
                        variant=rx.cond(task.status == "in_progress", "surface", "ghost"),
                        color_scheme=rx.cond(task.status == "in_progress", "yellow", "gray"),
                        class_name=rx.cond(
                            task.status == "in_progress",
                            "font-medium px-2 py-1",
                            "font-medium px-2 py-1 opacity-60"
                        )
                    ),
                    rx.button(
                        rx.cond(
                            State.current_language == "zh",
                            "已完成",
                            "Done"
                        ),
                        on_click=lambda: State.update_task_status(task.id, "done"),
                        size="1",
                        variant=rx.cond(task.status == "done", "surface", "ghost"),
                        color_scheme=rx.cond(task.status == "done", "green", "gray"),
                        class_name=rx.cond(
                            task.status == "done",
                            "font-medium px-2 py-1",
                            "font-medium px-2 py-1 opacity-60"
                        )
                    ),
                    spacing="2",
                    align="center"
                ),
                
                # Action buttons on right - always visible
                rx.hstack(
                    rx.button(
                        rx.icon("pencil", class_name="w-3.5 h-3.5"),
                        on_click=lambda: State.edit_task(task.id),
                        size="1",
                        variant="surface",
                        color_scheme="blue",
                        class_name="font-medium transition-all duration-200 hover:scale-105 px-2"
                    ),
                    rx.button(
                        rx.icon("trash", class_name="w-3.5 h-3.5"),
                        on_click=lambda: State.delete_task(task.id),
                        size="1",
                        variant="surface",
                        color_scheme="red",
                        class_name="font-medium transition-all duration-200 hover:scale-105 px-2"
                    ),
                    spacing="2",
                    align="center"
                ),
                
                spacing="3",
                align="center",
                width="100%",
                justify="between"
            ),
            spacing="3",
            width="100%"
        ),
        class_name=f"border-0 shadow-md hover:shadow-lg transition-all duration-300 transform hover:scale-[1.01] {priority_gradient}"
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