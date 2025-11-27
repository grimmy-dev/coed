"""
Application configuration settings.

Settings are loaded from environment variables with sensible defaults.
"""

import json
from typing import Union

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        redis_url: Redis connection URL
        cors_origins: List of allowed CORS origins
        base_url: Base URL for the application
        room_code_length: Length of generated room codes (in characters)
        room_ttl_seconds: Time-to-live for room data in Redis (in seconds)
    """

    # Redis configuration
    redis_url: str = "redis://localhost:6379"

    # CORS configuration
    cors_origins: str = "http://localhost:3000"

    # Application configuration
    base_url: str = "http://localhost:3000"
    room_code_length: int = 6
    room_ttl_seconds: int = 7200  # 2 hours

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields like NEXT_PUBLIC_*


# Global settings instance
settings = Settings()
