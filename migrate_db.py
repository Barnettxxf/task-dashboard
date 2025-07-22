#!/usr/bin/env python3
"""Database migration script to add user_id column to tasks table."""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add user_id column to tasks table and populate with default user."""
    db_path = "task_dashboard.db"
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if user_id column already exists
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'user_id' not in columns:
            print("Adding user_id column to tasks table...")
            
            # Add user_id column
            cursor.execute("ALTER TABLE tasks ADD COLUMN user_id INTEGER")
            
            # Create default user if users table is empty
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            if user_count == 0:
                print("Creating default admin user...")
                from task_dashboard.auth import AuthManager
                default_user = AuthManager.create_user("admin", "admin@example.com", "admin123")
                if default_user:
                    default_user_id = default_user['id']
                else:
                    # Manual insert if auth fails
                    cursor.execute("""
                        INSERT INTO users (username, email, password_hash, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, ("admin", "admin@example.com", "default_hash", datetime.utcnow(), datetime.utcnow()))
                    default_user_id = cursor.lastrowid
            else:
                # Use first existing user
                cursor.execute("SELECT id FROM users LIMIT 1")
                default_user_id = cursor.fetchone()[0]
            
            # Update all existing tasks to belong to the default user
            cursor.execute("UPDATE tasks SET user_id = ?", (default_user_id,))
            
            # Make user_id NOT NULL for new tasks
            cursor.execute("UPDATE tasks SET user_id = ? WHERE user_id IS NULL", (default_user_id,))
            
            print(f"Successfully migrated database. Assigned all tasks to user_id: {default_user_id}")
        else:
            print("user_id column already exists")
            
        conn.commit()
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()