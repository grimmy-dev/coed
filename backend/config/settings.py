"""
Application configuration loaded from environment variables.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    App settings with environment variable support.

    Create .env file with:
        REDIS_URL=redis://localhost:6379
        CORS_ORIGINS=http://localhost:3000
        ROOM_TTL_SECONDS=7200
    """

    # Redis connection
    redis_url: str = "redis://localhost:6379"

    # CORS - allowed frontend origins
    cors_origins: str = "http://localhost:3000"

    # Frontend base URL (for generating join links)
    base_url: str = "http://localhost:3000"

    # Room ID length in characters (6 chars = 16M combinations)
    room_code_length: int = 6

    # Room expiration time (2 hours = 7200 seconds)
    room_ttl_seconds: int = 7200

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra env vars like NEXT_PUBLIC_*


# Global settings instance (loaded once at startup)
settings = Settings()
