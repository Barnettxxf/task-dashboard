"""Authentication and user management functionality."""

import bcrypt
import hashlib
import secrets
from typing import Optional
from task_dashboard.database import UserModel, TaskModel, db_manager

class AuthManager:
    """Handles user authentication and session management."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """Verify password against stored hash."""
        try:
            # First try bcrypt (new format)
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        except:
            # If bcrypt fails, try old SHA-256 format for backward compatibility
            try:
                salt, hash_value = stored_hash.split('$')
                password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
                return password_hash == hash_value
            except:
                return False
    
    @staticmethod
    def create_user(username: str, email: str, password: str) -> Optional[dict]:
        """Create new user account."""
        try:
            with db_manager.get_session() as session:
                # Check if username or email already exists
                existing_user = session.query(UserModel).filter(
                    (UserModel.username == username) | (UserModel.email == email)
                ).first()
                
                if existing_user:
                    return None
                
                password_hash = AuthManager.hash_password(password)
                user = UserModel(
                    username=username,
                    email=email,
                    password_hash=password_hash
                )
                
                session.add(user)
                session.commit()
                session.refresh(user)
                
                return {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[dict]:
        """Authenticate user with username/email and password."""
        try:
            with db_manager.get_session() as session:
                user = session.query(UserModel).filter(
                    (UserModel.username == username) | (UserModel.email == username)
                ).first()
                
                if user and AuthManager.verify_password(password, user.password_hash):
                    return {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    }
                return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[dict]:
        """Get user by ID."""
        try:
            with db_manager.get_session() as session:
                user = session.query(UserModel).filter(UserModel.id == user_id).first()
                if user:
                    return {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    }
                return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None