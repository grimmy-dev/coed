"""
Collaborative Code Editor API

Real-time collaborative code editing with FastAPI, WebSockets, and Redis.
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
    Handle application startup and shutdown.

    Startup: Connect to Redis and verify connectivity
    Shutdown: Close Redis connection pool
    """
    # Startup
    await RedisClient.get_client()
    print("✓ Redis connection established")

    yield

    # Shutdown
    await RedisClient.close()
    print("✓ Redis connection closed")


# Initialize FastAPI app
app = FastAPI(
    title="Collaborative Code Editor API",
    description="Real-time collaborative code editing with WebSocket support",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS (allow frontend to make requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
app.include_router(websocket.router, tags=["websocket"])


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok", "service": "collaborative-code-editor", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
