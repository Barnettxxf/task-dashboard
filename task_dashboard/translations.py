"""Translation system for multi-language support."""

from typing import Dict

class TranslationManager:
    """Manages translations for multiple languages."""
    
    def __init__(self):
        self.translations = {
            "en": {
                # App Title
                "app_title": "Task Dashboard",
                
                # Navigation
                "welcome": "Welcome",
                "sign_in": "Sign In",
                "sign_up": "Sign Up",
                "logout": "Logout",
                "get_started": "Get Started",
                
                # Task Management
                "add_task": "Add Task",
                "edit_task": "Edit Task",
                "delete_task": "Delete Task",
                "update_task": "Update Task",
                "create_task": "Create Task",
                "save": "Save",
                "cancel": "Cancel",
                
                # Task Properties
                "title": "Title",
                "description": "Description",
                "priority": "Priority",
                "status": "Status",
                "due_date": "Due Date",
                "created": "Created",
                "no_due_date": "No due date",
                
                # Priorities
                "low": "Low",
                "medium": "Medium",
                "high": "High",
                
                # Statuses
                "todo": "To Do",
                "in_progress": "In Progress", 
                "done": "Done",
                
                # Statistics
                "total_tasks": "Total Tasks",
                "completion_rate": "Completion Rate",
                "statistics": "Statistics",
                "dashboard": "Dashboard",
                "task_management": "Task Management",
                "tasks_page": "Tasks",
                "stats_page": "Statistics",
                "task_statistics": "Task Statistics",
                "task_breakdown": "Task Breakdown",
                "priority_breakdown": "Priority Breakdown", 
                "todo_percentage": "To Do %",
                "in_progress_percentage": "In Progress %",
                "done_percentage": "Done %",
                
                # Filters
                "search_tasks": "Search tasks...",
                "filter_by_status": "Filter by status",
                "sort_by": "Sort by",
                "order": "Order",
                "all": "All",
                "created_at": "Created At",
                "due_date": "Due Date",
                "title": "Title",
                
                # Messages
                "no_tasks_found": "No tasks found",
                "please_login": "Please login to add tasks",
                "task_added": "Task added successfully!",
                "task_updated": "Task updated successfully!",
                "task_deleted": "Task deleted successfully!",
                "logged_out": "Logged out successfully",
                "welcome_back": "Welcome back",
                
                # Authentication
                "username": "Username",
                "email": "Email",
                "password": "Password",
                "confirm_password": "Confirm Password",
                "create_account": "Create Account",
                "already_have_account": "Already have an account?",
                "dont_have_account": "Don't have an account?",
                "sign_up_here": "Sign up here",
                "sign_in_here": "Sign in here",
                
                # Validation
                "all_fields_required": "All fields are required",
                "passwords_do_not_match": "Passwords do not match",
                "password_too_short": "Password must be at least 6 characters",
                "invalid_credentials": "Invalid username or password",
                
                # Sorting
                "ascending": "Ascending",
                "descending": "Descending",
                
                # Buttons
                "keep_adding": "Keep adding",
                "clear": "Clear",
                "today": "Today",
                "tomorrow": "Tomorrow",
                "next_week": "Next Week",
                
                # Language
                "language": "Language",
                
                # Welcome
                "welcome_to_dashboard": "Welcome to Task Dashboard",
                "dashboard_description": "Your personal task management solution. Create an account to get started with your own task dashboard.",
                
                # Misc
                "tasks": "tasks",
            },
            "zh": {
                # App Title
                "app_title": "任务看板",
                
                # Navigation
                "welcome": "欢迎",
                "sign_in": "登录",
                "sign_up": "注册",
                "logout": "登出",
                "get_started": "开始使用",
                
                # Task Management
                "add_task": "添加任务",
                "edit_task": "编辑任务",
                "delete_task": "删除任务",
                "update_task": "更新任务",
                "create_task": "创建任务",
                "save": "保存",
                "cancel": "取消",
                
                # Task Properties
                "title": "标题",
                "description": "描述",
                "priority": "优先级",
                "status": "状态",
                "due_date": "截止日期",
                "created": "创建于",
                "no_due_date": "无截止日期",
                
                # Priorities
                "low": "低",
                "medium": "中",
                "high": "高",
                
                # Statuses
                "todo": "待办",
                "in_progress": "进行中",
                "done": "已完成",
                
                # Statistics
                "total_tasks": "总任务数",
                "completion_rate": "完成率",
                "statistics": "统计",
                "dashboard": "仪表盘",
                "task_management": "任务管理",
                "tasks_page": "任务",
                "stats_page": "统计",
                "task_statistics": "任务统计",
                "task_breakdown": "任务分布",
                "priority_breakdown": "优先级分布",
                "todo_percentage": "待办百分比",
                "in_progress_percentage": "进行中百分比",
                "done_percentage": "已完成百分比",
                
                # Filters
                "search_tasks": "搜索任务...",
                "filter_by_status": "按状态筛选",
                "sort_by": "排序方式",
                "order": "顺序",
                "all": "全部",
                "created_at": "创建时间",
                "due_date": "截止日期",
                "title": "标题",
                
                # Messages
                "no_tasks_found": "未找到任务",
                "please_login": "请先登录以添加任务",
                "task_added": "任务添加成功！",
                "task_updated": "任务更新成功！",
                "task_deleted": "任务删除成功！",
                "logged_out": "登出成功",
                "welcome_back": "欢迎回来",
                
                # Authentication
                "username": "用户名",
                "email": "邮箱",
                "password": "密码",
                "confirm_password": "确认密码",
                "create_account": "创建账户",
                "already_have_account": "已有账户？",
                "dont_have_account": "没有账户？",
                "sign_up_here": "在此注册",
                "sign_in_here": "在此登录",
                
                # Validation
                "all_fields_required": "所有字段均为必填项",
                "passwords_do_not_match": "密码不匹配",
                "password_too_short": "密码至少需要6个字符",
                "invalid_credentials": "用户名或密码无效",
                
                # Buttons
                "keep_adding": "继续添加",
                "clear": "清除",
                "today": "今天",
                "tomorrow": "明天",
                "next_week": "下周",
                
                # Language
                "language": "语言",
                
                # Welcome
                "welcome_to_dashboard": "欢迎使用任务看板",
                "dashboard_description": "您的个人任务管理解决方案。创建账户开始使用您的专属任务看板。",
                
                # Misc
                "tasks": "任务",
            }
        }
    
    def get_translation(self, language: str, key: str) -> str:
        """Get translation for a specific language and key."""
        return self.translations.get(language, {}).get(key, key)
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get dictionary of available languages."""
        return {
            "en": "English",
            "zh": "中文"
        }

# Global translation manager instance
translation_manager = TranslationManager()