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
                            rx.hstack(
                                rx.button(
                                    State.t_tasks_page,
                                    on_click=lambda: State.navigate_to_page("tasks"),
                                    variant=rx.cond(State.current_page == "tasks", "surface", "ghost"),
                                    size="2",
                                    class_name="font-medium"
                                ),
                                rx.button(
                                    State.t_stats_page,
                                    on_click=lambda: State.navigate_to_page("stats"),
                                    variant=rx.cond(State.current_page == "stats", "surface", "ghost"),
                                    size="2",
                                    class_name="font-medium"
                                ),
                                spacing="2"
                            )
                        ),
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
                        # Page content based on current_page
                        rx.cond(
                            State.current_page == "stats",
                            # Statistics Page
                            rx.vstack(
                                # Page Header
                                rx.hstack(
                                    rx.icon("bar-chart-3", size=28, class_name="text-blue-600 dark:text-blue-400"),
                                    rx.heading(
                                        State.t_task_statistics,
                                        size="7",
                                        weight="bold",
                                        class_name="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"
                                    ),
                                    spacing="3",
                                    align="center"
                                ),
                                
                                # Modern Stats Cards with Gradient Backgrounds
                                rx.grid(
                                    # Total Tasks Card
                                    rx.card(
                                        rx.hstack(
                                            rx.vstack(
                                                rx.text(State.t_total_tasks, class_name="text-white/80 text-sm font-medium"),
                                                rx.text(State.total_tasks.to_string(), size="7", weight="bold", class_name="text-white"),
                                                rx.text(
                                                    f"{State.completion_rate.to_string()}% {State.t_completion_rate.lower()}", 
                                                    class_name="text-white/70 text-xs"
                                                ),
                                                spacing="1",
                                                align="start"
                                            ),
                                            rx.spacer(),
                                            rx.box(
                                                rx.text(
                                                    f"{State.completion_rate.to_string()}%",
                                                    size="4",
                                                    weight="bold",
                                                    class_name="text-white"
                                                ),
                                                class_name="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center border-2 border-white/30"
                                            ),
                                            spacing="4",
                                            align="center",
                                            width="100%"
                                        ),
                                        class_name="bg-gradient-to-br from-blue-500 via-blue-600 to-blue-700 dark:from-blue-600 dark:via-blue-700 dark:to-blue-800 border-0 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105"
                                    ),
                                    
                                    # To Do Tasks Card
                                    rx.card(
                                        rx.hstack(
                                            rx.vstack(
                                                rx.text(State.t_todo, class_name="text-white/80 text-sm font-medium"),
                                                rx.text(State.todo_count.to_string(), size="7", weight="bold", class_name="text-white"),
                                                rx.text(
                                                    f"{State.todo_percentage.to_string()}% of total",
                                                    class_name="text-white/70 text-xs"
                                                ),
                                                spacing="1",
                                                align="start"
                                            ),
                                            rx.spacer(),
                                            rx.box(
                                                rx.icon("circle", size=32, class_name="text-white/80"),
                                                class_name="bg-white/20 rounded-full p-3"
                                            ),
                                            spacing="4",
                                            align="center",
                                            width="100%"
                                        ),
                                        class_name="bg-gradient-to-br from-orange-500 via-orange-600 to-red-500 dark:from-orange-600 dark:via-orange-700 dark:to-red-600 border-0 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105"
                                    ),
                                    
                                    # In Progress Tasks Card
                                    rx.card(
                                        rx.hstack(
                                            rx.vstack(
                                                rx.text(State.t_in_progress, class_name="text-white/80 text-sm font-medium"),
                                                rx.text(State.in_progress_count.to_string(), size="7", weight="bold", class_name="text-white"),
                                                rx.text(
                                                    f"{State.in_progress_percentage.to_string()}% of total",
                                                    class_name="text-white/70 text-xs"
                                                ),
                                                spacing="1",
                                                align="start"
                                            ),
                                            rx.spacer(),
                                            rx.box(
                                                rx.icon("loader", size=32, class_name="text-white/80 animate-spin"),
                                                class_name="bg-white/20 rounded-full p-3"
                                            ),
                                            spacing="4",
                                            align="center",
                                            width="100%"
                                        ),
                                        class_name="bg-gradient-to-br from-yellow-500 via-yellow-600 to-orange-500 dark:from-yellow-600 dark:via-yellow-700 dark:to-orange-600 border-0 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105"
                                    ),
                                    
                                    # Done Tasks Card
                                    rx.card(
                                        rx.hstack(
                                            rx.vstack(
                                                rx.text(State.t_done, class_name="text-white/80 text-sm font-medium"),
                                                rx.text(State.done_count.to_string(), size="7", weight="bold", class_name="text-white"),
                                                rx.text(
                                                    f"{State.done_percentage.to_string()}% of total",
                                                    class_name="text-white/70 text-xs"
                                                ),
                                                spacing="1",
                                                align="start"
                                            ),
                                            rx.spacer(),
                                            rx.box(
                                                rx.icon("circle-check", size=32, class_name="text-white/80"),
                                                class_name="bg-white/20 rounded-full p-3"
                                            ),
                                            spacing="4",
                                            align="center",
                                            width="100%"
                                        ),
                                        class_name="bg-gradient-to-br from-green-500 via-green-600 to-emerald-500 dark:from-green-600 dark:via-green-700 dark:to-emerald-600 border-0 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105"
                                    ),
                                    columns="4",
                                    spacing="6",
                                    class_name="grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 mb-8"
                                ),
                                
                                # Modern Analytics Section - Full Width Grid
                                rx.grid(
                                    # Task Progress Chart
                                    rx.card(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon("pie-chart", size=20, class_name="text-purple-600 dark:text-purple-400"),
                                                rx.heading(State.t_task_breakdown, size="5", weight="medium", class_name="text-gray-900 dark:text-white"),
                                                spacing="2"
                                            ),
                                            rx.vstack(
                                                rx.hstack(
                                                    rx.hstack(
                                                        rx.box(class_name="w-3 h-3 bg-orange-500 rounded-full"),
                                                        rx.text(f"{State.t_todo}", class_name="text-gray-700 dark:text-gray-300 font-medium"),
                                                        spacing="2",
                                                        align="center"
                                                    ),
                                                    rx.hstack(
                                                        rx.text(State.todo_count.to_string(), class_name="font-semibold text-orange-600 dark:text-orange-400"),
                                                        rx.text(f"({State.todo_percentage.to_string()}%)", class_name="text-gray-500 dark:text-gray-400 text-sm ml-1"),
                                                        spacing="1",
                                                        align="center"
                                                    ),
                                                    spacing="2",
                                                    justify="between",
                                                    width="100%",
                                                    align="center"
                                                ),
                                                rx.hstack(
                                                    rx.hstack(
                                                        rx.box(class_name="w-3 h-3 bg-yellow-500 rounded-full"),
                                                        rx.text(f"{State.t_in_progress}", class_name="text-gray-700 dark:text-gray-300 font-medium"),
                                                        spacing="2",
                                                        align="center"
                                                    ),
                                                    rx.hstack(
                                                        rx.text(State.in_progress_count.to_string(), class_name="font-semibold text-yellow-600 dark:text-yellow-400"),
                                                        rx.text(f"({State.in_progress_percentage.to_string()}%)", class_name="text-gray-500 dark:text-gray-400 text-sm ml-1"),
                                                        spacing="1",
                                                        align="center"
                                                    ),
                                                    spacing="2",
                                                    justify="between",
                                                    width="100%",
                                                    align="center"
                                                ),
                                                rx.hstack(
                                                    rx.hstack(
                                                        rx.box(class_name="w-3 h-3 bg-green-500 rounded-full"),
                                                        rx.text(f"{State.t_done}", class_name="text-gray-700 dark:text-gray-300 font-medium"),
                                                        spacing="2",
                                                        align="center"
                                                    ),
                                                    rx.hstack(
                                                        rx.text(State.done_count.to_string(), class_name="font-semibold text-green-600 dark:text-green-400"),
                                                        rx.text(f"({State.done_percentage.to_string()}%)", class_name="text-gray-500 dark:text-gray-400 text-sm ml-1"),
                                                        spacing="1",
                                                        align="center"
                                                    ),
                                                    spacing="2",
                                                    justify="between",
                                                    width="100%",
                                                    align="center"
                                                ),
                                                spacing="3",
                                                width="100%"
                                            ),
                                            rx.divider(),
                                            rx.hstack(
                                                rx.box(
                                                    rx.text(
                                                        f"{State.done_percentage.to_string()}%",
                                                        size="5",
                                                        weight="bold",
                                                        class_name="text-green-600 dark:text-green-400"
                                                    ),
                                                    class_name="w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center border-2 border-green-200 dark:border-green-700"
                                                ),
                                                rx.vstack(
                                                    rx.text(State.t_completion_rate, class_name="text-sm text-gray-600 dark:text-gray-400"),
                                                    rx.text(
                                                        f"{State.completion_rate.to_string()}%",
                                                        size="4",
                                                        weight="bold",
                                                        class_name="text-green-600 dark:text-green-400"
                                                    ),
                                                    spacing="1",
                                                    align="start"
                                                ),
                                                spacing="4",
                                                align="center"
                                            ),
                                            spacing="4",
                                            width="100%"
                                        ),
                                        class_name="bg-white dark:bg-gray-800 border-0 shadow-lg hover:shadow-xl transition-all duration-300 w-full"
                                    ),
                                    
                                    # Priority Analytics
                                    rx.card(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon("flag", size=20, class_name="text-red-600 dark:text-red-400"),
                                                rx.heading(State.t_priority_breakdown, size="5", weight="medium", class_name="text-gray-900 dark:text-white"),
                                                spacing="2"
                                            ),
                                            rx.vstack(
                                                rx.hstack(
                                                    rx.hstack(
                                                        rx.box(class_name="w-3 h-3 bg-red-500 rounded-full"),
                                                        rx.text(f"{State.t_high}", class_name="text-gray-700 dark:text-gray-300 font-medium"),
                                                        spacing="2",
                                                        align="center"
                                                    ),
                                                    rx.hstack(
                                                        rx.text(State.high_priority_count.to_string(), class_name="font-semibold text-red-600 dark:text-red-400"),
                                                        rx.box(
                                                            rx.progress(
                                                                value=rx.cond(State.total_tasks > 0, (State.high_priority_count / State.total_tasks) * 100, 0),
                                                                max=100,
                                                                color_scheme="red",
                                                                size="1",
                                                            ),
                                                            class_name="w-20"
                                                        ),
                                                        spacing="2",
                                                        align="center"
                                                    ),
                                                    spacing="2",
                                                    justify="between",
                                                    width="100%",
                                                    align="center"
                                                ),
                                                rx.hstack(
                                                    rx.hstack(
                                                        rx.box(class_name="w-3 h-3 bg-yellow-500 rounded-full"),
                                                        rx.text(f"{State.t_medium}", class_name="text-gray-700 dark:text-gray-300 font-medium"),
                                                        spacing="2",
                                                        align="center"
                                                    ),
                                                    rx.hstack(
                                                        rx.text(State.medium_priority_count.to_string(), class_name="font-semibold text-yellow-600 dark:text-yellow-400"),
                                                        rx.box(
                                                            rx.progress(
                                                                value=rx.cond(State.total_tasks > 0, (State.medium_priority_count / State.total_tasks) * 100, 0),
                                                                max=100,
                                                                color_scheme="yellow",
                                                                size="1",
                                                            ),
                                                            class_name="w-20"
                                                        ),
                                                        spacing="2",
                                                        align="center"
                                                    ),
                                                    spacing="2",
                                                    justify="between",
                                                    width="100%",
                                                    align="center"
                                                ),
                                                rx.hstack(
                                                    rx.hstack(
                                                        rx.box(class_name="w-3 h-3 bg-green-500 rounded-full"),
                                                        rx.text(f"{State.t_low}", class_name="text-gray-700 dark:text-gray-300 font-medium"),
                                                        spacing="2",
                                                        align="center"
                                                    ),
                                                    rx.hstack(
                                                        rx.text(State.low_priority_count.to_string(), class_name="font-semibold text-green-600 dark:text-green-400"),
                                                        rx.box(
                                                            rx.progress(
                                                                value=rx.cond(State.total_tasks > 0, (State.low_priority_count / State.total_tasks) * 100, 0),
                                                                max=100,
                                                                color_scheme="green",
                                                                size="1",
                                                            ),
                                                            class_name="w-20"
                                                        ),
                                                        spacing="2",
                                                        align="center"
                                                    ),
                                                    spacing="2",
                                                    justify="between",
                                                    width="100%",
                                                    align="center"
                                                ),
                                                spacing="3",
                                                width="100%"
                                            ),
                                            rx.divider(),
                                            rx.hstack(
                                                rx.icon("info", size=16, class_name="text-gray-400"),
                                                rx.text(
                                                    f"Total: {State.total_tasks.to_string()} tasks",
                                                    class_name="text-sm text-gray-500 dark:text-gray-400"
                                                ),
                                                spacing="2"
                                            ),
                                            spacing="4",
                                            width="100%"
                                        ),
                                        class_name="bg-white dark:bg-gray-800 border-0 shadow-lg hover:shadow-xl transition-all duration-300 w-full"
                                    ),
                                    columns="2",
                                    spacing="6",
                                    width="100%",
                                    class_name="grid-cols-1 lg:grid-cols-2 mb-8"
                                ),
                                
                                spacing="6",
                                width="100%",
                                class_name="max-w-7xl mx-auto px-4"
                            ),
                            
                            # Tasks Page
                            rx.vstack(
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
                                        rx.text(f"({State.todo_count.to_string()} tasks)", size="2", class_name="text-gray-500 dark:text-gray-400"),
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
                                        rx.text(f"({State.in_progress_count.to_string()} tasks)", size="2", class_name="text-gray-500 dark:text-gray-400"),
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
                                        rx.text(f"({State.done_count.to_string()} tasks)", size="2", class_name="text-gray-500 dark:text-gray-400"),
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
        register_modal(),
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