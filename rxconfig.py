import reflex as rx

config = rx.Config(
    app_name="task_dashboard",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)