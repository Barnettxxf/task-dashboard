"""Database configuration and models for task management."""

import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone
from urllib.parse import quote_plus

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

Base = declarative_base()

def get_utc_now():
    """Get current UTC time."""
    return datetime.now(timezone.utc)

class UserModel(Base):
    """SQLAlchemy model for users."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

class TaskModel(Base):
    """SQLAlchemy model for tasks."""
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(20), default='todo')
    priority = Column(String(10), default='medium')
    due_date = Column(String(10))
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

class DatabaseManager:
    """Database connection and session management."""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.setup_database()
    
    def setup_database(self):
        """Setup database connection based on environment."""
        db_type = os.getenv('DB_TYPE', 'sqlite').lower().strip()
        
        if db_type == 'mysql':
            # MySQL configuration
            db_host = os.getenv('DB_HOST', 'localhost').strip()
            db_port = os.getenv('DB_PORT', '3306').strip()
            db_user = os.getenv('DB_USER', 'root').strip()
            db_password = os.getenv('DB_PASSWORD', '').strip()
            db_name = os.getenv('DB_NAME', 'task_dashboard').strip()
            
            # URL encode the password to handle special characters
            encoded_password = quote_plus(db_password)
            connection_string = f"mysql+pymysql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"
            print('use mysql')
        else:
            # Default SQLite configuration
            db_path = os.getenv('DB_PATH', 'task_dashboard.db').strip()
            connection_string = f"sqlite:///{db_path}"
            print('use sqlite')
        
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
