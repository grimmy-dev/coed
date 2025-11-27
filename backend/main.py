"""
Collaborative Code Editor API

A real-time collaborative code editing application built with FastAPI,
WebSockets, and Redis for state management and pub/sub messaging.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.redis_client import RedisClient
from config.settings import settings
from routers import rooms, websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.

    Startup:
        - Initialize Redis connection pool
        - Verify Redis connectivity

    Shutdown:
        - Close Redis connection pool
        - Clean up resources
    """
    # Startup
    await RedisClient.get_client()
    print("✓ Redis connection established")

    yield

    # Shutdown
    await RedisClient.close()
    print("✓ Redis connection closed")


# Initialize FastAPI application
app = FastAPI(
    title="Collaborative Code Editor API",
    description="Real-time collaborative code editing with WebSocket support",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
app.include_router(websocket.router, tags=["websocket"])


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Service status and name
    """
    return {"status": "ok", "service": "collaborative-code-editor", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
