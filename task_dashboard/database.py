"""Database configuration and models for task management."""

import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class TaskModel(Base):
    """SQLAlchemy model for tasks."""
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(20), default='todo')
    priority = Column(String(10), default='medium')
    due_date = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DatabaseManager:
    """Database connection and session management."""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.setup_database()
    
    def setup_database(self):
        """Setup database connection based on environment."""
        db_type = os.getenv('DB_TYPE', 'sqlite').lower()
        
        if db_type == 'mysql':
            # MySQL configuration
            db_host = os.getenv('DB_HOST', 'localhost')
            db_port = os.getenv('DB_PORT', '3306')
            db_user = os.getenv('DB_USER', 'root')
            db_password = os.getenv('DB_PASSWORD', '')
            db_name = os.getenv('DB_NAME', 'task_dashboard')
            
            connection_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            # Default SQLite configuration
            db_path = os.getenv('DB_PATH', 'task_dashboard.db')
            connection_string = f"sqlite:///{db_path}"
        
        self.engine = create_engine(connection_string, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get database session."""
        return self.SessionLocal()
    
    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()

# Global database manager instance
db_manager = DatabaseManager()