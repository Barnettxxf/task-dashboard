# Dockerfile for Task Dashboard Application
FROM python:3.11

# Set environment variables with defaults
ENV PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Create data directory for SQLite database persistence
RUN mkdir -p /app/data

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
# Initialize Reflex app
RUN reflex init

# Export frontend for production
RUN reflex export --frontend-only --no-zip

# Needed until Reflex properly passes SIGTERM on backend
STOPSIGNAL SIGTERM

# Expose both ports (3000 for frontend, 8000 for backend)
EXPOSE 3000 8000

# Start the application
CMD reflex run --env prod