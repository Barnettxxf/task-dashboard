"""Configuration for rate limiting thresholds."""

import os

class RateLimitConfig:
    """Rate limiting configuration settings."""
    
    # Check if we're in a test environment
    IS_TESTING = os.getenv("TESTING", "false").lower() == "true"
    
    # Registration rate limit (requests per minute)
    REGISTER_LIMIT = os.getenv("REGISTER_LIMIT", "100/minute" if IS_TESTING else "5/minute")
    
    # Login rate limit (requests per minute)
    LOGIN_LIMIT = os.getenv("LOGIN_LIMIT", "100/minute" if IS_TESTING else "10/minute")
    
    # General API rate limit (requests per minute)
    API_LIMIT = os.getenv("API_LIMIT", "1000/minute" if IS_TESTING else "100/minute")
    
    # Strict API rate limit for sensitive operations (requests per minute)
    STRICT_API_LIMIT = os.getenv("STRICT_API_LIMIT", "100/minute" if IS_TESTING else "10/minute")