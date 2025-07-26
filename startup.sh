#!/bin/bash

# startup.sh - Script to start the Task Dashboard application with configurable database

# Default to SQLite for development
export DB_TYPE=${DB_TYPE:-sqlite}
export DB_PATH=${DB_PATH:-/app/data/task_dashboard.db}

# For MySQL, set these environment variables:
# export DB_TYPE=mysql
# export DB_HOST=your_mysql_host
# export DB_PORT=3306
# export DB_USER=your_mysql_user
# export DB_PASSWORD=your_mysql_password
# export DB_NAME=your_database_name

# Start the Reflex application in production mode
reflex run --env prod