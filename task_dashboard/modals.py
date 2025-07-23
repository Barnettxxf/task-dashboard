"""Modal dialogs for task dashboard application."""

import reflex as rx
from task_dashboard.state import State

def add_task_modal() -> rx.Component:
    """Modern modal dialog for adding/editing tasks with refined design."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                # Modern header with gradient
                rx.dialog.title(
                    rx.cond(State.is_editing, State.t_edit_task, State.t_add_task),
                    class_name="text-2xl font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6 dark:from-blue-400 dark:to-purple-400"
                ),
                
                # Modern form container
                rx.vstack(
                    # Title with compact styling
                    rx.vstack(
                        rx.text(State.t_title, 
                               class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                        rx.input(
                            placeholder=State.t_title,
                            value=State.new_task_title,
                            on_change=State.set_new_task_title,
                            class_name="w-full px-3 py-2.5 border-0 bg-gray-50 dark:bg-gray-700 dark:text-white rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-600 transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500"
                        ),
                        spacing="1",
                        align_items="start"
                    ),
                    
                    # Description with compact styling
                    rx.vstack(
                        rx.text(State.t_description, 
                               class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                        rx.text_area(
                            placeholder=State.t_description,
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
                            rx.text(State.t_priority, 
                                   class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                            rx.select(
                                rx.cond(
                                    State.current_language == "zh",
                                    ["低", "中", "高"],
                                    ["Low", "Medium", "High"]
                                ),
                                value=rx.cond(
                                    State.current_language == "zh",
                                    rx.match(
                                        State.new_task_priority,
                                        ("low", "低"),
                                        ("medium", "中"),
                                        ("high", "高"),
                                        State.new_task_priority
                                    ),
                                    rx.match(
                                        State.new_task_priority,
                                        ("low", "Low"),
                                        ("medium", "Medium"),
                                        ("high", "High"),
                                        State.new_task_priority
                                    )
                                ),
                                on_change=lambda value: State.set_new_task_priority(
                                    rx.match(
                                        value,
                                        ("低", "low"),
                                        ("中", "medium"),
                                        ("高", "high"),
                                        ("Low", "low"),
                                        ("Medium", "medium"),
                                        ("High", "high"),
                                        value
                                    )
                                ),
                                class_name="w-full bg-gray-50 dark:bg-gray-700 dark:text-white rounded-lg border-0 px-3 py-2 h-10 focus:outline-none focus:ring-1 focus:ring-blue-500 transition-all duration-200"
                            ),
                            spacing="1",
                            width="100%",
                            align_items="start"
                        ),
                        rx.vstack(
                            rx.text(State.t_due_date, 
                                   class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                            rx.hstack(
                                rx.input(
                                    type="date",
                                    value=State.new_task_due_date,
                                    on_change=State.set_new_task_due_date,
                                    class_name="w-full px-3 py-2 border-0 bg-gray-50 dark:bg-gray-700 dark:text-white rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-600 transition-all duration-200 h-10 text-sm"
                                ),
                                rx.button(
                                    State.t_clear,
                                    on_click=lambda: State.set_new_task_due_date(""),
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
                                    State.t_today,
                                    on_click=State.set_due_date_today,
                                    size="1",
                                    variant="soft",
                                    class_name="text-xs px-2 py-1 h-6"
                                ),
                                rx.button(
                                    State.t_tomorrow,
                                    on_click=State.set_due_date_tomorrow,
                                    size="1",
                                    variant="soft",
                                    class_name="text-xs px-2 py-1 h-6"
                                ),
                                rx.button(
                                    State.t_next_week,
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
                        State.t_keep_adding,
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
                            State.t_cancel,
                            variant="ghost",
                            on_click=lambda: State.cancel_edit(),
                            class_name="px-4 py-2 text-sm font-semibold text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all duration-200"
                        )
                    ),
                    rx.dialog.close(
                        rx.button(
                            rx.cond(State.is_editing, State.t_save, State.t_create_task),
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
                    State.t_sign_in,
                    class_name="text-2xl font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6 dark:from-blue-400 dark:to-purple-400"
                ),
                
                rx.form(
                    rx.vstack(
                        rx.vstack(
                            rx.text(State.t_username, 
                                   class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                            rx.input(
                                placeholder=State.t_username,
                                name="username",
                                required=True,
                                class_name="w-full px-3 py-2.5 border-0 bg-gray-50 dark:bg-gray-700 dark:text-white rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-600 transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500"
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%"
                        ),
                        
                        rx.vstack(
                            rx.text(State.t_password, 
                                   class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                            rx.input(
                                type="password",
                                placeholder=State.t_password,
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
                                    State.t_cancel,
                                    variant="ghost",
                                    class_name="px-4 py-2 text-sm font-semibold text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all duration-200"
                                )
                            ),
                            rx.dialog.close(
                                rx.button(
                                    State.t_sign_in,
                                    type="submit",
                                    class_name="px-4 py-2 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-lg transition-all duration-200 shadow-md"
                                )
                            ),
                            spacing="2",
                            justify="end",
                            width="100%"
                        ),
                        
                        rx.text(
                            State.t_dont_have_account + " ",
                            rx.button(
                                State.t_sign_up_here,
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
                    State.t_create_account,
                    class_name="text-2xl font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6 dark:from-blue-400 dark:to-purple-400"
                ),
                
                rx.form(
                    rx.vstack(
                        rx.vstack(
                            rx.text(State.t_username, 
                                   class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                            rx.input(
                                placeholder=State.t_username,
                                name="username",
                                required=True,
                                class_name="w-full px-3 py-2.5 border-0 bg-gray-50 dark:bg-gray-700 dark:text-white rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-600 transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500"
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%"
                        ),
                        
                        rx.vstack(
                            rx.text(State.t_email, 
                                   class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                            rx.input(
                                type="email",
                                placeholder=State.t_email,
                                name="email",
                                required=True,
                                class_name="w-full px-3 py-2.5 border-0 bg-gray-50 dark:bg-gray-700 dark:text-white rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-600 transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500"
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%"
                        ),
                        
                        rx.vstack(
                            rx.text(State.t_password, 
                                   class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                            rx.input(
                                type="password",
                                placeholder=State.t_password + " (min 6 characters)",
                                name="password",
                                required=True,
                                class_name="w-full px-3 py-2.5 border-0 bg-gray-50 dark:bg-gray-700 dark:text-white rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-600 transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500"
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%"
                        ),
                        
                        rx.vstack(
                            rx.text(State.t_confirm_password, 
                                   class_name="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"),
                            rx.input(
                                type="password",
                                placeholder=State.t_confirm_password,
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
                                    State.t_cancel,
                                    variant="ghost",
                                    class_name="px-4 py-2 text-sm font-semibold text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all duration-200"
                                )
                            ),
                            rx.dialog.close(
                                rx.button(
                                    State.t_create_account,
                                    type="submit",
                                    class_name="px-4 py-2 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-lg transition-all duration-200 shadow-md"
                                )
                            ),
                            spacing="2",
                            justify="end",
                            width="100%"
                        ),
                        
                        rx.text(
                            State.t_already_have_account + " ",
                            rx.button(
                                State.t_sign_in_here,
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