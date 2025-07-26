# Docker Deployment for Task Dashboard

This directory contains Docker configuration files for deploying the Task Dashboard application.

## Files

- `Dockerfile`: Docker image for the application with configurable database settings
- `docker-compose.yml`: Docker Compose configuration
- `.dockerignore`: Files and directories to exclude from Docker builds

## Quick Start with Docker Compose

### For Development (SQLite database)
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### For Production (MySQL database)
Create a `.env` file with your MySQL configuration:
```bash
DB_TYPE=mysql
DB_HOST=your_mysql_host
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=your_database_name
```

Then run:
```bash
# Build and start services with production configuration
docker-compose --env-file .env up -d

# View logs
docker-compose --env-file .env logs -f

# Stop services
docker-compose --env-file .env down
```

The application will be available at:
- Web UI: http://localhost:3000
- API: http://localhost:8000

## Building and Running with Docker

### For Development
```bash
# Build the image
docker build -t task-dashboard .

# Run the container with SQLite (default)
docker run -p 3000:3000 -p 8000:8000 -v $(pwd)/data:/app/data task-dashboard
```

### For Production
```bash
# Run the container with MySQL configuration
docker run -p 3000:3000 -p 8000:8000 \
  -e DB_TYPE=mysql \
  -e DB_HOST=your_mysql_host \
  -e DB_PORT=3306 \
  -e DB_USER=your_mysql_user \
  -e DB_PASSWORD=your_mysql_password \
  -e DB_NAME=your_database_name \
  task-dashboard
```

## Configuration

The application supports both SQLite (default for development) and MySQL (for production) databases.
Database configuration is controlled through environment variables:

### SQLite Configuration (Default)
- `DB_TYPE=sqlite`
- `DB_PATH=/app/data/task_dashboard.db` (default path)

### MySQL Configuration
- `DB_TYPE=mysql`
- `DB_HOST` - Database host
- `DB_PORT` - Database port
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_NAME` - Database name

Environment variables can be passed at runtime or through an `.env` file rather than being hardcoded.

## Data Persistence

When using SQLite (default), data is persisted in a Docker volume named `task_data`. 
When using MySQL, data persistence is handled by your MySQL database setup.

To use a local directory for SQLite data instead of a Docker volume:
```bash
docker run -p 3000:3000 -p 8000:8000 \
  -v $(pwd)/local_data:/app/data \
  -e DB_TYPE=sqlite \
  task-dashboard
```