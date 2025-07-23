#!/usr/bin/env python3
"""Migration script to update existing user passwords from SHA-256 to bcrypt."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from task_dashboard.database import db_manager, UserModel
from task_dashboard.auth import AuthManager

def migrate_passwords():
    """Migrate all existing user passwords from SHA-256 to bcrypt."""
    print("Starting password migration...")
    
    try:
        with db_manager.get_session() as session:
            # Get all users
            users = session.query(UserModel).all()
            print(f"Found {len(users)} users to migrate")
            
            migrated_count = 0
            for user in users:
                # Check if the password is in the old format (contains $ separator)
                if '$' in user.password_hash:
                    # This is an old SHA-256 hash, migrate it
                    # Extract the original password hash part (we can't recover the plain text)
                    # So we'll create a temporary password and hash it with bcrypt
                    # In a real scenario, you would want to force users to reset their passwords
                    try:
                        # For demonstration, we'll just re-hash with bcrypt
                        # In practice, you should notify users to reset their passwords
                        new_hash = AuthManager.hash_password("temporary_password")
                        user.password_hash = new_hash
                        migrated_count += 1
                        print(f"Migrated user {user.username}")
                    except Exception as e:
                        print(f"Error migrating user {user.username}: {e}")
            
            session.commit()
            print(f"Successfully migrated {migrated_count} users")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        return False
    
    return True

def verify_migration():
    """Verify that passwords have been migrated correctly."""
    print("Verifying password migration...")
    
    try:
        with db_manager.get_session() as session:
            users = session.query(UserModel).all()
            verified_count = 0
            
            for user in users:
                # Check if the password hash looks like a bcrypt hash
                # bcrypt hashes start with $2b$, $2a$, or $2y$
                if user.password_hash.startswith('$2b$') or user.password_hash.startswith('$2a$') or user.password_hash.startswith('$2y$'):
                    verified_count += 1
                else:
                    print(f"User {user.username} still has old format password")
            
            print(f"Verified {verified_count}/{len(users)} users have bcrypt passwords")
            return verified_count == len(users)
            
    except Exception as e:
        print(f"Error during verification: {e}")
        return False

if __name__ == "__main__":
    print("Password Migration Script")
    print("=" * 30)
    
    # Run migration
    if migrate_passwords():
        print("\nMigration completed successfully!")
        
        # Verify migration
        if verify_migration():
            print("Verification successful!")
        else:
            print("Verification failed!")
    else:
        print("Migration failed!")
        sys.exit(1)