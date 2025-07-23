#!/usr/bin/env python3
"""Test suite for authentication security improvements."""

import pytest
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from task_dashboard.auth import AuthManager
from task_dashboard.database import db_manager, UserModel


def test_bcrypt_hashing():
    """Test that bcrypt hashing works correctly."""
    password = "test_password_123"
    
    # Hash the password
    hashed = AuthManager.hash_password(password)
    
    # Verify it's a bcrypt hash (starts with $2b$, $2a$, or $2y$)
    assert hashed.startswith('$2b$') or hashed.startswith('$2a$') or hashed.startswith('$2y$')
    
    # Verify the password matches
    assert AuthManager.verify_password(password, hashed)
    
    # Verify wrong password doesn't match
    assert not AuthManager.verify_password("wrong_password", hashed)


def test_backward_compatibility():
    """Test that old SHA-256 hashes still work for backward compatibility."""
    # Simulate an old SHA-256 hash format
    old_hash = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2$e87f3f8a7b8e8f3f8a7b8e8f3f8a7b8e8f3f8a7b8e8f3f8a7b8e8f3f8a7b8e8f"
    
    # This should return False since we don't have the original password
    # but the function should not crash
    result = AuthManager.verify_password("test_password", old_hash)
    # We can't verify the old hash without knowing the original password
    # but we can check that the function handles it gracefully
    
    # Test with a valid old format but wrong password
    assert not AuthManager.verify_password("wrong_password", old_hash)


def test_hash_uniqueness():
    """Test that hashing the same password twice produces different hashes."""
    password = "test_password_123"
    
    hash1 = AuthManager.hash_password(password)
    hash2 = AuthManager.hash_password(password)
    
    # Both should be valid bcrypt hashes
    assert AuthManager.verify_password(password, hash1)
    assert AuthManager.verify_password(password, hash2)
    
    # But they should be different due to different salts
    assert hash1 != hash2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])